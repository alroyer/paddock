import typer

app = typer.Typer()


@app.command()
def main():
    """
    Main entry point for the recorder application.
    """
    print("Recorder application started.")
