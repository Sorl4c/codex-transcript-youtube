# Cross-Platform Virtual Environment Guide

This guide provides practical recommendations for managing Python virtual environments across Windows and WSL in the same project.

## Quick Reference

### Current Project Setup
- **Environment**: Single `.venv/` directory
- **Activation**: `./activate_env.sh` (platform-aware)
- **Requirements**: `requirements.txt` (shared)
- **Status**: Working well with cross-platform support

### Platform Activation Commands

#### Windows (CMD)
```cmd
.\.venv\Scripts\activate.bat
```

#### Windows (PowerShell)
```powershell
.\.venv\Scripts\activate.ps1
```

#### WSL
```bash
source .venv/bin/activate
```

#### Universal (Recommended)
```bash
./activate_env.sh
```

## Implementation Strategies

### Strategy 1: Single Environment (Current)
**Best for**: Simple projects, small teams, limited cross-platform needs

```
project/
├── .venv/
├── activate_env.sh
├── requirements.txt
└── .gitignore
```

**Pros:**
- Simple setup and maintenance
- Reduced disk space usage
- Easy team onboarding
- Single set of dependencies to manage

**Cons:**
- Potential path conflicts
- Platform-specific package limitations
- Risk of environment corruption

### Strategy 2: Platform-Specific Environments
**Best for**: Complex projects, large teams, platform-specific dependencies

```
project/
├── .venv-win/
├── .venv-wsl/
├── activate-win.bat
├── activate-wsl.sh
├── requirements.txt
└── .gitignore
```

**Pros:**
- Complete platform isolation
- No path conflicts
- Platform-specific optimization
- Independent dependency management

**Cons:**
- Double disk space usage
- More complex maintenance
- Additional setup steps

## Setup Instructions

### For New Projects (Recommended)

1. **Create Platform-Specific Environments:**
```bash
# Windows (CMD)
python -m venv .venv-win

# WSL
python3 -m venv .venv-wsl
```

2. **Create Activation Scripts:**

**activate-win.bat:**
```batch
@echo off
call .venv-win\Scripts\activate.bat
```

**activate-wsl.sh:**
```bash
#!/bin/bash
source .venv-wsl/bin/activate
```

3. **Update .gitignore:**
```
.venv-win/
.venv-wsl/
```

### For Existing Projects (Like This One)

1. **Keep Current Setup** (Recommended for this project):
```bash
# Use existing platform-aware activation
./activate_env.sh
```

2. **Or Migrate to Platform-Specific:**
```bash
# Backup current environment
cp -r .venv .venv-backup

# Create platform-specific environments
python -m venv .venv-win
python3 -m venv .venv-wsl

# Install dependencies in both
source .venv-win/Scripts/activate
pip install -r requirements.txt

source .venv-wsl/bin/activate
pip install -r requirements.txt
```

## IDE Configuration

### Visual Studio Code

1. **Install Python Extension**
2. **Install WSL Extension** (for WSL development)
3. **Select Interpreter:**
   - Press `Ctrl+Shift+P`
   - Search for "Python: Select Interpreter"
   - Choose from `.venv` or platform-specific environments

### PyCharm

1. **File → Settings → Project → Python Interpreter**
2. **Add Interpreter:**
   - For Windows: Select `.venv-win\Scripts\python.exe`
   - For WSL: Select WSL interpreter, then `.venv-wsl/bin/python`

## Common Issues and Solutions

### Path Conflicts
**Problem**: Scripts can't find dependencies due to path differences
**Solution**: Use absolute paths or platform detection

### Platform-Specific Packages
**Problem**: Some packages only work on specific platforms
**Solution**: Use platform-specific requirements files or conditional installation

### Environment Corruption
**Problem**: Virtual environment becomes corrupted when switching platforms
**Solution**: Use platform-specific environments or recreate environment

### Activation Failures
**Problem**: Activation scripts fail across platforms
**Solution**: Use platform-aware activation scripts like `activate_env.sh`

## Best Practices

### Development Workflow
1. **Always activate environment** before working
2. **Use consistent activation method** across team
3. **Update requirements.txt** when adding new packages
4. **Test on both platforms** regularly
5. **Document platform-specific setup** if needed

### Team Collaboration
1. **Choose one strategy** and stick with it
2. **Document setup process** clearly
3. **Include activation instructions** in README
4. **Use consistent Python versions** across platforms
5. **Test CI/CD pipeline** on both platforms

### Maintenance
1. **Regular updates**: Keep dependencies updated
2. **Backup environments**: Before major changes
3. **Monitor disk space**: Especially with multiple environments
4. **Clean unused packages**: Regular maintenance
5. **Recreate environments**: When issues arise

## Advanced Configuration

### Multiple Python Versions
```
project/
├── .venv-win-py311/
├── .venv-wsl-py311/
├── .venv-win-py312/
└── .venv-wsl-py312/
```

### Environment Variables
Create `.env` files for platform-specific configuration:
```
# .env.win
PYTHONPATH=C:\path\to\project
MODEL_PATH=C:\local\modelos

# .env.wsl
PYTHONPATH=/mnt/c/path/to/project
MODEL_PATH=/mnt/c/local/modelos
```

### Automated Setup Script
```bash
#!/bin/bash
# setup.sh

echo "Setting up cross-platform virtual environments..."

# Create Windows environment
python -m venv .venv-win
source .venv-win/Scripts/activate
pip install -r requirements.txt

# Create WSL environment
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install -r requirements.txt

echo "Setup complete!"
echo "Windows: .venv-win\Scripts\activate"
echo "WSL: source .venv-wsl/bin/activate"
```

## Troubleshooting

### Environment Not Found
**Symptoms**: `activate_env.sh` says environment doesn't exist
**Solutions**:
1. Check if `.venv` directory exists
2. Run `python -m venv .venv` to create environment
3. Check file permissions

### Activation Fails
**Symptoms**: Activation script fails with errors
**Solutions**:
1. Ensure correct Python version
2. Check script permissions
3. Try manual activation
4. Recreate environment

### Package Installation Fails
**Symptoms**: `pip install` fails
**Solutions**:
1. Update pip: `python -m pip install --upgrade pip`
2. Check platform compatibility
3. Try installing from source
4. Use platform-specific wheels

### Path Issues
**Symptoms**: Module not found errors
**Solutions**:
1. Check `PYTHONPATH` environment variable
2. Verify activation worked
3. Use absolute paths in configuration
4. Check for path conflicts

## Conclusion

For this project, the **single environment approach with platform-aware activation** is working well and should be maintained. For new projects or projects with complex cross-platform needs, **platform-specific environments** are recommended.

The key is to choose a strategy based on project requirements and maintain consistency across the development team.