import configparser
import os
import sys

import matplotlib
matplotlib.use('Agg')
import pymc
import numpy as np # use numpy 1.11.3.. newer version break pymc

from startSimulation import parse_config_file
from startSimulation import check_variables
from startSimulation import calc_variables
from startSimulation import check_stability
from startSimulation import create_region_file
from startSimulation import create_init_file
from startSimulation import set_environment_variables
from startSimulation import call_simulation

from postProcessing import calc_tumor_near_surface_temperatures
from postProcessing import calc_vessels_temperatures
from postProcessing import calc_non_vessels_temperatures
from postProcessing import region_array_from_file
from postProcessing import surface_vessels_array_from_file

from helperFunctions import temperature_array_from_result

## Einflussgroessen (unabhaengig von der Simulation)
# Tumortiefe vs. Temperatur an der Oberflaeche

count = 0
params = {'NAME_CONFIGFILE_TEMPLATE' : ''}

def fitSimulation(targetValues):
    omega_normal = pymc.Uniform('omega_normal', 0.0014, 0.014, value=0.004)
    omega_tumor = pymc.Uniform('omega_tumor', 0.0005, 0.017, value=0.00975)
    omega_vessel = pymc.Uniform('omega_vessel', 0.0014, 0.014, value=0.004)
    T_blood = pymc.Uniform('T_blood', 36.7, 37.0, value=37.0)
    q_brain = pymc.Uniform('q_brain', 5725, 25000, value=25000)
    q_tumor = pymc.Uniform('q_tumor', 5725, 25000, value=25000)
    lambda_bt = pymc.Uniform('lambda_bt', 0.45, 0.6, value=0.5)
    rho_c_brain = pymc.Uniform('rho_c_brain', 3684600, 4388800, value=3796000)
    rho_c_tumor = pymc.Uniform('rho_c_tumor', 3684600, 4388800, value=3796000)
    h = pymc.Uniform('h', 8, 10, value=10)

    @pymc.deterministic(plot=False)
    def callScaFES(omega_normal=omega_normal,
                   omega_tumor=omega_tumor,
                   omega_vessel=omega_vessel,
                   T_blood=T_blood,
                   q_brain=q_brain,
                   q_tumor=q_tumor,
                   lambda_bt=lambda_bt,
                   rho_c_brain=rho_c_brain,
                   rho_c_tumor=rho_c_tumor,
                   h=h):

        global count
        global params
        count += 1

        print()
        print('##### ScaFES iteration: {} #####'.format(count))

        # Set normal, tumor, vessel,  perfusion to respective values.
        params = {'NAME_CONFIGFILE' : 'pymc_' + str(count) + '.ini'}
        params['NAME_RESULTFILE'] = ''
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read('Parameters.ini')
        # Omega.
        config['Brain']['OMEGA'] = str(omega_normal)
        config['Tumor']['OMEGA'] = str(omega_tumor)
        config['MRI']['USE_VESSELS_SEGMENTATION'] = 'True'
        config['MRI']['VARIABLES_VESSELS'] = 'omega'
        config['MRI']['VALUES_VESSELS'] = str(omega_vessel)
        config['MRI']['VALUES_NON_VESSELS'] = str(omega_normal)
        # T_blood.
        config['Brain']['T_BLOOD'] = str(T_blood)
        config['Tumor']['T_BLOOD'] = str(T_blood)
        # Q.
        config['Brain']['Q'] = str(q_brain)
        config['Tumor']['Q'] = str(q_tumor)
        # lambda.
        config['Brain']['LAMBDA'] = str(lambda_bt)
        config['Tumor']['LAMBDA'] = str(lambda_bt)
        # rho * c.
        config['Brain']['RHO'] = str(rho_c_brain)
        config['Brain']['C'] = str(1.0)
        config['Tumor']['RHO'] = str(rho_c_tumor)
        config['Tumor']['C'] = str(1.0)
        # h.
        config['Parameters']['H'] = str(h)

        with open(params['NAME_CONFIGFILE'], 'w') as configfile:
            config.write(configfile)

        # Call simulation.
        parse_config_file(params)
        check_variables(params)
        calc_variables(params)
        check_stability(params)
        if params['USE_MRI_FILE'] == False:
            create_region_file(params)
        create_init_file(params)
        set_environment_variables(params)
        call_simulation(params, 'RUN_HELPER.sh')

        # Compute temperatures of normal, tumor, vessel tisue.
        temp = temperature_array_from_result(params['NAME_RESULTFILE'])
        tumor = region_array_from_file(params['NAME_REGION_FILE'])
        vessels = surface_vessels_array_from_file(params['NAME_VESSELS_FILE'])

        T_tumor,_,_,_ = calc_tumor_near_surface_temperatures(temp, tumor)
        if params['USE_VESSELS_SEGMENTATION'] == True:
            temp = temp[-1,:,:]
            T_vessel,_,_,_ = calc_vessels_temperatures(temp, vessels)
            T_normal,_,_,_ = calc_non_vessels_temperatures(temp, vessels)
        else:
            T_vessel = -1.0
            T_normal = -1.0

        return [T_normal, T_tumor, T_vessel]

    y = pymc.Normal('simulated temperatures', mu=callScaFES, tau=1,
                    value=targetValues, observed=True)

    return locals()


