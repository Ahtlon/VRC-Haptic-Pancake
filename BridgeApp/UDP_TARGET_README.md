# UDP Target for Haptic Pancake

This document describes how to use the UDP target for sending haptic feedback commands to external receivers.

## Overview

The UDP target allows Haptic Pancake to send vibration commands to external devices via UDP packets using the SlimeVR packet protocol. This enables support for custom haptic hardware that can receive UDP commands.

## Packet Protocol

The UDP target uses the SlimeVR packet format for vibration commands:

### Vibrate Packet Structure

| Offset | Size | Type | Description |
|--------|------|------|-------------|
| 0-2 | 3 bytes | uint8[3] | Packet ID (SlimeVR identifier) |
| 3 | 1 byte | uint8 | Packet Type (2 = Vibrate) |
| 4-11 | 8 bytes | uint64 (BE) | Packet Number (sequence counter) |
| 12-13 | 2 bytes | uint16 (BE) | Duration in milliseconds |

**Total packet size:** 14 bytes

### Field Descriptions

- **Packet ID (bytes 0-2):** Standard SlimeVR packet identifier (currently `0x00 0x00 0x00`)
- **Packet Type (byte 3):** Must be `2` to indicate a Vibrate packet
- **Packet Number (bytes 4-11):** BigEndian uint64 for packet sequencing (increments with each packet)
- **Duration (bytes 12-13):** BigEndian uint16 (0-65535 milliseconds)
  - `0`: Turn off vibration immediately
  - `1-65535`: Vibrate for specified milliseconds

## Configuration

Each tracker/receiver needs its own UDP configuration in the Haptic Pancake settings:

### Per-Tracker UDP Settings

Each tracker configuration includes:

- **`udp_ip`** (string): IP address of the haptic receiver
  - Example: `"192.168.1.100"`
  - Default: `""` (empty, no UDP output)

- **`udp_port`** (integer): UDP port number for the receiver
  - Range: 1-65535
  - Default: `6969`

### Setting Up UDP Target in Code

```python
from target_udp import UDPTarget
from app_config import AppConfig

# Load configuration
config = AppConfig.load()

# Get tracker configuration for a specific device
tracker_config = config.get_tracker_config("LHR-12345678")

# Set the UDP IP address
tracker_config.set_udp_ip("192.168.1.100")

# Set the UDP port (optional, defaults to 6969)
tracker_config.set_udp_port(7000)

# Save configuration
config.save()

# Create UDP target instance
udp_target = UDPTarget(config)

# Add a device to be controlled
udp_target.add_device(
    serial="LHR-12345678",
    model="Vive Tracker",
    index=0
)

# Set vibration strength (0.0 to 1.0+)
udp_target.set_strength("LHR-12345678", 0.5)

# Send a manual pulse
udp_target.pulse_by_serial("LHR-12345678", pulse_length=200)
```

## Receiver Implementation

To receive haptic commands, your custom hardware/software needs to:

1. Listen for UDP packets on the configured port
2. Parse the 14-byte packet structure
3. Extract the duration from bytes 12-13 (big-endian uint16)
4. Trigger vibration for the specified duration

### Example Python Receiver

```python
import socket
import struct

def receive_haptic_commands(port=6969):
    """Example UDP receiver for haptic commands"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    
    print(f"Listening for haptic commands on port {port}...")
    
    while True:
        data, addr = sock.recvfrom(1024)
        
        if len(data) == 14:
            # Parse packet
            packet_id = data[0:3]
            packet_type = data[3]
            packet_num = struct.unpack('!Q', data[4:12])[0]
            duration = struct.unpack('!H', data[12:14])[0]
            
            if packet_type == 2:  # Vibrate packet
                print(f"Vibrate command: {duration}ms (packet #{packet_num})")
                # TODO: Trigger your haptic hardware here
                if duration == 0:
                    print("  -> Stop vibration")
                else:
                    print(f"  -> Vibrate for {duration}ms")

if __name__ == '__main__':
    receive_haptic_commands()
```

### Example Arduino/ESP32 Receiver (C++)

```cpp
#include <WiFiUdp.h>

WiFiUDP udp;
const int UDP_PORT = 6969;
const int HAPTIC_PIN = 5; // GPIO pin for haptic motor

void setup() {
    Serial.begin(115200);
    pinMode(HAPTIC_PIN, OUTPUT);
    
    // Connect to WiFi first (not shown)
    
    udp.begin(UDP_PORT);
    Serial.printf("Listening on UDP port %d\n", UDP_PORT);
}

void loop() {
    int packetSize = udp.parsePacket();
    
    if (packetSize == 14) {
        uint8_t packet[14];
        udp.read(packet, 14);
        
        // Check packet type (should be 2 for vibrate)
        if (packet[3] == 2) {
            // Extract duration (bytes 12-13, big-endian)
            uint16_t duration = (packet[12] << 8) | packet[13];
            
            Serial.printf("Vibrate: %d ms\n", duration);
            
            if (duration == 0) {
                // Stop vibration
                digitalWrite(HAPTIC_PIN, LOW);
            } else {
                // Vibrate for specified duration
                digitalWrite(HAPTIC_PIN, HIGH);
                delay(duration);
                digitalWrite(HAPTIC_PIN, LOW);
            }
        }
    }
}
```

## Usage Notes

- Each receiver must have a unique IP address configured
- The UDP protocol is connectionless, so no acknowledgment of received packets
- Packet numbers increment sequentially for packet loss detection (if needed)
- Duration of 0 immediately stops vibration
- Maximum duration is 65535 milliseconds (~65.5 seconds)

## Integration with Haptic Pancake

The UDP target integrates seamlessly with the existing Haptic Pancake framework:

- Uses the same `FeedbackThread` system as OpenVR targets
- Supports vibration patterns and multipliers
- Compatible with OSC and WebSocket input servers
- Respects battery threshold settings (always returns 100% for UDP targets)

## Troubleshooting

**No packets received:**
- Check that UDP IP and port are correctly configured
- Verify firewall settings allow UDP traffic on the specified port
- Ensure receiver is listening on the correct network interface

**Incorrect vibration duration:**
- Verify receiver correctly parses big-endian uint16 (bytes 12-13)
- Check for byte order issues (network byte order = big-endian)

**Packets out of order:**
- Use the packet number (bytes 4-11) to detect and handle reordering
- Consider buffering or ignoring out-of-order packets if timing is critical
