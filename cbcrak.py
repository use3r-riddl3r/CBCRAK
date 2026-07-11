#!/usr/bin/env python3
"""
CBCRAK — CBC Cipher Attack & Research Kit
==========================================
Author  : CBCRAK
Version : 1.0.0
License : MIT

Usage:
    python3 cbcrak.py

Requirements:
    pip install -r requirements.txt
"""

import sys
import re
from colorama import Fore, Style, init

init(autoreset=True)

from utils.banner import print_banner, print_divider, error

# ============================================================
# МЕНЮ
# ============================================================

WIDTH = 75

MENU_ITEMS = [
    ("1", "Encrypt",               "AES-CBC encryption with padding visualiser"),
    ("2", "Decrypt",               "AES-CBC decryption"),
    ("3", "Padding Oracle Attack", "Padding oracle (local or remote URL)"),
    ("4", "Bit Flipping Attack",   "Modify ciphertext to change plaintext"),
    ("5", "Padding Breakdown",     "PKCS#7 padding visualiser and reference"),
    ("6", "XOR Tool",              "XOR strings, hex, binary breakdown"),
    ("7", "Exit",                  ""),
]


def strip_ansi(text: str) -> str:
    return re.compile(r'\x1b\[[0-9;]*m').sub('', text)


def menu_row(key: str, name: str, desc: str, width: int) -> str:
    """
    Builds a menu row with correct border alignment.
    Calculates padding from visible text only, then wraps in colours.
    """
    # Сначала строит простую версию для измерения
    if desc:
        plain = f"  [{key}] {name:<24} {desc}"
    else:
        plain = f"  [{key}] {name}"

    padding = max(0, width - len(plain))

    # Теперь строит цветную версию
    if desc:
        coloured = (
            f"  {Fore.YELLOW}{Style.BRIGHT}[{key}]{Style.RESET_ALL}"
            f" {Fore.WHITE}{Style.BRIGHT}{name:<24}{Style.RESET_ALL}"
            f" {Fore.WHITE}{Style.DIM}{desc}{Style.RESET_ALL}"
        )
    else:
        coloured = (
            f"  {Fore.YELLOW}{Style.BRIGHT}[{key}]{Style.RESET_ALL}"
            f" {Fore.WHITE}{Style.BRIGHT}{name}{Style.RESET_ALL}"
        )

    return f"{Fore.CYAN}  ║{Style.RESET_ALL}{coloured}{' ' * padding}{Fore.CYAN}║{Style.RESET_ALL}"


def print_menu():
    W = WIDTH
    print(f"\n{Fore.CYAN}  ╔{'═' * W}╗{Style.RESET_ALL}")

    # Заголовок
    title = "CBCRAK MENU"
    pad_l = (W - len(title)) // 2
    pad_r = W - len(title) - pad_l
    title_content = f"{' ' * pad_l}{Fore.GREEN}{Style.BRIGHT}{title}{Style.RESET_ALL}{' ' * pad_r}"
    print(f"{Fore.CYAN}  ║{Style.RESET_ALL}{title_content}{Fore.CYAN}║{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  ╠{'═' * W}╣{Style.RESET_ALL}")

    for key, name, desc in MENU_ITEMS:
        if key == "7":
            print(f"{Fore.CYAN}  ╠{'═' * W}╣{Style.RESET_ALL}")
        print(menu_row(key, name, desc, W))

    print(f"{Fore.CYAN}  ╚{'═' * W}╝{Style.RESET_ALL}")


def get_choice() -> str:
    return input(f"\n  {Fore.CYAN}>{Style.RESET_ALL} Choose option: ").strip()


# ============================================================
# ЗАГРУЗЧИК МОДУЛЕЙ
# ============================================================

def load_module(name: str):
    """Lazy loads a module only when needed."""
    try:
        if name == "encrypt":
            from modules.encrypt import run
        elif name == "decrypt":
            from modules.decrypt import run
        elif name == "oracle":
            from modules.oracle import run
        elif name == "bitflip":
            from modules.bitflip import run
        elif name == "padding":
            from modules.padding import run
        elif name == "xortool":
            from modules.xortool import run
        else:
            return None
        return run
    except ImportError as e:
        error(f"Failed to load module '{name}': {e}")
        return None


# ============================================================
# ОСНОВНОЕ
# ============================================================

def main():
    print_banner()

    while True:
        print_menu()
        choice = get_choice()

        if choice == "1":
            run = load_module("encrypt")
            if run: run()
        elif choice == "2":
            run = load_module("decrypt")
            if run: run()
        elif choice == "3":
            run = load_module("oracle")
            if run: run()
        elif choice == "4":
            run = load_module("bitflip")
            if run: run()
        elif choice == "5":
            run = load_module("padding")
            if run: run()
        elif choice == "6":
            run = load_module("xortool")
            if run: run()
        elif choice == "7":
            print(f"\n  {Fore.CYAN}Later!{Style.RESET_ALL}\n")
            sys.exit(0)
        else:
            error("Invalid option. Pick 1-7.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {Fore.YELLOW}Interrupted. Later!{Style.RESET_ALL}\n")
        sys.exit(0)
