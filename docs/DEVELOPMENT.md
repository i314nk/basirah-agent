# Development Guide

## Virtual Environment Setup

This project uses a Python virtual environment to isolate dependencies. Always activate the virtual environment before working on the project.

### First-Time Setup

```bash
# Create virtual environment (only needed once)
python -m venv venv

# Activate it (see platform-specific commands below)

# Install dependencies
pip install -r requirements.txt
```

### Daily Development

#### Activating the Virtual Environment

**Windows (Git Bash):**
```bash
source venv/Scripts/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

#### Verify Activation

When activated, you'll see `(venv)` prefix in your terminal prompt:
```
(venv) user@machine:~/basira-agent$
```

You can also verify with:
```bash
which python  # Should point to venv/Scripts/python or venv/bin/python
python --version  # Should show Python 3.10.11
```

#### Deactivating

To exit the virtual environment:
```bash
deactivate
```

### Running the Application

**Always activate the venv first**, then run:

```bash
# Web UI
streamlit run src/ui/app.py

# Python API
python your_script.py

# Tests
pytest tests/
```

### Adding New Dependencies

1. Activate the virtual environment
2. Install the package: `pip install package-name`
3. Update requirements: `pip freeze > requirements.txt`
4. Commit both code and updated requirements.txt

### Troubleshooting

**Problem:** Commands not found after activation
**Solution:** Ensure you're using the correct activation command for your shell

**Problem:** Wrong Python version or packages
**Solution:**
```bash
deactivate  # Exit current environment
rm -rf venv  # Delete old venv
python -m venv venv  # Recreate
source venv/Scripts/activate  # Activate
pip install -r requirements.txt  # Reinstall
```

**Problem:** Permission errors on Windows
**Solution:** Run your terminal as Administrator or adjust execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Database Setup

The project uses PostgreSQL running in Docker:

```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# View logs
docker-compose logs -f db
```

## Project Structure

```
basira-agent/
├── venv/                    # Virtual environment (not in git)
├── src/
│   ├── agent/              # Core agent logic
│   ├── tools/              # SEC, GuruFocus, etc.
│   ├── storage/            # PostgreSQL & file storage
│   └── ui/                 # Streamlit application
├── tests/                  # Test files
├── docs/                   # Documentation
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (not in git)
```

## Useful Commands

```bash
# Check dependency versions
pip list

# Check for outdated packages
pip list --outdated

# Run specific test
pytest tests/test_file.py::test_function_name -v

# Run with coverage
pytest --cov=src tests/

# Format code
black src/ tests/

# Start Streamlit with custom port
streamlit run src/ui/app.py --server.port 8502
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key_here

# Optional but recommended
GURUFOCUS_API_KEY=your_gurufocus_key_here

# Database (defaults work with docker-compose)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=basirah
DB_USER=basirah
DB_PASSWORD=basirah123
```

## Best Practices

1. **Always use venv** - Activate before any Python work
2. **Keep requirements.txt updated** - After adding/removing packages
3. **Test before committing** - Run `pytest` to verify changes
4. **Format code** - Run `black` before committing
5. **Update documentation** - Keep docs in sync with code changes

## Git Workflow

```bash
# Pull latest changes
git pull

# Create feature branch (optional)
git checkout -b feature/your-feature

# Make changes, test, commit
git add .
git commit -m "Description of changes"

# Push to remote
git push origin main  # or your branch
```

## Getting Help

- **Documentation:** See `docs/` directory
- **Bug Fixes:** See `docs/bug_fixes/` for known issues
- **Issues:** https://github.com/i314nk/basirah-agent/issues
- **API Docs:**
  - [Anthropic Claude](https://docs.anthropic.com/)
  - [GuruFocus API](https://www.gurufocus.com/api.php)
  - [Streamlit](https://docs.streamlit.io/)
