#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#                               Equations which are used by the algorithm:
#
#
#                                            (Vin * R2) 
#       Potential Divider Equation:  Vout = ------------     ;     Ohm's Law:  V = IR
#                                            (R1 + R2)
#
#
#
#
#
#             Electrical schematic:
#
#           Vin-----R1------R2-----GND
#                        | 
#                        |
#                        |
#                       Vout
#
#
#
# How the algorithm works:
#
# *** This script uses the potential divider equation to calculate Vout for a given Vin (V), R1 (Ω) and R2 (Ω) 
#     and converts resistances to kΩ
#
# *** The current of the circuit is also calculated for each combination of resistors in mA
#
# *** Input parameters are required by the user mid-way through the script and 
#     these are Vout, Vin, margin below (for Vout), margin above (for Vout), 1 or 0 (prompt to add more resistors or not),
#     number of additional resistors, values of additional resistors
#
# *** Approximate solutions (based on the margins) and exact solutions to the combinations of resistors 
#     are provided at the end if available along with the respective currents at Vout


# In[ ]:


from BoB_handlers.Variables import Inputs
from BoB_handlers.Function_logic import Functions


# --- Resistors currently available in the BoB electronics boxes: 11, 150, 500, 9000, 3000, 240, 100, 5600, 10000, 270, 1000, 820
# --- Format of the arguments: number of resistors (11), R1, R2, R3, ... R11

BoB_resistors = Inputs([],[],0,[],[])

R1 = BoB_resistors.R1
R2 = BoB_resistors.R2
x  = BoB_resistors.x
Voltages = BoB_resistors.V
R = BoB_resistors.R

R = Inputs.generate_resistor_values_in_Ohm(R)


# --- R1 and R2 in the electrical schematic have an equal range of possible resistors

for v in range(len(R)):
    R1.append(R[v])
    R2.append(R[v])


# In[ ]:


# --- Input parameters by the user

print('\033[1m' + "\nEnter Vout, Vin, margin below, margin above:" + '\033[0m\n') # The 'Voltages' array is IMPORTANT as it will 
                                                                                  # be called later in the main algorithm

print("Suitable margins (i.e. input 3 and input 4) can be in the range of 0.1 V to 0.3 V\n")

Inputs.generate_voltage_parameters(Voltages,x)
    
R1, R2 = Inputs.input_additional_resistors('Yes',Voltages,R1,R2)

# --- Parameters for the BoB Pump driver amplitude 
# --- Input 1 = Vout = 1.3 V
# --- Input 2 = Vin  = 3.3 V


# In[ ]:


# --- Main algorithm. Computes the approximate and exact solutions for the voltage and current at Vout
# --- using the Potential divider Eqn. and Ohm's Law respectively


Solutions = Functions([],[])
P = Solutions.P
P2 = Solutions.P2

Functions.Run_main_algorithm(P,P2,R1,R2,Voltages)


# In[ ]:


# --- print statements to visualise the Electrical schematic and the equations

print('##### THE FOLLOWING PRINTS WORK BEST IN THE JUPYTER NOTEBOOK ENVIRONMENT #####')

print('\033[1m' + '\nElectrical schematic:' + '\033[0m' + '\n\n\nVin-----R1------R2-----GND\n'        
      + '             |\n             |\n             |\n            Vout\n\n')


print('                                     (Vin * R2)\n'
      + '\033[1m' + 'Potential Divider Equation: ' + '\033[0m' +  ' Vout = ------------\n'
      + '                                     (R1 + R2)\n\n')

print('\033[1m' + "Ohm's Law: " + '\033[0m' + "V = IR\n\n")


# --- Initial parameters

print('Available resistors = \n' + str(Functions.Divide_by_1E3(R1)) + ' kΩ\n')
print('Input parameters ---> [Vout , Vin , margin below , margin above] = ' + str(Voltages) + ' V\n\n')

# --- Approximate solutions for R1 and R2

if P2 != []:
    print('\033[1m' + 'Approximate solutions:\n' + '\033[0m')
    for l in range(len(P2)):
        print('[R2,R1] = ' + str(Functions.Divide_by_1E3(P2[l][0])) 
              + ' kΩ\n' + 'Vout = ' + str(round(P2[l][1],2)) 
              + ' V\n' + 'Iout = ' + str(round(Functions.Times_by_1E3(P2[l][2]),2)) + ' mA\n')
        
# --- Exact solutions for R1 and R2
    
if P != []:
    print('\033[1m' + '\nExact solutions:\n' + '\033[0m')

    for u in range(len(P)):
        print('[R2,R1] = ' + str(Functions.Divide_by_1E3(P[u][0])) + ' kΩ\n' + 'Vout = ' + 
              str(round(P[u][1],2)) + ' V\n' + 'Iout = ' 
              + str(round(Functions.Times_by_1E3(P[u][2]),2)) + ' mA\n')

# --- No results message

if P2 == [] and P == []:
    print('')
    print('\033[1m' + '\nNo results in the selected range, try increasing the margin below and margin above\n' + '\033[0m')


# In[ ]:




