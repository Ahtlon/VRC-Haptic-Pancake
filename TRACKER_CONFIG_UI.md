# Tracker Configuration UI - Implementation Summary

## Overview
Added comprehensive UI functionality for adding, configuring, and removing UDP haptic trackers directly from the GUI, eliminating the need to manually edit configuration files.

## Features Added

### 1. UDP IP and Port Configuration
**Location:** Tracker row display (app_gui.py, tracker_row method)

Each tracker now displays:
- **UDP IP Input Field**: Text input for entering the IP address of the UDP receiver (e.g., "192.168.1.100")
- **UDP Port Input Field**: Text input for entering the UDP port number (default: 6969)
- Real-time updates to configuration when values change

**Before:** Trackers showed only Battery threshold and Pulse multiplier
**After:** Trackers show Battery threshold, Pulse multiplier, UDP IP, and UDP Port

### 2. Add Tracker Button
**Location:** Devices section header (next to Refresh button)

A new "Add Tracker" button allows users to:
- Click to open a dialog for adding new trackers
- Enter tracker Serial/ID
- Enter UDP IP address
- Enter UDP port number  
- Optionally set OSC address
- Validate inputs before adding

**Dialog Fields:**
```
Add New UDP Tracker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tracker Serial/ID:    [                              ]
UDP IP Address:       [192.168.1.100                 ]
UDP Port:             [6969     ]
(Optional) OSC Address: [                           ]
                      [Add]  [Cancel]
```

### 3. Remove Tracker Button
**Location:** Each tracker row (far right)

Each tracker now has a red "Remove" button that:
- Removes the tracker from configuration
- Removes the device from UDP target
- Refreshes the GUI to remove the tracker display
- Saves changes to config file

### 4. Automatic Configuration Sync
**Location:** app_gui.py, update_tracker_config method

When users edit UDP IP or Port fields, changes are automatically:
- Validated using set_udp_ip() and set_udp_port() methods
- Saved to the tracker configuration
- Applied to the running UDP target

## Code Changes

### app_gui.py

**New Keys Added:**
```python
KEY_BTN_ADD_TRACKER = '-BTN-ADD-TRACKER-'
KEY_BTN_REMOVE_TRACKER = '-BTN-REMOVE-TRACKER-'
KEY_UDP_IP = '-UDP-IP-'
KEY_UDP_PORT = '-UDP-PORT-'
```

**GUIRenderer Constructor Updated:**
```python
def __init__(self, ..., add_tracker_event, remove_tracker_event):
    self.add_tracker_event = add_tracker_event
    self.remove_tracker_event = remove_tracker_event
```

**tracker_row Method Enhanced:**
- Added UDP IP input field (15 char width)
- Added UDP Port input field (5 char width)
- Added Remove button (red, per-tracker)
- All fields tied to tracker serial for unique identification

**New Method: show_add_tracker_dialog():**
- Modal dialog for adding new trackers
- Input validation (required fields, port range 1-65535)
- Calls add_tracker_event callback on success

**Event Handlers Added:**
```python
elif event[0] == KEY_BTN_REMOVE_TRACKER:
    self.remove_tracker_event(event[1])
elif event == KEY_BTN_ADD_TRACKER:
    self.show_add_tracker_dialog()
```

**Config Update Enhanced:**
```python
# Update UDP IP
key = (KEY_UDP_IP, tracker)
if key in values:
    self.config.get_tracker_config(tracker).set_udp_ip(values[key])

# Update UDP Port
key = (KEY_UDP_PORT, tracker)
if key in values:
    self.config.get_tracker_config(tracker).set_udp_port(values[key])
```

### main.py

**New Function: add_new_tracker()**
```python
def add_new_tracker(serial: str, udp_ip: str, udp_port: str, osc_address: str = ""):
    # Creates tracker config
    # Sets UDP IP and port
    # Optionally sets OSC address
    # Adds device to UDP target
    # Refreshes GUI
    # Saves configuration
```

**New Function: remove_tracker()**
```python
def remove_tracker(serial: str):
    # Removes from UDP target (vr.remove_device)
    # Removes from config dictionary
    # Removes from GUI tracker list
    # Recreates window to update display
    # Saves configuration
```

