# Provider Configuration UI - User Guide

## How to Configure Providers

### Step 1: Access Provider Settings

Navigate to the Provider Configuration page:

**Option A: From Providers Page**
1. Go to `http://localhost:3000/providers`
2. Click the **"Configure Providers"** button (top right)

**Option B: Direct URL**
1. Go to `http://localhost:3000/providers/settings`

---

### Step 2: Select a Provider

On the left sidebar, you'll see a list of all available providers:

```
┌─────────────────┐
│ Select Provider │
├─────────────────┤
│ ► Proxmox VE    │ ← Click to select
│   VirtualBox    │
│   Hyper-V       │
│   WSL2          │
└─────────────────┘
```

**Click on any provider** to load its configuration form.

The selected provider will be highlighted with:
- Blue border
- Darker background
- Active state indicator

---

### Step 3: Configure Provider Settings

After selecting a provider, configuration forms appear on the right.

#### Proxmox VE Configuration

```
┌────────────────────────────────────┐
│ Proxmox Host                       │
│ [proxmox.example.com             ] │
│                                    │
│ Username                           │
│ [root@pam                        ] │
│                                    │
│ Password                           │
│ [••••••••••                      ] │
│                                    │
│ ☑ Skip SSL verification           │
└────────────────────────────────────┘
```

**Fields:**
- **Proxmox Host**: IP or hostname (e.g., `192.168.1.100` or `proxmox.local`)
- **Username**: Proxmox user (default: `root@pam`)
- **Password**: Your Proxmox password
- **Skip SSL verification**: Check if using self-signed certificates

#### VirtualBox Configuration

```
┌────────────────────────────────────┐
│ ℹ VirtualBox is managed through   │
│   VBoxManage CLI                   │
│   Ensure VirtualBox is installed   │
│                                    │
│ Default VM Location                │
│ [C:\Users\...\VirtualBox VMs    ] │
└────────────────────────────────────┘
```

**Fields:**
- **Default VM Location**: Where VMs are stored (optional)

**Note:** VirtualBox must be installed on your system.

#### Hyper-V Configuration

```
┌────────────────────────────────────┐
│ ℹ Hyper-V requires Windows 10 Pro │
│   Enable with PowerShell:          │
│   Enable-WindowsOptionalFeature... │
│                                    │
│ Default Virtual Hard Disk Path     │
│ [C:\Users\Public\...\Virtual...  ] │
│                                    │
│ Default Virtual Switch             │
│ [Default Switch                  ] │
└────────────────────────────────────┘
```

**Fields:**
- **VHD Path**: Where virtual hard disks are stored
- **Virtual Switch**: Default network switch name

**Requirements:**
- Windows 10 Pro/Enterprise or Windows Server
- Hyper-V feature enabled

#### WSL Configuration

```
┌────────────────────────────────────┐
│ ℹ WSL2 requires Windows 10 2004+  │
│   Install with: wsl --install      │
│                                    │
│ Default Install Location           │
│ [C:\WSL                          ] │
│                                    │
│ Default Distribution               │
│ [Ubuntu-22.04                    ] │
└────────────────────────────────────┘
```

**Fields:**
- **Install Location**: Where WSL distributions are stored
- **Default Distribution**: Base distro to clone from

**Requirements:**
- Windows 10 version 2004+ or Windows 11
- WSL2 installed

---

### Step 4: Test Connection

After entering configuration:

1. Click **"Test Connection"** button
2. Wait for the test to complete
3. View results:

**Success:**
```
┌────────────────────────────────────┐
│ ✓ Connection Successful            │
│ Connected to Proxmox VE            │
│ Version: 8.0.4                     │
└────────────────────────────────────┘
```

**Failure:**
```
┌────────────────────────────────────┐
│ ✗ Connection Failed                │
│ Could not connect to host          │
└────────────────────────────────────┘
```

---

### Step 5: Save Configuration

Once connection test is successful:

1. Click **"Save Configuration"** button
2. Wait for confirmation: "Configuration saved!"
3. Your settings are now saved

**Saved configurations persist:**
- Between browser sessions
- When switching between providers
- Until manually changed

---

## Provider-Specific Setup

### Proxmox Setup

**Before configuring in UI:**

1. Ensure Proxmox is accessible from your network
2. Create API user if needed:
   ```bash
   # On Proxmox server
   pveum user add apiuser@pve
   pveum passwd apiuser@pve
   pveum aclmod / -user apiuser@pve -role PVEAdmin
   ```

3. Test connection manually:
   ```bash
   curl -k https://proxmox.example.com:8006/api2/json/version
   ```

**Common Issues:**
- **Firewall:** Ensure port 8006 is open
- **SSL Errors:** Enable "Skip SSL verification"
- **Authentication:** Verify username format (user@realm)

---

### VirtualBox Setup

**Before configuring in UI:**

1. Install VirtualBox:
   ```bash
   # Windows (Chocolatey)
   choco install virtualbox

   # Mac
   brew install --cask virtualbox

   # Linux
   sudo apt install virtualbox
   ```

