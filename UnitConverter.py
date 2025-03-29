# Converter.py

# Converts units (e.g. pixels, axis-rotation units, radians) to units and vice versa

import numpy as np
from terminal_utils import print_info, print_success, print_warning, print_error, print_status, print_header

class UnitConverter:
    """ Converts units to units and vice versa"""
    def __init__(self,
                 ARU_min = 989.0,       # minimum possible ARU value
                 ARU_max = 2012.0,      # maximum possible ARU value
                 px_min = 0.0,          # minimum possible px value
                 px_max = 640.0):       # maximum possible px value
        self.ARU_min = float(ARU_min)
        self.ARU_max = float(ARU_max)
        self.px_min = float(px_min)
        self.px_max = float(px_max)

    def ARU_to_px(self, ARU_value: float) -> float:
        """ Convert axis-rotation units (ARU) to pixels (px)
        
        ARU have a minimum of 989 and a maximum of 2012, which
        corresponds to a range of 1023 units. Pixels have a range
        of 640 units. The conversion is linear, so we can use
        the formula:
    
        px = (px_max - px_min) / (ARU_max - ARU_min) * (ARU_value - ARU_min) + px_min
        """
        px_value = ((self.px_max - self.px_min) / (self.ARU_max - self.ARU_min)
                    * (ARU_value - self.ARU_min)
                    + self.px_min)
        return max(min(px_value, self.px_max), self.px_min)  # ensure px value is within bounds
    
    def px_to_ARU(self, px_value: float) -> float:
        """ Convert pixels (px) to axis-rotation units (ARU)
        
        ARU have a minimum of 989 and a maximum of 2012, which
        corresponds to a range of 1023 units. Pixels have a range
        of 640 units. The conversion is linear, so we can use
        the formula:
    
        ARU = (ARU_max - ARU_min) / (px_max - px_min) * (px_value - px_min) + ARU_min
        """
        ARU_value = ((self.ARU_max - self.ARU_min) / (self.px_max - self.px_min) 
                     * (px_value - self.px_min)
                     + self.ARU_min)
        return max(min(ARU_value, self.ARU_max), self.ARU_min)  # ensure ARU value is within bounds
    
    def ARU_delta_to_radian_delta(self, ARU_delta: float) -> float:
        """ Converts delta ARU to delta radian """
        return ARU_delta * (2 * np.pi) / (self.ARU_max - self.ARU_min)
    
    def radian_delta_to_ARU_delta(self, radian_delta: float) -> float:
        """ Converts delta radian to delta ARU """
        return radian_delta * (self.ARU_max - self.ARU_min) / (2 * np.pi)

    def px_delta_to_radian_delta(self, px_delta: float) -> float:
        """ Converts px/s (a delta) to radian/s (a delta too) """
        return px_delta * (2 * np.pi) / (self.px_max - self.px_min)
    
    def radian_delta_to_px_delta(self, radian_delta: float) -> float:
        """ Converts radian/s (a delta) to px/s (a delta too) """
        return radian_delta * (self.px_max - self.px_min) / (2 * np.pi)

    def px_delta_to_ARU_delta(self, px_delta: float) -> float:
        """ Converts delta px to delta ARU by scaling with minmax-ratio """
        return px_delta * (self.ARU_max - self.ARU_min) / (self.px_max - self.px_min)
    
    def ARU_delta_to_px_delta(self, ARU_delta: float) -> float:
        """ Converts delta ARU to delta px by scaling with minmax-ratio """
        return ARU_delta * (self.px_max - self.px_min) / (self.ARU_max - self.ARU_min)
    
    def get_ARU_min(self) -> float:
        """ Returns the minimum ARU value """
        return self.ARU_min
    
    def get_ARU_max(self) -> float:
        """ Returns the maximum ARU value """
        return self.ARU_max
    
    def get_px_min(self) -> float:
        """ Returns the minimum px value """
        return self.px_min
    
    def get_px_max(self) -> float:
        """ Returns the maximum px value """
        return self.px_max
    

def main():
    converter_object = UnitConverter()
    
    print_header("Unit Converter Test Results")
    print_info(f"ARU to pixels: {converter_object.ARU_to_px(1500.0)}")
    print_info(f"Pixels to ARU: {converter_object.px_to_ARU(320.0)}")
    print_info(f"ARU delta to pixels delta: {converter_object.ARU_delta_to_px_delta(100.0)}")
    print_info(f"Pixels delta to ARU delta: {converter_object.px_delta_to_ARU_delta(100.0)}")


if __name__ == "__main__":
    main()