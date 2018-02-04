import matplotlib
matplotlib.use('Agg')
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import re
import sys

NUM_OF_PHASES = 12

UPDATE = 0
SYNC = 1
WRITE = 2
INIT = 3
CHECK_CONV = 4
COMP_ERR = 5
TRACE = 6
EVAL_KNOWN_DF = 7
ITERATE = 8
ITER_W_BARRIERS = 9
BARRIERS = 10
WO_UPDATE = 11

NAMES_OF_PHASES = [[] for i in range(NUM_OF_PHASES)]
NAMES_OF_PHASES[UPDATE] = 'Update'
NAMES_OF_PHASES[SYNC] = 'Sync'
NAMES_OF_PHASES[WRITE] = 'Write'
NAMES_OF_PHASES[INIT] = 'Init'
NAMES_OF_PHASES[CHECK_CONV] = 'Check Conv'
NAMES_OF_PHASES[COMP_ERR] = 'Comp Err'
NAMES_OF_PHASES[TRACE] = 'Trace'
NAMES_OF_PHASES[EVAL_KNOWN_DF] = 'Eval KnownDf'
NAMES_OF_PHASES[ITERATE] = 'Iterate'
NAMES_OF_PHASES[ITER_W_BARRIERS] = 'Iterate with Barriers'
NAMES_OF_PHASES[BARRIERS] = 'Barriers'
NAMES_OF_PHASES[WO_UPDATE] = 'Without Update'

# Function to plot all phases of a specific case,
# e.g. 5A, 120x120x10, 24 MPI processes
# with a stacked bar plot.
def plot_with_phases(phases, ind, title, path):
    width = 1
    p1, = plt.bar(ind, phases[UPDATE], width)
    dataset = phases[UPDATE]
    p2, = plt.bar(ind, phases[SYNC], width, bottom=dataset)
    dataset += phases[SYNC]
    p3, = plt.bar(ind, phases[WRITE], width, bottom=dataset)
    dataset += phases[WRITE]
    p4, = plt.bar(ind, phases[INIT], width, bottom=dataset)
    dataset += phases[INIT]
    p5, = plt.bar(ind, phases[CHECK_CONV], width, bottom=dataset)
    dataset += phases[CHECK_CONV]
    p6, = plt.bar(ind, phases[COMP_ERR], width, bottom=dataset)
    dataset += phases[COMP_ERR]
    p7, = plt.bar(ind, phases[TRACE], width, bottom=dataset)
    dataset += phases[TRACE]
    p8, = plt.bar(ind, phases[EVAL_KNOWN_DF], width, bottom=dataset)
    dataset += phases[EVAL_KNOWN_DF]
    p9, = plt.bar(ind, phases[BARRIERS], width, bottom=dataset)
    plt.ylabel('Runtime')
    plt.title(title)
    plt.xticks(ind)
    p = (p9, p8, p7, p6, p5, p4, p3, p2, p1)
    names = ('barriers', 'evalknownDf', 'trace', 'compErr', 'checkConv',
             'init', 'write', 'sync', 'update')
    plt.legend(p, names)
    plt.savefig(path)
    plt.gcf().clear()

