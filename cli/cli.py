import os
import sys
import json
import logging
import click
from chord_extraction import get_chords, get_chords_batch, check_backend_availability
from key_transpose_capo.transpose import transpose_chords
from key_transpose_capo.capo_advisor import recommend_capo
from flourish_engine.rule_based import apply_rule_based_flourishes
from flourish_engine.magenta_flourish import generate_magenta_flourish
from flourish_engine.gpt4all_flourish import suggest_chord_substitutions
from key_transpose_capo.key_analysis import detect_key_from_chords

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from cli.commands.extract_chords import extract_chords
from cli.commands.transpose import transpose
from cli.commands.capo import capo
from cli.commands.flourish import flourish
from cli.commands.key import key
from cli.commands.check_backends import check_backends
from cli.commands.download_audio import download_audio_cli

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

if __name__ == "__main__":
    cli()
