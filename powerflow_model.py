import polars as pl
import pandas as pd
from pvlib import pvsystem, modelchain, location, iotools
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

DATA_CENTER_LOAD_MW = 100 
SYSTEM_LIFETIME_YEARS = 20
BATT_ROUND_TRIP_EFFICIENCY = 0.92
BATT_DURATION_HOURS = 4
BATT_DEGRADATION_PER_YEAR = 0.35/20
SOLAR_DEGRADATION_PER_YEAR = 0.005
GENERATOR_HEATRATE = 8989.3 # BTU/kWh
DC_AC_RATIO = 1.2


########## PV_LIB_PARAMS ##########
# pdc0: DC power rating at Standard Test Conditions (STC)
# Normalized to 1 kW so we can scale the output later
# STC = 1000 W/m2 irradiance, 25°C cell temp, AM1.5 spectrum
PDC0 = 1
# gamma_pdc: Temperature coefficient of power in units of 1/°C
# Represents how much power output changes with cell temperature
# -0.004 means power decreases 0.4% per °C increase in temperature
GAMMA_PDC = -0.004

# Parameters for the Sandia temperature model that calculates
# cell temperature from ambient conditions
# a: Wind speed coefficient in units of °C/(W/m2)
# Represents how wind speed affects cell temperature
TEMP_A = -3.56
# b: Wind speed coefficient in units of °C/(W/m2)/(m/s)
# Represents how wind speed affects the rate of heat transfer
TEMP_B = -0.075
# deltaT: Temperature difference between cell and module back surface
# Typical value of 3°C for glass-back modules
TEMP_DELTA_T = 3

PVLIB_BASE_PARAMETERS = {
    'module_parameters': {'pdc0': PDC0, 'gamma_pdc': GAMMA_PDC},
    'temperature_model_parameters': {'a': TEMP_A, 'b': TEMP_B, 'deltaT': TEMP_DELTA_T}
}



def get_solar_ac_dataframe(latitude: float, longitude: float, system_type='single-axis', surface_tilt=20, surface_azimuth=180):
    """
    Calculate the AC output of a PV system based on location and system type.

    Parameters:
    - latitude (float): Latitude of the location
    - longitude (float): Longitude of the location
    - system_type (str): Type of mounting system ('fixed-tilt' or 'single-axis')
    - surface_tilt (float): Tilt angle of the panels in degrees from horizontal (default: 20)
                           Only used for fixed-tilt systems
    - surface_azimuth (float): Azimuth angle of the panels in degrees clockwise from north
                              (default: 180, which is facing south in northern hemisphere)
                              Only used for fixed-tilt systems

    Returns:
    - ac (pd.DataFrame): Dataframe containing the AC output of the PV system

    Raises:
    - ValueError: If an invalid system_type is provided
    """
    start_time = time.time()
    logger.info(f"Starting solar AC calculation for {latitude}, {longitude} with {system_type} system")

    # Create the appropriate mount and array based on system type
    mount_start = time.time()
    if system_type.lower() == 'fixed-tilt':
        mount = pvsystem.FixedMount(
            surface_tilt=surface_tilt,
            surface_azimuth=surface_azimuth
        )
    elif system_type.lower() == 'single-axis':
        mount = pvsystem.SingleAxisTrackerMount()
    else:
        raise ValueError("System_type must be either 'fixed-tilt' or 'single-axis'")
    logger.info(f"Mount creation took {(time.time() - mount_start)*1000:.1f} ms")

    # Create array and location
    array_start = time.time()
    array = pvsystem.Array(mount, **PVLIB_BASE_PARAMETERS)
    loc = location.Location(latitude, longitude)
    logger.info(f"Array and location creation took {(time.time() - array_start)*1000:.1f} ms")

    # Define the PV system
    system_start = time.time()
    system = pvsystem.PVSystem(
        arrays=[array],
        inverter_parameters=dict(pdc0=PDC0)  # Normalized inverter rating
    )
    logger.info(f"PV system creation took {(time.time() - system_start)*1000:.1f} ms")

    # Create the model chain
    chain_start = time.time()
    mc = modelchain.ModelChain(
        system,
        loc,
        aoi_model='physical',  # Use physical model for angle of incidence
        spectral_model='no_loss'  # Ignore spectral losses for simplicity
    )
    logger.info(f"Model chain creation took {(time.time() - chain_start)*1000:.1f} ms")

    # Fetch weather data
    weather_start = time.time()
    weather = iotools.get_pvgis_tmy(latitude, longitude)[0]
    logger.info(f"Weather data fetch took {(time.time() - weather_start)*1000:.1f} ms")

    # Run the model
    model_start = time.time()
    mc.run_model(weather)
    logger.info(f"Model run took {(time.time() - model_start)*1000:.1f} ms")

    total_time = time.time() - start_time
    logger.info(f"Total solar AC calculation took {total_time*1000:.1f} ms")

    return mc.results.ac


