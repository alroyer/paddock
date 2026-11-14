import os
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from typer import Typer

load_dotenv()

app = Typer()

console = Console()


@app.command()
def record_data() -> None:
    data_dir = Path(os.getenv("PADDOCK_CLI_DATA_DIR", "data"))

    console.print(f"{data_dir}")


if __name__ == "__main__":
    app()
