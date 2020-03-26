__author__ = 'Olivier Van Cutsem'

from electricitycostcalculator.electricity_rate_manager.rate_manager import ElectricityRateManager
from electricitycostcalculator.openei_tariff.openei_tariff_analyzer import *
import pandas as pd

# ----------- TEST DEMO -------------- #
READ_FROM_JSON = False

# useful functions
def utc_to_local(data, local_zone="America/Los_Angeles"):
    '''
    This method takes in pandas DataFrame and adjusts index according to timezone in which is requested by user
    '''

    data = data.tz_convert(local_zone)  # accounts for localtime shift
    # Gets rid of extra offset information so can compare with csv data
    data = data.tz_localize(None)

    return data

if __name__ == '__main__':

    meter_uuid = 'e9c51ce5-4aa1-399c-8172-92073e273a0b'

    #
    ### Reading power consumption data
    #

    print("--- Loading meter data ...")
    df = pd.read_csv('meter.csv', index_col=0)  # import times series energy data for meters
    df.index.name = 'Time'
    df = df.set_index(pd.to_datetime(df.index, infer_datetime_format=True, utc=True))
    df["date"] = df.index

    data_meter = df[meter_uuid]
    data_meter = utc_to_local(data_meter, local_zone="America/Los_Angeles")

    #
    ### Reading OpenEI-based tariff rates, and binding it to the ElectricityRateManager
    #

    print("--- Calling OpenEI API ...")

    # (a) Example of using the OpenEI WEB API

    tariff_openei_apidata = OpenEI_tariff(utility_id='14328',
                                       sector='Commercial',
                                       tariff_rate_of_interest='E-19',
                                       distrib_level_of_interest=None,
                                       # it is at the secondary level, so not specified in the name
                                       phasewing=None,
                                       # the word 'Poly' is to be excluded, because the names may omit this info ..
                                       tou=True,
                                       option_exclusion=['(X)', '(W)', 'Poly'])  # Need to reject the option X and W

    tariff_openei_apidata.call_api(store_as_json=True)

    # (b) Example of reading local data, encoded according to OpenEI structure


    elecrate_manager = ElectricityRateManager()

    # Binding an instance of ElectricityRateManager to a specific OpenEI tariff

    tariff_struct_from_openei_data(tariff_openei_apidata, elecrate_manager)  # This analyses the raw data from the openEI request and populate the "CostCalculator" object

    # BILLING PERIOD
    start_date_bill = datetime(2017, 7, 1, hour=0, minute=0, second=0)
    end_date_bill = datetime(2017, 7, 30, hour=23, minute=59, second=59)
    mask = (data_meter.index >= start_date_bill) & (data_meter.index <= end_date_bill)
    data_meter = data_meter.loc[mask]
    data_meter = data_meter.fillna(0)

    # 1) Get the bill over the period

    print("Calculating the bill for the period {0} to {1}".format(start_date_bill, end_date_bill))
    bill = elecrate_manager.compute_bill(data_meter, monthly_detailed=True)
    t, tt, ttt = elecrate_manager.print_aggregated_bill(bill)
    print(t)

    # 2) Get the electricity price per type of metric, for a specific period

    tariff_openei_jsondata = OpenEI_tariff(utility_id='14328', sector='Commercial', tariff_rate_of_interest='B-19S')

    if tariff_openei_jsondata.read_from_json(filename="tariff_revised/u14328_Commercial_B19S_revised.json") == 0:
        print("Tariff read from JSON successful")
    else:
        print("An error occurred when reading the JSON file")
        exit()

    elecrate_manager = ElectricityRateManager()

    tariff_struct_from_openei_data(tariff_openei_jsondata, elecrate_manager)  # This analyses the raw data from the openEI request and populate the "CostCalculator" object


    start_date_sig= datetime(2020, 1, 1, hour=0, minute=0, second=0)
    end_date_sig = datetime(2020, 1, 7, hour=23, minute=59, second=59)
    timestep = TariffElemPeriod.QUARTERLY  # We want a 1h period

    price_elec, map = elecrate_manager.get_electricity_price((start_date_sig, end_date_sig), timestep)

    print(price_elec)
