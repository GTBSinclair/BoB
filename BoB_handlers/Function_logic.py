from BoB_handlers.Variables import Inputs


class Functions(Inputs):

    def __init__(Is,P,P2) -> None:
        Is.P = P
        Is.P2 = P2

    # --- Unit conversion functions for lists and integers

    def Divide_by_1E3(unit):
        if isinstance(unit, list) == True:
            for g in range(len(unit)):
                unit[g] = unit[g]/1000
        else:
            unit = unit/1000
        return unit

    def Times_by_1E3(unit):
        if isinstance(unit, list) == True:
            for g in range(len(unit)):
                unit[g] = unit[g]*1000
        else: 
            unit = unit*1000
        return unit

    def Run_main_algorithm(P,P2,R1,R2,V):
        # P = Exact solutions
        # P2 = Approximate solutions

        for i in range(len(R1)):
            for j in range(len(R2)):
                if V[0] == (R2[j]*V[1])/(R1[i]+R2[j]): # Exact calculation
                    P.append([[R2[j],R1[i]],(R2[j]*V[1])/(R1[i]+R2[j]), 
                            V[1]/(R1[i]+R2[j])]) # Current (A) is calculated at the end of P.append
                elif ((R2[j]*V[1])/(R1[i]+R2[j]))>V[0]-V[2] and ((R2[j]*V[1])/(R1[i]+R2[j]))<V[0]+V[3]: # Approximate calculation
                    P2.append([[R2[j],R1[i]],(R2[j]*V[1])/(R1[i]+R2[j]),
                            V[1]/(R1[i]+R2[j])]) # Current (A) is calculated at the end of P2.append