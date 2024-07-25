import sys
import smaract.ctl as ctl

def assert_lib_compatibility():
    """
    Checks that the major version numbers of the Python API and the
    loaded shared library are the same to avoid errors due to 
    incompatibilities.
    Raises a RuntimeError if the major version numbers are different.
    """
    vapi = ctl.api_version
    vlib = [int(i) for i in ctl.GetFullVersionString().split('.')]
    if vapi[0] != vlib[0]:
        raise RuntimeError("Incompatible SmarActCTL python api and library version.")

def find_devices():
    buffer = ctl.FindDevices("")
    if len(buffer) == 0:
        raise ConnectionError("MCS2 no devices found.")
    return buffer.split("\n")

def initialize_device(locator):
    d_handle = ctl.Open(locator)
    channels = [0, 1, 2]  # X, Y, Z channels
    for channel in channels:
        ctl.SetProperty_i32(d_handle, channel, ctl.Property.MOVE_MODE, ctl.MoveMode.CL_ABSOLUTE)
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_VELOCITY, 1000000000)
        ctl.SetProperty_i64(d_handle, channel, ctl.Property.MOVE_ACCELERATION, 1000000000)
        ctl.SetProperty_i32(d_handle, channel, ctl.Property.AMPLIFIER_ENABLED, ctl.TRUE)
    return d_handle

def move_axis(d_handle, axis, pos_microns):
    try:
        pos_picometers = int(pos_microns * 1_000_000)  # Convert microns to picometers
        channel_index = {'X': 0, 'Y': 1, 'Z': 2}[axis]
        
        # Reverse the polarity for the Z-axis
        if axis == 'Z':
            pos_picometers = pos_picometers
        
        ctl.Move(d_handle, channel_index, pos_picometers)
        while ctl.GetProperty_i32(d_handle, channel_index, ctl.Property.CHANNEL_STATE) & ctl.ChannelState.ACTIVELY_MOVING:
            pass
        print(f"MCS2 reached the target position {axis}={pos_microns} microns.")
    except ctl.Error as e:
        print(f"Error: MCS2 {e.func}: {ctl.GetResultInfo(e.code)}, error: {ctl.ErrorCode(e.code).name} (0x{e.code:04X})")
        
def read_positions(d_handle):
    try:
        x_position_pm = ctl.GetProperty_i64(d_handle, 0, ctl.Property.POSITION)
        y_position_pm = ctl.GetProperty_i64(d_handle, 1, ctl.Property.POSITION)
        z_position_pm = ctl.GetProperty_i64(d_handle, 2, ctl.Property.POSITION)
        
        # Convert from picometers to microns
        x_position = x_position_pm / 1000000
        y_position = y_position_pm / 1000000
        z_position = -z_position_pm / 1000000  # Reverse the polarity for the Z-axis
        
        print(f"Current positions:\nX axis: {x_position} microns\nY axis: {y_position} microns\nZ axis: {z_position} microns")
    except ctl.Error as e:
        print(f"Error: MCS2 {e.func}: {ctl.GetResultInfo(e.code)}, error: {ctl.ErrorCode(e.code).name} (0x{e.code:04X})")

def close_device(d_handle):
    if d_handle:
        ctl.Close(d_handle)

def initialize_and_return_handle():
    print("*******************************************************")
    print("*  SmarAct MCS2 Programming Example (Simple Move)     *")
    print("*******************************************************")

    version = ctl.GetFullVersionString()
    print(f"SmarActCTL library version: '{version}'.")
    assert_lib_compatibility()

    try:
        locators = find_devices()
        print(f"MCS2 available devices: {locators[0]}")
        d_handle = initialize_device(locators[0])
        print(f"MCS2 opened {locators[0]}.")
        return d_handle
    except Exception as e:
        print(f"Error: {e}")
        return None

def set_mcs_position(d_handle, x, y, z):
    move_axis(d_handle, 'X', x)
    move_axis(d_handle, 'Y', y)
    move_axis(d_handle, 'Z', z)

if __name__ == "__main__":
    d_handle = initialize_and_return_handle()
    if d_handle:
        # Example usage
        move_axis(d_handle, 'X', 100)  # Move X axis to 100 microns
        read_positions(d_handle)  # Read current positions
        close_device(d_handle)  # Close device

    print("MCS2 close.")
    print("*******************************************************")
    print("Done.")
