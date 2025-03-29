# CompanionController.py

# Controls x-axis rotation with different methods, trivial to PID-controller;
# starts with a base class upon which different improvements are built; the
# x-axis is controlled in axis-rotation units per second [ARU/s]

from UnitConverter import UnitConverter

import time
from abc import ABC, abstractmethod
from simple_pid import PID


class BaseController(ABC):
    """ Base class for controllers, each will implement
    `compute_control' for yaw control signal """
    def __init__(self, converter: UnitConverter):
        self.converter = converter

    @abstractmethod
    def compute_control(self, error: float, dt: float) -> float:
        """ Computes yaw rate based on horizontal error

        :param error: difference between the center x (midpoint of frame)
                      and target x in pixels; right-oriented
        :param dt: time since last call in seconds
        :return: control signal for yaw in radians/s
        """
        pass


class ConstantRateController(BaseController):
    """ Constant rate controller: yaw is independent or error """
    def __init__(self,
                 converter: UnitConverter,
                 yaw_speed_px_per_s: float = 5.0,
                 dead_zone_px: float = 5.0):
        """ Constructor """
        super().__init__(converter)
        self.yaw_speed_px_per_s = yaw_speed_px_per_s
        self.dead_zone_px = dead_zone_px

    def compute_control(self, error_px: float) -> float:
        """ Computes yaw rate based on horizontal error

        :param error: difference between the center x (midpoint of frame)
                      and target x in pixels; right-oriented
        :return: control signal for yaw in radians/s
        """
        if abs(error_px) < self.dead_zone_px:
            px_rate = 0.0
        elif error_px > 0.0:            # turn right (positive yaw)
            px_rate = self.yaw_speed_px_per_s
        else:                           # turn left (negative yaw)
            px_rate = -self.yaw_speed_px_per_s

                                        # convert to rad/s   
        return self.converter.px_delta_to_radian_delta(px_rate)
    

class ProportionalController(BaseController):
    """ Proportional controller: yaw is proportional to error """
    def __init__(self,
                 converter: UnitConverter,
                                        # proportional lever factor in px
                 lever_factor_px: float = 0.1,
                                        # maximum yaw rate in px/s
                 max_px_rate: float = 100.0,
                 dead_zone_px: float = 5.0):
        """ Constructor """
        super().__init__(converter)
        self.lever_factor_px = lever_factor_px
        self.max_px_rate = max_px_rate
        self.dead_zone_px = dead_zone_px

    def compute_control(self, error_px: float) -> float:
        """ Computes yaw rate proportional to horizontal error """
        control_px_rate = error_px * self.lever_factor_px

        if control_px_rate > self.max_px_rate:
            control_px_rate = self.max_px_rate
        elif control_px_rate < -self.max_px_rate:
            control_px_rate = -self.max_px_rate

        if abs(error_px) < self.dead_zone_px:
            control_px_rate = 0.0
        elif error_px > 0.0:            # turn right (positive yaw)
            control_px_rate = control_px_rate
        else:                           # turn left (negative yaw)
            control_px_rate = -control_px_rate

                                        # convert to rad/s
        return self.converter.px_delta_to_radian_delta(control_px_rate)


# class PID_wrapper():
#     """ Wraps the simple-PID PID class for possible further alterations """
#     def __init__():
#         self.pid = PID(0.1, 0.01, 0.05, setpoint = 0)



# class PIDController(BaseController):
#     """ PID controller: proportional, integral and derivative control """
#     def __init__(self,
#                  converter: ARUConverter,
#                  proportional_factor_px: float = 0.2,
#                  integral_factor_px: float = 0.0,
#                  derivative_factor_px: float = 0.1,
#                  max_px_rate: float = 100.0):
#         """ Constructor """
#         super().__init__(converter)
#         self.proportional_factor_px = proportional_factor_px
#         self.integral_factor_px = integral_factor_px
#         self.derivative_factor_px = derivative_factor_px
#         self.max_px_rate = max_px_rate

#         self.prev_error_px = 0.0        # previous error rate in px
#         self.integral_px = 0.0          # 