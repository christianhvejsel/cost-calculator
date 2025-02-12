There are three ways to use:

## 1. Command line interface
```bash
python calculate_lcoe_one_shot.py --lat 31.9 --long -106.2 --solar-mw 250 --bess-mw 650 --generator-mw 125 --datacenter-load-mw 100
```

(See `calculate_lcoe_one_shot.py` for all possible args)

## 2. Streamlit interface
`streamlit run app.py`

## 3. Python
```python
# Get solar weather data
solar_ac_dataframe = get_solar_ac_dataframe(lat, long)

# Simulate powerflow
powerflow_results = simulate_system(lat, long, solar_ac_dataframe, ...)

# Create DataCenter instance and calculate LCOE
datacenter = DataCenter(
    powerflow_results=powerflow_results,
    solar=100, 
    bess=100, 
    generator=125, 
    generator_type="Gas Engine",
    # CAPEX rates
    solar_capex_total_dollar_per_w=0.25,
    bess_capex_total_dollar_per_kwh=0.10,
    # O&M rates
    solar_om_fixed_dollar_per_kw=0.01,
    bess_om_fixed_dollar_per_kw=0.01,
    ... # See `calculations.py` for all options and defaults
)

lcoe = datacenter.calculate_lcoe()
```

