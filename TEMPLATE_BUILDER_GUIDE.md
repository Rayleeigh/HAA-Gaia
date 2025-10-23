# Template Builder - Visual Block Coding Guide

## Overview

The Template Builder is a visual, block-based interface for creating VM templates without writing code. It works like Scratch or Node-RED - you click blocks, configure them, and the system generates the Vagrantfile automatically.

## Accessing the Builder

```
1. Navigate to Templates page: http://localhost:3000/templates
2. Click "Create Template" button
3. Or go directly to: http://localhost:3000/templates/builder
```

## Interface Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  Template Builder                     [Preview] [Save Template] │
│  Create VM templates using visual blocks                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────┐
│ Config Blocks    │  Template Name: [_______________]            │
│ Click to add     │  Description:   [_______________]            │
│                  │  Provider:      [VirtualBox ▼]              │
│ 📦 Base Config   │                                              │
│ ⚙️ Resources     │  ┌─────────────────────────────────────┐    │
│ 🌐 Network       │  │ Template Blocks (3)                  │    │
│ 💾 Storage       │  ├─────────────────────────────────────┤    │
│ 📁 Synced Folder │  │ 1 📦 Base Configuration          [×] │    │
│ 🔧 Provisioner   │  │   Box Image: [bento/ubuntu-22.04]    │    │
│                  │  │   Hostname:  [my-vm             ]    │    │
│                  │  ├─────────────────────────────────────┤    │
│                  │  │ 2 ⚙️ Resources                   [×] │    │
│                  │  │   CPUs:   [2  ]  Memory: [2048  ]    │    │
│                  │  ├─────────────────────────────────────┤    │
│                  │  │ 3 🔧 Shell Provisioner           [×] │    │
│                  │  │   Commands: [apt-get update      ]   │    │
│                  │  │             [apt-get install nginx]  │    │
│                  │  └─────────────────────────────────────┘    │
└──────────────────┴──────────────────────────────────────────────┘
     ↑ Click blocks        ↑ Configure blocks here