def simulate_battery_operation(df, battery_capacity_mwh, initial_battery_charge, generator_capacity, load, op_year):
    """
    Simulate the charging/discharging of the battery, calculate system performance.
    """
    battery_max_rate = battery_capacity_mwh / BATT_DURATION_HOURS
    battery_capacity_mwh = battery_capacity_mwh * (1 - BATT_DEGRADATION_PER_YEAR * (op_year - 1))
    battery_storage = initial_battery_charge
    curtailed_solar = []
    unmet_load = []
    battery_storage_list = []
    battery_charge_list = []
    battery_discharge_list = []
    generator_output_list = []

    # Loop through the dataset and simulate battery operation
    # This has to be a loop, not vectorised, because the battery state at each step depends on the past
    for i, row in df.iterrows():
        scaled_gen = row['scaled_solar_generation_mw']

        # Calculate excess power and deficit
        if scaled_gen > load:
            excess_power = scaled_gen - load
            available_storage = battery_capacity_mwh - battery_storage
            stored_energy = min(min(excess_power, battery_max_rate), available_storage)
            curtailed = excess_power - stored_energy
            battery_storage += stored_energy * BATT_ROUND_TRIP_EFFICIENCY ** 0.5
            unmet = 0
            discharge = 0
            generator_output = 0
        else:
            deficit = load - scaled_gen
            withdrawal = min(battery_max_rate, min(deficit / BATT_ROUND_TRIP_EFFICIENCY ** 0.5, battery_storage))
            battery_storage -= withdrawal
            discharge = withdrawal * BATT_ROUND_TRIP_EFFICIENCY ** 0.5
            deficit = deficit - discharge
            generator_output = min(deficit, generator_capacity)
            unmet = deficit - generator_output
            stored_energy = 0
            curtailed = 0

        # Record the results
        curtailed_solar.append(curtailed)
        unmet_load.append(unmet)
        battery_storage_list.append(battery_storage)
        battery_charge_list.append(stored_energy)
        battery_discharge_list.append(discharge)
        generator_output_list.append(generator_output)

    # Add columns to dataframe
    df['battery_storage'] = battery_storage_list
    df['battery_charge'] = battery_charge_list
    df['battery_discharge'] = battery_discharge_list
    df['curtailed_solar_mwh'] = curtailed_solar
    df['generator_output_mwh'] = generator_output_list
    df['unmet_load'] = unmet_load
    df['load_unmet'] = df['unmet_load'] > 0
    
    return df

def scale_solar_generation(df, installed_capacity, op_year):
    """
    Scale the solar generation in each year based on degradation.
    """
    df['scaled_solar_generation_mw'] = df['p_mp'] * (installed_capacity / DC_AC_RATIO) * (1 - SOLAR_DEGRADATION_PER_YEAR * (op_year - 1))
    return df

