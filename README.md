There are three ways to use:

## 1. Command line interface
```bash
python calculate_lcoe.py --location "El Paso, TX" --solar 100 --bess 100 --generator 125 --generator-type "Gas Engine"
```

(See `calculate_lcoe.py` for all options)

## 2. Streamlit interface
`streamlit run app.py`

## 3. Python
```python
from calculations import DataCenter

datacenter = DataCenter(
    location="El Paso, TX", 
    solar=100, 
    bess=100, 
    generator=125, 
    generator_type="Gas Engine",
    # CAPEX rates
    solar_capex_total_dollar_per_w=0.25,
    bess_capex_total_dollar_per_kwh=0.10,
    generator_capex_total_dollar_per_kw=0.15,
    system_integration_capex_total_dollar_per_kw=0.05,
    soft_costs_capex_total_pct=0.05,
    # O&M rates
    solar_om_fixed_dollar_per_kw=0.01,
    bess_om_fixed_dollar_per_kw=0.01,
    generator_om_fixed_dollar_per_kw=0.01,
    generator_om_variable_dollar_per_kwh=0.01,
    ... # See `calculations.py` for all options and defaults
)
lcoe = datacenter.calculate_lcoe()
```

