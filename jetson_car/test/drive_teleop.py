from gamepad_teleop import gamepad_teleop
import car as c
import traitlets
import sys

print('Loading Car Class...')
car = c.RealCar()
print('Loading Pad Class...')
pad = gamepad_teleop.Gamepad_teleop()


link_steering = traitlets.dlink((pad,"steering"), (car,"steering"))
link_throttle = traitlets.dlink((pad,"throttle"), (car,"throttle"))
print('Car-Pad Link Completed')

#init
pad.steering = 0
pad.throttle = 0

pad.loop_start()
stored_exception=None
while True:
    try:
        pass
    except KeyboardInterrupt:
        print("[CTRL+C detected]")
        break
    except:
        stored_exception=sys.exc_info()
        break
    
#terminate
pad.steering = 0
pad.throttle = 0

if stored_exception:
    raise stored_exception

sys.exit()