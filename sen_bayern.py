import os
import shutil
import urbs
import pandas as pd
import numpy as np

sen = [
    "A",
    "B",
    "C",
    "D",
    "E"
]

for idx, s in enumerate(sen):

    input_files = 'input_bayern_{}.xlsx'.format(s)  # for single year file name, for intertemporal folder name2
    input_dir = 'myopic/input'
    input_path = os.path.join('myopic', 'input', input_files)

    result_name = 'output_bayern_{}'.format(s)
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
        (2050, 'Bayern', 'Elec'),
        (2050, 'Bayern', 'Space heating'),
        (2050, 'Bayern', 'Process heating A'),
        (2050, 'Bayern', 'Process heating B'),
        (2050, 'Bayern', 'Process heating C'),
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
                                yr = 2050)