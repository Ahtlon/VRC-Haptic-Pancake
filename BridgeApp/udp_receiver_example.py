#!/usr/bin/env python3
"""
Simple UDP Haptic Receiver Example

This script demonstrates how to receive and parse haptic vibration
commands sent by the Haptic Pancake UDP target.

Usage:
    python udp_receiver_example.py [port]

Default port: 6969
"""

import socket
import struct
import sys
import time


def parse_vibrate_packet(data):
    """
    Parse a vibrate packet according to the SlimeVR protocol.
    
    Args:
        data: Raw packet bytes (should be 14 bytes)
        
    Returns:
        Tuple of (packet_id, packet_type, packet_num, duration) or None if invalid
    """
    if len(data) != 14:
        return None
    
    # Parse packet structure
    packet_id = data[0:3]
    packet_type = data[3]
    packet_num = struct.unpack('!Q', data[4:12])[0]  # Big-endian uint64
    duration = struct.unpack('!H', data[12:14])[0]   # Big-endian uint16
    
    # Verify this is a vibrate packet
    if packet_type != 2:
        return None
    
    return (packet_id, packet_type, packet_num, duration)


def run_receiver(port=6969):
    """
    Run the UDP receiver and print received haptic commands.
    
    Args:
        port: UDP port to listen on
    """
    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind to all interfaces on the specified port
    try:
        sock.bind(('0.0.0.0', port))
        print(f"UDP Haptic Receiver")
        print(f"=" * 60)
        print(f"Listening on port {port}")
        print(f"Waiting for packets from Haptic Pancake...")
        print(f"(Press Ctrl+C to stop)")
        print(f"=" * 60)
        print()
    except OSError as e:
        print(f"Error: Could not bind to port {port}")
        print(f"  {e}")
        print(f"Make sure the port is not already in use.")
        return
    
    packet_count = 0
    last_packet_num = None
    
    try:
        while True:
            # Receive packet
            data, addr = sock.recvfrom(1024)
            
            # Parse the packet
            result = parse_vibrate_packet(data)
            
            if result:
                packet_id, packet_type, packet_num, duration = result
                packet_count += 1
                
                # Check for packet loss
                lost = ""
                if last_packet_num is not None:
                    expected = (last_packet_num + 1) % (2**64)
                    if packet_num != expected:
                        lost = f" [LOST {packet_num - expected} PACKETS]"
                
                last_packet_num = packet_num
                
                # Format timestamp
                timestamp = time.strftime("%H:%M:%S")
                
                # Print received command
                if duration == 0:
                    action = "STOP vibration"
                else:
                    action = f"Vibrate for {duration} ms"
                
                print(f"[{timestamp}] Packet #{packet_num:6d}: {action:25s} | From: {addr[0]}{lost}")
                
                # TODO: Here you would trigger your actual haptic hardware
                # For example:
                # - Turn on/off a GPIO pin
                # - Send command to a motor driver
                # - Trigger a vibration motor via PWM
                # - etc.
                
            else:
                # Invalid or unknown packet
                print(f"[WARNING] Received invalid packet ({len(data)} bytes) from {addr[0]}")
    
    except KeyboardInterrupt:
        print(f"\n")
        print(f"=" * 60)
        print(f"Receiver stopped")
        print(f"Total packets received: {packet_count}")
        print(f"=" * 60)
    
    finally:
        sock.close()


if __name__ == '__main__':
    # Get port from command line or use default
    port = 6969
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
            if port < 1 or port > 65535:
                print(f"Error: Port must be between 1 and 65535")
                sys.exit(1)
        except ValueError:
            print(f"Error: Invalid port number '{sys.argv[1]}'")
            sys.exit(1)
    
    run_receiver(port)
