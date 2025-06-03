import json
import click
from key_transpose_capo.key_analysis import detect_key_from_chords

@click.command()
@click.argument('chords_json', type=click.File('r'))
def key(chords_json):
    """Detect key from chords."""
    try:
        chords = json.load(chords_json)
        key_result = detect_key_from_chords([c['chord'] for c in chords])
        click.echo(json.dumps({'key': key_result}, indent=2))
    except Exception as e:
        raise click.ClickException(f"Key detection failed: {e}")
