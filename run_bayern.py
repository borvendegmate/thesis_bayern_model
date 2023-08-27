import os
import shutil
import urbs
import pandas as pd
import numpy as np

years = [2020, 
         2025, 
         2030, 
         2035, 
         2040,
         2045, 
         2050]

# Create input file for first year
urbs.myopic_update("", years[0], True)

for idx, year in enumerate(years):

    input_files = 'input_bayern_{}.xlsx'.format(year)  # for single year file name, for intertemporal folder name2
    input_dir = 'myopic/input'
    input_path = os.path.join('myopic', 'input', input_files)

    result_name = 'output_bayern_{}'.format(year)
    result_dir = urbs.prepare_result_directory(result_name)

    # copy input file to result directory
    try:
        shutil.copytree(input_path, os.path.join(result_dir, input_dir))
    except NotADirectoryError:
        shutil.copyfile(input_path, os.path.join(result_dir, input_files))
    # copy run file to result directory
    shutil.copy(__file__, result_dir)

    # objective function
    objective = 'cost'  # set either 'cost' or 'CO2' as objective

    # Choose Solver (cplex, glpk, gurobi, ...)
    solver = 'gurobi'

    # simulation timesteps
    (offset, length) = (0,8760)  # time step selection
    timesteps = range(offset, offset+length+1)
    dt = 1  # length of each time step (unit: hours)

    # detailed reporting commodity/sites
    report_tuples = [
        #(2019, 'Bayern', 'Solar'),
        #(year, 'Bayern', 'CO2'),
        (year, 'Bayern', 'Elec'),
        (year, 'Bayern', 'Space heating'),
        (year, 'Bayern', 'Process heating A'),
        (year, 'Bayern', 'Process heating B'),
        (year, 'Bayern', 'Process heating C'),
        #(year, 'Bayern', 'Electric charging'),
        #(year, 'Bayern', 'Elec_Rest')
        ]

    # optional: define names for sites in report_tuples
    report_sites_name = {}

    # plotting commodities/sites
    plot_tuples = []

    # optional: define names for sites
    # 0000 0in plot_tuples
    plot_sites_name = {}

    # plotting timesteps
    plot_periods = {}

    # add or change plot colors
    my_colors = {}
    for country, color in my_colors.items():
        urbs.COLORS[country] = color

    # select scenarios to be run
    scenarios = [
                urbs.scenario_base
                ]

    for scenario in scenarios:
        prob = urbs.run_scenario(input_path, solver, timesteps, scenario,
                                result_dir, dt, objective,
                                plot_tuples=plot_tuples,
                                plot_sites_name=plot_sites_name,
                                plot_periods=plot_periods,
                                report_tuples=report_tuples,
                                report_sites_name=report_sites_name,
                                yr = year)
        
    if(year < years[-1]):

        # Create input Excel file for next year
        urbs.myopic_update(years[idx], years[idx+1], False)