#!/usr/bin/env python3
# -*- coding: utf-8 -*-

DATE = "8 Feb 2025"
VERSION = "v0.0.1"
AUTHOR = "Oliver Bonham-Carter"
AUTHORMAIL = "obonhamcarter@allegheny.edu"

from rich.console import Console
import typer

from captchaaudio import audio
from captchaaudio import launcher
from rich.style import Style

console = Console()

# create a Typer object to support the command-line interface
cli = typer.Typer()


@cli.command()
def main(capText: str = "", bighelp: bool = False):
    """Front end of the program."""

    if bighelp:
        bigHelp()
        exit()

    print(f"captext = {capText}")

    while capText == "":
        prmpt = "\tEnter alpha-numeric string: "
        capText = input(prmpt)

    console.print(
        "\t [bright_green]Captcha audio as wave file is being created.[/bright_green]"
    )

    console.print(
        f"\t [bright_green] Entered text: [bright_cyan]{capText}[/bright_cyan]"
    )
    getAudio(capText.upper())


# end of main()


def getAudio(capText: str) -> None:
    """A function to create the audio of the input string."""
    myAudio = audio.AudioCaptcha()

    captcha_text = capText
    # captcha_text = input(prmpt)

    # generate the audio of the given text
    audio_data = myAudio.generate(captcha_text)

    # Give the name of the audio file
    audio_file = "audio_" + captcha_text + ".wav"

    launcher.checkDataDir(launcher.MYOUTPUT_DIR)
    audio_file = launcher.MYOUTPUT_DIR + audio_file

    # Finally write the audio file and save it
    myAudio.write(captcha_text, audio_file)

    launcher.playSound(audio_file)


# end of getAudio()


def bigHelp():
    """Helper function -- give available command line prompts."""

    h_str = "   " + DATE + " | version: " + VERSION + " |" + AUTHOR + " | " + AUTHORMAIL
    console.print(f"[bold green] {len(h_str) * '-'}")
    console.print(f"[bold yellow]{h_str}")
    console.print(f"[bold green] {len(h_str) * '-'}")

    console.print(
        f'\n\t:coffee:[bold green] Command: [bold yellow]poetry run captchaaudio --captext "123ABC" '
    )


# end of bigHelp()
