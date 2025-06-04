import logging
import click

from cli.commands.extract_chords import extract_chords
from cli.commands.transpose import transpose
from cli.commands.capo import capo
from cli.commands.flourish import flourish
from cli.commands.key import key
from cli.commands.check_backends import check_backends
from cli.commands.download_audio import download_audio_cli
from cli.commands.get_lyrics import get_lyrics_cli
from cli.commands.fingering import fingering_cli # Added new command


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


@click.group()
def cli():
    """Acoustic Cover Assistant CLI"""
    pass


cli.add_command(extract_chords)
cli.add_command(transpose)
cli.add_command(capo)
cli.add_command(flourish)
cli.add_command(key)
cli.add_command(check_backends)
cli.add_command(download_audio_cli)
cli.add_command(get_lyrics_cli)
cli.add_command(fingering_cli) # Added new command


if __name__ == "__main__":
    cli()
