"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Bin Packing Problem (Python version)
# https://developers.google.com/optimization/bin/bin_packing#python
# Applied to Sagra Dosson 2020

# IMPLEMENT ALSO AN HEURISTIC WAY: start from the biggest value and try to fit the bin capacity with the second biggest value, and so on...
                                   if it is not possible, add a bin.
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

from __future__ import print_function
from ortools.linear_solver import pywraplp
import sys
import getopt
#import mysql.connector

# Create the data from DB
def create_data_model(day, pranzo, capacity):
    data = {}
    
    weights = []
    referenti = []
    
    """ Connection to DB """
    """connection = None
    try:
        connection = mysql.connector.connect(host='62.149.150.198', database='Sql695720_5', user='Sql695720', password='srqlawlns2')
        cursor = connection.cursor()
        
        query = "SELECT referente, postiprenotati FROM prenotazioni WHERE giorno=%s AND pranzo=%s"
        giorno = (5,)
        pranzo = (0,)
        
        cursor.execute(query, (giorno, pranzo))
        
        for (referente, postiprenotati) in cursor:
            weights.append(postiprenotati)
            referenti.append(referente)
            
    except mysql.connector.Error as err:
        print(err)
          
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()"""
    
    """ Read file from disk """
    f = open("prenotazioni.txt", "r")
    lines = f.readlines()
    for line in lines:
        l = line.split('|')
        l = l[1:]
        
        day_temp = int(l[1])
        pranzo_temp = int(l[2])
        
        if day_temp == day and pranzo_temp == pranzo: # select GIORNO and PRANZO
            referenti.append(l[3])
            weights.append(int(l[4]))
    f.close()
    
    data['weights'] = weights
    data['items'] = list(range(len(weights)))
    data['bins'] = data['items']
    data['bin_capacity'] = capacity   # The capacity of each table (or array of tables)
    
    return data, referenti


def main(day, pranzo, capacity):
    data, referenti = create_data_model(day, pranzo, capacity)
    
    print("\nPRENOTAZIONI GIORNO", day, "- pranzo:", pranzo, "\n")
    for count, item in enumerate(data['items']):
        print("Prenotazione", item, "(", referenti[count], "->", data['weights'][item], "posti)")

    # Create the mip solver with the CBC backend.
    solver = pywraplp.Solver.CreateSolver('bin_packing_mip', 'CBC')

    # Variables
    # x[i, j] = 1 if item i is packed in bin j.
    x = {}
    for i in data['items']:
        for j in data['bins']:
            x[(i, j)] = solver.IntVar(0, 1, 'x_%i_%i' % (i, j))

    # y[j] = 1 if bin j is used.
    y = {}
    for j in data['bins']:
        y[j] = solver.IntVar(0, 1, 'y[%i]' % j)

    # Constraints
    # Each item must be in exactly one bin.
    for i in data['items']:
        solver.Add(sum(x[i, j] for j in data['bins']) == 1)

    # The amount packed in each bin cannot exceed its capacity.
    for j in data['bins']:
        solver.Add(
            sum(x[(i, j)] * data['weights'][i] for i in data['items']) <= y[j] *
            data['bin_capacity'])

    # Objective: minimize the number of bins used.
    solver.Minimize(solver.Sum([y[j] for j in data['bins']]))

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        num_bins = 0
        for j in data['bins']:
            if y[j].solution_value() == 1:
                bin_items = []
                ref_items = []
                bin_weight = 0
                for i in data['items']:
                    if x[i, j].solution_value() > 0:
                        bin_items.append(i)
                        ref_items.append(referenti[i])
                        bin_weight += data['weights'][i]
                if bin_weight > 0:
                    num_bins += 1
                    print('\nTABLE ', j)
                    print('  Items packed:', bin_items)
                    print('  Referenti:', ref_items)
                    print('  Total weight:', bin_weight)
        print()
        print('Number of bins used:', num_bins)
        print('Time = ', solver.WallTime(), ' milliseconds\n')
    else:
        print('\nThe problem does not have an optimal solution!\n')


if __name__ == '__main__':
    short_options = "g:p:c:h"
    long_options = ["giorno=", "pranzo=", "capacity=", "help"]
    
    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    help = None
    day = None
    pranzo = None
    capacity = None
    
    # Evaluate given options
    for current_argument, current_value in arguments:
        if current_argument in ("-g", "--giorno"):
            day = int(current_value)
        elif current_argument in ("-p", "--pranzo"):
            pranzo = int(current_value)
        elif current_argument in ("-c", "--capacity"):
            capacity = int(current_value)
        elif current_argument in ("-h", "--help"):
            help = 1
            print("\nExecute this script passing three values:")
            print("-g or --giorno to set the day")
            print("-p or --pranzo to set the lunch (0 or 1)")
            print("-c or --capacity to set maximum capacity of each table")
    
    if day is not None and pranzo is not None and capacity is not None:
        main(day, pranzo, capacity)
    else:
        print("\nBPP needs three arguments. See -h or --help\n")
