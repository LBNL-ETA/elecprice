# The Electricity Rate library

This library is a generic tool for manipulating the tariffs of electricity, with a emphasis on commercial Time-Of-Use (TOU) rates in US.  Typical uses of the package are:

1)  **Price signal generation**: from a specific tariff and a given time window, the tool creates a pandas dataframes containing the various components of the electricity charges, at each time step. This is particularly useful for Demand Response (DR) applications, such as price-based optimization of energy in buildings.

2)  **Bill computation**: from a pandas dataframe of power consumption and a specific tariff, the tool returns the corresponding cost of electricity, as well as a breakdown per type of rate.  

The library relies on [OpenEI](https://openei.org/apps/USURDB/) data structures and APIs. Most electricity tariffs in the US are made of various types of charges and credits, that fall into one of the following rate type:

- FIXED: a fixed charge, generally expressed in $/day or $/month.
- ENERGY: a charge per energy consumption, generally expressed in $/kWh. This charge may vary during the day, and may be different for each month.
- DEMAND: a charge per demand, generally expressed in $/kW. The demand is defined as the maximum of the power consumption average over 15 minutes, taken over the whole billing period (or daily in some cases). The demand may also be applied to specific hours of the day, in a cumulative way.

## Installation instructions

The installation can be done through _pip_ by typing:

`pip install electricitycostcalculator`

The project (in Python3) relies on the following libraries: pandas, pytz, requests, lxml, holidays

## How to use the package

In the `example/` folder, the `openei_test.py` script drives you through typical uses of the package, namely the generation of price signals and the computation of electricity bills. Both use cases require the creation of two objects: an instance of `ElectricityRateManager`, the main object that will be handled, and an instance of `OpenEI_tariff`, the object describing the raw structure of the tariff.

### Objects initialization

Instantiating the `ElectricityRateManager` object does not require any parameter:

```python
from electricitycostcalculator.electricity_rate_manager.rate_manager import ElectricityRateManager

elec_rate_handler = ElectricityRateManager()
```

Next, the object `elec_rate_handler`needs to be filled in with structured data related to the electricity tariff it represents. To this end, one needs to instanciate the `OpenEI_tariff`with OpenEI fields that will be directly used for a subsequent Web API call:

```python
from electricitycostcalculator.openei_tariff.openei_tariff_analyzer import *

tariff_data = OpenEI_tariff(
	 utility_id='14328',  
	 sector='Commercial',  
	 tariff_rate_of_interest='A-6', 
	 distrib_level_of_interest="Secondary", 
	 tou=True)
  
tariff_data.call_api()
```

In this example, tariff corresponding to commercial TOU program 'A-6' of PG&E (id '14328') at the secondary level should be retrieved. More information about the possible parameters can be found in the `OpenEI_tariff` class definition.

The raw data contained in the `tariff_data`can now be binded to `elec_rate_handler`:
```python
tariff_struct_from_openei_data(tariff_data, elec_rate_handler)
```

### Generate prices signals

Prices of electricity are made of fixed, energy, and demand rates. Getting a timeseries version of them in a given time window can be done in the following way:

```python
timestep = TariffElemPeriod.QUARTERLY
time_range = (start_date, end_date)
price_elec, map_columns = elec_rate_handler.get_electricity_price(time_range, timestep)
```
where `timestep`is 15 minutes, `start_date` and `end_date` are `datetime`instances, `price_elec`is a `pandas` dataframe containing the timeseries data, and `map_columns` is a dictionnary mapping the columns of `price_elec` to a type of rate.

### Electricity bill computation

Computing the electricity bill given power consumption data (kW) can be done by calling the `compute_bill`method:

```python
bill = elec_rate_handler.compute_bill(data_meter)
```

where `data_meter` is a pandas dataframe containing the power data over the billing period and `bill`is a dictionnary mapping each type of rate to the corresponding cost. In order to manipulate the `bill`object, the method`print_aggregated_bill()` allows for a breakdown of the bill:

```python
total_cost, cost_per_rate, cost_detailed = elec_rate_handler.print_aggregated_bill(bill)
```

## Reading local (revised) tariffs

Data from OpenEI might not be up to date or might even be missing for a given tariff. In this case, the library offer an alternative to `call_api()`by reading a local file that follows the same structure as data from OpenEI API:

```python
if tariff_data.read_from_json(filename="tariff_revised/a_revised_tariff.json") == 0:
	print("Tariff read from JSON successful")
else:
	print("An error occurred when reading the JSON file")
```
## Handling PDP events

 Peak Day Pricing is a popular program in the US for increasing the energy prices at specific days throughout the year, while compensating the subscriber with a credit on energy/demand charges. The list of PDP days can be provided at the object instantiation:
 
```python
tariff_struct_from_openei_data(tariff_data, elec_rate_handler, pdp_events_path="path/to/pdp_events.json")
```

And updated as days go by:

```python
update_pdp_json(openei_tarif, pdp_dict, pdp_events_path):
```

## Package limitation and future work

-   The code has only been tested for Commercial building. The tiers in energy tariff that can be encountered at the residential level are not supported.
-   The tool doesn't take into account the reactive power cost (power factor adaptation or price per kVARh)
-   The credits for the non-PDP event are applied even on the PDP event days. As the effect is neglectable for the price of energy, it might impact the demand cost. However, the user can read the demand credit days in the bill details and decide to apply it or not.