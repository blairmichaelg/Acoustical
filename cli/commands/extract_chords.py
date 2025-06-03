import os
import sys
import click
from chord_extraction import get_chords, get_chords_batch
from audio_input.utils import check_audio_file
from common.utils import format_error, serialize_result

@click.command()
@click.argument('audio_path', type=click.Path(exists=True))
@click.option('--batch', is_flag=True, help='Batch process all audio files in a directory')
def extract_chords(audio_path, batch):
    """Extract chords from audio file or directory."""
    try:
        if batch and os.path.isdir(audio_path):
            files = [os.path.join(audio_path, f) for f in os.listdir(audio_path) if f.lower().endswith(('.mp3', '.wav', '.flac'))]
            valid_files = []
            for f in files:
                try:
                    check_audio_file(f)
                    valid_files.append(f)
                except Exception as e:
                    click.echo(format_error(f"Skipping {f}", e), err=True)
            if not valid_files:
                click.echo(format_error("No valid audio files found."), err=True)
                sys.exit(1)
            results = get_chords_batch(valid_files)
            click.echo(serialize_result(results))
        else:
            check_audio_file(audio_path)
            chords = get_chords(audio_path)
            click.echo(serialize_result(chords))
    except Exception as e:
        click.echo(format_error("Chord extraction failed", e), err=True)
        click.echo("Tip: Run 'python cli/cli.py check-backends' to diagnose backend availability.", err=True)
        sys.exit(1)
