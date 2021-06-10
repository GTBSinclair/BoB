 # Description:
 #  This class aims to control the ADS1248 from Texas Instrument (https://www.ti.com/lit/ds/symlink/ads1248.pdf)
 #  The default configuration is made to Read RTD sensor in a ratiometric measurement
 #  It has been adapted to read the voltage output of any 5V analog sensors
 #
 #  Code derived from:
 #    ADS1248 CircuitPython library
 #    https://github.com/AdinAck/ADS1248-CircuitPython
 #    By Adin Ackerman
 #
 #  Adapted for BAMMsat on BEXUS (BoB) by Adrien Bolliand
    # Changed the order of the methods
    # Removed the function for all ADS1248
    # removed the uses of the START and RESET pin (less pin used for the system)
    # Edit the use of DRDY pin so that the class can work with the ADS1248 in DOUT/DRDY mode to allow only one DRDY pin for all the ADS1248 (less pin used for the system)
    # Changes or remove default values (like Vref)
    # extended the comment
    # Added functions related to specif BoB hardware:
    #   - function to read RTDs (a Ratiometric measurement is performed)
    #   - function to read 5V input sensor like the photoresistor, photodiode or the bubble sensor
    #   - function to read the internal temperature sensor of the ADS1248
    # Modified to use the pigpio library instead of the Adafruit's
 # ======================================================================================================================
 #
 # The attributes of the ADS1248 class are:
    # list          (list of the ADC instantiated)
    # Rref          (float) Reference resistor for RTD ratiometric reading in ohm
    # Vref_2        (float) Reference voltage for 5 V sensor reading in volt
    # internal_Vref (float) the internal reference of the ADS1248 nominally at 2.048 V
    # verbose       (boolean) will print status info if True
    # CVM_A; CVM_B; CVM_Ro (float) the parameters of the Callendar-Van Dusen equation (CVM equation)
    # cs            (digital pin) output of the raspberry pi for Chip Select
    # G             (int) the value of the PGA gain, to change along the register 3
    # spi           (spi object) define the spi connection (see example code)
    # freq          (int) data rate, MAX: 2 049 180 Hz  ~ 2 MHz
    # drdy          (digital pin) input of the raspberry pi. Connected to all the DOUT/DRDY of the ADS1248 pulled low by the ADS1248 when data is ready to be transmitted
 #
 # The methods of the ADS1248 class are:
    # setup (spi, drdy_pin, freq)                   Setup for all the ADS1248 of the BOB electronic. input the SPI object, the DRDY pin that will be used to monitor if the data is ready for all the ADS1248 and the frequency od the data rate
    # __init__(cs_pin, Rref,list_res_mis,Vref_2)    Object builder. Input the Chip Select (CS) pin, the value in ohm of the Reference resistor for RTD measurement, the list of the values in ohm of the resistance mismatch of the RTD wires form RTD calibration, the Reference voltage for other sensors  
    # wakeup()                                      Out of sleep mode
    # sleep()                                       Enter sleep mode
    # rst()                                         Send the reset command
    # rreg(register_int,count)                      Return the value of the ADS register from "register_int" and the "count" after
    # wreg(register_int,data_hex_list)              Write "data_hex_list" from the register "register_int" (register int start at 0)
    # selfOffset()                                  Start the self offset calibration procedure. Automatically write in the OFC1 and OFC2 (5 and 6) register the result
    # fetch(AINP+,AINN-)                            Retrieve the 24 bits converted value between AINP+ and AINN-
    # receive ()                                    Used by the fetch method to catch the 24 bits
    # Converstion_R_to_C(Resistance_of_an_RTD)      Using the CVM equation return a temperature value in Celsius form an RTD resistance value
    # Read_RTD(RTD_id_number)                      Read and return the resistance and the temperature of the RTD number "RTD_id_number". The wiring is specified below and in the method
    # Read_5V_sensor(sensor_num_id_number)          Read and return the voltage of the "sensor_num_id_number". The wiring is specified below and in the method
 #
 ## wiring RTDs
        # Max four RTD per ADC
        #       RTD_id_number = 1 ==> AIN 0 (N) - AIN 1 (P)   (P) 1 wire side, positive voltage (N) 2 wire side, Negative voltage for the ADS1248 MUX
        #       RTD_id_number = 2 ==> AIN 2 (N) - AIN 3 (P)
        #       RTD_id_number = 3 ==> AIN 4 (N) - AIN 5 (P)
        #       RTD_id_number = 4 ==> AIN 6 (N) - AIN 7 (P)
        ##
 #
 ## wiring 5 Volt sensors
        # Max seven 5 Volt sensors per ADC
        # Vref = 1/2 AVDD ~~ 2.5 V
        #     sensor_num_id_number = 1 ==> AIN 7 (Vref) - AIN 0 (sensor)   (P) positive voltage (N) Negative voltage for the ADS1248 MUX
        #     sensor_num_id_number = 2 ==> AIN 7 (Vref) - AIN 1 (sensor)
        #     sensor_num_id_number = 3 ==> AIN 7 (Vref) - AIN 2 (sensor)
        #     sensor_num_id_number = 4 ==> AIN 7 (Vref) - AIN 3 (sensor)
        #     sensor_num_id_number = 5 ==> AIN 7 (Vref) - AIN 4 (sensor)
        #     sensor_num_id_number = 6 ==> AIN 7 (Vref) - AIN 5 (sensor)
        #     sensor_num_id_number = 7 ==> AIN 7 (Vref) - AIN 6 (sensor)
        ##