def simulate_system(latitude: float, longitude: float, solar_capacity: float, battery_power: float, generator_capacity: float):
    """
    Simulate the system for a single configuration over its lifetime.

    Parameters:
    - latitude (float): Latitude of the location.
    - longitude (float): Longitude of the location.
    - solar_capacity (float): Solar capacity in MW-DC
    - battery_power (float): Battery power capacity in MW.
    - generator_capacity (float): Generator capacity in MW.

    Returns:
    - pl.DataFrame: A Polars DataFrame containing the system performance for each year.
    """
    logger.info(f"Starting simulation for lat={latitude}, lon={longitude}, solar={solar_capacity} MW, "
                f"battery={battery_power} MW/{battery_power * BATT_DURATION_HOURS} MWh, generator={generator_capacity} MW")

    # Calculate battery energy from power
    battery_energy = battery_power * BATT_DURATION_HOURS

    # Get solar AC output data
    solar_ac_generation_df = (get_solar_ac_dataframe(latitude, longitude, system_type='single-axis')
                             .reset_index()
                             .rename(columns={'index': 'time(UTC)', 'value': 'p_mp'}))
    solar_ac_generation_df['time(UTC)'] = pd.to_datetime(solar_ac_generation_df['time(UTC)'])

    results = []
    for op_year in range(1, SYSTEM_LIFETIME_YEARS + 1):
        logger.info(f"Simulating year {op_year} of {SYSTEM_LIFETIME_YEARS}")

        # Scale solar generation for the current year to account for degradation
        scaled_df = scale_solar_generation(solar_ac_generation_df.copy(), solar_capacity, op_year)

        # Set initial battery charge (0 in the final year, otherwise full capacity)
        initial_battery_charge = 0 if op_year == SYSTEM_LIFETIME_YEARS else battery_energy

        # Simulate battery operation
        result_df = simulate_battery_operation(scaled_df, battery_energy, initial_battery_charge, generator_capacity, DATA_CENTER_LOAD_MW, op_year)

        # Calculate annual energy metrics (all in MWh)
        # annual_metrics = {
        #     'total_load_mwh': DATA_CENTER_LOAD_MW * 8760,  # Constant load × hours in year
        #     'unmet_load': result_df['unmet_load'].sum(),
        #     'raw_solar_mwh': result_df['scaled_solar_generation_mw'].sum(),
        #     'battery_charge': result_df['battery_charge'].sum(),
        #     'battery_discharge': result_df['battery_discharge'].sum(),
        #     'generator_output_mwh': result_df['generator_output_mwh'].sum(),
        #     'curtailed_solar_mwh': result_df['curtailed_solar_mwh'].sum()
        # }

        # Calculate performance metrics
        # performance = (annual_metrics['total_load_mwh'] - annual_metrics['unmet_load']) * 100 / annual_metrics['total_load_mwh']
        # curtailment_share = (annual_metrics['curtailed_solar_mwh'] * 100 / annual_metrics['raw_solar_mwh']) if annual_metrics['raw_solar_mwh'] > 0 else 0
        # generator_share = annual_metrics['generator_output_mwh'] * 100 / annual_metrics['total_load_mwh']

        solar_mwh_raw_tot = result_df['scaled_solar_generation_mw'].sum()
        solar_mwh_curtailed_tot = result_df['curtailed_solar_mwh'].sum()
        # Append results for the current year
        results.append({
            'system_spec': f"{int(solar_capacity)}MW | {int(battery_power)}MW | {int(generator_capacity)}MW",
            'operating_year': op_year,
            'Solar Output - Raw (MWh)': round(solar_mwh_raw_tot),
            'Solar Output - Curtailed (MWh)': round(solar_mwh_curtailed_tot),
            'Solar Output - Net (MWh)': round(solar_mwh_raw_tot - solar_mwh_curtailed_tot),
            'BESS charged (MWh)': round(result_df['battery_charge'].sum()),
            'BESS discharged (MWh)': round(result_df['battery_discharge'].sum()),
            'Generator Output (MWh)': round(result_df['generator_output_mwh'].sum()),
            'Generator Fuel Input (MMBtu)': round(result_df['generator_output_mwh'].sum() * GENERATOR_HEATRATE / 1000),
            # This method of calculating load served produces sliiightly different results to the original,
            # but I think this may be more correct.
            'Load Served (MWh)': round(DATA_CENTER_LOAD_MW * 8760 - result_df['unmet_load'].sum())
        })

    # Convert results to a Polars DataFrame
    results_df = pl.DataFrame(results)
    logger.info("Simulation completed successfully")
    return results_df

# Example usage
if __name__ == "__main__":
    latitude = 31.9  # El Paso, TX
    longitude = -106.2
    solar_capacity = 250  # MW-dc
    battery_power = 50  # MW
    generator_capacity = 0  # MW

    results = simulate_system(latitude, longitude, solar_capacity, battery_power, generator_capacity)
    results.write_csv('output_20_yrs.csv')
    print(results)

