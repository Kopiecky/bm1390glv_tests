from bm1390glv import BM1390
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

bm1390 = BM1390()
plt.style.use('fivethirtyeight')
pressure_v = []
temperature_v = []
iv =[]

def animate(i):
    raw_pressure = bm1390.read_pressure()
    raw_temperature = bm1390.read_temperature()

    pressure_v.append(raw_pressure)
    temperature_v.append(raw_temperature)
    iv.append(i/5)
    if(len(pressure_v) > 100):
        pressure_v.pop(0)
        iv.pop(0)
        temperature_v.pop(0)


    plt1.cla()
    plt2.cla()

    plt1.plot(iv, pressure_v, label = "Pressure, hPa", color = "red")
    plt2.plot(iv, temperature_v, label = "Temperature, C", color = "green")
    plt1.legend(loc = 'upper left')
    plt2.legend(loc = 'upper left')
    plt.tight_layout()

fig, (plt1, plt2) = plt.subplots(nrows = 2, ncols = 1)
animation = FuncAnimation(plt.gcf(), animate, interval = 100)
plt.tight_layout()
plt.show()