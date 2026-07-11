#!/usr/bin/env python3
"""
CBCRAK - decrypt.py
AES-CBC decryption module.
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from colorama import Fore, Style

from utils.banner import print_header, success, error, info, result
from utils.helpers import (get_input, get_key, get_hex_input,
                            to_hex, BLOCK_SIZE, press_enter)
from utils.display import print_key_value_box, print_recovered_block


# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================

def aes_cbc_decrypt(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """Decrypts AES-CBC ciphertext. Returns unpadded plaintext bytes."""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(ciphertext)
    return unpad(decrypted, BLOCK_SIZE)


# ============================================================
# ИНТЕРАКТИВНОЕ МЕНЮ
# ============================================================

def run():
    print_header("DECRYPT — AES-CBC")

    # --- Шифротекст ---
    info("Enter ciphertext as hex (spaces optional)")
    ciphertext = get_hex_input("Ciphertext (hex)")

    # --- IV ---
    info("Enter IV as hex (32 hex chars = 16 bytes)")
    iv = get_hex_input("IV (hex)")
    if len(iv) != 16:
        error("IV must be exactly 16 bytes (32 hex characters). Aborting.")
        return

    # --- Ключ ---
    key = get_key()

    # --- Проверка длины шифротекста ---
    if len(ciphertext) % BLOCK_SIZE != 0:
        error(f"Ciphertext length ({len(ciphertext)} bytes) is not a multiple of {BLOCK_SIZE}. Aborting.")
        return

    # --- Расшифровка ---
    info("Decrypting...")
    try:
        plaintext = aes_cbc_decrypt(ciphertext, key, iv)

        pad_len = len(ciphertext) - len(plaintext) if len(ciphertext) > len(plaintext) else 0

        print_header("RESULTS")
        print_key_value_box({
            "Ciphertext (hex)" : to_hex(ciphertext),
            "IV (hex)"         : to_hex(iv),
            "Key"              : key.decode(),
            "Key size"         : f"AES-{len(key)*8}-CBC",
            "Block count"      : str(len(ciphertext) // BLOCK_SIZE),
            "Padding removed"  : f"{pad_len} bytes",
            "Plaintext"        : plaintext.decode(errors="replace"),
            "Plaintext (hex)"  : to_hex(plaintext),
        })

        success("Decryption complete!")

    except ValueError as e:
        error(f"Decryption failed: {e}")
        info("Possible causes:")
        print(f"  {Fore.YELLOW}  - Wrong key{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  - Wrong IV{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  - Corrupted ciphertext{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}  - Invalid padding (this is the basis of the Padding Oracle attack!){Style.RESET_ALL}")

    press_enter()