import pigpio
import time

class ADS1248:

    list = [] # list of the ADC instanciated
    verbose = False # False by default ==> will NOT print status, use this for debugging
    internal_Vref = 2.068     # The internal reference voltage value of every ADS1248. Used to read the internal temperature of the chip
    # for the Callendar-Van Dusen equation (CVM equation)
    CVM_A  = 3.9083 * 10**-3  # °C^-1
    CVM_B  = -5.775 * 10**-7  # °C^-2
    CVM_Ro = 100              # ohm for RTDs Pt100 only

    def __init__(self, cs_pin, Rref = 821, list_res_mis = [0,0,0,0], Vref_2 = 2.5):
        ADS1248.list.append(self) # update the list of instanciated ADS1248 object

        # Define the reference value of the ADS1248
        self.rref = Rref # define the value of the reference resistor to read RTDs sensors
        self.Rmis = list_res_mis # Define the wire resistance mismatch. value unique to each RTD and was obtained by calibration
        self.vref_2 = Vref_2 # value of the second reference voltage, nominally use to read 5 V analog sensor. The reference voltage should be around 2.5 V
        
        # CS pin attribute
        self.cs = cs_pin
        ADS1248.pigpio.set_mode(self.cs, pigpio.OUTPUT)
        ADS1248.pigpio.write(self.cs, 1) # True by default, to close communication with the ADS1248 the CS pin is set to high or low in the methods

        # send a reset command at initialisation
        self.rst()

        # default ADS1248 set-up for BoB. The default set up is meant to read RTDs.
        self.wreg(2, [0x20]) # In the MUX1  register (2) ==> Internal reference enabled, REFP0 and REFN0 reference inputs selected (0x20)
        print("Sending to IDAC0 register...")
        self.wreg(10,[0x0E]) # In the IDAC0 register (10)==> DOUT/DRDY mode 1 ENABLED, excitation current set to 1 mA
        self.wreg(3, [0x32]) # In the SYS0  register (3) ==> the PGA gain to 8 and Data rate to 20 SPS (0x32)
        self.G  = 8          # PGA gain

    def setup(pi, spi_handle, drdy_pin, freq=2000000, verbose = False):
        ###To run before any object build with __init__
        ADS1248.pigpio =  pi # the input pigpio shall be an instance of the pigpio declared in a scrip using this class
        ADS1248.freq = freq # store the data rate as an attribute
        ADS1248.spi_handle = spi_handle # SPI set up
        
        # DRDY pin attribute for all the ADS1248
        ADS1248.drdy = drdy_pin
        ADS1248.pigpio.set_mode(ADS1248.drdy, pigpio.INPUT)
        
   
    ##
    ## generic methods/commands for ADS in the BoB flight configuration
    ##

    def wakeup(self): # 0x00 or 0x01
        ADS1248.pigpio.write(self.cs, 0) # allow communication with the ADS1248
        time.sleep(1*10**(-8)) # t_CSSC wait time after CS is set to low before communication
        ADS1248.pigpio.spi_write(ADS1248.spi_handle, b'\x00') #send the wakeup command 
        ADS1248.pigpio.write(self.cs, 1) # close communication with the ADS1248
        if ADS1248.verbose:
            print("[ADS1248] [{}] [WAKEUP] Wakeup command sent.".format(ADS1248.list.index(self)))

    def sleep(self): # 0x02 or 0x03
        #### MAY NOT BE USED FOR FLIGHT ####
        ADS1248.pigpio.write(self.cs, 0) # allow communication with the ADS1248
        time.sleep(1*10**(-8)) # t_CSSC wait time after CS is set to low before communication
        ADS1248.pigpio.spi_write(ADS1248.spi_handle, b'\x02') # send the sleep command
        ADS1248.pigpio.write(self.cs, 1) # close communication with the ADS1248
        if ADS1248.verbose:
            print("[ADS1248] [{}] [SLEEP] Sleep command sent.".format(ADS1248.list.index(self)))

    def rst(self): # 0x06 or 0x07
        #### MAY NOT BE USED FOR FLIGHT ####
        ADS1248.pigpio.write(self.cs, 0) # allow communication with the ADS1248
        time.sleep(1*10**(-8)) # t_CSSC wait time after CS is set to low before communication
        ADS1248.pigpio.spi_write(ADS1248.spi_handle, b'\x06') # send the reset command
        ADS1248.pigpio.write(self.cs, 1) # close communication with the ADS1248
        time.sleep(.0006) # Wait before sending any more commands after reset
        if ADS1248.verbose:
            print("[ADS1248] [{}] [RESET] Reset command sent.".format(ADS1248.list.index(self)))

    def rreg(self,register_int,count): # 0x2_
        ADS1248.pigpio.write(self.cs, 0) # allow communication with the ADS1248
        time.sleep(1*10**(-8)) # t_CSSC wait time after CS is set to low before communication
        send = [32+register_int, count-1] # create the byte sequence to send that will request the content of the method input register and the number of register to read.
        ADS1248.pigpio.spi_write(ADS1248.spi_handle, bytearray(send)) # send the byte sequence
        nb_bytes, recv = ADS1248.pigpio.spi_xfer(ADS1248.spi_handle, [0xFF] * count) # catch the response and send 0xFF, it is the NOP command at teh same time, which tells the ADS1248 to send bytes
        ADS1248.pigpio.write(self.cs, 1) # close communication with the ADS1248
        if ADS1248.verbose:
            print("[ADS1248] [{0}] [RREG] Received {1}.".format(ADS1248.list.index(self),recv))

        return [i for i in recv]

    def wreg(self,register_int,data_hex_list): # the register has to be the number of the register between 0 and 15. data is a list of command in hexadecimal
        ADS1248.pigpio.write(self.cs, 0) # allow communication with the ADS1248
        time.sleep(1*10**(-8)) # t_CSSC wait time after CS is set to low before communication
        send = [64+register_int, len(data_hex_list)-1] + data_hex_list # generate the sequence to send by concatenation, "data" as to be a list
        # print("Debug wreg send: ", send) # uncomment for debugging
        ADS1248.pigpio.spi_write(ADS1248.spi_handle, bytearray(send)) # send the sequence that will modify the register
        ADS1248.pigpio.write(self.cs, 1) # close communication with the ADS1248
        if ADS1248.verbose:
            print("[ADS1248] [{0}] [WREG] Wrote {1} to register {2}.".format(ADS1248.list.index(self),data_hex_list,register_int))

    def selfOffset(self):
        #### MAY NOT BE USED FOR FLIGHT ####
        if ADS1248.verbose:
            print("[ADS1248] [{}] [SELFOFFSET] Calibrating voltage offset internally...".format(ADS1248.list.index(self)))
        ADS1248.pigpio.write(self.cs, 0) # allow communication with the ADS1248
        time.sleep(1*10**(-8)) # t_CSSC wait time after CS is set to low before communication
        ADS1248.pigpio.spi_write(ADS1248.spi_handle, b'\x62') # Send the self Offset command

        counter = 0
        while ADS1248.pigpio.read(self.drdy):
            if counter < 100:
                counter += 1
            else:
                print("[ADS1248] [{}] [SELFOFFSET] ADC did not complete calibration before timeout.".format(ADS1248.list.index(self)))
                print("\tCurrent DRDY values:", [adc.drdy.value for adc in ADS1248.list])
                return
            time.sleep(.1)
        ADS1248.pigpio.write(self.cs, 1) # close communication with the ADS1248
        if ADS1248.verbose:
            print("[ADS1248] [{}] [SELFOFFSET] Calibration complete.".format(ADS1248.list.index(self)))

    def fetch(self, ref, inputs):
        result = []
        for i in range(len(inputs)):
            self.wreg(0,[inputs[i]*8+ref]) # modify the register in order to read the right analog input
            result.append(self.receive()) # catch the result with the receive() method
        return result

    def receive(self):
        ADS1248.pigpio.write(self.cs, 0) # allow communication with the ADS1248
        if ADS1248.pigpio.read(self.drdy): # if drdy pin is high, it mean that the data will be ready. when DRDY pin goes low, it means that the signal has been converted into bytes and is ready to be read
            if self.verbose:
                print("[ADS1248] [{}] [RECEIVE] Waiting for ADC...".format(ADS1248.list.index(self)))

            counter = 0
            while ADS1248.pigpio.read(self.drdy): # Wait until ADC conversion is completed. when DRDY pin goes low, it means that the signal has been converted into bytes and is ready to be read
                if counter < 100:
                    counter += 1
                else:
                    print("[ADS1248] [{}] [RECEIVE] ADC did not complete conversion before timeout.".format(ADS1248.list.index(self)))
                    print("\tCurrent DRDY value:", ADS1248.pigpio.read(self.drdy))
                    return
                time.sleep(.05)
            # Goes out of the loop out of the loop when data is ready
            nb_bytes, recv = ADS1248.pigpio.spi_xfer(ADS1248.spi_handle, [0xFF] * 3) # catch the response and send 0xFF, it is the NOP command at teh same time, which tells the ADS1248 to send bytes
            ADS1248.pigpio.spi_write(ADS1248.spi_handle, b'\xFF') # send the NOP command at the end of the conversion
            ADS1248.pigpio.write(self.cs, 1) # close communication with the ADS1248
            if self.verbose:
                print("[ADS1248] [{0}] [RECEIVE] {1} received.".format(ADS1248.list.index(self),recv))
            result = [i for i in recv] # Convert to array of integers
            result_int = result[0]*2**16+result[1]*2**8+result[2] # Convert to integer
            result_bin = str(bin(result_int))[2:] # Convert to binary
            if len(result_bin) == 24: # Test if negative
                result_int = int(result_bin[1:], 2)-(2**23) # Convert to correct integer
            return result_int
        else:
            print("[ADS1248] [{}] [RECEIVE] Unable to retreive data because DRDY was low during a conversion period.".format(ADS1248.list.index(self)))
    
 #####
 ##### function specific for BoB set up
 #####

    def Converstion_R_to_C(self, Resistance_RTD):
        # using quadratic CVD equation working above 0 °C. Quadratic equation is probably excessive for the experiment temperature range. linear would most likely work
        a = self.CVM_Ro*self.CVM_B
        b = self.CVM_Ro*self.CVM_A
        c = self.CVM_Ro-Resistance_RTD
        Delta = b**2 - 4*a*c
        degree_value = (-b+(Delta**0.5))/(2*a)
        return degree_value

    def Read_RTD(self, RTD):

        ## wiring
        #   there is 4 RTD per ADC
        #       RTD = 1 ==> AIN 0 (N) - AIN 1 (P)   (P) 1 wire side, positive voltage (N) 2 wire side, Negative voltage for the ADS1248 MUX
        #       RTD = 2 ==> AIN 2 (N) - AIN 3 (P)
        #       RTD = 3 ==> AIN 4 (N) - AIN 5 (P)
        #       RTD = 4 ==> AIN 6 (N) - AIN 7 (P)
        ##

        if RTD not in [1,2,3,4] : # Retrun none if the function inputs are not expected
            return [None, None, None, None]
        if self.G !=8: # Because the experiment temperature range, the gain should be 8 to read the RTDs
            self.wreg(3, [0x32]) # In the SYS0  register (3) ==> PGA gains to 8 and Data rate to 20 SPS (0x32)
            self.G = 8 # Set the gain to 8
        list_to_average = [] # empty list of value to average
        Ain_p = (RTD*2)-1 # positive analog input (AIN) number name
        Ain_n = (RTD*2)-2 # Negative analog input (AIN) number name
        current_source_1 = [Ain_n * 16 + Ain_p] # the data that shall be written into the register to set the current source in the 1st configuration for the 1st reading to average
        current_source_2 = [Ain_p * 16 + Ain_n] # the data that shall be written into the register to set the current source in the 2nd configuration for the 2nd reading to average
        self.wreg(11, current_source_1) # In the IDAC1 register (11) ==> set up the excitation current into the right analog input (AIN).
        raw = self.fetch(Ain_n,[Ain_p]) # retrieve the conversion data of the 1st reading to average
        try: # if retrieve is successful convert the reading into the value of the RDT resistance in ohm
            reading_source_1 = self.Rmis[RTD-1] + 2*((raw[0]*self.rref)/(self.G*((2**23)-1))) # convert the 1st reading to average in ohm
            reading = True
        except:
            reading = False
        self.wreg(11,current_source_2) # swaps the current sources. In IDAC1 register (11) ==> set up the excitation current into AIN 0 and 1. The current that goes through the RTD is from the source 1
        raw = self.fetch(Ain_n,[Ain_p]) # retrieve the conversion data of the 2nd reading to average
        try: # if retrieve is successfully convert the readind into the value of the RDT resistance in ohm
            reading_source_2 = self.Rmis[RTD-1] + 2*((raw[0]*self.rref)/(self.G*((2**23)-1))) # convert the 2nd reading to average in ohm
        except:
            reading = False
        self.wreg(11,[0xFF]) # In the IDAC1 register (11) ==> Shut OFF the excitation currents
        if reading: # if both reading were successfull
            RTD_res = (reading_source_1 + reading_source_2)/2 # average the 2 reading in ohm to compensate for current source mismatch
            RTD_degree = self.Converstion_R_to_C(RTD_res) # convert averaged ohm reading into temperature in °C
            result=[RTD_res, RTD_degree, reading_source_1, reading_source_2] # format result
        else:
             return [None, None, None, None]
        return result


    def Read_5V_sensor(self, sensor_num):

        ## wiring
        # Vref = 1/2 AVDD ~ 2.5 V
        #     sensor_num = 1 ==> AIN 7 (Vref) - AIN 0 (sensor)   (P) positive voltage (N) Negative voltage for the ADS1248 MUX
        #     sensor_num = 2 ==> AIN 7 (Vref) - AIN 1 (sensor)
        #     sensor_num = 3 ==> AIN 7 (Vref) - AIN 2 (sensor)
        #     sensor_num = 4 ==> AIN 7 (Vref) - AIN 3 (sensor)
        #     sensor_num = 5 ==> AIN 7 (Vref) - AIN 4 (sensor)
        #     sensor_num = 6 ==> AIN 7 (Vref) - AIN 5 (sensor)
        #     sensor_num = 7 ==> AIN 7 (Vref) - AIN 6 (sensor) 
        ##

        if sensor_num not in [1,2,3,4,5,6,7]:
                return None
        if self.G != 1: # Because sensor output could reach 5V, the gain shall be 1
            self.wreg(3, [0x02]) # In the SYS0  register (3) ==> the PGA gains to 1 and Data rate to 20 SPS (0x32)
            self.G = 1 # Gain shall be at 1 to read a 5v output sensor
        Ain_p = sensor_num-1 # positive analog input (AIN) number name
        Ain_n = 7 # negative analog input (AIN) number name. it shall always be pin AIN 7 forced at REFP (positive reference input) nominally at 2.5 V
        # change the default parameter for a 5 V sensor reading
        self.wreg(2, [0x28]) # In the MUX1  register (2) ==> internal reference enabled, REFP1 and REFN1 reference inputs selected (0x28)
        # reading and conversion to voltage
        raw = self.fetch(Ain_n,[Ain_p]) # retrieve the conversion data of sensor between the pin AIN7
        try:
            result =  self.vref_2*(1+raw[0]/((2**23)- 1)) # Converter conversion in volt
        except:
            print("Error reading 5V sensor")
            result = None
        # Set back default parameter
        self.wreg(2, [0x20]) # In the MUX1  register (2) ==> internal reference enabled, REFP0 and REFN0 reference inputs selected (0x20)
        return result

    def Read_internal_temperature(self): # in this configuration Can read temperature up to 49 °C. If higher, the gain shall be changed
        # Change default setting to enable the reading 
        self.wreg(2, [0x33]) # In the MUX1 register (2) ==> the ref voltage set on the internal reference and AIN input on the internal temperature sensor
        # the set up induce by the line above forces the gain to 1 
        # get the conversion
        raw = self.receive()
        # Back to default settings
        self.wreg(2, [0x20]) # In the MUX1  register (2) ==> internal reference enabled, REFP0 and REFN0 reference inputs selected (0x20)
        # Computing the temperature
        try: # if reading successful
            Vin = self.internal_Vref * raw / ((2**23)-1) # convert conversion in volt
            internal_temperature = 2469.135802 * Vin -  266.3580247 # convert volt value into temperature in °C. equation deduced from the datasheet p10
        except:
            internal_temperature = None
        return internal_temperature
