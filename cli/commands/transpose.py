import json
import click
from key_transpose_capo.transpose import transpose_chords


@click.command()
@click.argument(
    'chords_json',
    type=click.File('r')
)
@click.option(
    '--semitones',
    type=int,
    required=True,
    help='Number of semitones to transpose'
)
def transpose(chords_json, semitones):
    """Transpose chords by semitones."""
    try:
        chords = json.load(chords_json)
        transposed = transpose_chords(
            [c['chord'] for c in chords],
            semitones
        )
        for i, c in enumerate(chords):
            c['chord'] = transposed[i]
        click.echo(json.dumps(chords, indent=2))
    except Exception as e:
        raise click.ClickException(f"Transposition failed: {e}")
