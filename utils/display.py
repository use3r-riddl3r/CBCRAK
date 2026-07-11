#!/usr/bin/env python3
"""
CBCRAK - display.py
Progress bars, byte displays, and formatted output helpers.
"""

import time
from colorama import Fore, Style
from tqdm import tqdm

from utils.banner import success, info, result, print_divider, RESET


# ============================================================
# ПАНЕЛЬ ПРОГРЕССА
# ============================================================

def brute_force_bar(total: int = 256, desc: str = "Brute forcing") -> tqdm:
    """Returns a styled tqdm progress bar for brute force loops."""
    return tqdm(
        total=total,
        desc=f"{Fore.YELLOW}  {desc}{Style.RESET_ALL}",
        bar_format="  {l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
        colour="yellow",
        leave=False
    )


# ============================================================
# ОТОБРАЖЕНИЕ БАЙТ/HEX
# ============================================================

def print_hex_row(label: str, data: bytes, highlight_index: int = None):
    """
    Prints a row of hex bytes with optional highlighted byte.
    highlight_index: which byte to highlight in green (0-indexed)
    """
    label_str = f"  {Fore.CYAN}{label:<20}{Style.RESET_ALL}:"
    hex_bytes = []
    for i, b in enumerate(data):
        byte_str = f"{b:02x}"
        if i == highlight_index:
            hex_bytes.append(f"{Fore.GREEN}{Style.BRIGHT}{byte_str}{Style.RESET_ALL}")
        else:
            hex_bytes.append(f"{Fore.WHITE}{byte_str}{Style.RESET_ALL}")
    print(f"{label_str} {' '.join(hex_bytes)}")


def print_xor_operation(a: bytes, b: bytes, result: bytes,
                        label_a: str = "A", label_b: str = "B", label_r: str = "A XOR B"):
    """Prints a formatted XOR operation showing three rows."""
    print_divider()
    print_hex_row(label_a, a)
    print(f"  {Fore.YELLOW}{'XOR':<21}{Style.RESET_ALL}  {'  '.join(['^^'] * len(b))}")
    print_hex_row(label_b, b)
    print(f"  {Fore.YELLOW}{'='*53}{Style.RESET_ALL}")
    print_hex_row(label_r, result)
    print_divider()


def print_padding_visual(plaintext: bytes, padded: bytes, block_size: int = 16):
    """Visual display of PKCS#7 padding being applied."""
    pad_len = len(padded) - len(plaintext)
    pad_val = padded[-1]

    print(f"\n  {Fore.CYAN}Plaintext bytes:{Style.RESET_ALL}")
    pt_hex = [f"{Fore.WHITE}{b:02x}{Style.RESET_ALL}" for b in plaintext]
    print(f"  {' '.join(pt_hex)}")

    print(f"\n  {Fore.CYAN}After PKCS#7 padding (+{pad_len} bytes of 0x{pad_val:02x}):{Style.RESET_ALL}")
    padded_display = []
    for i, b in enumerate(padded):
        if i >= len(plaintext):
            padded_display.append(f"{Fore.YELLOW}{Style.BRIGHT}{b:02x}{Style.RESET_ALL}")
        else:
            padded_display.append(f"{Fore.WHITE}{b:02x}{Style.RESET_ALL}")
    print(f"  {' '.join(padded_display)}")


# ============================================================
# ОТОБРАЖЕНИЕ АТАКИ ОРАКУЛА
# ============================================================

def print_oracle_progress(byte_index: int, found_value: int,
                          intermediate: int, plaintext_byte: int, total: int = 16):
    """Prints progress of padding oracle attack for each found byte."""
    bar = f"{Fore.GREEN}{'█' * (total - byte_index)}{Fore.RED}{'░' * byte_index}{Style.RESET_ALL}"
    print(f"\n  {bar}")
    success(
        f"Byte {total - byte_index:>2}/{total} │ "
        f"guess={Fore.YELLOW}0x{found_value:02x}{Style.RESET_ALL} │ "
        f"intermediate={Fore.CYAN}0x{intermediate:02x}{Style.RESET_ALL} │ "
        f"plaintext={Fore.GREEN}{Style.BRIGHT}0x{plaintext_byte:02x} "
        f"({chr(plaintext_byte) if 32 <= plaintext_byte <= 126 else '?'}){Style.RESET_ALL}"
    )


def print_recovered_block(raw_bytes: list, label: str = "Recovered block"):
    """Prints a fully recovered block with hex and ASCII side by side."""
    print_divider()
    hex_part = " ".join(f"{b:02x}" for b in raw_bytes)
    ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in raw_bytes)
    result(label + " (hex)", hex_part)
    result(label + " (ascii)", ascii_part)
    print_divider()


# ============================================================
# ОТОБРАЖЕНИЕ BIT FLIP
# ============================================================

def print_bitflip_step(step: int, description: str, before: bytes,
                       after: bytes, changed_index: int):
    """Shows a step in the bit flipping attack."""
    print(f"\n  {Fore.MAGENTA}{Style.BRIGHT}Step {step}: {description}{Style.RESET_ALL}")
    print_hex_row("Before", before, changed_index)
    print_hex_row("After ", after,  changed_index)


# ============================================================
# ОБЩИЕ ВСПОМОГАТЕЛИ
# ============================================================

def print_key_value_box(items: dict):
    """Prints a neat box of key-value pairs."""
    print_divider()
    for k, v in items.items():
        result(k, v)
    print_divider()


def animate_text(text: str, delay: float = 0.03):
    """Prints text character by character for dramatic effect."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def confirm(prompt: str) -> bool:
    """Yes/no confirmation prompt."""
    ans = input(f"\n  {Fore.YELLOW}{prompt} [y/N]: {Style.RESET_ALL}").strip().lower()
    return ans == "y"
