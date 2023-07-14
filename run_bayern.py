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

    # optional: define names for sites in plot_tuples
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

        # Import Excel file for reference
        xls = pd.ExcelFile(f'myopic/input/input_bayern_{year}.xlsx')

        input_file = {}
        for sheet in xls.sheet_names:
            input_file[sheet] = xls.parse(sheet_name = sheet, index_col = 0)


        # Import timeseries data
        xls = pd.ExcelFile(f'myopic/input/timeseries.xlsx')

        timeseries = {}
        for sheet in xls.sheet_names:
            timeseries[sheet] = xls.parse(sheet_name = sheet, index_col = 0)


        # Update 'Global' sheet
        input_file['Global'].at['Support timeframe', 'value'] = years[idx+1]
        input_file['Global'].at['CO2 limit', 'value'] = timeseries['co2_budget'].at['CO2 budget', years[idx+1]] * 1e6


        # Update 'Commodity'
        input_file['Commodity'] = input_file['Commodity'].reset_index()
        timeseries['prices'] = timeseries['prices'].reset_index()

        input_file['Commodity']['price'] = timeseries['prices'][years[idx+1]]
        input_file['Commodity'] = input_file['Commodity'].set_index('Site')
        input_file['Commodity'].head()


        # Update 'Process' sheet

        input_file['Process'] = input_file['Process'].reset_index()
        timeseries['retiring'] = timeseries['retiring'].reset_index()
        timeseries['capup'] = timeseries['capup'].reset_index()
        timeseries['capex'] = timeseries['capex'].reset_index()

        input_file['Process']['inst-cap'] = timeseries['retiring'][years[idx+1]]
        
        input_file['Process']['cap-up'] = timeseries['capup'][years[idx+1]]
        input_file['Process']['inv-cost'] = timeseries['capex'][years[idx+1]]

        input_file['Process'] = input_file['Process'].set_index('Site')
        input_file['Process'].head()


        # Update 'Demand' sheet
        # only woodcutter approach, will loop through demand type commodities, standarized names in 'timeseries', and catch-try

        input_file['Demand']['Bayern.Space heating'] = timeseries['profiles']['profile_space_heating'] * timeseries['demand'].at['Space heating', years[idx+1]] * 1e6
        input_file['Demand']['Bayern.Process heating A'] = timeseries['profiles']['profile_process_heating'] * timeseries['demand'].at['Process heating A', years[idx+1]] * 1e6
        input_file['Demand']['Bayern.Process heating B'] = timeseries['profiles']['profile_process_heating'] * timeseries['demand'].at['Process heating B', years[idx+1]] * 1e6
        input_file['Demand']['Bayern.Process heating C'] = timeseries['profiles']['profile_process_heating'] * timeseries['demand'].at['Process heating C', years[idx+1]] * 1e6
        input_file['Demand']['Bayern.Electric charging'] = timeseries['profiles']['profile_charging'] * timeseries['demand'].at['Electric charging', years[idx+1]] * 1e6
        input_file['Demand']['Bayern.Elec_Rest'] = timeseries['profiles']['profile_electricity'] * timeseries['demand'].at['Electricity', years[idx+1]] * 1e6


        # Write DataFrame dictionary into a 
        with pd.ExcelWriter(f"myopic/input/input_bayern_{years[idx+1]}.xlsx") as writer:
            for sheet in list(input_file.keys()):
                input_file[sheet].to_excel(writer, sheet_name = sheet)
