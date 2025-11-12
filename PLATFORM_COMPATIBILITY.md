# Platform Compatibility Guide

## Overview

The ExamShield Licensing System is designed to work on both **Windows** and **Linux**, with some platform-specific considerations.

## Component Compatibility

### ✅ License Server (Flask API)
**Status:** Fully cross-platform

- Works on Windows, Linux, and macOS
- Uses standard Python libraries
- No platform-specific code
- File paths are relative or configurable

**Requirements:**
- Python 3.8+
- Flask
- python-dotenv

### ✅ Client License Module (`client/license.py`)
**Status:** Cross-platform (updated)

- Automatically detects OS
- Uses appropriate paths for each platform:
  - **Windows:** `%APPDATA%\ExamShield\` (e.g., `C:\Users\Username\AppData\Roaming\ExamShield\`)
  - **Linux (root):** `/etc/examshield/`
  - **Linux (user):** `~/.examshield/`

**Works on:**
- Windows 10/11
- Linux (Ubuntu, Debian, etc.)
- macOS

### ⚠️ ExamShield Daemon (`examshield.py`)
**Status:** Linux-specific (by design)

- Designed for Linux systems
- Uses Linux-specific paths:
  - `/etc/examshield/` for config
  - `/var/log/examshield/` for logs
  - `/opt/examshield/` for installation
- Uses Linux system commands (systemctl, etc.)

**Note:** The licensing system itself works on Windows, but the ExamShield daemon is Linux-only.

### ⚠️ Installer (`installer.py`)
**Status:** Cross-platform GUI, Linux-specific installation

- GUI works on Windows and Linux (uses tkinter)
- Installation scripts are Linux-specific (systemd, apt, etc.)
- License verification works on both platforms

### ⚠️ Build Script (`build_examshield_full.sh`)
**Status:** Linux-specific

- Bash script for Linux
- Creates Debian package (`.deb`)
- Requires Linux build environment

## Platform-Specific Paths

### Windows Paths

```
License File:     C:\Users\<User>\AppData\Roaming\ExamShield\license.json
Trial File:       C:\Users\<User>\AppData\Roaming\ExamShield\trial.json
Server Data:      .\data\license_db.json (relative to server directory)
```

### Linux Paths

```
License File:     /etc/examshield/license.json (root)
                  ~/.examshield/license.json (user)
Trial File:       /etc/examshield/trial.json (root)
                  ~/.examshield/trial.json (user)
Server Data:      ./data/license_db.json (relative to server directory)
```

## Usage by Platform

### Windows Usage

#### Running License Server:
```cmd
cd server
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python license_server.py
```

Or use: `start_server.bat`

#### Testing Client:
```cmd
cd client
python license.py
```

#### License Files Location:
- Check: `%APPDATA%\ExamShield\`
- Or: `C:\Users\<YourUsername>\AppData\Roaming\ExamShield\`

### Linux Usage

#### Running License Server:
```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 license_server.py
```

#### Testing Client:
```bash
cd client
python3 license.py
```

#### License Files Location:
- Root: `/etc/examshield/`
- User: `~/.examshield/`

## Cross-Platform Testing

### Test License Module on Both Platforms:

**Windows:**
```cmd
cd client
python license.py
```

**Linux:**
```bash
cd client
python3 license.py
```

Both should:
- Generate device fingerprint
- Show license status
- Create trial files in appropriate location

## Platform-Specific Considerations

### Windows

**Advantages:**
- No sudo/root required
- Files in user directory
- Easy GUI testing

**Limitations:**
- ExamShield daemon not designed for Windows
- No systemd service
- Different file permissions model

### Linux

**Advantages:**
- Full ExamShield integration
- Systemd service support
- Standard deployment paths
- Debian package support

**Limitations:**
- May require root for system paths
- Different permission model

## Deployment Scenarios

### Scenario 1: License Server on Windows, Clients on Linux

✅ **Works perfectly**
- Server runs on Windows
- Linux clients connect via network
- No issues

### Scenario 2: License Server on Linux, Clients on Windows

✅ **Works perfectly**
- Server runs on Linux
- Windows clients connect via network
- License module works on Windows

### Scenario 3: Everything on Windows

✅ **Works for licensing**
- Server works
- Client license module works
- ExamShield daemon won't work (Linux-specific)

### Scenario 4: Everything on Linux

✅ **Full compatibility**
- All components work
- Standard deployment
- Production-ready

## Making Code Cross-Platform

The license module automatically detects the platform:

```python
import platform
system = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)

if system == 'Windows':
    # Windows paths
else:
    # Linux/Unix paths
```

## Testing Checklist

### Windows Testing:
- [ ] Server starts: `python server/license_server.py`
- [ ] Client works: `python client/license.py`
- [ ] License files created in `%APPDATA%\ExamShield\`
- [ ] Registration works: `http://localhost:8080/register-page`
- [ ] Verification works

### Linux Testing:
- [ ] Server starts: `python3 server/license_server.py`
- [ ] Client works: `python3 client/license.py`
- [ ] License files created in `/etc/examshield/` or `~/.examshield/`
- [ ] Registration works: `http://localhost:8080/register-page`
- [ ] Verification works
- [ ] ExamShield daemon integration works

## Common Issues

### Windows: Permission Denied
**Solution:** Files are in user directory, should work without admin rights.

### Linux: Permission Denied
**Solution:** 
- Run as root for system paths: `sudo python3 ...`
- Or use user directory: `~/.examshield/`

### Path Not Found
**Solution:** License module creates directories automatically.

### Import Error
**Solution:** Make sure `client/license.py` is in Python path or use absolute path.

## Recommendations

1. **Development/Testing:** Use Windows or Linux - both work fine
2. **License Server:** Can run on either platform
3. **Production Deployment:** Linux recommended for:
   - Better integration with ExamShield
   - Systemd service support
   - Standard deployment practices
   - Debian package distribution

## Summary

| Component | Windows | Linux | Notes |
|-----------|---------|-------|-------|
| License Server | ✅ | ✅ | Fully cross-platform |
| Client License Module | ✅ | ✅ | Auto-detects OS, cross-platform |
| ExamShield Daemon | ❌ | ✅ | Linux-specific by design |
| Installer GUI | ✅ | ✅ | tkinter works on both |
| Installer Scripts | ❌ | ✅ | Linux-specific (systemd, apt) |
| Build Script | ❌ | ✅ | Bash/Linux-specific |

**Bottom Line:** The licensing system works on both Windows and Linux. The ExamShield daemon itself is Linux-only, but the licensing components are cross-platform.

