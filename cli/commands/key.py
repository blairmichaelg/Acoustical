import json
import click
from key_transpose_capo.key_analysis import detect_key_from_chords


@click.command()
@click.argument('chords_json', type=click.File('r'))
def key(chords_json):
    """Detect key from chords."""
    try:
        chords_data = json.load(chords_json)  # Renamed for clarity
        # Correctly access the list of chord objects under the "chords" key
        chord_objects = chords_data['chords']
        chord_strings = [c['chord'] for c in chord_objects]
        key_result = detect_key_from_chords(chord_strings)
        click.echo(json.dumps({'key': key_result}, indent=2))
    except Exception as e:
        raise click.ClickException(f"Key detection failed: {e}")