```

## Available Blocks

### 1. 📦 Base Configuration
**What it does:** Sets the base VM image and hostname

**Fields:**
- **Box Image**: The base box to use (e.g., `bento/ubuntu-22.04`, `debian/bookworm64`)
- **Hostname**: VM hostname (e.g., `my-vm`, `dev-server`)

**Example:**
```
Box Image: bento/ubuntu-22.04
Hostname: ubuntu-dev
```

---

### 2. ⚙️ Resources
**What it does:** Configures CPU and memory allocation

**Fields:**
- **CPUs**: Number of CPU cores (1-32)
- **Memory (MB)**: RAM in megabytes (512+, increments of 512)

**Example:**
```
CPUs: 4
Memory: 8192
```

---

### 3. 🌐 Network
**What it does:** Configures network settings

**Fields:**
- **Type**: Network type (dropdown)
  - `private_network`: Host-only network with static IP
  - `public_network`: Bridged network
  - `forwarded_port`: Port forwarding from host to guest

**Conditional fields:**

**For `private_network`:**
- **IP Address**: Static IP (e.g., `192.168.56.10`)

**For `forwarded_port`:**
- **Guest Port**: Port inside VM (e.g., `80`)
- **Host Port**: Port on host machine (e.g., `8080`)

**Example 1 (Private Network):**
```
Type: private_network
IP Address: 192.168.56.10
```

**Example 2 (Port Forwarding):**
```
Type: forwarded_port
Guest Port: 80
Host Port: 8080
```

---

### 4. 💾 Storage
**What it does:** Configures disk size

**Fields:**
- **Disk Size (MB)**: Virtual disk size in megabytes

**Example:**
```
Disk Size: 32768  (32 GB)
```

---

### 5. 📁 Synced Folder
**What it does:** Shares a folder between host and VM

**Fields:**
- **Host Path**: Path on your computer (e.g., `./data`, `C:\Projects`)
- **Guest Path**: Path inside VM (e.g., `/vagrant/data`, `/home/user/shared`)

**Example:**
```
Host Path: ./project
Guest Path: /home/vagrant/project
```

---

### 6. 🔧 Shell Provisioner
**What it does:** Runs shell commands when VM is created

**Fields:**
- **Shell Commands**: One command per line

**Example:**
```
apt-get update
apt-get install -y nginx docker.io
systemctl start nginx
echo "Setup complete!"
```

---

## How to Use

### Step 1: Enter Template Info

At the top of the canvas:

1. **Template Name**: Give your template a name (e.g., "Ubuntu Dev Server")
2. **Description**: Describe what it's for (e.g., "Development environment with Docker")
3. **Provider**: Choose the virtualization provider (VirtualBox, Proxmox, Hyper-V, WSL)

### Step 2: Add Blocks

Click blocks from the left sidebar to add them to your template:

```
Click "📦 Base Configuration" → Block appears in canvas
Click "⚙️ Resources" → Another block appears
Click "🔧 Shell Provisioner" → Another block appears
```

**You can add:**
- ✅ One Base Configuration block
- ✅ One Resources block
- ✅ Multiple Network blocks (for multiple network interfaces)
- ✅ One Storage block
- ✅ Multiple Synced Folder blocks
- ✅ Multiple Provisioner blocks

### Step 3: Configure Each Block

Click inside the block's input fields and type your values:

**Example: Configuring Base Configuration**
```
1. Click in "Box Image" field
2. Type: bento/ubuntu-22.04
3. Click in "Hostname" field
4. Type: my-dev-vm
```

**Example: Configuring Network**
```
1. Click "Type" dropdown
2. Select: forwarded_port
3. New fields appear!
4. Type Guest Port: 80
5. Type Host Port: 8080
```

### Step 4: Preview Vagrantfile

Click the **"Preview Vagrantfile"** button to see the generated code:

```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-22.04"
  config.vm.hostname = "my-dev-vm"

  config.vm.network "forwarded_port", guest: 80, host: 8080

  config.vm.provider "virtualbox" do |vb|
    vb.cpus = 2
    vb.memory = 2048
  end

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y nginx
  SHELL
