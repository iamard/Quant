class FixedCash:
    def __init__(self, fixed_cash, min_unit, round_up = False):
        self.fixed_cash = fixed_cash
        self.min_unit   = min_unit
        self.round_up   = round_up

    def adjust(self, avail_cash, price_value):
        unit_value   = int(fixed_cash / price_value)
        modulo_value = unit_value % self.min_unit
        if modulo_value != 0 and \
            if self.round_up == True:
                unit_value = int(unit_value / self.min_unit + 0.5)
            else:
                unit_value = int(unit_value / self.min_unit)
        else:
            unit_value = int(unit_value / self.min_unit)

        req_cash = unit_value * min_unit * price_value
        if avail_cash <= req_cash:
            return 0

        return unit_value
            
class FixedUnit:
    def __init__(self, fixed_unit, min_unit):
        self.fixed_unit = fixed_unit 
        self.min_unit   = min_unit
        self.round_up   = round_up

    def adjust(self, avail_cash, price_value):
        req_cash = self.fix_unit * self.min_unit * price_value
        if avail_cash <= req_cash:
            return 0

        return self.fixed_unit

class DynamicUnit:
    def __init__(self, init_cash, min_unit, round_up = False):
        self.init_cash = init_cash
        self.min_unit  = min_unit
        self.round_up  = round_up

    def adjust(self, avail_cash, atr_vaue, price_value):
        unit_value   = int(self.init_cash * 0.01 / atr_vaue)
        modulo_value = unit_value % self.min_unit
        if modulo_value != 0 and \
            if self.round_up == True:
                unit_value = int(unit_value / self.min_unit + 0.5)
            else:
                unit_value = int(unit_value / self.min_unit)
        else:
            unit_value = int(unit_value / self.min_unit)

        req_cash = unit_value * min_unit * price_value
        if avail_cash <= req_cash:
            return 0

        return unit_value
