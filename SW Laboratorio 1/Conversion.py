std_unit = ["C", "F", "K"]

class Conversion:

    def __init__(self, value, unit, tUnit):
        self.value = value
        self.unit = unit
        self.tUnit = tUnit
        self.target = 0

    def convert(self):
        # Celsius <->  Fahrenheit
        if self.unit == 'C' and self.tUnit == 'F':
            self.target = self.value * (9 / 5) + 32
        if self.unit == 'F' and self.tUnit == 'C':
            self.target = (5 / 9) * (self.value - 32)

        # Celsius <->  Kelvin
        if self.unit == 'C' and self.tUnit == 'K':
            self.target = self.value + 273
        if self.unit == 'K' and self.tUnit == 'C':
            self.target = self.value - 273

        # Kelvin <->  Fahrenheit
        if self.unit == 'F' and self.tUnit == 'K':
            self.target = (5 / 9) * (self.value - 32) + 273
        if self.unit == 'K' and self.tUnit == 'F':
            self.target = (self.value - 273) * (9 / 5) + 32

    def checkValues(self):
        if self.unit not in std_unit or self.tUnit not in std_unit:
            return -1
        else:
            return 0

    def getValue(self):
        return self.value

    def getUnit(self):
        return self.unit

    def get_tUnit(self):
        return self.tUnit

    def getTarget(self):
        return self.target