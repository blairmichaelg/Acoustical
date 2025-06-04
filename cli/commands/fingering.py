import click
import logging
from typing import List, Optional # Added Optional
from key_transpose_capo.fingering_advisor import suggest_fingerings, score_shape_playability
from music_theory.fretboard import Fretboard
from common.utils import format_error, serialize_result

log = logging.getLogger(__name__)


@click.command("fingering")
@click.argument("chord_string", type=str)
@click.option(
    "--num_suggestions", "-n", type=int, default=5,
    help="Number of fingering suggestions to display."
)
@click.option(
    "--tuning", "-t", type=str, default=None,
    help="Custom tuning, e.g., DADGBe. Comma-separated."
)
def fingering_cli(chord_string: str, num_suggestions: int, tuning: Optional[str]):
    """
    Suggests guitar fingerings for a given CHORD_STRING.
    """
    try:
        fretboard_tuning: Optional[List[str]] = None
        if tuning:
            fretboard_tuning = [s.strip() for s in tuning.split(',')]
            log.info(f"Using custom tuning: {fretboard_tuning}")

        fb = Fretboard(tuning=fretboard_tuning)
        suggestions = suggest_fingerings(chord_string, fretboard=fb)

        if not suggestions:
            click.echo(
                format_error(
                    f"No fingerings found for '{chord_string}'.",
                    "Try a more common chord or check spelling."
                )
            )
            return

        output_suggestions = []
        for i, shape in enumerate(suggestions):
            if i >= num_suggestions:
                break
            # Recalculate score for display consistency
            score = score_shape_playability(shape, fb)
            output_suggestions.append({
                "name": shape.name,
                # This is the actual root after transposition
                "root": shape.template_root_note_str,
                "type": shape.chord_type,
                # Actual base/barre fret
                "base_fret": shape.base_fret_of_template,
                "fingerings": shape.fingerings,
                "score": score,
                "is_movable": shape.is_movable,
                "barre_strings": shape.barre_strings_offset
            })

        click.echo(serialize_result({
            "chord": chord_string,
            "suggestions": output_suggestions
        }))

    except Exception as e:
        log.error(f"Error in fingering CLI for '{chord_string}': {e}", exc_info=True)
        click.echo(
            format_error(f"Failed to suggest fingerings for '{chord_string}'.", e),
            err=True
        )
