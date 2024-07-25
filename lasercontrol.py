import serial
import serial.tools.list_ports as port_list
import numpy as np
from time import sleep 

class laser1(object):
    """ Class to control Arroyo Instrument's TEC Sources """

    def __init__(self):
        """ Sets up connection to Arroyo device """
        try:
            ports = list(port_list.comports())
            
            if ports:
                selected_port = ports[0][0]  # Choose the first port
                print(f"Connecting to port {selected_port}")
                
                self.ser = serial.Serial(port=selected_port, baudrate=38400, timeout=0)
                
                if self.ser.is_open:
                    print(f"Connected to {selected_port}")
                    self.ser.write(b'*IDN? \r\n')
                    sleep(0.1)
                    print("Instrument model: " + bytes.decode(self.ser.read(256)))
            else:
                print("No COM ports available.")
        except serial.SerialException as e:
            print(f"Failed to connect: {e}")

    def write_command(self, command):
        """Takes in string type AT command and returns string type response"""
        response = None
        self.ser.write(str.encode(command) + b'\r\n')
        sleep(0.1)
        response = bytes.decode(self.ser.read(256))
        return response


    def close(self):
        """ Closes serial connection with controller """
        self.ser.close()
        sleep(0.1)
        if not self.ser.is_open:
            print("\n" + self.port + " has been closed.\n")
        return



    def read_mode(self):
        """ Queries the operation mode of the controller 
            Returns 1 of 3 string values:
                T   Temperature
                R   Resistance
                ITE Current """
        response = self.write_command("LASer:MODE? ").split("\r")[0]
        return(response)

    def set_mode(self, mode):
        """ Sets the operation mode of the controller 
            Takes 1 of 3 string values:
                T   Temperature
                R   Resistance
                ITE Current """
        print("Controller mode is set to: " + self.read_mode())
        print("mode=",mode)
        self.write_command("LASer:MODE:BURST " + mode + " ")
        if mode == self.read_mode():
            print("Controller mode updated to: " + mode)
        else:
            print("Failed to update controller mode!")
        return()

    def read_current(self):
        """ Queries the measured output value of the current
            Returns a float type value """
        response = float(self.write_command("LASer:set:LDI? "))
        return(response)

    def set_current(self, set_point):
        """ """
        # if self.read_mode() != "LDI":
        print(self.read_mode(),str(set_point))
        self.write_command("LAS:LDI " + str(set_point) + " ")
        if float(set_point) == self.read_current():
            print("Updated current set point to: " + str(set_point) + " mA")
            return True
        else:
            print("Failed to update current set point!")
            return False

# Usage example
if __name__ == "__main__":
    # Create an instance of the arroyo class
    laser = laser1()

    # Prompt the user to enter the desired current value
    try:
        current_set_point = float(input("Enter the desired current value (mA): "))
        # Set the current to the user-specified value
        laser.set_current(current_set_point)
    except ValueError:
        print("Invalid input! Please enter a valid numeric value for the current.")
