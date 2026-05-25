# Agents - geopy-mcp

MCP Server exposing GeoPy data via the Model Context Protocol.

- SDK: https://github.com/modelcontextprotocol/python-sdk
- GeoPy: https://github.com/geopy/geopy

## Commands

This project uses `toml-run` — run any `[tool.scripts]` entry by name:

| Command      | What it does                                 |
| ------------ | -------------------------------------------- |
| `run build`  | hatch build                                  |
| `run cli`    | python -m geopy_mcp                          |
| `run dev`    | uvicorn w/ --reload                          |
| `run server` | uvicorn w/ --host 0.0.0.0                    |
| `run lint`   | Full lint: should always be used to lint     |
| `run format` | Full format: should always be used to format |
