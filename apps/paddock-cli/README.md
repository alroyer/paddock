# paddock-cli

CLI for recording and analyzing F1 telemetry data.

## Commands

- `record`: record UDP telemetry packets into a `.bin` file
- `analyze`: analyze the player's session and suggest ways to improve

```bash
uv run paddock-cli record --port 8080
uv run paddock-cli analyze ./data/telemetry_data_2026-07-21_10-22-44.bin
uv run paddock-cli analyze ./data/telemetry_data_2026-07-21_10-22-44.bin --car "Driver Name"
```
