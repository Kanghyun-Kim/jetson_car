import traitlets
from adafruit_servokit import ServoKit
import threading

class Car(traitlets.HasTraits):
    steering = traitlets.Float()
    throttle = traitlets.Float()
    
    @traitlets.validate('steering')
    def _clip_steering(self, proposal):
        if proposal['value'] > 1.0:
            return 1.0
        elif proposal['value'] < -1.0:
            return -1.0
        else:
            return proposal['value']
        
    @traitlets.validate('throttle')
    def _clip_throttle(self, proposal):
        if proposal['value'] > 1.0:
            return 1.0
        elif proposal['value'] < -1.0:
            return -1.0
        else:
            return proposal['value']
        
class RealCar(Car):
    i2c_address = traitlets.Integer(default_value=0x40)
    steering_gain = traitlets.Float(default_value=-0.65)
    steering_offset = traitlets.Float(default_value=0.08)
    steering_channel = traitlets.Integer(default_value=0)
    throttle_gain = traitlets.Float(default_value=0.25)
    throttle_channel = traitlets.Integer(default_value=1)
    max_real_throttle_fwd = traitlets.Float(default_value=0.15)
    max_real_throttle_bwd = traitlets.Float(default_value=-0.25)
    status = 0
    target = 0
    timer = None
    
    def __init__(self, *args, **kwargs):
        super(RealCar, self).__init__(*args, **kwargs)
        self.kit = ServoKit(channels=16, address=self.i2c_address)
        self.kit._pca.frequency = 60
        self.steering_motor = self.kit.continuous_servo[self.steering_channel]
        self.throttle_motor = self.kit.continuous_servo[self.throttle_channel]
        self.steering_motor.throttle = 0
        self.throttle_motor.throttle = 0
    
    @traitlets.observe('steering')
    def _on_steering(self, change):
        self.steering_motor.throttle = change['new'] * self.steering_gain + self.steering_offset
        print('realcar steering:', self.steering_motor.throttle)
    
    @traitlets.observe('throttle')
    def _on_throttle(self, change):
        value = change['new'] * self.throttle_gain
        self.throttle_motor.throttle = self._clip_real_throttle(value)
        print('realcar throttle:', self.throttle_motor.throttle)
    
    def _clip_real_throttle(self, value):
        if value > self.max_real_throttle_fwd:
            return self.max_real_throttle_fwd
        elif value < self.max_real_throttle_bwd:
            return self.max_real_throttle_bwd
        else:
            return value