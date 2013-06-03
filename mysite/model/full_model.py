from math import log
from math import expm1
from math import exp
from math import sin
from math import e
from math import pi
import matplotlib.pyplot as plt
from decimal import Decimal as D
from scipy.special import lambertw
from numpy import arange
import os
import csv
import truerandom
import random
from scipy import interpolate

from mppt import mppt as mppt_controller
from discrete_pid import PID as PIDfilter

# init status, should not be changed
q = 1.6e-19
k = 1.38e-23
Isc = 8.8
Voc = 37.7 / 60
W = 37.6
# parameters
mpptDelta = .02
mpptSlope = 33.128
pidKp = 14.5
pidKd = 0.0
pidKi = 2.0
pidMa = 0.0
pidMi = 0.0
#pidKp = 0.154417
#pidKd = 2.405137
#pidKi = 0.017758
#pidMa = 36.88964
#pidMi = 25.39791
# compiling options
DATA_INPUT = "SINE"
DATA_INPUT_HALF_CYCLE = 90
FILE_NAME = "irrad_map.csv"
MAX_GAIN_VALUE = 1000.0
MAX_TIMESTEPS = 100
NEW_MAP = 1
# when set to 1, noise would add into input data
ADD_NOISE = 1
NOISE_AMPLITUDE = 10.0
INTERPOLATE = 1
INTERPOLATE_NUM = 200  # stands for update frequency per irradiation change
                      # ex. irradiation change frequency is 1Hz
                      #     inerpolate number is 300
                      #     update frequency is 300Hz  

def createMap(fileName):
    currentValue = 700.0
    r = 10.0
    # generate number list

    if DATA_INPUT == "SINE":
        mapBase = [(sin(float(i)*pi/DATA_INPUT_HALF_CYCLE)+1)*MAX_GAIN_VALUE/2 for i in range(MAX_TIMESTEPS)]
    elif DATA_INPUT == "SQUARE":
        mapBase = [(i/DATA_INPUT_HALF_CYCLE%2)*MAX_GAIN_VALUE for i in range(MAX_TIMESTEPS)]
    elif DATA_INPUT == "TRIANGLE":
        mapBase = [float(i%DATA_INPUT_HALF_CYCLE)/DATA_INPUT_HALF_CYCLE*MAX_GAIN_VALUE for i in range(MAX_TIMESTEPS)]
    else:
        random.seed()
        mapBase = [random.uniform(0,MAX_GAIN_VALUE) for i in range(MAX_TIMESTEPS)]

    # interpolate
    if INTERPOLATE == 1:
        x = range(MAX_TIMESTEPS)
        f = interpolate.interp1d(x,mapBase)
        xnew = arange(0, MAX_TIMESTEPS-1, 1.0/INTERPOLATE_NUM)
        mapBase = f(xnew)
    if ADD_NOISE == 1:
        mapBase = [abs(i+(random.random()-0.5)*NOISE_AMPLITUDE) for i in mapBase]
    storeMap(fileName, mapBase)
    # return
    return mapBase

def loadMap(fileName):
    list_map = list(csv.reader(open(fileName, "rb")))
    mapLoad = []
    for time in range(len(list_map)):
        mapLoad.append(float(list_map[time][0]))
    return mapLoad

def storeMap(fileName, mapStore):
    csvWriter = csv.writer(open(fileName, 'wb'), delimiter=',',
                           quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for i in mapStore:
        csvWriter.writerow([i])

def mppt_update(mppt_func, map):
    mppt = mppt_controller(mpptDelta, mpptSlope, len(map))
    [power, mpp] = mppt.update(getattr(mppt, mppt_func), map)
    return [power,mpp]

def pid_update(pid_func, map):
    pid = PIDfilter(pidKp, pidKd, pidKi, pidMa, pidMi, 1.0/INTERPOLATE_NUM, len(map))
    [positions, distance_list] = pid.update(getattr(pid, pid_func), map)
    return [positions]
    
def plot_result(inputData, dataAmount, labels, savePlot=0, saveName="", showPlot=0):
    plt.figure()
    x = arange(0, MAX_TIMESTEPS-1, 1.0/INTERPOLATE_NUM)
    for i in range(len(inputData) -1):
        plt.plot(x, inputData[i], label = labels[i+4])
    plt.title(labels[0])
    plt.xlabel(labels[1])
    plt.ylabel(labels[2])
    plt.legend(loc='lower left')

    plt.twinx()
    plt.plot(x, inputData[-1], 'r', label = labels[-1])
    plt.ylabel(labels[3])

    plt.legend(loc='lower right')
    if savePlot == 1:
        plt.savefig("results/"+saveName)
    if showPlot == 1:
        plt.show()

    
def main():
    try:
	os.mkdir("results")
    except OSError:
	pass
    if NEW_MAP:
        map_irra = createMap(FILE_NAME)
    else:
        map_irra = load_map(FILE_NAME)
    [pvPower, mpp] = mppt_update("update_mppt_inc0", map_irra)

#    plot_result([pvPower,mpp,pvI], len(pvPower), \
#               ["Result of MPPT, Update Frequency = "+str(INTERPOLATE_NUM/10)+" Hz", "Time(10s)", "Power(W)","Current(A)", "Actual Power","MPP Power", "PV Current"], \
#                saveName="MPPTResult"+DATA_INPUT+".png",showPlot=1)
    [gridPower] = pid_update("update_amelio", pvPower)
#    plot_result([pvPower,gridPower,Wdc], len(gridPower), \
#                    ["Result of Energy Balance", "Time(10s)", "Power(W)","Voltage(V)", "PV Power", "Grid Power", "Dc link Voltage"], \
#                    saveName="PIDResult"+DATA_INPUT+".png",showPlot=1)
    x = arange(0, MAX_TIMESTEPS-1, 1.0/INTERPOLATE_NUM)
    return [x, pvPower, mpp, gridPower]

if __name__ == "__main__":
    main()
