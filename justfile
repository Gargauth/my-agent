# agent project justfile
set dotenv-load := true

export VIRTUAL_ENV := ""

_sandbox_url := env("AGENT_SANDBOX_URL", "")
default_url := if _sandbox_url == "" { "http://localhost:7600" } else { _sandbox_url }

# List available commands
default:
    @just --list

# Start the listen server
listen:
    cd apps/listen && uv run python main.py

# Send a job to the listen server
send prompt url=default_url:
    cd apps/direct && uv run python main.py start {{url}} "{{prompt}}"

# Send a job from a local file
sendf file url=default_url:
    #!/usr/bin/env bash
    prompt="$(cat '{{file}}')"
    cd apps/direct && uv run python main.py start '{{url}}' "$prompt"

# Get a job's status
job id url=default_url:
    cd apps/direct && uv run python main.py get {{url}} {{id}}

# List all jobs (pass --archived to see archived)
jobs *flags:
    cd apps/direct && uv run python main.py list {{default_url}} {{flags}}

# Show full details of the latest N jobs (default: 1)
latest n="1" url=default_url:
    cd apps/direct && uv run python main.py latest {{url}} {{n}}

# Show live output of a running job
log id url=default_url:
    cd apps/direct && uv run python main.py log {{url}} {{id}}

# Follow live output of a running job (refreshes every 2s)
logf id url=default_url:
    cd apps/direct && uv run python main.py log {{url}} {{id}} --follow

# Stop a running job
stop id url=default_url:
    cd apps/direct && uv run python main.py stop {{url}} {{id}}

# Archive all jobs
clear url=default_url:
    cd apps/direct && uv run python main.py clear {{url}}

# Run a custom prompt directly with Claude Code (local, no listen server)
steer-cc prompt:
    claude --dangerously-skip-permissions "/listen-drive-and-steer-user-prompt {{prompt}}"
