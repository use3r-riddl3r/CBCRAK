#!/usr/bin/env python3
"""
CBCRAK - banner.py
Handles ASCII art banner and colour definitions.
"""

from colorama import Fore, Back, Style, init

init(autoreset=True)

# ============================================================
# ЯРЛЫКИ ЦВЕТОВ
# ============================================================

SUCCESS  = Fore.GREEN
ERROR    = Fore.RED
WARNING  = Fore.YELLOW
INFO     = Fore.CYAN
HEADER   = Fore.MAGENTA
DIM      = Style.DIM
BOLD     = Style.BRIGHT
RESET    = Style.RESET_ALL
WHITE    = Fore.WHITE


def c(colour, text):
    """Wrap text in a colour."""
    return f"{colour}{text}{RESET}"


# ============================================================
# БАННЕР
# ============================================================

BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}
 ██████╗██████╗  ██████╗██████╗  █████╗ ██╗  ██╗
██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██║ ██╔╝
██║     ██████╔╝██║     ██████╔╝███████║█████╔╝ 
██║     ██╔══██╗██║     ██╔══██╗██╔══██║██╔═██╗ 
╚██████╗██████╔╝╚██████╗██║  ██║██║  ██║██║  ██╗
 ╚═════╝╚═════╝  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
{Style.RESET_ALL}{Fore.WHITE}          CBC Cipher Attack & Research Kit
{Fore.YELLOW}          [ Padding Oracle | Bit Flip | Encrypt | Decrypt ]
{Fore.MAGENTA}          [ github.com/use3r-riddl3r/CBCRAK  ]   
{Style.RESET_ALL}"""


def print_banner():
    print(BANNER)


# ============================================================
# ЗАГОЛОВКИ РАЗДЕЛОВ
# ============================================================

def print_header(title: str):
    width = 55
    bar = "═" * width
    print(f"\n{Fore.CYAN}{Style.BRIGHT}╔{bar}╗")
    print(f"║  {title:<{width-2}}║")
    print(f"╚{bar}╝{Style.RESET_ALL}")


def print_subheader(title: str):
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}  ┌─ {title} {'─' * (45 - len(title))}┐{Style.RESET_ALL}")


def print_divider():
    print(f"{Fore.CYAN}  {'─' * 53}{Style.RESET_ALL}")


# ============================================================
# СООБЩЕНИЯ О СТАТУСЕ
# ============================================================

def success(msg: str):
    print(f"{Fore.GREEN}{Style.BRIGHT}  [+]{Style.RESET_ALL} {msg}")


def error(msg: str):
    print(f"{Fore.RED}{Style.BRIGHT}  [!]{Style.RESET_ALL} {msg}")


def info(msg: str):
    print(f"{Fore.CYAN}{Style.BRIGHT}  [*]{Style.RESET_ALL} {msg}")


def warning(msg: str):
    print(f"{Fore.YELLOW}{Style.BRIGHT}  [~]{Style.RESET_ALL} {msg}")


def result(label: str, value: str):
    print(f"  {Fore.CYAN}{label:<20}{Style.RESET_ALL}: {Fore.WHITE}{Style.BRIGHT}{value}{Style.RESET_ALL}")
