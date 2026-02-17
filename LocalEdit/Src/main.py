# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
dist/
build/
*.whl

# Virtual environments
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# OS
Thumbs.db
desktop.ini

# User media files (don't commit user's projects)
projects/
exports/
temp/
*.mp4
*.mov
*.avi
*.mkv
*.mp3
*.wav
*.flac

# Logs
*.log
logs/

# Config files with personal settings
config.local.json
settings.local.json

# Testing
.pytest_cache/
.coverage
htmlcov/

# Documentation builds
docs/_build/

# Temporary files
tmp/
*.tmp
*.bak
Copy this and save it as .gitignore in your root folder!
What it does:
Keeps Python cache files out of git
Ignores user's video/audio projects (privacy!)
Excludes IDE settings
No temporary or log files in repo
Next: Should we start on the actual code? Src/main.py?
