class Conversion:

    def __init__(self, value, unit, tUnit):

        self.value = value
        self.unit = unit
        self.tUnit = tUnit

        # Celsius <->  Fahrenheit
        if unit == 'C' and tUnit == 'F':
            self.target = value * (9 / 5) + 32
        if unit == 'F' and tUnit == 'C':
            self.target = (5 / 9) * (value - 32)

        # Celsius <->  Kelvin
        if unit == 'C' and tUnit == 'K':
            self.target = value + 273
        if unit == 'K' and tUnit == 'C':
            self.target = value - 273

        # Kelvin <->  Fahrenheit
        if unit == 'F' and tUnit == 'K':
            self.target = (5 / 9) * (value - 32) + 273
        if unit == 'K' and tUnit == 'F':
            self.target = (value - 273) * (9 / 5) + 32

    def getValue(self):
        return self.value

    def getUnit(self):
        return self.unit

    def get_tUnit(self):
        return self.tUnit

    def getTarget(self):
        return self.target
