"""
UDP Target for Haptic Pancake Bridge

This module implements a UDP-based target for sending haptic feedback commands
to receivers using the SlimeVR packet protocol.

Packet Structure (Vibrate Packet):
    Offset | Size     | Type        | Description
    -------|----------|-------------|----------------------------------
    0-2    | 3 bytes  | uint8[3]    | Packet ID (SlimeVR identifier)
    3      | 1 byte   | uint8       | Packet Type (2 = Vibrate)
    4-11   | 8 bytes  | uint64 (BE) | Packet Number (sequence)
    12-13  | 2 bytes  | uint16 (BE) | Duration in milliseconds
    
Duration Field:
    - 0: Turn off vibration immediately
    - 1-65535: Vibrate for specified milliseconds
"""

import socket
import struct
import threading
import time
from app_runner import FeedbackThread
from app_config import AppConfig, VRTracker
from typing import Dict, List


class UDPTarget:
    """
    UDP Target handler for sending haptic feedback commands via UDP packets.
    
    This class manages UDP sockets for each tracker and sends vibration commands
    using the SlimeVR packet protocol.
    """
    
    # SlimeVR packet identifier (3 bytes)
    PACKET_ID = bytes([0x00, 0x00, 0x00])
    
    # Packet type for vibration command
    PACKET_TYPE_VIBRATE = 2
    
    def __init__(self, config: AppConfig):
        """
        Initialize the UDP target handler.
        
        Args:
            config: Application configuration containing tracker settings
        """
        self.config = config
        self.devices: List[VRTracker] = []
        self.vibration_managers: Dict[str, FeedbackThread] = {}
        self.sockets: Dict[str, socket.socket] = {}
        self.packet_numbers: Dict[str, int] = {}  # Track packet sequence per device
        self.lock = threading.Lock()  # Thread safety for socket operations
        
    def add_device(self, serial: str, model: str, index: int = 0):
        """
        Add a device to be controlled via UDP.
        
        Args:
            serial: Unique serial number of the device
            model: Model name of the device
            index: Device index (for compatibility with FeedbackThread)
        """
        # Create a VRTracker object
        tracker = VRTracker(index, model, serial)
        
        # Check if device already exists
        if serial not in [d.serial for d in self.devices]:
            self.devices.append(tracker)
            self.packet_numbers[serial] = 0
            
            # Start a feedback thread for this device
            if serial not in self.vibration_managers:
                thread = FeedbackThread(
                    self.config, 
                    tracker, 
                    self._send_pulse, 
                    self._get_battery_level
                )
                thread.daemon = True
                thread.start()
                self.vibration_managers[serial] = thread
                
            print(f"[UDPTarget] Added device: {serial} ({model})")
    
    def remove_device(self, serial: str):
        """
        Remove a device and clean up its resources.
        
        Args:
            serial: Serial number of the device to remove
        """
        # Remove from devices list
        self.devices = [d for d in self.devices if d.serial != serial]
        
        # Stop the vibration manager thread
        if serial in self.vibration_managers:
            del self.vibration_managers[serial]
            
        # Close the socket
        with self.lock:
            if serial in self.sockets:
                self.sockets[serial].close()
                del self.sockets[serial]
                
        # Clear packet counter
        if serial in self.packet_numbers:
            del self.packet_numbers[serial]
            
        print(f"[UDPTarget] Removed device: {serial}")
    
    def _get_socket(self, serial: str) -> socket.socket:
        """
        Get or create a UDP socket for the specified device.
        
        Args:
            serial: Serial number of the device
            
        Returns:
            UDP socket for the device
        """
        with self.lock:
            if serial not in self.sockets:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sockets[serial] = sock
            return self.sockets[serial]
    
    def _get_next_packet_number(self, serial: str) -> int:
        """
        Get the next packet sequence number for a device.
        
        Args:
            serial: Serial number of the device
            
        Returns:
            Next packet sequence number
        """
        with self.lock:
            if serial not in self.packet_numbers:
                self.packet_numbers[serial] = 0
            packet_num = self.packet_numbers[serial]
            # Increment and wrap at max uint64
            self.packet_numbers[serial] = (packet_num + 1) % (2**64)
            return packet_num
    
    def _build_vibrate_packet(self, serial: str, duration_ms: int) -> bytes:
        """
        Build a vibrate packet according to the SlimeVR protocol.
        
        Packet Structure:
            - Bytes 0-2: Packet ID (3 bytes)
            - Byte 3: Packet Type (1 byte, value = 2 for vibrate)
            - Bytes 4-11: Packet Number (8 bytes, big-endian uint64)
            - Bytes 12-13: Duration (2 bytes, big-endian uint16)
        
        Args:
            serial: Serial number of the device
            duration_ms: Vibration duration in milliseconds (0-65535)
            
        Returns:
            14-byte packet ready to send
        """
        # Clamp duration to valid range
        duration_ms = max(0, min(duration_ms, 65535))
        
        # Get next packet number
        packet_num = self._get_next_packet_number(serial)
        
        # Build packet
        # Format: 3 bytes (BBB) + 1 byte (B) + 8 bytes (Q) + 2 bytes (H)
        # '!' means network byte order (big-endian)
        packet = struct.pack(
            '!BBBBQH',
            self.PACKET_ID[0],           # Byte 0: First byte of packet ID
            self.PACKET_ID[1],           # Byte 1: Second byte of packet ID  
            self.PACKET_ID[2],           # Byte 2: Third byte of packet ID
            self.PACKET_TYPE_VIBRATE,    # Byte 3: Packet type (2 = vibrate)
            packet_num,                  # Bytes 4-11: Packet number (big-endian uint64)
            duration_ms                  # Bytes 12-13: Duration (big-endian uint16)
        )
        
        return packet
    
    def _send_pulse(self, index: int, pulse_length: int):
        """
        Send a haptic pulse via UDP.
        
        This method is called by FeedbackThread to trigger vibration.
        
        Args:
            index: Device index (used to look up serial)
            pulse_length: Duration of the pulse in milliseconds
        """
        # Find the device by index
        device = None
        for d in self.devices:
            if d.index == index:
                device = d
                break
        
        if device is None:
            return
        
        # Get the tracker configuration
        tracker_config = self.config.get_tracker_config(device.serial)
        
        # Get the UDP IP address from tracker config
        # Check if udp_ip is set in the tracker config
        udp_ip = getattr(tracker_config, 'udp_ip', None)
        
        if not udp_ip:
            # No IP configured, cannot send
            return
        
        # Get the UDP port (default to 6969 if not specified)
        udp_port = getattr(tracker_config, 'udp_port', 6969)
        
        try:
            # Build the packet
            packet = self._build_vibrate_packet(device.serial, pulse_length)
            
            # Get the socket and send
            sock = self._get_socket(device.serial)
            sock.sendto(packet, (udp_ip, udp_port))
            
        except Exception as e:
            print(f"[UDPTarget] Error sending pulse to {device.serial}: {e}")
    
    def _get_battery_level(self, index: int) -> float:
        """
        Get battery level for a device.
        
        For UDP targets, battery level is not available, so always return 100%.
        
        Args:
            index: Device index
            
        Returns:
            Battery level as a float (0.0 to 1.0), always 1.0 for UDP targets
        """
        return 1.0
    
    def set_strength(self, serial: str, strength: float):
        """
        Set the vibration strength for a device.
        
        Args:
            serial: Serial number of the device
            strength: Vibration strength (0.0 to 1.0+)
        """
        if serial in self.vibration_managers:
            self.vibration_managers[serial].set_strength(strength)
    
    def pulse_by_serial(self, serial: str, pulse_length: int = 200):
        """
        Trigger a manual pulse for a device.
        
        Args:
            serial: Serial number of the device
            pulse_length: Duration of the pulse in milliseconds
        """
        if serial in self.vibration_managers:
            self.vibration_managers[serial].force_pulse(pulse_length)
    
    def get_devices(self) -> List[VRTracker]:
        """
        Get the list of managed devices.
        
        Returns:
            List of VRTracker objects
        """
        return self.devices
    
    def query_devices(self, quiet_refresh: bool = False) -> List[VRTracker]:
        """
        Query and return available UDP devices from configuration.
        
        For UDP targets, devices are populated from the configuration file
        (tracker_config_dict) rather than being discovered like OpenVR devices.
        This method loads devices that have a udp_ip configured.
        
        Args:
            quiet_refresh: If True, suppress log output
            
        Returns:
            List of VRTracker objects with UDP configuration
        """
        # Load devices from config that have UDP IP configured
        for serial, tracker_config in self.config.tracker_config_dict.items():
            if tracker_config.udp_ip:  # Only add devices with UDP IP configured
                # Check if device already exists
                if serial not in [d.serial for d in self.devices]:
                    # Create a tracker with a reasonable index
                    index = len(self.devices)
                    model = "UDP Haptic Device"
                    self.add_device(serial, model, index)
                    if not quiet_refresh:
                        print(f"[UDPTarget] Loaded UDP device from config: {serial} -> {tracker_config.udp_ip}:{tracker_config.udp_port}")
        
        return self.devices
    
    @property
    def is_alive(self) -> bool:
        """
        Check if the UDP target is operational.
        
        For UDP targets, we're always "alive" since we don't depend on
        an external runtime like OpenVR. Returns True as long as the
        target is initialized.
        
        Returns:
            Always True for UDP targets
        """
        return True
    
    @property
    def is_app_bundled(self) -> bool:
        """
        Check if the application is bundled (PyInstaller, etc.).
        
        For UDP targets, this property is only used for GUI display purposes
        and doesn't affect functionality. Returns True for GUI compatibility
        to avoid showing "app unbundled" messages.
        
        Returns:
            Always True for UDP targets (for GUI compatibility)
        """
        return True
    
    def resync_autostart(self) -> bool:
        """
        Resync autostart configuration with the VR runtime.
        
        UDP targets don't support autostart functionality since they
        don't integrate with OpenVR/SteamVR.
        
        Returns:
            Always False (no autostart changes)
        """
        return False
    
    def setup_autostart(self, autostart: bool):
        """
        Setup autostart with the VR runtime.
        
        UDP targets don't support autostart functionality since they
        don't integrate with OpenVR/SteamVR. This is a no-op for
        compatibility with the GUI.
        
        Args:
            autostart: Ignored for UDP targets
        """
        # No-op: UDP targets don't support autostart
        pass
    
    def shutdown(self):
        """
        Shut down the UDP target and clean up resources.
        """
        print("[UDPTarget] Shutting down...")
        
        # Close all sockets
        with self.lock:
            for sock in self.sockets.values():
                sock.close()
            self.sockets.clear()
        
        # Clear devices
        self.devices.clear()
        self.vibration_managers.clear()
        self.packet_numbers.clear()
        
        print("[UDPTarget] Shutdown complete")
