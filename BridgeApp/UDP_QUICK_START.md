# UDP Target Quick Start Guide

## What is the UDP Target?

The UDP Target allows Haptic Pancake to send vibration commands to external devices over your network using UDP packets. This is useful for:
- Custom haptic hardware (ESP32, Arduino, etc.)
- Remote haptic devices
- DIY haptic vests or accessories
- Any device that can receive UDP packets

## Quick Setup

### 1. Test the Receiver

First, test that you can receive packets:

```bash
cd BridgeApp
python3 udp_receiver_example.py
```

This will listen on port 6969 and display any haptic commands it receives.

### 2. Configure a Tracker

In your Haptic Pancake configuration, each tracker needs:
- **UDP IP Address**: The IP of your haptic device (e.g., `192.168.1.100`)
- **UDP Port**: The port to send to (default: `6969`)

Edit your `hapticpancake-config.json`:

```json
{
  "tracker_config_dict": {
    "LHR-12345678": {
      "udp_ip": "192.168.1.100",
      "udp_port": 6969,
      ...
    }
  }
}
```

### 3. Use the UDP Target

```python
from target_udp import UDPTarget
from app_config import AppConfig

config = AppConfig.load()
udp_target = UDPTarget(config)

# Add your tracker
udp_target.add_device("LHR-12345678", "Vive Tracker", index=0)

# Send haptic commands
udp_target.set_strength("LHR-12345678", 0.5)  # 50% intensity
```

## Packet Format

Each packet is 14 bytes:
- Bytes 0-2: Packet ID (always `00 00 00`)
- Byte 3: Type (always `2` for vibrate)
- Bytes 4-11: Packet number (increments each packet)
- Bytes 12-13: Duration in milliseconds (0 = stop, 1-65535 = vibrate)

## Example Receiver (Python)

```python
import socket
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 6969))

while True:
    data, addr = sock.recvfrom(1024)
    if len(data) == 14 and data[3] == 2:  # Vibrate packet
        duration = struct.unpack('!H', data[12:14])[0]
        print(f"Vibrate for {duration}ms")
        # TODO: Trigger your haptic hardware
```

## Example Receiver (Arduino/ESP32)

```cpp
WiFiUDP udp;
udp.begin(6969);

void loop() {
    int size = udp.parsePacket();
    if (size == 14) {
        uint8_t packet[14];
        udp.read(packet, 14);
        
        if (packet[3] == 2) {  // Vibrate packet
            uint16_t duration = (packet[12] << 8) | packet[13];
            
            if (duration > 0) {
                digitalWrite(MOTOR_PIN, HIGH);
                delay(duration);
                digitalWrite(MOTOR_PIN, LOW);
            }
        }
    }
}
```

## Troubleshooting

**No packets received?**
- Check IP address is correct
- Verify port is not blocked by firewall
- Make sure receiver is running
- Test with `udp_receiver_example.py` first

**Packets but no vibration?**
- Check your hardware connections
- Verify duration parsing (big-endian!)
- Add debug prints to see packet contents

## More Information

- Full documentation: `UDP_TARGET_README.md`
- Implementation details: `target_udp.py` (fully commented)
- Working example: `udp_receiver_example.py`

## Support

For questions or issues with the UDP target, please open an issue on GitHub or join the Discord server.
