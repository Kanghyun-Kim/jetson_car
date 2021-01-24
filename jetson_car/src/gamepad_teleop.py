# Gamepad Driver Class for Jetson Teleoperation with Shanwan Gamepad.
# Released by Applesquiz (https://github.com/Kanghyun-Kim/gamepad)
# Inspired by the gist by rdb:
# https://gist.github.com/rdb/8864666

# Typical usage example:
#  pad = Gamepad_teleop()
#  pad = run()

import os, struct, array
from fcntl import ioctl
from threading import Thread
import traitlets

class Gamepad_teleop(Thread, traitlets.HasTraits):
    maps = {'axis':['x', 'y', 'z', 'rz', 'hat0x', 'hat0y'],
            'button':['btn_y', 'btn_b', 'btn_a', 'btn_x', 'btn_xx', 'btn_xxx', 'tl', 'tr', 'tl2', 'tr2', 'select', 'start', 'mode']}
    x = traitlets.Float(default_value=0) #0x00 left=-1, right=1
    y = traitlets.Float(default_value=0) #0x01 up = -1, down = 1
    z = traitlets.Float(default_value=0)
    rz = traitlets.Float(default_value=0)
    btn_y = traitlets.Integer(default_value=0)
    btn_b = traitlets.Integer(default_value=0)
    btn_a = traitlets.Integer(default_value=0)
    btn_x = traitlets.Integer(default_value=0)
    throttle = traitlets.Float(default_value=0)
    steering = traitlets.Float(default_value=0)
    js = None # joystick io.bufferedreader
    
    def __init__(self):
        super().__init__()
        self.connect()
        self.update_maps()
        self.daemon = True
        
    def loop_start(self):
        print("--start--")
        self.start()
    
    def connect(self, js='/dev/input/js0'):
        print('Open %s...' % js)
        self.js = open(js, 'rb')
        
    def run(self):
        # Main event loop
        while True:
            self.update()
            
    def update(self):
        event_buf = self.js.read(8)
        if event_buf:
            time, value, event_type, number = struct.unpack('IhBB', event_buf)

            if event_type & 0x01:
                button = self.maps['button'][number]
                if button == "btn_y":
                    self.btn_y = value
                elif button == "btn_b":
                    self.btn_b = value
                elif button == "btn_a":
                    self.btn_a = value
                elif button == "btn_x":
                    self.btn_x = value

            if event_type & 0x02:
                axis = self.maps['axis'][number]
                if axis == "x":
                    self.x = value/32767.0
                elif axis == "y":
                    self.y = value/32767.0
                elif axis == "rz":
                    self.rz = value/32767.0
                elif axis == "z":
                    self.z = value/32767.0
    
    def update_maps(self):
        axis_names = {
            0x00 : 'x',
            0x01 : 'y',
            0x02 : 'z',
            0x03 : 'rx',
            0x04 : 'ry',
            0x05 : 'rz',
            0x06 : 'trottle',
            0x07 : 'rudder',
            0x08 : 'wheel',
            0x09 : 'gas',
            0x0a : 'brake',
            0x10 : 'hat0x',
            0x11 : 'hat0y',
            0x12 : 'hat1x',
            0x13 : 'hat1y',
            0x14 : 'hat2x',
            0x15 : 'hat2y',
            0x16 : 'hat3x',
            0x17 : 'hat3y',
            0x18 : 'pressure',
            0x19 : 'distance',
            0x1a : 'tilt_x',
            0x1b : 'tilt_y',
            0x1c : 'tool_width',
            0x20 : 'volume',
            0x28 : 'misc',
        }

        button_names = {
            0x120 : 'trigger',
            0x121 : 'thumb',
            0x122 : 'thumb2',
            0x123 : 'top',
            0x124 : 'top2',
            0x125 : 'pinkie',
            0x126 : 'base',
            0x127 : 'base2',
            0x128 : 'base3',
            0x129 : 'base4',
            0x12a : 'base5',
            0x12b : 'base6',
            0x12f : 'dead',
            0x130 : 'a',
            0x131 : 'b',
            0x132 : 'c',
            0x133 : 'x',
            0x134 : 'y',
            0x135 : 'z',
            0x136 : 'tl',
            0x137 : 'tr',
            0x138 : 'tl2',
            0x139 : 'tr2',
            0x13a : 'select',
            0x13b : 'start',
            0x13c : 'mode',
            0x13d : 'thumbl',
            0x13e : 'thumbr',

            0x220 : 'dpad_up',
            0x221 : 'dpad_down',
            0x222 : 'dpad_left',
            0x223 : 'dpad_right',

            # XBox 360 controller uses these codes.
            0x2c0 : 'dpad_left',
            0x2c1 : 'dpad_right',
            0x2c2 : 'dpad_up',
            0x2c3 : 'dpad_down',
        }
        # Get number of axes and buttons.
        buf = array.array('B', [0])
        ioctl(self.js, 0x80016a11, buf) # JSIOCGAXES
        num_axes = buf[0]

        buf = array.array('B', [0])
        ioctl(self.js, 0x80016a12, buf) # JSIOCGBUTTONS
        num_buttons = buf[0]

        # Get the axis map.
        axis_map = []
        buf = array.array('B', [0] * 0x40)
        ioctl(self.js, 0x80406a32, buf) # JSIOCGAXMAP
        for axis in buf[:num_axes]:
            axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
            axis_map.append(axis_name)
        
        
        # Get the button map.
        button_map = []
        buf = array.array('H', [0] * 200)
        ioctl(self.js, 0x80406a34, buf) # JSIOCGBTNMAP
        for btn in buf[:num_buttons]:
            btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
            button_map.append(btn_name)
        
        self.maps['axis'] = axis_map
        self.maps['button'] = button_map
        print("Keymap Update Completed")
            
    @traitlets.observe('y')
    def monitor_throttle(self, change):
        self.throttle = -change['new']
        print('throttle : ', self.throttle)
    
    @traitlets.observe('z')
    def monitor_steering(self, change):
        self.steering = change['new']
        print('steering : ', self.steering)

if __name__ == '__main__':
    pad = Gamepad_teleop()
    pad.run()
    