def main():
    print('Starting MCMC simulation and fit.')
    global params
    # Check if path to configfile is provided and if file exists.
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]) == True:
            params['NAME_CONFIGFILE_TEMPLATE'] = sys.argv[1]
            params['RUN_SCRIPT'] = 'RUN_HELPER.sh'
        else:
            print('* ERROR:', sys.argv[1], 'does not exist.')
        if len(sys.argv) > 2:
            if os.path.isfile(sys.argv[2]) == True:
                params['RUN_SCRIPT'] = sys.argv[2]
            else:
                print('* ERROR: Optional run script', sys.argv[2],
                      'does not exist.')
                print('Aborting.')
                exit()
    else:
        print('* ERROR: No command line argument for configfile provided.')

    if params['NAME_CONFIGFILE_TEMPLATE'] == '':
        print('Usage: python3', sys.argv[0],
              '<PATH/TO/CONFIGFILE> [<PATH/TO/RUN/SCRIPT]')
        print('Aborting.')
        exit()

    sample_iterations = 5
    sample_burns = 1
    print('Number of sample iterations: {}.'.format(sample_iterations))
    print('Number of sample burns: {}.'.format(sample_burns))

    # Target values for this dataset.
    # [T_normal, T_tumor, T_vessel]
    targetValues = [32.8, 30.0, 34.5]
    print('Target values: [T_normal, T_tumor, T_vessel]')
    print('Target values for this dataset: {}.'.format(targetValues))

    # Apply MCMC sampler.
    MDL = pymc.MCMC(fitSimulation(targetValues))
    MDL.sample(iter=sample_iterations, burn=sample_burns)
    print()

    # Extract and plot results.
    temperatures = MDL.stats()['callScaFES']['mean']
    omega_normal = MDL.stats()['omega_normal']['mean']
    omega_tumor = MDL.stats()['omega_tumor']['mean']
    omega_vessel = MDL.stats()['omega_vessel']['mean']
    T_blood = MDL.stats()['T_blood']['mean']
    q_brain = MDL.stats()['q_brain']['mean']
    q_tumor = MDL.stats()['q_tumor']['mean']
    lambda_bt = MDL.stats()['lambda_bt']['mean']
    rho_c_brain = MDL.stats()['rho_c_brain']['mean']
    rho_c_tumor = MDL.stats()['rho_c_tumor']['mean']
    h = MDL.stats()['h']['mean']
    pymc.Matplot.plot(MDL)
    print()
    print('T_final: [T_normal, T_tumor, T_vessel]')
    print('T_final:', temperatures)
    print()
    print('omega_normal:', omega_normal)
    print('omega_tumor:', omega_tumor)
    print('omega_vessel:', omega_vessel)
    print('T_blood:', T_blood)
    print('q_brain:', q_brain)
    print('q_tumor:', q_tumor)
    print('lambda_bt:', lambda_bt)
    print('rho_c_brain:', rho_c_brain)
    print('rho_c_tumor:', rho_c_tumor)
    print('h:', h)

    graph = pymc.graph.graph(MDL)
    graph.write_png('graph.png')

    print()
    print('Number of ScaFES calls:', count)
    print()

    print('Done.')

if __name__ == "__main__":
    main()
