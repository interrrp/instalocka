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
