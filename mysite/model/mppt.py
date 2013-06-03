from math import expm1
from math import exp
from math import log
from math import e
from scipy.special import lambertw
import warnings

class mppt:
    """
    mppt control
    """

    def __init__(self, delta, slope, test_times):
        self.q = 1.6e-19
        self.k = 1.38e-23
        self.vol = 0.5
        self.cur = 1.0
        self.pow = 0.5
        self.vol_old = 0.0
        self.cur_old = 0.0
        self.pow_old = 0.0
        self.output = 0.0
        self.alpha = 1.0
        self.delta = delta
        self.sign = 1
        self.slope = slope
        self.test_times = test_times
        self.mpp = 0.0

        self.rec = []

    """ 
    equation from www.ni.com/white-paper/7230/en
    I = Il- Id = Il - Io * (exp(qv/kT) - 1 )
    U = log((Il - I)/Io + 1)kT/q
    Input Isc and Voc are test result working under T = 47.5 + 273.5K S = 1000W/m^2 from swemodule datasheet
    T - tempreture
    S - Irradiation
    I - Current
    """
    def pvModel(self, Isc, Voc, T, I, s):
        Il = Isc * (1.0 - 0.0032 * (47.5 - T)) * (s/1000)
        Io = Il / expm1(self.q * Voc * (1.0 - 0.00077 * (47.5 - T)) * ((s/10000) + 0.9) / self.k / (T + 273.5))
        if I > Il:
            I_cal = Il - (10.0**-10)
        else:
            I_cal = I
        U = log(round((Il - I_cal)/Io + 1, 7)) * (T+273.5)* self.k / self.q
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            Impp = Il + Io - Io * exp(lambertw((Il+Io)*e/Io) -1)
            w = filter(lambda i: issubclass(i.category, UserWarning), w)
            if len(w):
                print Il , Io
        return [U, Impp]
        
    def update(self, mppt_func, current_value):
        # intitial output data array 
        distance_list = [0] * self.test_times
        positions = [0] * self.test_times
        mpp_list = [0] * self.test_times
        Isc = 8.4
        Voc = 36.8 / 60
        T = 47.5

        for time in range(self.test_times):
            irradiation = current_value[time]
            mppt_func()
            self.cur_old = self.cur
            if self.output>0:
                self.cur = self.output
            else:
                self.cur = 0
            self.vol_old = self.vol
            [self.vol, Impp] = self.pvModel(Isc, Voc, T, self.cur, irradiation)
            self.pow_old = self.pow
            self.pow = self.vol * self.cur
            self.mpp = self.vol * Impp

            positions[time] = self.pow * 60
            distance_list[time] = self.mpp * 60
            self.rec.append(self.cur)
        return [positions, distance_list]
        
    """ Basic P&O algorithm """
    def mppt_pd0(self) :
        if self.pow > self.pow_old :
            self.output = self.cur + self.delta
        else:
            self.output = self.cur - self.delta

    """ 
    Consider with old voltage value
    from: Energy Comparison of Seven MPPT Techniques 
    for PV Systems
    """
    def mppt_pd1(self) :
        if self.pow > self.pow_old:
            if self.cur > self.cur_old:
                self.output = self.cur + self.delta
            else:
                self.output = self.cur - self.delta
        else:
            if self.cur > self.cur_old:
                self.output = self.cur - self.delta
            else:
                self.output = self.cur + self.delta

    """ 
    Optimized P&O algorithm
    from: Energy Comparison of Seven MPPT Techniques 
    for PV Systems  
    """
    def mppt_pd2(self) :

        cur_step = self.cur - self.cur_old
        pow_step = self.pow - self.pow_old

        if cur_step == 0 :
            if pow_step != 0:
                if  pow_step > 0 :
                    self.sign = 1
                else:
                    self.sign = -1
        else:
            self.alpha = abs(pow_step / cur_step) * self.slope
            if pow_step / cur_step < 0:
                self.sign = -1
            else:
                self.sign = 1

        self.output = self.cur + self.sign * self.alpha * self.delta

    """ 
    non-linear P&O increasing value
    from: Experimental analysis of impact of MPPT methods 
    on energy efficiency for photovoltaic power systems
    """
    def update_mppt_pd3(self) :

        s1_p = 0.01
        s2_p = 0.02
        s1_n = s1_p * -1
        s2_n = s2_p * -1
        delta_2 = self.delta - (s2_p - s1_p) * self.slope
        if self.cur == self.cur_old:
            step = 0
        else:
            step = (self.pow - self.pow_old) / (self.cur - self.cur_old)

        if step > 0:
            if step > s1_p:
                if step > s2_p:
                    inc = self.delta
                else:
                    inc = (step - s1_p) * self.slope + delta_2
            else:
                inc = delta_2
        else:
            if step < s1_n:
                if step < s2_n:
                    inc = -1 * self.delta
                else:
                    inc = (step + s1_p) * self.slope - delta_2
            else:
                inc = -1 * delta_2
        
        self.output = self.cur + inc
        
    """ 
    basic incremental conductance algorithm
    """
    def update_mppt_inc0(self) :
        step_i = self.cur - self.cur_old
        step_v = self.vol - self.vol_old
              
        if step_v == 0:
            if step_i == 0:
                sign = 1
            else:
                if step_i > 0:
                    sign = 1
                else:
                    sign = -1
        else:
            temp = self.cur + step_i / step_v * self.vol
            if temp == 0:
                sign = 1
            else:
                if temp > 0:
                    sign = -1
                else:
                    sign = 1
        
        self.output = self.cur + self.delta * sign
            
