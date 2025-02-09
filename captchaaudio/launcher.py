#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
from rich.console import Console

MYOUTPUT_DIR = "0_out/"  # all results are saved in this local directory

console = Console()


def get_platformType():
    """A function to dermine the OS type."""
    platforms = {
        "darwin": "OSX",
        "win32": "Windows",
        "linux1": "Linux",
        "linux2": "Linux",
    }
    if sys.platform not in platforms:
        return sys.platform
    return platforms[sys.platform]


# end of get_platformType()


def playSound(fname_str: str) -> None:
    """A function to play the outputted wav file"""

    console.print(f"\t [bright_green] PLAYING wav file :[bright_cyan]{fname_str}")

    platform_str = get_platformType()
    if platform_str.lower() == "linux":
        console.print(
            f"\t [bright_blue] Playing wav using aplay on Linux...[/bright_blue]"
        )
        os.system(f"aplay {fname_str}")  # this may only work on linux machines...

    if platform_str.lower() == "osx":
        console.print(
            f"\t [bright_blue] Playing wav using aplay on MacOS...[/bright_blue]"
        )
        os.system(f"afplay {fname_str}")  # this may only work on linux machines...


# end of playSound()


def checkDataDir(dir_str):
    """A function to determine whether a data output directory exists.
    if the directory does not exist, then it is created."""

    try:
        os.makedirs(dir_str)
        # if MYOUTPUT_DIR doesn't exist, create directory
        # printByPlatform("\t Creating :{}".format(dir_str))
        return 1

    except OSError:
        # printErrorByPlatform("\t Error creating directory or directory already present ... ")
        return 0


# end of checkDataDir()
