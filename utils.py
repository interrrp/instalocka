import ctypes
from functools import lru_cache

import pyautogui


@lru_cache(maxsize=None)
def get_screen_size() -> tuple[int, int]:
    """Get the size of the screen in pixels."""
    return pyautogui.size()


@lru_cache(maxsize=None)
def get_screen_size_str() -> str:
    """Gets the screen size as a string in the :code:`WxH` format."""

    screen_size = get_screen_size()
    return f"{screen_size[0]}x{screen_size[1]}"


def get_active_window_title() -> str | None:
    """Gets the current active window title (for Windows only)"""

    user32 = ctypes.windll.user32

    # Foreground window = "active" window
    foreground_window = user32.GetForegroundWindow()

    # *sigh* Get the window title by the Windows C API
    title_len = user32.GetWindowTextLengthW(foreground_window)
    buf = ctypes.create_unicode_buffer(title_len + 1)
    user32.GetWindowTextW(foreground_window, buf, title_len + 1)

    return buf.value


def is_focused_on_valorant() -> bool:
    """Check if the foreground (active) window is VALORANT."""

    active_window_title = get_active_window_title()
    return active_window_title is not None and active_window_title.startswith("VALORANT")
