# Attidude.py
# Receives attitude data in yaw, pitch, roll; sends attitude back in quaternion format

import time
import math
import threading
from pymavlink import mavutil
from terminal_utils import print_info, print_success, print_warning, print_error, print_status

SERIAL_PORT = "/dev/ttyAMA0"
BAUD_RATE = 115200
MSG_ID_ATTITUDE = mavutil.mavlink.MAVLINK_MSG_ID_ATTITUDE

class Attitude:
    def __init__(self,
                receiver_ip = '192.168.0.103', 
                receiver_port = 14550, 
                sender_ip = '192.168.0.103', 
                sender_port = 14550, 
                local_ip = '192.168.0.104', 
                local_port = 14550):
        """
        :param receiver_ip: IP address where ATTITUDE messages are received (default '192.168.0.103')
        :param receiver_port: port for receiving ATTITUDE messages (default 14550)
        :param sender_ip: IP address to which we send SET_ATTITUDE_TARGET messages (default '192.168.0.103')
        :param sender_port: port to which we send SET_ATTITUDE_TARGET messages (default 14550)
        :param local_ip: local IP address from which we send messages (default '192.168.0.104')
        :param local_port: local port from which we send messages (default 14550)
        """             
                                        # receiving
        self.receiver_address = f'udp:{receiver_ip}:{receiver_port}'

                                        # sending
        self.sender_address = f'udpout:{sender_ip}:{sender_port}'
        self.source_address = (local_ip, local_port)
                                        # initiate sending connection
        self.connection = self.__establish_connection()

        self.start_time = None          # starting time for elapsed time calculation

        self.d_msg_time_boot_ms = 0.0   # stores ATTITUDE message information
        self.d_msg_roll = 0.0
        self.d_msg_pitch = 0.0
        self.d_msg_yaw = 0.0
        self.d_msg_rollspeed = 0.0
        self.d_msg_pitchspeed = 0.0
        self.d_msg_yawspeed = 0.0

        self.d_time_boot_ms = 0.0       # stores latest ATTITUDE message information (state)
        self.d_roll = 0.0
        self.d_pitch = 0.0
        self.d_yaw = 0.0
        self.d_rollspeed = 0.0
        self.d_pitchspeed = 0.0
        self.d_yawspeed = 0.0

        # Thread control
        self.receiver_thread = None
        self.running = False

    def __establish_connection(self):
        """ Establishes connection """
        # Using UDP connection for testing without physical connection
        connection = mavutil.mavlink_connection('udpout:localhost:14550')

        print_info("Waiting for heartbeat...")
        connection.wait_heartbeat()
        print_success(f"Heartbeat received from system {connection.target_system}")

        # Set stream
        self.set_attitude_rate(connection, 10, True)
        return connection

    def set_attitude_rate(self, master, hz=10, enable=True):
        """
        Set the rate at which ATTITUDE messages are requested from the flight controller.
        
        :param master: MAVLink connection object
        :param hz: Frequency in Hz (default 10Hz)
        :param enable: Whether to enable or disable the stream
        """
        rate_us = int(1e6 / hz) if enable else 0
        print_info(f"[+] {'Requesting' if enable else 'Disabling'} ATTITUDE at {hz if enable else 0} Hz")

        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL,
            0,
            MSG_ID_ATTITUDE,
            rate_us,
            0, 0, 0, 0, 0
        )


    def _receiver_loop(self):
        """ Internal method for the receiver thread loop """
        while self.running:
            # 'blocking = true' means it will wait for a message to arrive
            msg = self.connection.recv_match(type = 'ATTITUDE', blocking = True)
            if msg:
                self.d_msg_time_boot_ms = msg.time_boot_ms
                self.d_msg_roll = msg.roll
                self.d_msg_pitch = msg.pitch
                self.d_msg_yaw = msg.yaw
                self.d_msg_rollspeed = msg.rollspeed
                self.d_msg_pitchspeed = msg.pitchspeed
                self.d_msg_yawspeed = msg.yawspeed

                print_status("Received ATTITUDE message", "info")
                print_info(f"Time Boot (ms): {self.d_msg_time_boot_ms}")
                print_info(f"Roll (rad): {self.d_msg_roll}")
                print_info(f"Pitch (rad): {self.d_msg_pitch}")
                print_info(f"Yaw (rad): {self.d_msg_yaw}")
                print_info(f"Roll Speed (rad/s): {self.d_msg_rollspeed}")
                print_info(f"Pitch Speed (rad/s): {self.d_msg_pitchspeed}")
                print_info(f"Yaw Speed (rad/s): {self.d_msg_yawspeed}")

    def start_receiving(self):
        """ Starts the receiver thread """
        if not self.running:
            self.running = True
            self.receiver_thread = threading.Thread(target=self._receiver_loop)
            self.receiver_thread.daemon = True  # Thread will exit when main program exits
            self.receiver_thread.start()
            print_success("Receiver thread started")

    def stop_receiving(self):
        """ Stops the receiver thread """
        self.running = False
        if self.receiver_thread:
            self.receiver_thread.join()
            print_warning("Receiver thread stopped")

    def set_attitude(self):
        """ Sets the object state to the new """
        self.d_time_boot_ms = self.d_msg_time_boot_ms
        self.d_roll = self.d_msg_roll
        self.d_pitch = self.d_msg_pitch
        self.d_yaw = self.d_msg_yaw
        self.d_rollspeed = self.d_msg_rollspeed
        self.d_pitchspeed = self.d_msg_pitchspeed
        self.d_yawspeed = self.d_msg_yawspeed
        print_status("Updated state", "info")
        print_info(f"Time Boot (ms): {self.d_time_boot_ms}")
        print_info(f"Roll (rad): {self.d_roll}")
        print_info(f"Pitch (rad): {self.d_pitch}")
        print_info(f"Yaw (rad): {self.d_yaw}")
        print_info(f"Roll Speed (rad/s): {self.d_rollspeed}")
        print_info(f"Pitch Speed (rad/s): {self.d_pitchspeed}")
        print_info(f"Yaw Speed (rad/s): {self.d_yawspeed}")

    def get_attitude(self) -> tuple:
        """ Returns the latest attitude """
        return (self.d_roll, self.d_pitch, self.d_yaw)

    def send_attitude(self, roll: float, pitch: float, yaw: float):
        """ Sends ATTITUDE (once calculated) """
        self.start_time = time.time()

        try:
            target_system = 1           # Example target system ID
            target_component = 1        # Example target component ID
            type_mask = (1 << 6)        # Bitmask to ignore throttle/thrust

            q = self.__euler_to_quaternion(roll, pitch, yaw)
            if not q:                   # Default to identity quaternion if conversion fails
                                        # (so no rotation)
                q = (1.0, 0.0, 0.0, 0.0)
            body_roll_rate = roll       # Roll rate in rad/s
            body_pitch_rate = pitch     # Pitch rate in rad/s
            body_yaw_rate = yaw         # Yaw rate in rad/s
            thrust = 0.0                # Example thrust (50%)

            time_boot_ms = int((time.time() - self.start_time) * 1000)
            print_info(f"Sending SET_ATTITUDE_TARGET message with time_boot_ms = {time_boot_ms}...")

            self.connection.mav.set_attitude_target_send(
                time_boot_ms,
                target_system,
                target_component,
                type_mask,
                q,
                body_roll_rate,
                body_pitch_rate,
                body_yaw_rate,
                thrust
            )

            print_success("Message sent successfully")

        except KeyboardInterrupt:
            print_warning("Transmission stopped by user")

        
    def __euler_to_quaternion(self, roll: float, pitch: float, yaw: float) -> tuple:
        """ Convert roll (x), pitch (y), and yaw (z) into a quaternion
        
        Example usage:
        q = to_quaternion(roll_in_radians, pitch_in_radians, yaw_in_radians)
        print_info(f"Quaternion: w = {q[0]}, x = {q[1]}, y = {q[2]}, z = {q[3]}")
        where roll_in_radians, pitch_in_radians, and yaw_in_radians are the Euler angles in radians
        """
        cr = math.cos(roll * 0.5)
        sr = math.sin(roll * 0.5)
        cp = math.cos(pitch * 0.5)
        sp = math.sin(pitch * 0.5)
        cy = math.cos(yaw * 0.5)
        sy = math.sin(yaw * 0.5)

        w = cr * cp * cy + sr * sp * sy
        x = sr * cp * cy - cr * sp * sy
        y = cr * sp * cy + sr * cp * sy
        z = cr * cp * sy - sr * sp * cy

        return (w, x, y, z)                 # quaternion (w, x, y, z) format


if __name__ == "__main__":
    attitude = Attitude()
    
    # Uncomment depending on which functionality to test
    # attitude.start_receiving()
