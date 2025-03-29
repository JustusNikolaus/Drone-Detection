import os
import time
from typing import Optional

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text: str):
    """Print a header with a fancy border."""
    width = len(text) + 4
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * width}")
    print(f"= {text} =")
    print(f"{'=' * width}{Colors.ENDC}\n")

def print_success(text: str):
    """Print a success message in green."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print a warning message in yellow."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print an error message in red."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print an info message in blue."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def print_loading(text: str, duration: float = 1.0):
    """Print a loading animation."""
    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    start_time = time.time()
    frame_idx = 0
    
    while time.time() - start_time < duration:
        print(f"\r{Colors.CYAN}{frames[frame_idx]} {text}{Colors.ENDC}", end='', flush=True)
        time.sleep(0.1)
        frame_idx = (frame_idx + 1) % len(frames)
    
    print(f"\r{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_menu(options: list[str], title: Optional[str] = None):
    """Print a numbered menu with options."""
    if title:
        print_header(title)
    
    for i, option in enumerate(options, 1):
        print(f"{Colors.CYAN}{i}. {option}{Colors.ENDC}")

def print_status(text: str, status: str):
    """Print a status message with a colored status indicator."""
    status_colors = {
        'success': Colors.GREEN,
        'warning': Colors.WARNING,
        'error': Colors.FAIL,
        'info': Colors.BLUE
    }
    color = status_colors.get(status.lower(), Colors.ENDC)
    print(f"{color}{text}{Colors.ENDC}") 