import json
import click
from flourish_engine.rule_based import apply_rule_based_flourishes
from flourish_engine.magenta_flourish import generate_magenta_flourish
from flourish_engine.gpt4all_flourish import suggest_chord_substitutions


@click.command()
@click.argument('chords_json', type=click.File('r'))
@click.option('--magenta', is_flag=True, help='Use Magenta for AI flourishes.')
@click.option('--gpt4all', is_flag=True, help='Use GPT4All LLM suggestions.')
def flourish(chords_json, magenta, gpt4all):
    """Suggest flourishes using rule-based, Magenta, or GPT4All."""
    try:
        if magenta and gpt4all:
            msg = ("Cannot use both --magenta and --gpt4all flags "
                   "simultaneously. Please choose one.")
            raise click.ClickException(msg)

        data = json.load(chords_json)
        chord_objects_list = data.get('chords', [])
        if not chord_objects_list:
            # Or handle as an error if the JSON must contain 'chords'
            error_payload = {
                'flourishes': [],
                'error': "No 'chords' array found in JSON or it's empty."
            }
            click.echo(json.dumps(error_payload, indent=2))
            return

        # Full chord progression (list of dicts) for rule_based and gpt4all.
        # Chord names (list of strings) for magenta_flourish.
        
        if magenta:
            chord_names_only = [c.get('chord') for c in chord_objects_list]
            flourishes = generate_magenta_flourish(chord_names_only)
        elif gpt4all:
            # Pass the full chord progression to GPT4All
            flourishes = suggest_chord_substitutions(chord_objects_list)
        else:
            # Default to rule-based, pass the full chord progression
            flourishes = apply_rule_based_flourishes(chord_objects_list)
        
        click.echo(json.dumps({'flourishes': flourishes}, indent=2))
    except Exception as e:
        raise click.ClickException(f"Flourish suggestion failed: {e}")