**GUIRenderer Initialization Updated:**
```python
gui = GUIRenderer(config, pulse_test, restart_bridge_server, refresh_vr, 
                  add_external_target, setup_autostart, 
                  add_new_tracker, remove_tracker)
```

## UI Layout Changes

### Devices Section Header
**Before:**
```
Devices: [0 Online / 0 Total]         [Refresh]
```

**After:**
```
Devices: [0 Online / 0 Total]  [Add Tracker] [Refresh]
```

### Tracker Display Row
**Before:**
```
● Tracker-001 - Vive Tracker    [OSC Address Input]  [Setup] [Identify]
  Battery threshold: [20]% | Pulse multiplier: [1.0]
```

**After:**
```
● Tracker-001 - Vive Tracker    [OSC Address Input]  [Setup] [Identify]
  Battery threshold: [20]% | Pulse multiplier: [1.0] | 
  UDP IP: [192.168.1.100  ] Port: [6969] | [Remove]
```

## Usage Flow

### Adding a New Tracker
1. User clicks "Add Tracker" button
2. Dialog appears with input fields
3. User enters:
   - Serial/ID (e.g., "CHEST-HAPTIC-01")
   - UDP IP (e.g., "192.168.1.100")
   - UDP Port (e.g., "6969")
   - Optional OSC address
4. User clicks "Add"
5. Validation checks inputs
6. If valid:
   - Tracker added to config
   - Device added to UDP target
   - GUI refreshes
   - Tracker appears in list
7. Changes auto-saved to config file

### Configuring Existing Tracker
1. User sees tracker in device list
2. User edits UDP IP or Port fields
3. Changes detected via enable_events=True
4. update_tracker_config() called automatically
5. Values validated and saved
6. Config file updated

### Removing a Tracker
1. User clicks red "Remove" button on tracker
2. Confirmation (implicit via button color)
3. Tracker removed from:
   - UDP target device list
   - Configuration dictionary
   - GUI tracker list
4. Window recreated to show updated list
5. Config file saved

## Benefits

1. **User-Friendly**: No need to manually edit JSON config files
2. **Immediate Feedback**: See trackers immediately after adding
3. **Error Prevention**: Input validation prevents invalid configurations
4. **Live Updates**: Changes to IP/port apply in real-time
5. **Safe Removal**: Remove trackers cleanly from all systems

## Testing Performed

✅ Tracker configuration backend (set_udp_ip, set_udp_port)
✅ UDP target device loading with IP configuration
✅ Config save/load with UDP settings
✅ Add tracker function creates correct config
✅ Remove tracker function cleans up properly
✅ GUI code structure validation
✅ Python syntax validation

## Technical Details

### Key Components

**TrackerConfig (app_config.py):**
- `udp_ip`: str - IP address of UDP receiver
- `udp_port`: int - Port number (1-65535)
- `set_udp_ip(value)`: Validates and sets IP
- `set_udp_port(value)`: Validates and sets port

**UDPTarget (target_udp.py):**
- `add_device(serial, model, index)`: Adds device to UDP target
- `remove_device(serial)`: Removes device and cleans up resources
- `query_devices()`: Loads devices from config where udp_ip is set

**GUIRenderer (app_gui.py):**
- `tracker_row()`: Generates tracker UI with new fields
- `show_add_tracker_dialog()`: Modal dialog for adding trackers
- `update_tracker_config()`: Syncs GUI values to config

### Event Flow

```
User Action → GUI Event → Callback in main.py → 
Config Update → UDP Target Update → GUI Refresh → Config Save
```

### Data Validation

**UDP IP:**
- String field, no strict validation (allows hostnames)
- Empty string treated as unconfigured
- Whitespace trimmed automatically

**UDP Port:**
- Must be integer between 1 and 65535
- Validated in dialog before adding
- Validated in config setter

**Tracker Serial:**
- Required field
- Used as unique identifier
- No special character restrictions

## Future Enhancements (Optional)

- Add tracker presets (chest, hips, etc.) with default IPs
- Test UDP connection button per tracker
- Import/export tracker configurations
- Duplicate tracker button
- Batch add multiple trackers
- Visual IP address validation (format check)
