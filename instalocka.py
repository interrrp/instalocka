#! /usr/bin/python3

import os
from argparse import ArgumentParser

import pyautogui

pyautogui.PAUSE = 0.01


class ImageNotFoundException(Exception):
    pass


def parse_args() -> dict:
    """Parse command-line arguments into a dictionary using :code:`ArgumentParser`."""

    parser = ArgumentParser(prog="instalocka", description="Insta-lock your favorite VALORANT agent!")
    parser.add_argument("agent", help="The agent to instalock")

    # Parse the arguments, then "turn" it into a dictionary using __dict__
    return parser.parse_args().__dict__


def click_agent(agent: str) -> None:
    """Aim and click at the agent's avatar."""

    # Validate the avatar image, if it actually exists
    avatar_path = f"assets/avatars/{agent}.png"
    if not os.path.exists(avatar_path):
        raise ValueError(f"Avatar image {avatar_path} does not exist")

    # Locate the avatar on the screen
    avatar_pos = pyautogui.locateOnScreen(avatar_path, grayscale=True, confidence=0.8)

    # Was it actually found?
    if not avatar_pos:
        raise ImageNotFoundException(f"The avatar for agent {agent.title()} was not found on the screen")

    # Get the center of the avatar to prevent the chance of clicking on the wrong thing
    avatar_pos_center = pyautogui.center(avatar_pos)

    # Click on it :D
    pyautogui.click(avatar_pos_center)


def lock_in() -> None:
    """Click the lock in button."""

    # Locate the button
    lock_in_button_pos = pyautogui.locateOnScreen("assets/lock_in.png", grayscale=True, confidence=0.8)

    # Was it actually found?
    if not lock_in_button_pos:
        raise ImageNotFoundException("Could not find the lock in button")

    # Blah blah blah, center of button
    lock_in_button_pos_center = pyautogui.center(lock_in_button_pos)

    # Lock!
    # I know I could've used pyautogui.click, but the click doesn't register
    pyautogui.moveTo(lock_in_button_pos_center)
    pyautogui.mouseDown()
    pyautogui.mouseUp()


def main() -> None:
    args = parse_args()
    agent = args["agent"]

    print(f"Watching for {agent.title()}...")
    while True:
        try:
            click_agent(agent)
            lock_in()
        except ImageNotFoundException:
            pass
        else:
            print("Locked!")
            break


if __name__ == "__main__":
    main()