from electricitycostcalculator.electricity_rate_manager.rate_manager import ElectricityRateManager
from electricitycostcalculator.openei_tariff.openei_tariff_analyzer import *
import pandas as pd
import time

if __name__ == '__main__':

    #
    ###
    ##### TEST OF OPENEI
    ###
    #

    tariff_openei_data = OpenEI_tariff(utility_id='14328',
                                       sector='Commercial',
                                       tariff_rate_of_interest='B-19 Medium General Demand TOU (Secondary)',
                                       distrib_level_of_interest=None,
                                       # it is at the secondary level, so not specified in the name
                                       phasewing=None,
                                       # the word 'Poly' is to be excluded, because the names may omit this info ..
                                       tou=True,
                                       option_exclusion=['R'])  # Need to reject the option X and W

    tariff_openei_data.call_api()

    elec_rate_handler = ElectricityRateManager()

    tariff_struct_from_openei_data(tariff_openei_data, elec_rate_handler)

    start_date = datetime(2019, 7, 30, hour=0, minute=0, second=0)
    end_date = datetime(2019, 7, 30, hour=23, minute=59, second=59)


    time_start = time.time()
    price_elec, map = elec_rate_handler.get_electricity_price((start_date, end_date), TariffElemPeriod.QUARTERLY)

    print(time.time() - time_start)

    #print(price_elec)

    #
    ###
    ##### TEST OF READING DATA FROM JSON - B-19 Option S
    ###
    #

    tariff_b19s = OpenEI_tariff(utility_id='14328',
                                       sector='Commercial',
                                       tariff_rate_of_interest='B-19 S',
                                       distrib_level_of_interest=None)  # Need to reject the option X and W

    tariff_b19s.read_from_json(filename="/home/olivier/development/electricitycostcalculator/example/tariff_revised/u14328_Commercial_B19S_revised.json")


    elec_rateB19S_handler = ElectricityRateManager()

    tariff_struct_from_openei_data(tariff_b19s, elec_rateB19S_handler)

    start_date = datetime(2020, 7, 30, hour=0, minute=0, second=0)
    end_date = datetime(2020, 7, 30, hour=23, minute=59, second=59)


    time_start = time.time()
    price_elec, map = elec_rateB19S_handler.get_electricity_price((start_date, end_date), TariffElemPeriod.QUARTERLY)

    print(time.time() - time_start)
    print(price_elec)
