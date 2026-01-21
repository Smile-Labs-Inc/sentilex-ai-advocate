# 1. Start a New Project
uv init <project-name>
cd <project-name>

# 2. Manage Python Version
uv python install 3.12          # Install specific version
uv python pin 3.12              # Lock project to this version

# 3. Add Dependencies
uv add <package-name>           # Production (e.g., fastapi, pandas)
uv add --dev <package-name>     # Development (e.g., pytest, ruff)

# 4. Run Commands (No activation required)
uv run <script.py>              # Run a script
uv run <command>                # Run a CLI tool (e.g., uv run uvicorn)

# 5. Maintenance
uv sync                         # Sync venv with pyproject.toml
uv lock --upgrade               # Update all packages to latest allowed
uv self update                  # Update uv itself
