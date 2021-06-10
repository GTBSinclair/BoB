import pigpio
from datetime import datetime
from time import perf_counter
from time import sleep
import csv
from ADS1248_AB import ADS1248
import sys
import board

## Initialize SPI
pi = pigpio.pi()
frq = 2*10**6
spi = pi.spi_open(0, frq, 1)
## ADS1248 declarations
ADS1248.setup(pi, spi, board.17, frq) # (spi, drdy_pin)
adc1 = ADS1248(board.8, 820)  # (cs_pin, Rref = 820 ohm) Define ADC1 objects
Vsupply = 5.2
Pmax = 15
Pmin = 0

while True:
    read_A0 = adc1.Read_5V_sensor(1) #pin 2 is equivalent to AIN1
    read_A1 = adc1.Read_5V_sensor(2) 
    read_A2 = adc1.Read_5V_sensor(3)
    read_A3 = adc1.Read_5V_sensor(4)
    read_A4 = adc1.Read_5V_sensor(5)
    read_A5 = adc1.Read_5V_sensor(6)
    read_A6 = adc1.Read_5V_sensor(7)
    #Pmeas = ((read_A0 - 0.1*Vsupply)*(Pmax-Pmin)/(0.8*Vsupply))+Pmin
    print ("A0  " + str(read_A0))
    print ("A1  " + str(read_A1))
    print ("A2  " + str(read_A2))
    print ("A3  " + str(read_A3))
    print ("A4  " + str(read_A4))
    print ("A5  " + str(read_A5))
    print ("A6  " + str(read_A6))
#    print (read_A7)
    #print (Pmeas)
    print ("---------")
    print (" ")
    sleep (2)
    #temperature_list = Read_RTD(2)
    #temperature = temperature_list[1]
