import typer
import pathlib

DEFAULT_DATA_PATH = pathlib.Path("./data")
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8080

app = typer.Typer()


@app.command()
def main(
    host: str = typer.Option(DEFAULT_HOST, help="Host to bind the server to"),
    port: int = typer.Option(DEFAULT_PORT, help="Port to bind the server to"),
    data_path: pathlib.Path = typer.Option(DEFAULT_DATA_PATH, help="Path to the data directory"),
):
    print(f"""
   _______________/___                     |
  |                   |                    | Host: {host}
  |   [REC] ●         |==\\    /|           | Port: {port}
  |                   |   |==| |           |
  |   ____________    |==/    \\|           | Data path: {data_path}
  |  |____________|   |                    |
  |___________________|                    |
         /     \\                           |
        /       \\                          |
       /         \\                         |

""")

    _create_data_directory(data_path)


def _create_data_directory(data_path: pathlib.Path):
    if not data_path.exists():
        data_path.mkdir(parents=True, exist_ok=True)
        print(f"Created data directory at {data_path}")
    else:
        print(f"Data directory already exists at {data_path}")


if __name__ == "__main__":
    app()
