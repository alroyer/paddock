# paddock-cli

CLI for recording and viewing F1 telemetry data.

## Commands

- `record`: record UDP telemetry packets into a `.bin` file
- `view`: load a telemetry `.bin` file and inspect its packets

```bash
uv run paddock-cli record --port 8080
uv run paddock-cli view ./data/telemetry_data_2026-07-21_10-22-44.bin --packet-id Session
```
