import json
import click
from key_transpose_capo.capo_advisor import recommend_capo


@click.command()
@click.argument('chords_json', type=click.File('r'))
def capo(chords_json):
    """Recommend capo position."""
    try:
        chords = json.load(chords_json)
        capo_fret, transposed = recommend_capo([c['chord'] for c in chords])
        for i, c in enumerate(chords):
            c['chord'] = transposed[i]
        click.echo(json.dumps({'capo': capo_fret, 'chords': chords}, indent=2))
    except Exception as e:
        raise click.ClickException(f"Capo recommendation failed: {e}")
