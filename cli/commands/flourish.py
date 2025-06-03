import json
import click
from flourish_engine.rule_based import apply_rule_based_flourishes
from flourish_engine.magenta_flourish import generate_magenta_flourish
from flourish_engine.gpt4all_flourish import suggest_chord_substitutions

@click.command()
@click.argument('chords_json', type=click.File('r'))
@click.option('--magenta', is_flag=True, help='Use Magenta for AI flourishes')
@click.option('--gpt4all', is_flag=True, help='Use GPT4All for LLM suggestions')
def flourish(chords_json, magenta, gpt4all):
    """Suggest flourishes using rule-based, Magenta, or GPT4All."""
    try:
        chords = json.load(chords_json)
        chord_list = [c['chord'] for c in chords]
        if magenta:
            flourishes = generate_magenta_flourish(chord_list)
        elif gpt4all:
            flourishes = suggest_chord_substitutions(chord_list)
        else:
            flourishes = apply_rule_based_flourishes(chord_list)
        click.echo(json.dumps({'flourishes': flourishes}, indent=2))
    except Exception as e:
        raise click.ClickException(f"Flourish suggestion failed: {e}")