2. Verify installation:
   ```bash
   VBoxManage --version
   ```

3. Ensure VBoxManage is in PATH

**Common Issues:**
- **PATH not set:** Add VirtualBox to system PATH
- **Permissions:** Run as administrator (Windows)
- **Conflicts:** Cannot run with Hyper-V enabled

---

### Hyper-V Setup

**Before configuring in UI:**

1. Enable Hyper-V:
   ```powershell
   # PowerShell as Administrator
   Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
   # Restart required
   ```

2. Verify installation:
   ```powershell
   Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V
   Get-VM
   ```

3. Create virtual switch (optional):
   ```powershell
   New-VMSwitch -Name "External" -NetAdapterName "Ethernet"
   ```

**Common Issues:**
- **VirtualBox conflict:** Disable Hyper-V or uninstall VirtualBox
- **Permissions:** Must run as Administrator
- **Edition:** Requires Pro/Enterprise edition

---

### WSL Setup

**Before configuring in UI:**

1. Install WSL:
   ```powershell
   wsl --install
   # Restart required
   ```

2. Set WSL2 as default:
   ```powershell
   wsl --set-default-version 2
   ```

3. Install a distribution:
   ```powershell
   wsl --install -d Ubuntu-22.04
   ```

4. Verify setup:
   ```powershell
   wsl --status
   wsl --list --verbose
   ```

**Common Issues:**
- **Version:** Need Windows 10 2004+ or Windows 11
- **Virtualization:** Enable in BIOS
- **No distributions:** Install at least one Linux distro

---

## Usage Tips

### Switching Between Providers

1. Click different provider in left sidebar
2. Configuration auto-loads from saved settings
3. Test and save each provider independently

### Editing Configurations

- **Text fields are editable** - Click and type
- **Passwords are hidden** - Use password fields for security
- **Checkboxes toggle** - Click to enable/disable
- **Changes auto-populate** - Type and values update immediately

### Managing Multiple Environments

**Development Setup:**
```
Proxmox → Production environment (192.168.1.100)
VirtualBox → Local development (localhost)
Hyper-V → Windows testing (localhost)
WSL → Quick Linux testing (localhost)
```

### Keyboard Shortcuts

- **Tab**: Navigate between fields
- **Enter**: Save configuration (when button focused)
- **Escape**: Clear form (custom implementation needed)

---

## Troubleshooting

### "Loading providers..." never completes

**Cause:** Backend not running

**Solution:**
```bash
# Check backend status
docker-compose ps backend

# View logs
docker-compose logs backend

# Restart if needed
docker-compose restart backend
```

### Configuration not saving

**Cause:** localStorage blocked or full

**Solution:**
1. Check browser console for errors
2. Clear browser cache
3. Enable localStorage in browser settings

### Test connection always fails

**Cause:** Provider not installed or accessible

**Solution:**
1. Verify provider is installed
2. Check network connectivity
3. Review error message details
4. Check provider logs

### Form fields not editable

**Cause:** JavaScript error or state issue

**Solution:**
1. Refresh the page (F5)
2. Clear browser cache
3. Check browser console for errors
4. Try different browser

---

## API Integration

The UI communicates with these backend endpoints:

```javascript
// List available providers
GET /api/v1/providers

// Test provider connection
GET /api/v1/providers/{name}/status

// (Future) Save configuration
POST /api/v1/providers/{name}/config
```

**Current Storage:** localStorage (browser)
**Future:** Backend database with encryption

---

## Example Configurations

### Example 1: Proxmox Lab

```
Host: 192.168.1.100
User: root@pam
Password: your-secure-password
☑ Skip SSL verification
```

### Example 2: VirtualBox Development

```
Default VM Location: C:\Dev\VirtualBox VMs
```

### Example 3: Hyper-V Testing

```
VHD Path: D:\Hyper-V\Virtual Hard Disks
Virtual Switch: External Switch
```

### Example 4: WSL Development

```
Install Location: C:\WSL
Default Distribution: Ubuntu-22.04
```

---

## Security Notes

- **Passwords in localStorage**: Currently stored in browser
- **Production recommendation**: Move to backend with encryption
- **SSL verification**: Only disable for development/self-signed certs
- **Access control**: No authentication yet (add in production)

---

## Next Steps After Configuration

1. Go to **VMs** page
2. Click **"Create VM"**
3. Select configured provider from dropdown
4. Fill in VM details
5. Click **"Create VM"**

Your provider is now ready to use!

---

## Quick Reference

| Provider | Port | Protocol | Notes |
|----------|------|----------|-------|
| Proxmox | 8006 | HTTPS | Web UI / API |
| VirtualBox | - | CLI | Local only |
| Hyper-V | - | PowerShell | Local only |
| WSL | - | CLI | Local only |

---

**Need Help?**
- Check [PROVIDERS.md](PROVIDERS.md) for detailed provider docs
- Review [GETTING_STARTED.md](GETTING_STARTED.md) for setup
- Visit GitHub Issues for support
