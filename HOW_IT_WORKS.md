# How the Provider UI Works - Visual Guide

## Page Layout

When you open `/providers/settings`, you see this layout:

```
┌─────────────────────────────────────────────────────────────────┐
│  Provider Configuration                                         │
│  Configure virtualization provider connections                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┬──────────────────────────────────────────────┐
│                  │                                              │
│ Select Provider  │  Proxmox VE Configuration                    │
│                  │                                              │
│ ┌──────────────┐ │  ┌────────────────────────────────────────┐ │
│ │ ► Proxmox VE │◄┼──│  Proxmox Host                          │ │
│ │   (ACTIVE)   │ │  │  [________________________]            │ │
│ └──────────────┘ │  │                                        │ │
│                  │  │  Username                              │ │
│ ┌──────────────┐ │  │  [________________________]            │ │
│ │  VirtualBox  │ │  │                                        │ │
│ └──────────────┘ │  │  Password                              │ │
│                  │  │  [________________________]            │ │
│ ┌──────────────┐ │  │                                        │ │
│ │   Hyper-V    │ │  │  ☑ Skip SSL verification              │ │
│ └──────────────┘ │  └────────────────────────────────────────┘ │
│                  │                                              │
│ ┌──────────────┐ │  [Test Connection]  [Save Configuration]    │
│ │     WSL2     │ │                                              │
│ └──────────────┘ │                                              │
│                  │                                              │
└──────────────────┴──────────────────────────────────────────────┘
   ↑                ↑
   Click to select  Configuration form appears here
```

## How It Works

### 1. Provider List (Left Side)

The left sidebar shows all 4 providers:

```jsx
// Code that renders the list
{providers.map((provider) => (
  <div
    className="provider-item"
    onClick={() => setSelectedProvider(provider.name)}  ← Click handler
  >
    <div className="provider-name">{provider.display_name}</div>
    <div className="provider-type">{provider.name}</div>
  </div>
))}
```

**What happens when you click:**
1. `onClick` fires
2. `setSelectedProvider(provider.name)` runs
3. Provider becomes "active" (highlighted)
4. Configuration form on the right changes

### 2. Active State Indicator

```jsx
className={`provider-item ${selectedProvider === provider.name ? 'active' : ''}`}
```

**CSS:**
```css
.provider-item.active {
  background: var(--bg-tertiary);  /* Darker background */
  color: var(--primary);            /* Blue text */
  border-left-color: var(--primary); /* Blue left border */
}
```

### 3. Dynamic Form Rendering (Right Side)

```jsx
const renderConfigForm = () => {
  switch (selectedProvider) {
    case 'proxmox':
      return <ProxmoxForm />
    case 'virtualbox':
      return <VirtualBoxForm />
    case 'hyperv':
      return <HyperVForm />
    case 'wsl':
      return <WSLForm />
  }
}
```

### 4. Text Input Fields

**All fields are editable:**

```jsx
<input
  type="text"
  value={config.host || ''}                              ← Shows current value
  onChange={(e) => setConfig({...config, host: e.target.value})} ← Updates on type
  placeholder="proxmox.example.com"
/>
```

**How typing works:**
1. User types in field
2. `onChange` event fires
3. `setConfig()` updates state
4. React re-renders with new value
5. Field shows updated text

## Step-by-Step User Flow

### Example: Configuring Proxmox

**Step 1: User opens page**
```
URL: http://localhost:3000/providers/settings
```

**Step 2: Providers load automatically**
```javascript
useEffect(() => {
  loadProviders()  // Calls API to get provider list
}, [])
```

**Step 3: First provider auto-selected**
```javascript
if (response.data.length > 0) {
  setSelectedProvider(response.data[0].name)  // Auto-select Proxmox
}
```

**Step 4: User sees Proxmox form (default)**
```
Left side: Proxmox VE highlighted
Right side: Proxmox configuration form
```

**Step 5: User clicks "VirtualBox"**
```
onClick fires → setSelectedProvider('virtualbox')
→ Form changes to VirtualBox config
→ Previous Proxmox data saved in state
```

**Step 6: User clicks back to "Proxmox VE"**
```
onClick fires → setSelectedProvider('proxmox')
→ Form switches back to Proxmox
→ Saved Proxmox config loads from localStorage
```

**Step 7: User types in fields**
```
Host field: User types "192.168.1.100"
→ onChange fires on each keystroke
→ config.host updates: "1", "19", "192", etc.
→ Field displays updated value
```

**Step 8: User clicks "Test Connection"**
```
onClick fires → testConnection() runs
→ API call: GET /api/v1/providers/proxmox/status
→ Show "Testing..." button state
→ Display result (success/error)
```

**Step 9: User clicks "Save Configuration"**
```
onClick fires → saveConfig() runs
→ localStorage.setItem('provider_config_proxmox', JSON.stringify(config))
→ Show "Saving..." button state
→ Alert: "Configuration saved!"
```

## State Management

The component uses React hooks to manage state:

