# Import data management libraries
import urbs
import pandas as pd
import time

def myopic_update(prev_year, next_year, is_first_year):

    print(f"Starting myopic update for {next_year}")
    start_update = time.perf_counter()

    # Import Excel file for reference and structure 
    xls = pd.ExcelFile(f'myopic/input/urbs_ref.xlsx') ###################################################

    # Create a dict of DataFrames representing a multipage spreadsheet
    df = {}
    for sheet in xls.sheet_names:
        df[sheet] = xls.parse(sheet_name = sheet, index_col = 0)

    # Import longtable with timeseries information 
    ts = pd.read_excel("./myopic/input/longtable.xlsx") #################################################

    # Import profiles
    profiles = pd.read_excel("./myopic/input/profiles.xlsx") ############################################
    
    
    if is_first_year:

        print("Updating Global sheet")
        update_global(df, ts, next_year)

        print("Updating Demand sheet")
        update_demand(df, ts, profiles, next_year)

        print("Updating Commodity sheet")
        update_commodity(df, ts, next_year)

    else:

        # Import output from previous year
        output = urbs.load(f"myopic/output/output_bayern_{prev_year}.h5")._result #######################

        print("Updating Global sheet")
        update_global(df, ts, next_year)

        print("Updating Demand sheet")
        update_demand(df, ts, profiles, next_year)

        print("Updating Commodity sheet")
        update_commodity(df, ts, next_year)

        print("Updating Process sheet")
        update_process(df, ts, output, next_year)

        print("Updating Storage sheet")
        update_storage(df, ts, output, next_year)

    print("Writing Excel file")
    write_excel(df, next_year)

    end_update = time.perf_counter()
    print(f"Finished myopic update for {next_year} in {end_update-start_update} seconds")


# Update the Global tab
def update_global(df, ts, next_year):
    # Update parameters on the Global tab
    df['Global'].at['Support timeframe', 'value'] = next_year

    # Update the CO2 limit
    df['Global'].at['CO2 limit', 'value'] = ts.loc[(ts['Sheet'] == 'Global') & (ts['Parameter'] == 'CO2 limit')][next_year] * 1e6


# Update the Demand tab
def update_demand(df, ts, profiles, next_year):

    for col in df['Demand'].columns:
        # Get commodity names from the column names
        comm = col.split('.')[1]

        # Update demand timeseries with the new annual consumption values and profiles
        df['Demand'].loc[:, col] = float(ts.loc[(ts['Sheet'] == 'Demand') & (ts['ID'] == comm)][next_year]) * 1e6 * profiles[comm]


# Update the Commodity tab
def update_commodity(df, ts, next_year):

    for param in ts[ts['Sheet'] == 'Commodity']['Parameter'].unique():

        for idx in ts.loc[(ts['Parameter'] == param)]['ID'].unique():

            df['Commodity'].loc[df['Commodity']['Commodity'] == idx, param] = float(ts.loc[(ts['Sheet'] == 'Commodity') & (ts['Parameter'] == param) & (ts['ID'] == idx)][next_year])


# Update the Process tab
def update_process(df, ts, output, next_year):

    for param in ts[ts['Sheet'] == 'Process']['Parameter'].unique():

        for idx in ts.loc[(ts['Parameter'] == param)]['ID'].unique():

            df['Process'].loc[df['Process']['Process'] == idx, param] = float(ts.loc[(ts['Sheet'] == 'Process') & (ts['Parameter'] == param) & (ts['ID'] == idx)][next_year])
            
            if(param == 'inst-cap'):
                df['Process'].loc[df['Process']['Process'] == idx, param] += output['cap_pro_new'].unstack()[idx][0]


# Update the Storage tab
def update_storage(df, ts, output, next_year):

    for param in ts[ts['Sheet'] == 'Storage']['Parameter'].unique():

        for idx in ts.loc[(ts['Parameter'] == param)]['ID'].unique():

            # Update parameters based on the update table
            df['Storage'].loc[df['Storage']['Storage'] == idx, param] = float(ts.loc[(ts['Sheet'] == 'Storage') & (ts['Parameter'] == param) & (ts['ID'] == idx)][next_year])
            
            # Add installed capacities from the previous year
            if(param == 'inst-cap-c'):
                df['Storage'].loc[df['Storage']['Storage'] == idx, param] += output['cap_sto_c_new'].unstack().loc[output['cap_sto_c_new'].unstack().index.get_level_values('sto') == idx, :].max().max()

            # Add installed capacities from the previous year
            if(param == 'inst-cap-p'):
                df['Storage'].loc[df['Storage']['Storage'] == idx, param] += output['cap_sto_p_new'].unstack().loc[output['cap_sto_p_new'].unstack().index.get_level_values('sto') == idx, :].max().max()

# Write output file to Excel
def write_excel(next_year_dict, next_year):
    with pd.ExcelWriter(f"myopic/input/input_bayern_{next_year}.xlsx") as writer: ##############################################################################
            for sheet in list(next_year_dict.keys()):
                next_year_dict[sheet].to_excel(writer, sheet_name = sheet)