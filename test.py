import pigpio
from ADS1248_AB import ADS1248

 

pi = pigpio.pi()
frq = 2*10**6
spi = pi.spi_open(0, frq, 1)
## ADS1248 declarations
ADS1248.setup(pi, spi, 11, frq) # (spi, drdy_pin)
adc1 = ADS1248(24, 820)  # (cs_pin, Rref = 820 ohm) Define ADC1 objects
 


ADS1248.verbose = True

 

print(adc1.rreg(0,16)) # Read all registers
 

adc1.rst()

 

print(adc1.rreg(0,16)) # Read all registers
