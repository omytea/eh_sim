## {{{ http://code.activestate.com/recipes/577231/ (r1)
#The recipe gives simple implementation of a Discrete Proportional-Integral-Derivative (PID) controller. PID controller gives output value for error between desired reference input and measurement feedback to minimize error value.
#More information: http://en.wikipedia.org/wiki/PID_controller
#
#cnr437@gmail.com
#
#######	Example	#########
#
#p=PID(3.0,0.4,1.2)
#p.setPoint(5.0)
#while True:
#     pid = p.update(measurement_value)
#
#


class PID:
	"""
	Discrete PID control
	"""

	def __init__(self, P, I, D, ma, mi, dt, run_times):

		self.Kp=P
		self.Ki=I
		self.Kd=D
		self.test_times = run_times

		self.I_value = 0.0
                self.Derivator = 0.0
                self.Integrator = 0.0
		self.error_1 = 0.0
		self.error_2 = 0.0
                self.PID = 0.0
		self.Integrator_max=ma
		self.Integrator_min=mi
		self.set_point=0.0
		self.error=0.0

		self.pvP = 0.0        # pv panel power
		self.dcU = 0.0      # dc link voltage
		self.dcC = 470.0 * 10e-6 * 4
		self.gU = 230.0       # grid voltage
		self.gI = 0.0         # grid current
		self.dt = dt

		self.rec_1 = []
		self.rec_2 = []

	"""
	I_pv * U_pv = P_pv = W_pv / t
	I_grid * U_grid = P_grid = W_grid /t
	C_dc * V_dc^2 / 2 = W_dc = W_dc' + W_pv - W_grid
	"""
	def dcLinkModel(self):
		Wdc = (self.dcU**2) * self.dcC / 2
		Pdc_d = self.pvP * 0.95 - self.gI * self.gU * 0.95
		if Wdc > Pdc_d * self.dt * -1:
			self.dcU = ((Wdc + Pdc_d * self.dt)*2/self.dcC) ** 0.5
		else:
			self.dcU = 0
		self.rec_2.append(self.dcU)

	"""
	Main Function
	Call one PID algorithm and return the result of running history
	"""
	def update(self, pid_func, current_value):
		# intitial output data array 
		distance_list = [0] * self.test_times
		positions = [0] * self.test_times

		for time in range(self.test_times):
			self.pvP = current_value[time]
			self.dcLinkModel()
			self.error = self.dcU - 400.0 # Update current value
			pid_func() # Call one pid function
			if self.PID >0:
				self.gI = self.PID # update target value
			else:
				self.gI = 0.0
			self.rec_1.append(self.gI)
			positions[time] = self.gI * self.gU # store output data, only for simulation
			distance_list[time] = self.gI * self.gU - self.pvP

		return [positions, distance_list]
		

        def update_basic_pos(self):
            """ 
            basic position algorithm
            uk = Kp * ek + Ki * eksum + Kd * (ek - ekk)
            """
            P_value = self.Kp * self.error
            D_value = self.Kd * (self.error - self.Derivator)
            self.Derivator = self.error

            self.Integrator = self.Integrator + self.error
            self.I_value = self.Ki * self.Integrator
            
            self.PID = P_value + self.I_value + D_value
            return 

        def update_basic_inc(self):
            """ 
            basic increase algorithm
            duk = Kp *(ek - ekk) + Ki * ek + Kp * (ek - 2ekk + ekkkk)
            uk = ukk + duk
            """
            P_value = self.Kp * (self.error - self.error_1)
            self.I_value = self.Ki * self.error
            D_value = self.Kd * (self.error - 2 * self.error_1 + self.error_2)
            self.error_2 = self.error_1
            self.error_1 = self.error
            
            self.PID = P_value + self.I_value + D_value + self.PID
            return

	def update_disconnection(self):
		"""
		Calculate PID output value with integral disconnetion
                uk = Kp * ek + Ki * Kl * eksum + Kd * (ek - ekk)
                Kl = 0, when ek > A
                Kl = 1, when ek <= A
		"""
		P_value = self.Kp * self.error
		D_value = self.Kd * ( self.error - self.Derivator)
		self.Derivator = self.error

		self.Integrator = self.Integrator + self.error

		if self.Integrator > self.Integrator_max:
                    self.I_value = 0
                else:
                    self.I_value = self.Integrator * self.Ki

		self.PID = P_value + self.I_value + D_value

		return

	def update_deadzone(self):
		"""
		Calculate PID output value with deadzone
                uk = Kp * ek + Ki * Kl * eksum + Kd * (ek - ekk) , when ek > A
                uk = 0, when ek <= A
		"""

		P_value = self.Kp * self.error
		D_value = self.Kd * ( self.error - self.Derivator)
		self.Derivator = self.error

		self.Integrator = self.Integrator + self.error
                self.I_value = self.Integrator * self.Ki

		if abs(self.error) > self.Integrator_max:
                    self.PID = P_value + self.I_value + D_value
                else:
                    self.PID = 0

		return 

	def deadzone_2(self):
		"""
		! too much parameters !
		Calculate PID output value with improved deadzone
                uk = Kp * ek + Ki * Kl * eksum + Kd * (ek - ekk) , when ek > A
                uk = 0, when ek <= A
		"""

		if self.error > self.Integrator_max:
                    P_value = self.Kp * self.error
                    if P_value > 100 or P_value < -100:
                        self.I_value = 0
                    else:
                        self.I_value = self.error * self.Ki + self.I_value
                    
                    if self.I_value > 100 :
                        self.I_value = 100
                    if self.I_value < 0 :
                        self.I_value = 0

                    D_value = self.Kd * ( self.error - self.Derivator)
                    self.Derivator = self.error

                    self.PID = P_value + self.I_value + D_value
                else:
                    self.PID = self.I_value

		return 

	def update_amelio(self):
		"""
		Calculate PID output value with ameliorated integration 
                uk = Kp * ek + Ki * Kl * eksum + Kd * (ek - ekk)
                Kl = 0, when ek > A
                Kl = 1, when ek <= A
		"""

		P_value = self.Kp * self.error
		D_value = self.Kd * ( self.error - self.Derivator)
		self.Derivator = self.error

		self.Integrator = self.Integrator + self.error

		if (self.PID > self.Integrator_max and self.error > 0) or (self.PID < self.Integrator_min and self.error < 0):
                    self.I_value = 0
                else:
                    self.I_value = self.Integrator * self.Ki

		self.PID = P_value + self.I_value + D_value

		return 

        def incomplete_deri(self):
            """
	    ! not finished yet !
            Calculate PID output value with incomplete derivation 
            """

	    P_value = self.Kp * self.error
	    self.Integrator = self.Integrator + self.error
	    self.I_value = self.Integrator * self.Ki
                # not done yet
	    D_value = self.Kd * ( self.error - self.Derivator)
	    self.Derivator = self.error
	    
	    self.PID = P_value + self.I_value + D_value

	    return 

	def update_discrete(self):
		"""
		Calculate PID output value for given 
		reference input and feedback
		"""

		P_value = self.Kp * self.error
		D_value = self.Kd * ( self.error - self.Derivator)
		self.Derivator = self.error

		self.Integrator = self.Integrator + self.error

		if self.Integrator > self.Integrator_max:
			self.Integrator = self.Integrator_max
		elif self.Integrator < self.Integrator_min:
			self.Integrator = self.Integrator_min

		self.I_value = self.Integrator * self.Ki

		self.PID = P_value + self.I_value + D_value

		return 

	def setPoint(self,set_point):
		"""
		Initilize the setpoint of PID
		"""
		self.set_point = set_point
		self.Integrator=0
		self.Derivator=0

	def setIntegrator(self, Integrator):
		self.Integrator = Integrator

	def setDerivator(self, Derivator):
		self.Derivator = Derivator

	def setKp(self,P):
		self.Kp=P

	def setKi(self,I):
		self.Ki=I

	def setKd(self,D):
		self.Kd=D

	def getPoint(self):
		return self.set_point

	def getError(self):
		return self.error

	def getIntegrator(self):
		return self.Integrator

	def getDerivator(self):
		return self.Derivator
## end of http://code.activestate.com/recipes/577231/ }}}