end
```

### Step 5: Save Template

Click **"Save Template"** to save your template to the database.

You can now use this template to quickly create VMs!

---

## Block Examples

### Example 1: Simple Web Server

**Blocks:**
1. 📦 Base Config: `bento/ubuntu-22.04`, hostname: `webserver`
2. ⚙️ Resources: 2 CPUs, 2048 MB
3. 🌐 Network: forwarded_port, guest: 80, host: 8080
4. 🔧 Provisioner:
   ```
   apt-get update
   apt-get install -y nginx
   systemctl start nginx
   ```

**Result:** Ubuntu VM with Nginx, accessible at http://localhost:8080

---

### Example 2: Development Environment

**Blocks:**
1. 📦 Base Config: `bento/ubuntu-22.04`, hostname: `dev-machine`
2. ⚙️ Resources: 4 CPUs, 8192 MB
3. 🌐 Network: private_network, IP: 192.168.56.10
4. 📁 Synced Folder: Host: `./code`, Guest: `/home/vagrant/code`
5. 🔧 Provisioner:
   ```
   apt-get update
   apt-get install -y build-essential git nodejs npm
   npm install -g yarn
   ```

**Result:** Powerful dev VM with shared code folder

---

### Example 3: Database Server

**Blocks:**
1. 📦 Base Config: `bento/ubuntu-22.04`, hostname: `db-server`
2. ⚙️ Resources: 2 CPUs, 4096 MB
3. 💾 Storage: 65536 MB (64 GB)
4. 🌐 Network: private_network, IP: 192.168.56.20
5. 🔧 Provisioner:
   ```
   apt-get update
   apt-get install -y postgresql postgresql-contrib
   systemctl start postgresql
   ```

**Result:** PostgreSQL server with large disk

---

## Tips & Tricks

### Tip 1: Start with Base + Resources
Always add Base Configuration and Resources blocks first - they're required for most VMs.

### Tip 2: Multiple Networks
You can add multiple Network blocks for complex networking:
```
Block 1: private_network with IP
Block 2: forwarded_port for SSH
Block 3: forwarded_port for HTTP
```

### Tip 3: Order Matters for Provisioners
If you add multiple Provisioner blocks, they run in order from top to bottom.

### Tip 4: Use Provisioners for Setup
Provisioners are great for:
- Installing software
- Configuring services
- Creating users
- Downloading files
- Running setup scripts

### Tip 5: Test Before Saving
Always click "Preview Vagrantfile" to check the generated code before saving.

---

## Removing Blocks

Click the **trash icon (🗑️)** in the block header to remove it.

Blocks are numbered, so when you remove one, the numbers update automatically.

---

## Dynamic Fields

Some blocks have **conditional fields** that only appear based on other selections:

**Network Block Example:**
```
Type: private_network → Shows "IP Address" field
Type: public_network  → No extra fields
Type: forwarded_port  → Shows "Guest Port" and "Host Port" fields
```

The interface automatically shows/hides fields based on your selections!

---

## Keyboard Shortcuts

- **Tab**: Move between fields in a block
- **Enter**: (in text fields) Move to next field
- **Escape**: Close preview modal

---

## Technical Details

### How It Works

1. **You add blocks** → Creates JSON configuration
2. **You fill in values** → Updates JSON in real-time
3. **You click Preview** → Sends JSON to API
4. **API generates Vagrantfile** → Returns formatted code
5. **You click Save** → Stores template in database

### Data Flow

```
Blocks → buildConfig() → JSON →
  → API /vagrantfiles/generate →
  → Vagrantfile Generator →
  → Formatted Vagrantfile
```

### Storage

Templates are saved in the PostgreSQL database with:
- Name, description, provider
- Complete block configuration
- Tags for categorization
- Creation timestamp

---

## Troubleshooting

### Issue: "Preview" shows error

**Cause:** Missing required fields (box image)

**Fix:** Add Base Configuration block and fill in box image

---

### Issue: Can't type in fields

**Cause:** Block not fully loaded

**Fix:** Refresh page and try again

---

### Issue: Blocks won't add

**Cause:** JavaScript error

**Fix:** Check browser console (F12) for errors

---

### Issue: Save fails

**Cause:** Missing template name or backend error

**Fix:** Ensure template name is filled in, check backend logs

---

## What Gets Generated

The blocks generate different Vagrantfile sections:

| Block | Vagrantfile Section |
|-------|-------------------|
| 📦 Base | `config.vm.box`, `config.vm.hostname` |
| ⚙️ Resources | `vb.cpus`, `vb.memory` in provider block |
| 🌐 Network | `config.vm.network` statements |
| 💾 Storage | Provider-specific disk config |
| 📁 Synced Folder | `config.vm.synced_folder` |
| 🔧 Provisioner | `config.vm.provision "shell"` |

---

## Next Steps

After saving your template:

1. Go to **Templates** page
2. See your template in the list
3. Click **"Use Template"** to create a VM from it
4. Or use it in the **Create VM** page by selecting it

---

## Advanced: Template JSON Structure

Internally, your blocks are stored as JSON:

```json
{
  "name": "My Template",
  "provider": "virtualbox",
  "config": {
    "box": "bento/ubuntu-22.04",
    "hostname": "my-vm",
    "cpus": 2,
    "memory": 2048,
    "networks": [
      {"type": "forwarded_port", "guest_port": 80, "host_port": 8080}
    ],
    "provisioners": [
      {"type": "shell", "inline": ["apt-get update", "apt-get install -y nginx"]}
    ]
  }
}
```

This JSON is sent to the Vagrantfile generator API!