# Parses out files for all runs of a specific case,
# e.g. 5A, 120x120x10, 24 MPI processes.
def parse_outfiles(outs):
    phases = np.zeros(NUM_OF_PHASES)
    checkConv = np.zeros(0)
    compErr = np.zeros(0)
    init = np.zeros(0)
    update = np.zeros(0)
    write = np.zeros(0)
    trace = np.zeros(0)
    evalKnownDf = np.zeros(0)
    sync = np.zeros(0)
    iterate = np.zeros(0)
    iterWBarriers = np.zeros(0)
    woUpdate = np.zeros(0)
    # Save result for each phase in a numpy array.
    for out in outs: # *.slurm.out files
        if os.path.isfile(out) == True:
            with open(out) as f:
                for line in f:
                    if "checkConv)" in line:
                        result = re.search('= (.*) s', line)
                        checkConv = np.append(checkConv, float(result.group(1)))
                        #print(line)
                    elif "compErr)" in line:
                        result = re.search('= (.*) s', line)
                        compErr = np.append(compErr, float(result.group(1)))
                        #print(line)
                    elif "init)" in line:
                        result = re.search('= (.*) s', line)
                        init = np.append(init, float(result.group(1)))
                        #print(line)
                    elif "update)" in line:
                        result = re.search('= (.*) s', line)
                        update = np.append(update, float(result.group(1)))
                        #print(line)
                    elif "write)" in line:
                        result = re.search('= (.*) s', line)
                        write = np.append(write, float(result.group(1)))
                        #print(line)
                    elif "trace)" in line:
                        result = re.search('= (.*) s', line)
                        trace = np.append(trace, float(result.group(1)))
                        #print(line)
                    elif "evalKnownDf)" in line:
                        result = re.search('= (.*) s', line)
                        evalKnownDf = np.append(evalKnownDf, float(result.group(1)))
                        #print(line)
                    elif "sync)" in line:
                        result = re.search('= (.*) s', line)
                        sync = np.append(sync, float(result.group(1)))
                        #print(line)
                    elif " iterate)" in line:
                        result = re.search('= (.*) s', line)
                        iterate = np.append(iterate, float(result.group(1)))
                        #print(line)
                    elif "w.barriers" in line:
                        result = re.search('= (.*) s', line)
                        iterWBarriers = np.append(iterWBarriers, float(result.group(1)))
                        #print(line)
                    else:
                        pass
    # Final result is mean value of all runs.
    phases[UPDATE] = np.mean(update)
    phases[SYNC] = np.mean(sync)
    phases[WRITE] = np.mean(write)
    phases[INIT] = np.mean(init)
    phases[CHECK_CONV] = np.mean(checkConv)
    phases[COMP_ERR] = np.mean(compErr)
    phases[TRACE] = np.mean(trace)
    phases[EVAL_KNOWN_DF] = np.mean(evalKnownDf)
    phases[ITERATE] = np.mean(iterate)
    phases[ITER_W_BARRIERS] = np.mean(iterWBarriers)
    phases[BARRIERS] = phases[ITER_W_BARRIERS] - phases[ITERATE]
    phases[WO_UPDATE] = phases[ITER_W_BARRIERS] - phases[UPDATE]

    return phases

