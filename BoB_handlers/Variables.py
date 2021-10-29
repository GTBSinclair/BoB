class Inputs:

    def __init__(Is, R1, R2, x, Voltages, R):
        Is.R1 = R1
        Is.R2 = R2
        Is.x = x
        Is.V = Voltages
        Is.R = R

    def generate_resistor_values_in_Ohm(R):

        num = 0
        for i in range(int(input("Enter number of resistors:\n"))):
            num += 1
            s = (float(input("Resistor" + str(num) + " : ")))
            R.append(s)
        return R

    def generate_voltage_parameters(V,x):
        for i in range(4):
            x += 1
            s = (float(input("input" + str(x) + " : ")))
            V.append(s)


    def input_additional_resistors(Answer,V,R1,R2):
        # Answer: Type Yes to add more resistors, otherwise type No to use available BoB resistors only:
        x1 = len(V)
        additional_resistors = []

        if Answer == 'Yes':
            inputY = int(input("Additional resistors selected. How many resistors need to be added? : "))
            print('\nUse the SI unit Ω:\n')
            for c in range(inputY):
                x1 += 1
                s1 = (float(input("input" + str(x1) + " : ")))
                additional_resistors.append(s1)
            R1 = R1 + additional_resistors
            R2 = R2 + additional_resistors
            print('\n The updated list of resistors is: ' + str(R1) + '\n')
        elif Answer == 'No':
            print('\nNo additional resistors selected. Available resistors are: ' + str(R1))

        return R1,R2
            #print('\nAvailable resistors are: [150, 500, 9000, 3000, 240, 100, 5600, 10000, 270, 1000, 820] Ω')

        # --- Parameters for the BoB Pump driver amplitude 
        # --- Input 1 = Vout = 1.3 V
        # --- Input 2 = Vin  = 3.3 V