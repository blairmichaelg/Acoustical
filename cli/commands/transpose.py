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
        # Ensure the file is properly closed using a 'with' statement
        with chords_json as f:
            data = json.load(f)  # Load the entire JSON object
        
        # Extract the list of chord objects
        chord_objects = data.get('chords', [])
        if not chord_objects:
            raise ValueError("No 'chords' array found in JSON or it's empty.")

        original_chord_strings = [c.get('chord') for c in chord_objects]
        
        transposed_chord_strings = transpose_chords(
            original_chord_strings,
            semitones
        )
        
        # Update the chord strings in the original list of chord objects
        for i, chord_obj in enumerate(chord_objects):
            chord_obj['chord'] = transposed_chord_strings[i]
        
        # data['chords'] is already updated if chord_objects was a direct reference
        # If it was a copy, then data['chords'] = chord_objects would be needed.
        # Assuming chord_objects is a reference to the list within data.
        
        # Echo the modified full data structure
        click.echo(json.dumps(data, indent=2))
    except Exception as e:
        raise click.ClickException(f"Transposition failed: {e}")
