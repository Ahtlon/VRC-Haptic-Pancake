# UDP Target GUI Integration

## Overview

The Haptic Pancake Bridge GUI has been updated to use the UDP target instead of the OpenVR target. This allows the application to send haptic feedback commands over the network using UDP packets, rather than directly to OpenVR/SteamVR trackers.

## Changes Made

### 1. `target_udp.py` - Added GUI Compatibility Methods

Added the following methods to make UDPTarget compatible with the GUI interface:

- **`query_devices(quiet_refresh=False)`**: Loads UDP devices from the configuration file. Unlike OpenVR which discovers devices automatically, UDP devices must be pre-configured with an IP address in the `hapticpancake-config.json` file.

- **`is_alive` property**: Always returns `True` since UDP targets don't depend on an external VR runtime.

- **`is_app_bundled` property**: Always returns `True` for compatibility with the GUI.

- **`resync_autostart()`**: Returns `False` - autostart is not supported for UDP targets.

- **`setup_autostart(autostart)`**: No-op method - autostart functionality is only relevant for OpenVR/SteamVR integration.

### 2. `main.py` - Switched to UDP Target

- Changed import from `target_ovr.OpenVRHandler` to `target_udp.UDPTarget`
- Updated type annotation from `OpenVRHandler` to `UDPTarget`
- Changed instantiation from `OpenVRHandler(config)` to `UDPTarget(config)`

### 3. `app_gui.py` - Updated UI for UDP Target

- **Autostart Checkbox**: Hidden with `visible=False` since autostart is not applicable to UDP targets
- **Status Message**: Changed from "SteamVR running/closed" to "UDP Target Ready"
- **Tooltip**: Updated to reflect that autostart is not supported

## Configuration

To use UDP haptic devices, you need to configure them in your `hapticpancake-config.json`:

```json
{
  "tracker_config_dict": {
    "MY-UDP-DEVICE-001": {
      "udp_ip": "192.168.1.100",
      "udp_port": 6969,
      "address_list": ["/avatar/parameters/HapticChest"],
      "enabled": true,
      "multiplier_override": 1.0,
      "battery_threshold": 20
    },
    "MY-UDP-DEVICE-002": {
      "udp_ip": "192.168.1.101",
      "udp_port": 6970,
      "address_list": ["/avatar/parameters/HapticHips"],
      "enabled": true
    }
  }
}
```

**Important**: Only devices with a `udp_ip` configured will be loaded. Devices without an IP address will be ignored.

## Device Serial Numbers

For UDP devices, the serial number (device ID) can be any string. Common conventions:
- `UDP-CHEST-01`
- `HAPTIC-VEST-LEFT`
- `MY-CUSTOM-DEVICE`

Choose meaningful names that help you identify which physical device or body location the configuration applies to.

## How It Works

1. **Application Start**: The GUI initializes a `UDPTarget` instance
2. **Device Loading**: `query_devices()` reads the config and creates devices for each entry with a `udp_ip`
3. **Haptic Feedback**: When OSC/WebSocket messages arrive, `set_strength()` is called
4. **UDP Transmission**: Vibration commands are sent as UDP packets to the configured IP:port
5. **Receiver**: Your custom hardware receives and processes the packets

## Testing

You can test UDP packet reception using the included example receiver:

```bash
cd BridgeApp
python3 udp_receiver_example.py
```

This will listen on port 6969 and display received haptic commands.

## Differences from OpenVR Target

| Feature | OpenVR Target | UDP Target |
|---------|---------------|------------|
| Device Discovery | Automatic via OpenVR | Manual via config file |
| Autostart | Supported (with SteamVR) | Not supported |
| Battery Level | Real battery data | Always 100% |
| Network Required | No | Yes (local network) |
| Hardware Required | VR trackers | Custom receivers |
| Flexibility | Limited to OpenVR devices | Any UDP-capable device |

## Advantages of UDP Target

1. **Custom Hardware**: Use any device that can receive UDP packets (ESP32, Arduino, Raspberry Pi, etc.)
2. **Multiple Receivers**: Send to multiple devices on your network
3. **Remote Operation**: Devices don't need to be OpenVR-compatible
4. **DIY Friendly**: Build your own haptic feedback hardware
5. **Cost Effective**: No need for expensive VR trackers

## Next Steps

- See `UDP_QUICK_START.md` for quick setup instructions
- See `UDP_TARGET_README.md` for detailed protocol documentation
- See `udp_receiver_example.py` for receiver implementation examples

## Support

For questions or issues with the UDP target integration, please open an issue on GitHub.
