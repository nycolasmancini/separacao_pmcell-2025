import os
import pytest
from pathlib import Path


def test_project_structure():
    """Test if project structure is correctly created"""
    base_path = Path(__file__).parent.parent.parent
    
    # Backend structure
    assert (base_path / "backend").exists()
    assert (base_path / "backend" / "app").exists()
    assert (base_path / "backend" / "app" / "api").exists()
    assert (base_path / "backend" / "app" / "core").exists()
    assert (base_path / "backend" / "app" / "models").exists()
    assert (base_path / "backend" / "app" / "schemas").exists()
    assert (base_path / "backend" / "app" / "services").exists()
    assert (base_path / "backend" / "tests").exists()
    
    # Frontend structure
    assert (base_path / "frontend").exists()
    assert (base_path / "frontend" / "src").exists()
    assert (base_path / "frontend" / "package.json").exists()
    
    # Configuration files
    assert (base_path / "docker-compose.yml").exists()
    assert (base_path / "Makefile").exists()
    assert (base_path / ".gitignore").exists()


def test_backend_files():
    """Test if essential backend files exist"""
    base_path = Path(__file__).parent.parent
    
    assert (base_path / "app" / "main.py").exists()
    assert (base_path / "app" / "core" / "config.py").exists()
    assert (base_path / "app" / "api" / "v1" / "health.py").exists()
    assert (base_path / "requirements.txt").exists()
    assert (base_path / ".env.example").exists()


def test_frontend_config():
    """Test if frontend configuration files exist"""
    base_path = Path(__file__).parent.parent.parent / "frontend"
    
    assert (base_path / "vite.config.js").exists()
    assert (base_path / "tailwind.config.js").exists()
    assert (base_path / "postcss.config.js").exists()
    assert (base_path / "src" / "App.jsx").exists()
    assert (base_path / "src" / "index.css").exists()