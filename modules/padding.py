#!/usr/bin/env python3
"""
CBCRAK - padding.py
PKCS#7 padding breakdown and visualiser.
"""

import binascii
from Crypto.Util.Padding import pad
from colorama import Fore, Style

from utils.banner import print_header, info, success, result
from utils.helpers import get_input, to_hex, BLOCK_SIZE, press_enter
from utils.display import print_padding_visual
from utils.banner import print_divider


# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================

def pkcs7_breakdown(plaintext: str, block_size: int = BLOCK_SIZE) -> dict:
    """Returns full PKCS#7 padding breakdown for a plaintext string."""
    pt_bytes   = plaintext.encode()
    padded     = pad(pt_bytes, block_size)
    pad_len    = block_size - (len(pt_bytes) % block_size)
    if pad_len == 0:
        pad_len = block_size
    pad_val    = padded[-1]
    blocks     = [padded[i:i+block_size] for i in range(0, len(padded), block_size)]

    return {
        "plaintext"    : plaintext,
        "pt_bytes"     : pt_bytes,
        "padded"       : padded,
        "pad_len"      : pad_len,
        "pad_val"      : pad_val,
        "blocks"       : blocks,
        "block_size"   : block_size,
        "total_length" : len(padded),
    }


# ============================================================
# ИНТЕРАКТИВНОЕ МЕНЮ
# ============================================================

def run():
    print_header("PKCS#7 PADDING BREAKDOWN")

    plaintext = get_input("Enter plaintext to analyse")
    breakdown = pkcs7_breakdown(plaintext)

    pt_bytes = breakdown["pt_bytes"]
    pad_len  = breakdown["pad_len"]
    pad_val  = breakdown["pad_val"]
    padded   = breakdown["padded"]
    blocks   = breakdown["blocks"]

    # --- Сводка ---
    print_divider()
    result("Plaintext",      plaintext)
    result("Length",         f"{len(pt_bytes)} bytes")
    result("Block size",     f"{BLOCK_SIZE} bytes")
    result("Blocks needed",  str(len(blocks)))
    result("Bytes short",    f"{pad_len} bytes")
    result("Padding value",  f"0x{pad_val:02x} ({pad_val} decimal)")
    result("Padding rule",   f"Add {pad_len} bytes of 0x{pad_val:02x}")
    print_divider()

    # --- Визуализация ---
    info("Padding visualised:")
    print_padding_visual(pt_bytes, padded)

    # --- Разбор блоков ---
    info(f"Block breakdown ({len(blocks)} block{'s' if len(blocks) > 1 else ''}):")
    for i, block in enumerate(blocks, 1):
        hex_bytes = []
        for j, b in enumerate(block):
            byte_str = f"{b:02x}"
            global_index = (i - 1) * BLOCK_SIZE + j
            if global_index >= len(pt_bytes):
                hex_bytes.append(f"{Fore.YELLOW}{Style.BRIGHT}{byte_str}{Style.RESET_ALL}")
            else:
                hex_bytes.append(f"{Fore.WHITE}{byte_str}{Style.RESET_ALL}")
        print(f"\n  {Fore.CYAN}Block {i}:{Style.RESET_ALL} {' '.join(hex_bytes)}")

    print(f"\n  {Fore.YELLOW}Yellow bytes = padding{Style.RESET_ALL}")

    # --- Примечание особого случая ---
    if len(pt_bytes) % BLOCK_SIZE == 0:
        print(f"\n  {Fore.YELLOW}[~]{Style.RESET_ALL} Plaintext was already a multiple of {BLOCK_SIZE} bytes.")
        print(f"      A full extra block of {BLOCK_SIZE} × 0x{pad_val:02x} was added.")
        print(f"      This ensures the receiver can always find and strip padding.")

    # --- Справочная таблица PKCS#7 ---
    info("PKCS#7 quick reference (for 16-byte AES blocks):")
    print_divider()
    print(f"  {Fore.CYAN}{'Bytes short':<15} {'Pad value':<12} {'Example (last 4 bytes)'}{Style.RESET_ALL}")
    print_divider()
    for n in [1, 2, 3, 4, 5, 6, 7, 8, 14, 15, 16]:
        example = " ".join(f"{n:02x}" for _ in range(min(n, 4)))
        if n > 4:
            example = f"... {example}"
        active = f"{Fore.GREEN}← you{Style.RESET_ALL}" if n == pad_len else ""
        print(f"  {n:<15} 0x{n:02x}        {example}  {active}")
    print_divider()

    success("Padding breakdown complete!")
    press_enter()