# Function for MPI and OpenMP only tests.
def single_tests(filepath):
    filepath = os.path.normpath(filepath)
    # Check if this test case does exist.
    # If not, return to main function.
    if os.path.isdir(filepath) == False:
        print(filepath, 'does not exist.')
        return
    # Check if MPI or OpenMP test.
    type_of_test = os.path.basename(filepath)
    print('Looking for results in {}.'.format(filepath))
    cases = glob.glob(filepath + '/*')
    # Create all variables to save results.
    list_x = list()
    list_yy = list()
    list_title = list()
    list_x_speedup = list()
    list_y_speedup = list()
    list_title_speedup = list()
    # Iterate through all result folders.
    for case in cases: # Cases, e.g. 5A, 7C, ...
        nodes = glob.glob(case + '/*')
        for node in nodes: # Nodes, e.g. 120x120x10, 120x120x50, ...
            processes = sorted(glob.glob(node + '/*'), key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
            serial_time = -1.0
            x = np.zeros(0)
            yy = [np.zeros(0) for i in range(NUM_OF_PHASES)]
            x_speedup = np.zeros(0)
            y_speedup = np.zeros(0)
            for process in processes: # MPI processes or OpenMP threads, e.g. 1, 2, 4, ...
                outs = glob.glob(process + '/*.slurm.out')
                # Get all the phases from result file (*.slurm.out).
                phases = parse_outfiles(outs)
                # Plot this result with all its phases.
                x = np.append(x, int(os.path.basename(process)))
                for elem in range(0, len(phases)):
                    yy[elem] = np.append(yy[elem], phases[elem])
                ind = np.zeros(0)
                ind = np.append(ind, int(os.path.basename(process)))
                path = './figures/' + type_of_test + '/' + os.path.basename(case)
                if os.path.exists(path) == False:
                    os.makedirs(path)
                path =  path + '/' + os.path.basename(case) + '_' + os.path.basename(node) + '_' + type_of_test + '_' + \
                       str(os.path.basename(process)).zfill(4) + '.eps'
                title = 'Case: ' + os.path.basename(case) + ', ' + os.path.basename(node) + \
                        ', ' + type_of_test + ': ' + os.path.basename(process)
                plot_with_phases(phases, ind, title, path)
                # Speedup calculation.
                # Only calculate speedup if there is a serial runtime.
                if int(os.path.basename(process)) == 1:
                    serial_time = phases[ITER_W_BARRIERS]
                if serial_time > -0.5:
                    speedup = serial_time/phases[ITER_W_BARRIERS]
                    x_speedup = np.append(x_speedup, int(os.path.basename(process)))
                    y_speedup = np.append(y_speedup, speedup)
            # Save results for later.
            list_x.append(x)
            list_yy.append(yy)
            list_title.append(str(os.path.basename(case) + ', ' + os.path.basename(node)))
            if serial_time > -0.5:
                list_x_speedup.append(x_speedup)
                list_y_speedup.append(y_speedup)
                list_title_speedup.append(str(os.path.basename(case) + ', ' + os.path.basename(node)))
    # Labels and filenames depends on type of test.
    if type_of_test == 'MPI':
        xlabel = 'MPI processes [-]'
        path = 'MPI'
    elif type_of_test == 'OpenMP':
        xlabel = 'OpenMP threads [-]'
        path = 'OpenMP'
    else:
        plt.xlabel('Unknown [-]')
        path = 'Unknown'
    if os.path.exists('./figures/' + type_of_test + '/details') == False:
        os.makedirs('./figures/' + type_of_test + '/details')
    # Plot all saved results.
    for phase in range(NUM_OF_PHASES):
        plt.xlabel(xlabel)
        plt.ylabel('Runtime [s]')
        for elem in range(0, len(list_x)):
            plt.plot(list_x[elem], list_yy[elem][phase], linestyle='--', marker='o')
        plt.legend(list_title)
        plt.title('Runtime of \'' + NAMES_OF_PHASES[phase] + '\' with ' + type_of_test + ' parallelization')
        plt.grid()
        plt.savefig('./figures/' + type_of_test + '/details/' + path + '_' + NAMES_OF_PHASES[phase].replace(' ', '_') + '.eps')
        plt.close()
    # Plot just the total runtime.
    plt.xlabel(xlabel)
    plt.ylabel('Runtime [s]')
    for elem in range(0, len(list_x)):
        plt.plot(list_x[elem], list_yy[elem][ITER_W_BARRIERS], linestyle='--', marker='o')
    plt.legend(list_title)
    plt.title('Total runtime with ' + type_of_test + ' parallelization')
    plt.grid()
    plt.savefig('./figures/' + type_of_test + '/' + path + '_runtime.eps')
    plt.close()
    # Plot speedup results if there are any results to plot.
    if len(list_x_speedup) > 0:
        plt.xlabel(xlabel)
        plt.ylabel('Speedup [-]')
        # Plot linear speedup.
        plt.plot(list_x_speedup[0], list_x_speedup[0], linestyle='--')
        # Plot speedup from results.
        for elem in range(0, len(list_x_speedup)):
            plt.plot(list_x_speedup[elem], list_y_speedup[elem], linestyle='--', marker='o')
        list_title_speedup = ['linear speedup'] + list_title_speedup
        plt.legend(list_title_speedup)
        plt.title('Speedup with ' + type_of_test + ' parallelization')
        plt.grid()
        plt.savefig('./figures/' + type_of_test + '/' + path + '_speedup.eps')
        plt.close()

# Function for Hybrid (MPI and OpenMP) tests.
def hybrid_tests(filepath):
    filepath = os.path.normpath(filepath)
    # Check if this test case does exist.
    # If not, return to main function.
    if os.path.isdir(filepath) == False:
        print(filepath, 'does not exist.')
        return
    # Get Hybrid name.
    type_of_test = os.path.basename(filepath)
    print('Looking for results in {}.'.format(filepath))
    cases = glob.glob(filepath + '/*')
    # Create all variables to save results.
    # Iterate through all result folders.
    for case in cases: # Cases, e.g. 5A, 7C, ...
        nodes = glob.glob(case + '/*')
        for node in nodes: # Nodes, e.g. 120x120x10, 120x120x50, ...
            list_x = list()
            list_yy = list()
            list_title = list()
            list_x_speedup = list()
            list_y_speedup = list()
            list_title_speedup = list()
            tasks_per_node = glob.glob(node + '/*')
            for task_per_node in tasks_per_node:
                processes = sorted(glob.glob(task_per_node + '/*'), key=lambda x: int(os.path.splitext(os.path.basename(x))[0]))
                x = np.zeros(0)
                yy = [np.zeros(0) for i in range(NUM_OF_PHASES)]
                x_speedup = np.zeros(0)
                y_speedup = np.zeros(0)
                serial_time = -1.0
                outs = './results/MPI/' + os.path.basename(case) + '/' + os.path.basename(node) + '/1'
                if os.path.exists(outs) == True:
                    outs = glob.glob(outs + '/*.slurm.out')
                    phases = parse_outfiles(outs)
                    serial_time = phases[ITER_W_BARRIERS]
                    speedup = serial_time/phases[ITER_W_BARRIERS]
                    x_speedup = np.append(x_speedup, 1)
                    y_speedup = np.append(y_speedup, speedup)
                for process in processes: # MPI processes or OpenMP threads, e.g. 1, 2, 4, ...
                    outs = glob.glob(process + '/*.slurm.out')
                    # Get all the phases from result file (*.slurm.out).
                    phases = parse_outfiles(outs)
                    # Plot this result with all its phases.
                    num_proc = int(os.path.basename(process)) * int(str(os.path.basename(task_per_node)).split('x')[1])
                    x = np.append(x, num_proc)
                    for elem in range(0, len(phases)):
                        yy[elem] = np.append(yy[elem], phases[elem])
                    ind = np.zeros(0)
                    ind = np.append(ind, num_proc)
                    path = './figures/' + type_of_test + '/' + os.path.basename(case)
                    if os.path.exists(path) == False:
                        os.makedirs(path)
                    path =  path + '/' + os.path.basename(case) + '_' + os.path.basename(node) + '_' + type_of_test + '_' + \
                            os.path.basename(task_per_node) + '_' + \
                            str(num_proc).zfill(4) + '.eps'
                    title = 'Case: ' + os.path.basename(case) + ', ' + os.path.basename(node) + \
                            ', ' + type_of_test + ': ' + str(num_proc) + ' (per node: ' + os.path.basename(task_per_node) + ')'
                    plot_with_phases(phases, ind, title, path)
                    # Speedup calculation.
                    # Only calculate speedup if there is a serial runtime.
                    if serial_time > -0.5:
                        speedup = serial_time/phases[ITER_W_BARRIERS]
                        x_speedup = np.append(x_speedup, num_proc)
                        y_speedup = np.append(y_speedup, speedup)
                # Save results for later.
                list_x.append(x)
                list_yy.append(yy)
                list_title.append(str(os.path.basename(case) + ', ' + os.path.basename(node) + ' (' + os.path.basename(task_per_node) + ')'))
                if serial_time > -0.5:
                    list_x_speedup.append(x_speedup)
                    list_y_speedup.append(y_speedup)
                    list_title_speedup.append(str(os.path.basename(case) + ', ' + os.path.basename(node) + ' (' + os.path.basename(task_per_node) + ')'))
            if os.path.exists('./figures/' + type_of_test + '/details') == False:
                os.makedirs('./figures/' + type_of_test + '/details')
            # Plot all results.
            for phase in range(NUM_OF_PHASES):
                path = 'Hybrid_' + os.path.basename(case) + '_' + os.path.basename(node)
                plt.xlabel('MPI processes x OpenMP threads [-]')
                plt.ylabel('Runtime [s]')
                for elem in range(0, len(list_x)):
                    plt.plot(list_x[elem], list_yy[elem][phase], linestyle='--', marker='o')
                plt.legend(list_title)
                plt.title('Runtime of \'' + NAMES_OF_PHASES[phase] + '\' with ' + type_of_test + ' parallelization')
                plt.grid()
                plt.savefig('./figures/' + type_of_test + '/details/' + path + '_' + NAMES_OF_PHASES[phase].replace(' ', '_') + '.eps')
                plt.close()
            # Plot just total runtime.
            path = 'Hybrid_' + os.path.basename(case) + '_' + os.path.basename(node)
            plt.xlabel('MPI processes x OpenMP threads [-]')
            plt.ylabel('Runtime [s]')
            for elem in range(0, len(list_x)):
                plt.plot(list_x[elem], list_yy[elem][ITER_W_BARRIERS], linestyle='--', marker='o')
            plt.legend(list_title)
            plt.title('Total runtime with ' + type_of_test + ' parallelization')
            plt.grid()
            plt.savefig('./figures/' + type_of_test + '/' + path + '_runtime.eps')
            plt.close()
            # Plot speedup results if there are any results to plot.
            if len(list_x_speedup) > 0:
                plt.xlabel('MPI processes x OpenMP threads [-]')
                plt.ylabel('Speedup [-]')
                # Plot linear speedup.
                plt.plot(list_x_speedup[1], list_x_speedup[1], linestyle='--')
                # Plot speedup from results.
                for elem in range(0, len(list_x_speedup)):
                    plt.plot(list_x_speedup[elem], list_y_speedup[elem], linestyle='--', marker='o')
                list_title_speedup = ['linear speedup'] + list_title_speedup
                plt.legend(list_title_speedup)
                plt.title('Speedup with ' + type_of_test + ' parallelization')
                plt.grid()
                plt.savefig('./figures/' + type_of_test + '/' + path + '_speedup.eps')
                plt.close()

def main():
    # Check if path to folder is provided and if folder exists.
    if len(sys.argv) > 1:
        if os.path.isdir(sys.argv[1]) == True:
            filepath = sys.argv[1]
        else:
            print(sys.argv[1], 'does not exist or is not a folder.')
            print('Usage: python3', sys.argv[0], '<PATH/TO/FOLDER>')
            print('Aborting.')
            exit()
    else:
        print('No command line argument for result folder provided.')
        print('Usage: python3', sys.argv[0], '<PATH/TO/FOLDER>')
        print('Aborting.')
        exit()

    # Create folder for results if it does not exist.
    if os.path.exists('./figures') == False:
        os.makedirs('./figures')
    if os.path.exists('./figures/MPI') == False:
        os.makedirs('./figures/MPI')
    if os.path.exists('./figures/OpenMP') == False:
        os.makedirs('./figures/OpenMP')
    if os.path.exists('./figures/Hybrid') == False:
        os.makedirs('./figures/Hybrid')

    # Call function for every testcase.
    single_tests(filepath + '/MPI')
    single_tests(filepath + '/OpenMP')
    hybrid_tests(filepath + '/Hybrid')

    print('Done.')

if __name__ == '__main__':
    main()
