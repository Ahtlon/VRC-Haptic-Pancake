# Tracker Configuration UI - Visual Mockup

## Before (No Tracker Configuration UI)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Haptic Pancake Bridge v0.8.0-beta.2                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Server Settings:                                                        │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │ Type: [OSC (VRChat) ▼]                                             ││
│  │ □ Auto-detect port (OSCQuery)                                      ││
│  │ IP: [127.0.0.1      ]  Port: [9001 ]                 [Apply]      ││
│  │ Status: Listening on 127.0.0.1:9001                                ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
│  Haptic settings:                                                        │
│  ┌──────────────────────┐  ┌──────────────────────┐                    │
│  │ Proximity Feedback   │  │ Velocity Feedback    │                    │
│  │ ...                  │  │ ...                  │                    │
│  └──────────────────────┘  └──────────────────────┘                    │
│                                                                          │
│  Devices: 1 Online / 1 Total                           [Refresh]       │
│  ┌────────────────────────────────────────────────────────────────────┐│
│  │ ● UDP-DEVICE-001 - UDP Haptic Device                               ││
│  │   [/avatar/parameters/HapticChest        ]  [Setup] [Identify]     ││
│  │                                                                     ││
│  │   Battery threshold: [20]% | Pulse multiplier: [1.0]               ││
│  │                                                                     ││
│  └────────────────────────────────────────────────────────────────────┘│
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

NOTE: To add trackers, user must manually edit hapticpancake-config.json:
{
  "tracker_config_dict": {
    "UDP-DEVICE-001": {
      "udp_ip": "192.168.1.100",
      "udp_port": 6969,
      ...
    }
  }
}
```

## After (With Tracker Configuration UI)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Haptic Pancake Bridge v0.8.0-beta.2                                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  Server Settings:                                                                │
│  ┌────────────────────────────────────────────────────────────────────────────┐│
│  │ Type: [OSC (VRChat) ▼]                                                     ││
│  │ □ Auto-detect port (OSCQuery)                                              ││
│  │ IP: [127.0.0.1      ]  Port: [9001 ]                         [Apply]      ││
│  │ Status: Listening on 127.0.0.1:9001                                        ││
│  └────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
│  Haptic settings:                                                                │
│  ┌──────────────────────┐  ┌──────────────────────┐                            │
│  │ Proximity Feedback   │  │ Velocity Feedback    │                            │
│  │ ...                  │  │ ...                  │                            │
│  └──────────────────────┘  └──────────────────────┘                            │
│                                                                                  │
│  Devices: 2 Online / 2 Total               [Add Tracker] [Refresh]     ◄── NEW │
│  ┌────────────────────────────────────────────────────────────────────────────┐│
│  │ ● UDP-CHEST - UDP Haptic Device                                            ││
│  │   [/avatar/parameters/HapticChest        ]  [Setup] [Identify]             ││
│  │                                                                             ││
│  │   Battery threshold: [20]% | Pulse multiplier: [1.0] |                     ││
│  │   UDP IP: [192.168.1.100  ] Port: [6969] | [Remove] ◄──────────────── NEW ││
│  │                            ▲                    ▲                           ││
│  │                            NEW                  NEW                         ││
│  ├─────────────────────────────────────────────────────────────────────────────┤│
│  │ ● UDP-HIPS - UDP Haptic Device                                             ││
│  │   [/avatar/parameters/HapticHips         ]  [Setup] [Identify]             ││
│  │                                                                             ││
│  │   Battery threshold: [20]% | Pulse multiplier: [1.0] |                     ││
│  │   UDP IP: [192.168.1.101  ] Port: [6969] | [Remove]                       ││
│  │                                                                             ││
│  └────────────────────────────────────────────────────────────────────────────┘│
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Add Tracker Dialog

When user clicks "Add Tracker" button:

```
┌─────────────────────────────────────────────┐
│  Add New UDP Tracker                        │
├─────────────────────────────────────────────┤
│                                             │
│  Tracker Serial/ID:                         │
│  [UDP-CHEST-01                          ]   │
│                                             │
│  UDP IP Address:                            │
│  [192.168.1.100                         ]   │
│                                             │
│  UDP Port:                                  │
│  [6969     ]                                │
│                                             │
│  (Optional) OSC Address:                    │
│  [/avatar/parameters/HapticChest        ]   │
│                                             │
│              [Add]    [Cancel]              │
└─────────────────────────────────────────────┘
```

## Key UI Improvements

### 1. Inline UDP Configuration
- **Before**: Hidden in config file
- **After**: Visible and editable in each tracker row

### 2. Add Tracker Workflow
- **Before**: Edit JSON manually → restart app → hope it works
- **After**: Click button → fill form → instant feedback

### 3. Remove Tracker Workflow
- **Before**: Edit JSON → remove entry → restart app
- **After**: Click red "Remove" button → tracker gone

### 4. Visual Feedback
- Each tracker shows complete configuration
- UDP IP and Port clearly visible
- Easy to spot misconfigured trackers
- Remove button in tracker red (destructive action)

## Layout Dimensions

### Tracker Row Layout:
```
[Status][Icon] Serial - Model     [OSC Address (35 chars)] [Setup] [Identify]
  [Space] Battery: [spin(3)] | Pulse: [input(4)] | UDP IP: [input(15)] Port: [input(5)] | [Remove]
```

### Field Sizes:
- OSC Address: 35 characters
- Pulse Multiplier: 4 characters
- UDP IP: 15 characters (fits IPv4 addresses)
- UDP Port: 5 characters (fits 1-65535)

### Button Colors:
- Setup: Default theme
- Identify: Default theme  
- Remove: Red (button_color='red')
- Add Tracker: Default theme
- Refresh: Default theme

## User Experience Flow

### Adding First Tracker:
1. Start with empty device list
2. Click "Add Tracker"
3. Enter details in dialog
4. Click "Add"
5. See tracker appear immediately
6. Configure UDP IP if not set in dialog

### Configuring Existing Tracker:
1. See tracker in list
2. Click in UDP IP field
3. Type new IP address
4. Field auto-saves on change
5. Tracker immediately uses new IP

### Removing Tracker:
1. See tracker in list
2. Click red "Remove" button
3. Tracker disappears from list
4. Configuration automatically saved

## Validation Messages

### Add Tracker Dialog Errors:
- "Please enter a tracker serial/ID" (empty serial)
- "Please enter a UDP IP address" (empty IP)
- "Please enter a UDP port" (empty port)
- "Port must be between 1 and 65535" (invalid range)
- "Port must be a valid number" (non-numeric)

### Success Indicators:
- Tracker appears in device list
- Status shows as online (green ●)
- All fields populated correctly
