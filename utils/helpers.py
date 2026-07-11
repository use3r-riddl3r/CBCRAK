#!/usr/bin/env python3
"""
CBCRAK - helpers.py
Shared utility functions used across all modules.
"""

import binascii
import os
from colorama import Fore, Style

from utils.banner import error, warning


BLOCK_SIZE = 16


# ============================================================
# ВСПОМОГАТЕЛИ ВВОДА
# ============================================================

def get_input(prompt: str, allow_empty: bool = False) -> str:
    """Styled input prompt."""
    while True:
        val = input(f"\n  {Fore.CYAN}>{Style.RESET_ALL} {prompt}: ").strip()
        if val or allow_empty:
            return val
        error("Input cannot be empty. Try again.")


def get_key(prompt: str = "Enter key (16, 24, or 32 characters)") -> bytes:
    """Prompts for and validates an AES key."""
    while True:
        key = get_input(prompt)
        if len(key) in [16, 24, 32]:
            return key.encode()
        error(f"Key must be 16, 24, or 32 characters. Yours is {len(key)}.")


def get_hex_input(prompt: str) -> bytes:
    """Prompts for a hex string and converts to bytes."""
    while True:
        val = get_input(prompt)
        try:
            return binascii.unhexlify(val.replace(" ", ""))
        except Exception:
            error("Invalid hex string. Use format: 31 31 31 or 313131")


def get_url(prompt: str = "Enter target URL") -> str:
    """Prompts for a URL."""
    while True:
        url = get_input(prompt)
        if url.startswith("http://") or url.startswith("https://"):
            return url
        error("URL must start with http:// or https://")


def get_choice(options: list, prompt: str = "Choose") -> str:
    """Prompts user to pick from a list of options."""
    for i, opt in enumerate(options, 1):
        print(f"  {Fore.YELLOW}[{i}]{Style.RESET_ALL} {opt}")
    while True:
        choice = get_input(prompt)
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        error(f"Pick a number between 1 and {len(options)}")


# ============================================================
# ВСПОМОГАТЕЛИ КОНВЕРТАЦИИ
# ============================================================

def to_hex(data: bytes, sep: str = " ") -> str:
    """Converts bytes to spaced hex string."""
    return sep.join(f"{b:02x}" for b in data)


def to_bytes(hex_str: str) -> bytes:
    """Converts hex string to bytes, strips spaces."""
    return binascii.unhexlify(hex_str.replace(" ", ""))


def to_binary(byte: int) -> str:
    """Converts a single byte to 8-bit binary string."""
    return format(byte, "08b")


def bytes_to_ascii(data: bytes) -> str:
    """Converts bytes to printable ASCII, replaces non-printable with '.'"""
    return "".join(chr(b) if 32 <= b <= 126 else "." for b in data)


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XORs two byte strings together."""
    return bytes(x ^ y for x, y in zip(a, b))


# ============================================================
# ВСПОМОГАТЕЛИ ПРОВЕРКИ
# ============================================================

def validate_block_size(data: bytes, block_size: int = BLOCK_SIZE) -> bool:
    """Checks if data length is a multiple of block size."""
    return len(data) % block_size == 0


def validate_key_size(key: bytes) -> bool:
    """Checks if key is a valid AES key size."""
    return len(key) in [16, 24, 32]


def validate_iv(iv: bytes) -> bool:
    """Checks if IV is exactly 16 bytes."""
    return len(iv) == BLOCK_SIZE


# ============================================================
# КРИПТО ВСПОМОГАТЕЛИ
# ============================================================

def generate_random_iv() -> bytes:
    """Generates a cryptographically random 16-byte IV."""
    return os.urandom(BLOCK_SIZE)


def split_blocks(data: bytes, block_size: int = BLOCK_SIZE) -> list:
    """Splits data into block_size chunks."""
    return [data[i:i+block_size] for i in range(0, len(data), block_size)]


def pkcs7_pad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    """Applies PKCS#7 padding."""
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def pkcs7_unpad(data: bytes) -> bytes:
    """Removes PKCS#7 padding. Raises ValueError on invalid padding."""
    if not data:
        raise ValueError("Empty data")
    pad_len = data[-1]
    if pad_len == 0 or pad_len > BLOCK_SIZE:
        raise ValueError(f"Invalid padding byte: {pad_len}")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Invalid padding")
    return data[:-pad_len]


def is_valid_padding(data: bytes) -> bool:
    """Returns True if data has valid PKCS#7 padding."""
    try:
        pkcs7_unpad(data)
        return True
    except ValueError:
        return False


# ============================================================
# ПАУЗА / ПРОДОЛЖИТЬ
# ============================================================

def press_enter(msg: str = "Press Enter to continue..."):
    input(f"\n  {Fore.YELLOW}{msg}{Style.RESET_ALL}")
