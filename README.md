# paddock

## paddock-cli

### Record

Start the telemetry recorder:

```bash
uv run paddock-cli record
```

Options:

- `--host`: Host to bind (default: `0.0.0.0`)
- `--port`: Port to bind (default: `8080`)
- `--data-path`: Directory to save telemetry data (default: `./data`)

Example with custom options:

```bash
uv run paddock-cli record --host 127.0.0.1 --port 9090 --data-path ./my_data
```

Type `/quit` or `/bye` in the terminal to stop the recorder.

### View

Inspect a recorded telemetry file:

```bash
uv run paddock-cli view ./data/telemetry_data_2026-07-21_10-22-44.bin
```

Filter by packet type:

```bash
uv run paddock-cli view ./data/telemetry_data_2026-07-21_10-22-44.bin --packet-id Session
```
