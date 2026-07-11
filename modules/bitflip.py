#!/usr/bin/env python3
"""
CBCRAK - bitflip.py
CBC Bit Flipping Attack — visual step by step demonstration.
"""

import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from colorama import Fore, Style

from utils.banner import print_header, info, success, error, warning, result
from utils.helpers import (get_input, get_key, get_hex_input, get_choice,
                            generate_random_iv, to_hex, xor_bytes,
                            BLOCK_SIZE, press_enter)
from utils.display import (print_bitflip_step, print_hex_row,
                            print_key_value_box, animate_text)
from utils.banner import print_divider


# ============================================================
# ОСНОВНЫЕ ФУНКЦИИ
# ============================================================

def encrypt_cbc(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    padded = pad(plaintext, BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(padded)


def decrypt_cbc(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    try:
        return unpad(decrypted, BLOCK_SIZE)
    except ValueError:
        return decrypted  # возвращает необработанное, если padding недействителен — все еще показывает изменение


def flip_byte(ciphertext: bytes, block: int, byte_pos: int,
              original_char: str, target_char: str) -> bytes:
    """
    Flips a byte in a ciphertext block to change a specific plaintext byte.

    In CBC, flipping byte i in block N-1 of ciphertext changes byte i in block N of plaintext.
    Formula: ciphertext_byte XOR original_char XOR target_char

    Args:
        ciphertext    : full ciphertext bytes
        block         : which ciphertext block to modify (0-indexed)
        byte_pos      : which byte within that block (0-indexed)
        original_char : the plaintext character currently at that position
        target_char   : the plaintext character we want instead

    Returns:
        Modified ciphertext bytes
    """
    ct = bytearray(ciphertext)
    index = block * BLOCK_SIZE + byte_pos
    ct[index] = ct[index] ^ ord(original_char) ^ ord(target_char)
    return bytes(ct)


# ============================================================
# ПОШАГОВАЯ ВИЗУАЛИЗАЦИЯ
# ============================================================

def show_attack_steps(plaintext: str, key: bytes, iv: bytes,
                      target_block: int, byte_pos: int,
                      original_char: str, target_char: str):
    """Walks through the bit flip attack visually step by step."""

    # Шаг 1: Шифрование
    print_header("STEP 1 — Encrypt original plaintext")
    pt_bytes   = plaintext.encode()
    ciphertext = encrypt_cbc(pt_bytes, key, iv)
    decrypted  = decrypt_cbc(ciphertext, key, iv)

    info(f"Plaintext  : '{plaintext}'")
    print_hex_row("IV", iv)
    print_hex_row("Ciphertext", ciphertext)
    print_hex_row("Decrypted", decrypted)
    time.sleep(0.5)

    # Шаг 2: Объяснение атаки
    print_header("STEP 2 — The bit flip principle")
    info("In CBC decryption:")
    print(f"\n  {Fore.CYAN}  Plaintext[i] = Decrypt(Ciphertext[i]) XOR Ciphertext[i-1]{Style.RESET_ALL}")
    print(f"\n  {Fore.WHITE}  Modifying byte {byte_pos} of ciphertext block {target_block}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}  will change byte {byte_pos} of plaintext block {target_block + 1}{Style.RESET_ALL}")
    print(f"\n  {Fore.YELLOW}  Formula: CT[byte] = CT[byte] XOR ord('{original_char}') XOR ord('{target_char}'){Style.RESET_ALL}")
    time.sleep(0.5)

    # Шаг 3: Выполнить изменение
    print_header("STEP 3 — Flip the byte")
    global_index = target_block * BLOCK_SIZE + byte_pos
    original_ct_byte = ciphertext[global_index]
    modified = flip_byte(ciphertext, target_block, byte_pos, original_char, target_char)
    new_ct_byte = modified[global_index]

    info(f"Target position : block {target_block}, byte {byte_pos} (global index {global_index})")
    info(f"Original CT byte: 0x{original_ct_byte:02x}")
    info(f"XOR with        : ord('{original_char}')=0x{ord(original_char):02x} XOR ord('{target_char}')=0x{ord(target_char):02x} = 0x{ord(original_char)^ord(target_char):02x}")
    info(f"New CT byte     : 0x{new_ct_byte:02x}")
    print_divider()
    print_bitflip_step(3, "Ciphertext before and after flip",
                       ciphertext, modified, global_index)
    time.sleep(0.5)

    # Шаг 4: Расшифровать измененный шифротекст
    print_header("STEP 4 — Decrypt modified ciphertext")
    modified_plaintext = decrypt_cbc(modified, key, iv)

    warning("Note: The block containing the flipped byte will be garbled!")
    warning("Only the TARGET block (next block) gets our intended change.")
    print_divider()
    print_hex_row("Original plaintext", pt_bytes)
    print_hex_row("Modified plaintext", modified_plaintext, byte_pos + BLOCK_SIZE)
    print_divider()

    # Шаг 5: Результат
    print_header("STEP 5 — Result")
    try:
        orig_char_at_pos = chr(pt_bytes[BLOCK_SIZE + byte_pos]) if len(pt_bytes) > BLOCK_SIZE + byte_pos else "?"
        new_char_at_pos  = chr(modified_plaintext[BLOCK_SIZE + byte_pos]) if len(modified_plaintext) > BLOCK_SIZE + byte_pos else "?"
    except Exception:
        orig_char_at_pos = original_char
        new_char_at_pos  = target_char

    print_key_value_box({
        "Original plaintext"  : plaintext,
        "Modified plaintext"  : modified_plaintext.decode(errors="replace"),
        f"Byte {byte_pos} block {target_block+1} was" : f"'{orig_char_at_pos}' (0x{ord(orig_char_at_pos):02x})",
        f"Byte {byte_pos} block {target_block+1} now" : f"'{new_char_at_pos}' (0x{ord(new_char_at_pos):02x})",
    })

    animate_text(f"\n  {Fore.GREEN}{Style.BRIGHT}Bit flip successful! "
                 f"'{original_char}' → '{target_char}' without knowing the key.{Style.RESET_ALL}",
                 delay=0.04)


# ============================================================
# ИНТЕРАКТИВНОЕ МЕНЮ
# ============================================================

def run():
    print_header("BIT FLIPPING ATTACK — CBC")

    info("The CBC bit flipping attack modifies ciphertext bytes to predictably")
    info("change plaintext bytes in the NEXT block — without knowing the key.")
    print_divider()

    # --- Режим ---
    mode = get_choice([
        "Demo mode (auto example — user=guest → user=admin)",
        "Custom mode (enter your own plaintext and target)"
    ], "Choose mode")

    if mode.startswith("Demo"):
        # Классический пример: изменить "guest" на "admin" в блоке 2
        plaintext     = "USERNAME=guestXXXROLE=user.....!"
        key           = get_key("Enter a 16-byte key for this demo")
        iv            = generate_random_iv()
        target_block  = 0   # изменить шифротекст блока 0
        byte_pos      = 9   # позиция 'g' в "guest"
        original_char = "g"
        target_char   = "a"

        info(f"Plaintext    : '{plaintext}'")
        info(f"Target       : change '{original_char}' → '{target_char}' at block {target_block}, byte {byte_pos}")

    else:
        plaintext = get_input("Enter plaintext (at least 32 chars for 2 blocks)")
        if len(plaintext) < BLOCK_SIZE + 1:
            warning(f"Plaintext should be at least {BLOCK_SIZE + 1} chars to affect block 2.")

        key           = get_key()
        iv            = generate_random_iv()

        info("Which byte to flip (in the CIPHERTEXT to change the NEXT plaintext block):")
        try:
            target_block  = int(get_input("Ciphertext block to modify (0-indexed)"))
            byte_pos      = int(get_input(f"Byte position within block (0-{BLOCK_SIZE-1})"))
        except ValueError:
            error("Invalid input. Must be integers.")
            press_enter()
            return

        original_char = get_input("Original character at that plaintext position")
        target_char   = get_input("Target character to flip to")

        if len(original_char) != 1 or len(target_char) != 1:
            error("Must be single characters.")
            press_enter()
            return

    show_attack_steps(plaintext, key, iv, target_block, byte_pos, original_char, target_char)

    success("Bit flip attack demonstration complete!")
    press_enter()
