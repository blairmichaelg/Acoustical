import json
import click
from key_transpose_capo.capo_advisor import recommend_capo


@click.command()
@click.argument('chords_json', type=click.File('r'))
def capo(chords_json):
    """Recommend capo position."""
    try:
        with chords_json as f:
            data = json.load(f)  # Load the entire JSON object

        chord_objects = data.get('chords', [])
        if not chord_objects:
            raise ValueError("No 'chords' array found in JSON or it's empty.")

        original_chord_strings = [c.get('chord') for c in chord_objects]

        capo_fret, new_chord_shapes = recommend_capo(original_chord_strings)

        # Update the chord strings in the list of chord objects
        for i, chord_obj in enumerate(chord_objects):
            if i < len(new_chord_shapes):  # Ensure we don't go out of bounds
                chord_obj['chord'] = new_chord_shapes[i]
            else:
                # This case should ideally not happen if recommend_capo returns
                # a list of the same length as input. Handle defensively.
                chord_obj['chord'] = "N/A (shape error)" 
        
        # 'data' now contains the modified chord_objects.
        # Output: {'capo': fret, 'chords': original_data_with_new_shapes}
        click.echo(json.dumps({'capo': capo_fret, 'chords': data}, indent=2))
    except Exception as e:
        raise click.ClickException(f"Capo recommendation failed: {e}")
