#!/usr/bin/env python3
"""
CBCRAK - encrypt.py
AES-CBC encryption module.
"""

import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from colorama import Fore, Style

from utils.banner import print_header, success, info, warning, result
from utils.helpers import (get_input, get_key, get_hex_input, get_choice,
                            generate_random_iv, to_hex, BLOCK_SIZE)
from utils.display import print_padding_visual, print_key_value_box
from utils.helpers import press_enter


# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================

def aes_cbc_encrypt(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    """Encrypts plaintext bytes using AES-CBC. Returns raw ciphertext bytes."""
    padded = pad(plaintext, BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return cipher.encrypt(padded)


# ============================================================
# ИНТЕРАКТИВНОЕ МЕНЮ
# ============================================================

def run():
    print_header("ENCRYPT — AES-CBC")

    # --- Открытый текст ---
    plaintext_str = get_input("Enter plaintext to encrypt")
    plaintext = plaintext_str.encode()

    # --- Ключ ---
    key = get_key()

    # --- IV ---
    info("IV options:")
    iv_choice = get_choice(["Random IV (recommended)", "Custom IV (16 chars)", "Custom IV (hex)"], "Choose IV type")

    if iv_choice == "Random IV (recommended)":
        iv = generate_random_iv()
        warning("Random IV generated — store this alongside your ciphertext!")
    elif iv_choice == "Custom IV (16 chars)":
        while True:
            iv_str = get_input("Enter IV (exactly 16 characters)")
            if len(iv_str) == 16:
                iv = iv_str.encode()
                break
            from utils.banner import error
            error(f"IV must be exactly 16 characters. Yours is {len(iv_str)}.")
    else:
        iv = get_hex_input("Enter IV as hex (32 hex chars = 16 bytes)")
        if len(iv) != 16:
            from utils.banner import error
            error("IV must be 16 bytes. Aborting.")
            return

    # --- Визуализация padding ---
    from Crypto.Util.Padding import pad as crypto_pad
    padded = crypto_pad(plaintext, BLOCK_SIZE)
    info("PKCS#7 padding applied:")
    print_padding_visual(plaintext, padded)

    # --- Шифровать ---
    ciphertext = aes_cbc_encrypt(plaintext, key, iv)

    # --- Размер ключа ---
    key_bits = len(key) * 8

    # --- Результаты ---
    print_header("RESULTS")
    print_key_value_box({
        "Plaintext"       : plaintext_str,
        "Key"             : key.decode(),
        "Key size"        : f"AES-{key_bits}-CBC",
        "IV (hex)"        : to_hex(iv),
        "Ciphertext (hex)": to_hex(ciphertext),
        "Block count"     : str(len(ciphertext) // BLOCK_SIZE),
        "Padding added"   : f"{len(padded) - len(plaintext)} bytes of 0x{padded[-1]:02x}",
    })

    success("Encryption complete!")
    warning("Store the IV alongside the ciphertext — you need it to decrypt.")
    warning("IV is NOT a secret. Key IS a secret.")

    press_enter()
