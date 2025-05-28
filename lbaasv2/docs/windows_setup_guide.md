# Windows Environment Setup Guide for LBaaS API

This guide provides specific instructions for setting up and running the LBaaS API project on Windows environments.

## Directory Structure

Ensure your project has the following directory structure after extraction:

```
D:\MyCode\lbaasv2\
├── ansible\
│   ├── playbooks\
│   ├── roles\
│   ├── inventory\
│   └── vars\
├── api\
│   ├── controllers\
│   ├── models\
│   ├── middleware\
│   └── main.py
├── business\
├── docker\
├── docs\
├── integration\
├── mock\
├── tests\
├── docker-compose.yml
├── docker-compose-windows.yml
└── README.md
```

## Common Windows-Specific Issues

### 1. Path Separators

Windows uses backslashes (`\`) for file paths, while Docker and Linux use forward slashes (`/`). Docker Compose files should always use forward slashes, even on Windows.

### 2. Volume Mounting

When using Docker Desktop for Windows, ensure:
- Volume paths use forward slashes
- Paths are relative when possible
- Docker Desktop has permission to access your project directory

### 3. Docker Context Issues

If you encounter "unable to prepare context" errors:
- Check that the referenced directories exist
- Use the correct docker-compose file (`docker-compose-windows.yml`)
- Ensure Docker Desktop has access to the drive where your project is located

## Using the Windows-Compatible Docker Compose File

1. Open a command prompt or PowerShell window
2. Navigate to your project directory:
   ```
   cd D:\MyCode\lbaasv2
   ```
3. Use the Windows-specific docker-compose file:
   ```
   docker-compose -f docker-compose-windows.yml up -d
   ```

## Troubleshooting

### Error: "unable to prepare context"
- Verify the directory structure matches the one shown above
- Ensure all referenced directories exist
- Check Docker Desktop settings to confirm it has access to the drive

### Error: "Error response from daemon: invalid mount config"
- Use forward slashes in all path references
- Ensure Docker Desktop has permission to access the mounted directories
- Try using absolute paths if relative paths don't work

### Error: "The system cannot find the path specified"
- Check for typos in directory names
- Ensure case sensitivity matches (Windows is case-insensitive, but Docker can be case-sensitive)
- Verify the directory exists at the specified location

## Additional Windows Considerations

1. **Line Endings**: Windows uses CRLF line endings, while Linux uses LF. Configure Git to handle this:
   ```
   git config --global core.autocrlf input
   ```

2. **File Permissions**: Windows doesn't have the same permission system as Linux. If you encounter permission issues:
   - Add appropriate user to Docker Desktop
   - Use Docker volumes instead of bind mounts for sensitive directories

3. **WSL Integration**: Consider using Docker with WSL2 integration for better performance and Linux compatibility:
   - Enable WSL2 in Windows features
   - Configure Docker Desktop to use WSL2 backend
   - Store project files in the WSL2 filesystem for better performance

## Getting Help

If you continue to experience Windows-specific issues:
1. Check the Docker Desktop logs
2. Verify your Docker Desktop version is up to date
3. Consult the Docker documentation for Windows-specific guidance
4. Contact the LBaaS support team at lbaas-support@example.com
