#!/usr/bin/env python3
"""
CBCRAK - xortool.py
XOR utility — hex strings, plaintext strings, binary visualiser.
"""

from colorama import Fore, Style

from utils.banner import print_header, info, success, error, result
from utils.helpers import (get_input, get_hex_input, get_choice,
                            to_hex, to_binary, xor_bytes, press_enter)
from utils.display import print_xor_operation
from utils.banner import print_divider


# ============================================================
# ОСНОВНЫЕ ФУНКЦИИ
# ============================================================

def xor_strings(a: str, b: str) -> bytes:
    """XORs two strings of equal length."""
    return xor_bytes(a.encode(), b.encode())


def xor_hex(a: bytes, b: bytes) -> bytes:
    """XORs two byte strings."""
    return xor_bytes(a, b)


def show_binary_xor(a: int, b: int):
    """Shows XOR of two single bytes in binary, bit by bit."""
    result_byte = a ^ b
    bin_a = to_binary(a)
    bin_b = to_binary(b)
    bin_r = to_binary(result_byte)

    print(f"\n  {Fore.CYAN}Bit-by-bit XOR breakdown:{Style.RESET_ALL}")
    print_divider()

    # Заголовок
    print(f"  {'Bit':<6}", end="")
    for i in range(8):
        print(f"  {7-i}", end="")
    print()
    print_divider()

    # Строка A
    print(f"  {Fore.WHITE}A (0x{a:02x}){Style.RESET_ALL:<3}", end="  ")
    for bit in bin_a:
        colour = Fore.GREEN if bit == "1" else Fore.RED
        print(f"  {colour}{bit}{Style.RESET_ALL}", end="")
    print()

    # Строка B
    print(f"  {Fore.WHITE}B (0x{b:02x}){Style.RESET_ALL:<3}", end="  ")
    for bit in bin_b:
        colour = Fore.GREEN if bit == "1" else Fore.RED
        print(f"  {colour}{bit}{Style.RESET_ALL}", end="")
    print()

    print(f"  {Fore.YELLOW}{'XOR rule':<9}{Style.RESET_ALL}", end="  ")
    for ba, bb in zip(bin_a, bin_b):
        rule = "≠" if ba != bb else "="
        colour = Fore.GREEN if ba != bb else Fore.RED
        print(f"  {colour}{rule}{Style.RESET_ALL}", end="")
    print()

    print_divider()

    # Результат
    print(f"  {Fore.GREEN}{Style.BRIGHT}Result   {Style.RESET_ALL}", end="  ")
    for bit in bin_r:
        colour = Fore.GREEN if bit == "1" else Fore.RED
        print(f"  {colour}{Style.BRIGHT}{bit}{Style.RESET_ALL}", end="")
    print()
    print_divider()

    print(f"\n  {Fore.CYAN}0x{a:02x} XOR 0x{b:02x} = {Fore.GREEN}{Style.BRIGHT}0x{result_byte:02x}{Style.RESET_ALL} "
          f"({result_byte} decimal)")

    # Демонстрация обратимости
    check = result_byte ^ b
    print(f"\n  {Fore.YELLOW}Reversibility check:{Style.RESET_ALL}")
    print(f"  0x{result_byte:02x} XOR 0x{b:02x} = {Fore.GREEN}{Style.BRIGHT}0x{check:02x}{Style.RESET_ALL} "
          f"← back to A! XOR cancels itself out.")


# ============================================================
# ИНТЕРАКТИВНОЕ МЕНЮ
# ============================================================

def run():
    print_header("XOR TOOL")

    info("XOR mode:")
    mode = get_choice([
        "XOR two plaintext strings",
        "XOR two hex strings",
        "Single byte binary breakdown",
        "XOR string with key (repeating)"
    ], "Choose mode")

    if mode == "XOR two plaintext strings":
        a = get_input("String A")
        b = get_input("String B")
        if len(a) != len(b):
            error(f"Lengths must match. A={len(a)}, B={len(b)}")
            press_enter()
            return
        result_bytes = xor_strings(a, b)
        print_xor_operation(a.encode(), b.encode(), result_bytes,
                            label_a=f"A '{a}'",
                            label_b=f"B '{b}'",
                            label_r="A XOR B")
        result("Result (hex)", to_hex(result_bytes))
        result("Result (dec)", " ".join(str(b) for b in result_bytes))

    elif mode == "XOR two hex strings":
        info("Enter two hex strings of equal byte length")
        a = get_hex_input("Hex string A")
        b = get_hex_input("Hex string B")
        if len(a) != len(b):
            error(f"Byte lengths must match. A={len(a)}, B={len(b)}")
            press_enter()
            return
        result_bytes = xor_hex(a, b)
        print_xor_operation(a, b, result_bytes,
                            label_a="A (hex)",
                            label_b="B (hex)",
                            label_r="A XOR B")
        result("Result (hex)", to_hex(result_bytes))

    elif mode == "Single byte binary breakdown":
        info("Enter two single bytes to XOR with full binary breakdown")
        try:
            a = int(get_input("Byte A (decimal or 0x hex)"), 0)
            b = int(get_input("Byte B (decimal or 0x hex)"), 0)
            if not (0 <= a <= 255 and 0 <= b <= 255):
                error("Values must be 0-255")
                press_enter()
                return
            show_binary_xor(a, b)
        except ValueError:
            error("Invalid input. Use decimal (65) or hex (0x41)")

    elif mode == "XOR string with key (repeating)":
        plaintext = get_input("Plaintext string")
        key       = get_input("Key (repeats if shorter than plaintext)")
        key_repeated = (key * ((len(plaintext) // len(key)) + 1))[:len(plaintext)]
        result_bytes = xor_strings(plaintext, key_repeated)
        info(f"Key repeated to match length: '{key_repeated}'")
        print_xor_operation(
            plaintext.encode(), key_repeated.encode(), result_bytes,
            label_a="Plaintext",
            label_b="Key (repeated)",
            label_r="XOR result"
        )
        result("Result (hex)", to_hex(result_bytes))

    success("XOR operation complete!")
    press_enter()