```javascript
const [providers, setProviders] = useState([])          // List of all providers
const [selectedProvider, setSelectedProvider] = useState(null)  // Currently selected
const [config, setConfig] = useState({})                // Current form data
const [testResult, setTestResult] = useState(null)      // Test results
const [saving, setSaving] = useState(false)             // Save button state
const [testing, setTesting] = useState(false)           // Test button state
```

## Data Flow

```
1. Component Mounts
   ↓
2. loadProviders() called
   ↓
3. API: GET /api/v1/providers
   ↓
4. setProviders([...]) updates state
   ↓
5. First provider auto-selected
   ↓
6. loadSavedConfig() loads from localStorage
   ↓
7. Form renders with data
   ↓
8. User types → onChange → setConfig()
   ↓
9. User clicks Test → testConnection()
   ↓
10. API: GET /api/v1/providers/{name}/status
    ↓
11. setTestResult() updates state
    ↓
12. Result displayed
    ↓
13. User clicks Save → saveConfig()
    ↓
14. localStorage.setItem()
    ↓
15. Alert shown
```

## Why Fields ARE Editable

Each input field has these key properties:

```jsx
<input
  type="text"
  value={config.host || ''}           ← Controlled component
  onChange={(e) => setConfig({        ← Event handler
    ...config,                        ← Spread existing config
    host: e.target.value              ← Update specific field
  })}
/>
```

**This makes the field:**
- ✅ Editable (onChange handler exists)
- ✅ Controlled (value from state)
- ✅ Reactive (updates on every keystroke)

## Switching Between Providers

```javascript
useEffect(() => {
  if (selectedProvider) {
    loadSavedConfig(selectedProvider)  // Load saved data
    setTestResult(null)                // Clear old test results
  }
}, [selectedProvider])  // Runs when selectedProvider changes
```

**What happens:**
1. User clicks different provider
2. `setSelectedProvider()` updates
3. `useEffect` detects change
4. Loads saved config for that provider
5. Clears old test results
6. Form updates with new data

## localStorage Keys

Each provider's config is stored separately:

```javascript
// Proxmox
localStorage.setItem('provider_config_proxmox', '{"host":"...","user":"..."}')

// VirtualBox
localStorage.setItem('provider_config_virtualbox', '{"vm_folder":"..."}')

// Hyper-V
localStorage.setItem('provider_config_hyperv', '{"vhd_path":"..."}')

// WSL
localStorage.setItem('provider_config_wsl', '{"install_path":"..."}')
```

## Testing the UI

### Check if providers are loading:

```javascript
// Open browser console (F12)
// On the Provider Settings page, run:
console.log(providers)

// Should see:
[
  {name: "proxmox", display_name: "Proxmox VE", ...},
  {name: "virtualbox", display_name: "VirtualBox", ...},
  {name: "hyperv", display_name: "Hyper-V", ...},
  {name: "wsl", display_name: "WSL2", ...}
]
```

### Check selected provider:

```javascript
console.log(selectedProvider)
// Should see: "proxmox" or "virtualbox" etc.
```

### Check form config:

```javascript
console.log(config)
// Should see: {host: "...", user: "...", password: "..."}
```

### Verify localStorage:

```javascript
// View all saved configs
Object.keys(localStorage)
  .filter(key => key.startsWith('provider_config_'))
  .forEach(key => {
    console.log(key, localStorage.getItem(key))
  })
```

## Common Issues & Fixes

### Issue: No providers showing

**Debug:**
```javascript
// Check if API call succeeded
fetch('http://localhost:8000/api/v1/providers')
  .then(r => r.json())
  .then(console.log)
```

**Fix:** Ensure backend is running

---

### Issue: Can't type in fields

**Debug:**
```javascript
// Check if onChange is defined
console.log(document.querySelector('input').onchange)
// Should not be null
```

**Fix:** Check React DevTools for state updates

---

### Issue: Config not saving

**Debug:**
```javascript
// Check localStorage
console.log(localStorage.getItem('provider_config_proxmox'))
```

**Fix:** Ensure localStorage is enabled in browser

---

### Issue: Provider not highlighting

**Debug:**
```javascript
// Check selectedProvider state
console.log(selectedProvider)

// Check if CSS class is applied
document.querySelector('.provider-item.active')
```

**Fix:** Verify click handler and CSS

---

## Visual States

### Normal State
```
┌─────────────┐
│ VirtualBox  │  ← Gray background, normal text
└─────────────┘
```

### Hover State
```
┌─────────────┐
│ VirtualBox  │  ← Darker background
└─────────────┘
```

### Active State
```
┌─────────────┐
│►VirtualBox  │  ← Blue border, darker background, blue text
└─────────────┘
```

## Summary

The Provider Settings page works like this:

1. **Left sidebar**: Click to select provider (fully functional)
2. **Right panel**: Shows configuration form for selected provider
3. **All inputs**: Editable text fields with live updates
4. **Test button**: Checks if provider is accessible
5. **Save button**: Persists config to localStorage
6. **Auto-load**: Saved configs load when switching providers

**The UI is fully functional!** All text fields are editable, all buttons work, and provider switching is smooth.
