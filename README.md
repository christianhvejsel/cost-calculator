# Introduction
This is a cost calculator for a datacenter powered by wind, solar, batteries, and gas generation.

It can simulate a datacenter of any load anywhere in the world, with any combination of wind, solar, battery, and gas generation. The output is a Levelized Cost of Energy (LCOE) in $/MWh, and a yearly financial model.
 
The code calculates the LCOE using the following steps:
1. It pulls weather data for the speciifed `(lat, long)`
2. It simulates the wind and solar power from the weather data
3. It simulates the powerflow of the system between the wind, solar, battery, generator, and datacenter.
4. It calculates the annual cashflows and the LCOE of the system.

# Usage
There are three ways to use this code:

## 1. Streamlit interface
`streamlit run app.py`


## 2. Command line interface
#### One-shot LCOE calculation
This simulates a single case.
```bash
python calculate_lcoe_one_shot.py --lat 31.9 --long -106.2 --wind-mw 150 --solar-mw 250 --bess-mw 100 --generator-mw 125 --datacenter-load-mw 100
```

(See `calculate_lcoe_one_shot.py` for all possible args)

#### LCOE Ensemble Calculation
This simulates a range of cases and saves the results to a CSV file.
The "raw results" for every case are saved as a CSV, as well as the Pareto-optimal frontier on LCOE vs renewable-percentage. 
```bash
python run_ensemble.py
```
You can define the test cases in `run_ensemble.py`.

## 3. Python
```python
"""There are three steps to calculate the LCOE:
1. Get wind and solar weather data
2. Simulate powerflow
3. Calculate LCOE
"""

# 1. Get wind solar weather data
solar_ac_dataframe = get_solar_ac_dataframe(lat, long)
#ToDo wind_ac_dataframe = get_wind_ac_dataframe(lat, long)

# 2. Simulate powerflow
powerflow_results = simulate_system(lat, long, solar_ac_dataframe, wind_ac_dataframe ...)

# 3. Create DataCenter instance and calculate LCOE
datacenter = DataCenter(
    powerflow_results=powerflow_results,
    wind=100,
    solar=100, 
    bess=100, 
    generator=125, 
    generator_type="Gas Engine",
    # CAPEX rates
    wind_solar_capex_total_dollar_per_w = 0.45,
    solar_capex_total_dollar_per_w=0.25,
    bess_capex_total_dollar_per_kwh=0.10,
    # O&M rates
    wind_om_fixed_dollar_per_kw=0.035,
    solar_om_fixed_dollar_per_kw=0.01,
    bess_om_fixed_dollar_per_kw=0.01,
    ... # See `datacenter.py` for all options and defaults
)

lcoe = datacenter.calculate_lcoe()
```

## Authors

* [Ben James](https://github.com/bengineer19)
