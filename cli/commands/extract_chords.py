import os
import sys
import click
from chord_extraction import get_chords, get_chords_batch
from audio_input.utils import check_audio_file
from common.utils import format_error, serialize_result

@click.command()
@click.argument('source', type=str) # Changed to 'source' and type=str to accept URLs or paths
@click.option('--batch', is_flag=True, help='Batch process all audio files in a local directory (source must be a directory path).')
def extract_chords(source, batch):
    """
    Extract chords from an audio file (local path or URL) or a local directory.
    If --batch is used, source must be a local directory.
    """
    try:
        if batch:
            if not os.path.isdir(source):
                click.echo(format_error(f"Batch mode requires a local directory path, but '{source}' is not a directory."), err=True)
                sys.exit(1)
            
            files = [os.path.join(source, f) for f in os.listdir(source) if f.lower().endswith(('.mp3', '.wav', '.flac'))]
            valid_files = []
            for f in files:
                try:
                    # check_audio_file is for local files, get_chords will handle URL validation
                    # For batch, we assume local files
                    check_audio_file(f) 
                    valid_files.append(f)
                except Exception as e:
                    click.echo(format_error(f"Skipping {f}", e), err=True)
            if not valid_files:
                click.echo(format_error("No valid audio files found in batch directory."), err=True)
                sys.exit(1)
            results = get_chords_batch(valid_files)
            click.echo(serialize_result(results))
        else:
            # Determine if source is a URL or a local file path
            is_url = source.startswith(("http://", "https://"))
            
            if not is_url:
                # For local files, perform existence check
                if not os.path.isfile(source):
                    click.echo(format_error(f"Local audio file not found: {source}"), err=True)
                    sys.exit(1)
                # check_audio_file also performs basic mime type check for local files
                check_audio_file(source) 
            
            # get_chords now handles both local paths and URLs internally
            chords = get_chords(source)
            click.echo(serialize_result(chords))
    except Exception as e:
        click.echo(format_error("Chord extraction failed", e), err=True)
        click.echo("Tip: Run 'python cli/cli.py check-backends' to diagnose backend availability or check your URL/file path.", err=True)
        sys.exit(1)
