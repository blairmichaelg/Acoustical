import click
from chord_extraction import check_backend_availability

@click.command()
def check_backends():
    """Check available chord extraction backends and print troubleshooting info."""
    availability = check_backend_availability()
    for backend, available in availability.items():
        status = 'Available' if available else 'Unavailable'
        click.echo(f"{backend}: {status}")
    if not any(availability.values()):
        click.echo("No chord extraction backends available. See README for setup instructions.")
