#!/usr/bin/env bash
# ==============================================================================
# Para Academic Operations Platform - Developer Onboarding & Environment Setup
# ==============================================================================

set -euo pipefail

echo "=================================================================="
echo "🎓 Para Platform - Automated Developer Environment Setup"
echo "=================================================================="

# 1. Check Python version
PYTHON_BIN=""
for candidate in python3.12 python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        PYTHON_BIN="$candidate"
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "❌ Error: Python 3.11+ is required but not found in PATH."
    exit 1
fi

echo "✅ Found Python interpreter: $($PYTHON_BIN --version)"

# 2. Check Docker
if command -v docker >/dev/null 2>&1; then
    echo "✅ Found Docker: $(docker --version)"
else
    echo "⚠️ Warning: Docker is not installed or not in PATH."
fi

# 3. Setup Virtual Environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment at ./venv..."
    "$PYTHON_BIN" -m venv venv
else
    echo "✅ Virtual environment already exists at ./venv."
fi

echo "🔄 Upgrading pip and installing dependencies..."
./venv/bin/pip install --upgrade pip --quiet
./venv/bin/pip install -r requirements.txt -r requirements-dev.txt --quiet
echo "✅ Dependencies installed successfully."

# 4. Configure Pre-Commit Git Hooks
if command -v git >/dev/null 2>&1 && [ -d ".git" ]; then
    echo "🔒 Installing pre-commit git hooks..."
    ./venv/bin/pre-commit install
    echo "✅ Pre-commit hooks active."
fi

# 5. Initialize .env from .env.example if missing
if [ ! -f ".env" ]; then
    echo "📄 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️ Please fill in valid tokens and passwords in .env before starting services."
else
    echo "✅ .env file exists."
fi

# 6. Ensure runtime directories exist
mkdir -p logs data data/redis data/api data/bot
touch logs/.gitkeep data/.gitkeep

# 7. Run test verification
echo "🧪 Executing test verification suite..."
PYTHONPATH=. ./venv/bin/pytest tests/ -q

echo "=================================================================="
echo "🎉 Setup complete! You can now use 'make test', 'make lint', or 'make up'."
echo "=================================================================="
