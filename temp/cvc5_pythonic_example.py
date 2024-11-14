from cvc5.pythonic import *

solver = Solver() 

option_names = solver.getOptionNames()

used_names = set()
for option in option_names: 

    infoo = solver.getOptionInfo(option)
    neww = False 

    for k in infoo.keys(): 
        if k not in used_names: 
            neww = True
            used_names.add(k)
    
    if neww == True: 
        print(infoo)

