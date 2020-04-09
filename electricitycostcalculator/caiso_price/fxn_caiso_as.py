# fetch CAISO LMP data from OASIS (see "Interface Specification for OASIS API)

import datetime
import time
import pytz
import requests
import pandas as pd
import os
from zipfile import ZipFile

# Return Pandas dataframe with end time, nodes, and LMP price aggregration
# NODES could be single string or a list.
def get_caiso_price(start_date=datetime.datetime(2019, 1, 1, 8, 0, 0),
                     end_date=datetime.datetime(2019, 1, 2, 8, 0, 0),
                     market_run_id='RTM', 
                     nodes=['DLAP_PGAE-APND', 'DLAP_SCE-APND'],
                     tz_name='UTC'):

    if not isinstance(nodes, list):
        nodes = [nodes]

    dataframes = None
    for node in nodes:
        df = get_CAISO_lmp(start_date, end_date, market_run_id, node, tz_name)
        if dataframes is not None:
            dataframes = dataframes.append(df)
        else:
            dataframes = df

    dataframes = dataframes[['INTERVALENDTIME_GMT', 'XML_DATA_ITEM', 'PNODE_RESMRID', 'MW']]

    summary_filename = "caiso_LMP_" + str(start_date.year) + "_" + market_run_id + "_" + nodes[0][:4] \
                              + "_interval_ending_summary.csv"
    
    summary_df = pd.pivot_table(dataframes, values='MW', index=['INTERVALENDTIME_GMT', 'PNODE_RESMRID'], columns='XML_DATA_ITEM', aggfunc=sum)
    summary_df.to_csv(summary_filename)

    return summary_df

# Return Pandas dataframe of CAISO data according to the parameters.
def get_CAISO_lmp(start_date=datetime.datetime(2019, 1, 1, 8, 0, 0),
                  end_date=datetime.datetime(2019, 1, 2, 8, 0, 0),
                  market_run_id='DAM', 
                  node='DLAP_SCE-APND',
                  tz_name='UTC'):

    url = get_api_url(start_date, end_date, market_run_id, node, tz_name)

    start = start_date.strftime("%Y%m%d")
    end = end_date.strftime("%Y%m%d")

    filename = "caiso_lmp_node_" + node + "_" + market_run_id + "_" + start + "_" + end + ".csv"
    old_filename = download_and_extract_csv(url)
    os.rename(old_filename, filename)
    
    time.sleep(5)

    return pd.read_csv(filename)

# Download ZIP from URL and extract the CSV file, return the CSV file name.
def download_and_extract_csv(url):
    print("Getting url: ", url)
    caiso_data = requests.get(url, stream=False)

    filename = caiso_data.headers['Content-Disposition'][17:-1]
    print("Downloaded zip: ", filename)
    with open(filename, 'wb') as f:
        f.write(caiso_data.content)

    with ZipFile(filename, 'r') as zipObj:
        file_csv = zipObj.namelist()[0]
        print("Downloaded csv: ", file_csv, "\n")
        zipObj.extract(file_csv)

    return file_csv

# Return CAISO API URL according to the parameters.
def get_api_url(start_date, end_date, market_run_id, node, tz_name):
    #define base URL
    baseURL = 'http://oasis.caiso.com/oasisapi/SingleZip?'
    duration = end_date - start_date

    if duration.days > 31 or duration.days < 1:
        print("ERROR: duration must be at least 1 day and at most 31 days")
        return

    if market_run_id == 'RTM':
        market_query = 'queryname=PRC_INTVL_LMP&resultformat=6&version=1&market_run_id=RTM'

    if market_run_id == 'DAM':
        market_query = 'queryname=PRC_LMP&resultformat=6&version=1&market_run_id=DAM'

    timezone = pytz.timezone(tz_name)

    # Set timezone
    start_date = timezone.localize(start_date)
    end_date = timezone.localize(end_date)

    # Convert date to the desired timezone
    utc_start_date = start_date.astimezone(pytz.utc)
    utc_end_date = end_date.astimezone(pytz.utc)

    utc_start_date = utc_start_date.strftime("%Y%m%dT%H:%M-0000")
    utc_end_date = utc_end_date.strftime("%Y%m%dT%H:%M-0000")

    datetime_query = "&startdatetime=" + utc_start_date + "&enddatetime=" + utc_end_date
    node_query = "&node=" + node

    url = baseURL + market_query + datetime_query + node_query

    return url