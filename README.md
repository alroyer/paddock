# paddock

## Recorder

Start the telemetry recorder:

```bash
cd apps/recorder && uv run main.py
```

Options:

- `--host`: Host to bind (default: `0.0.0.0`)
- `--port`: Port to bind (default: `8080`)
- `--data-path`: Directory to save telemetry data (default: `./data`)

Example with custom options:

```bash
cd apps/recorder && uv run main.py --host 127.0.0.1 --port 9090 --data-path ./my_data
```

Type `/quit` or `/bye` in the terminal to stop the recorder.
