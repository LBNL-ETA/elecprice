# fetch CAISO LMP data from OASIS (see "Interface Specification for OASIS API)

import datetime
import pytz
import requests
import pandas as pd
from zipfile import ZipFile

# fn_name(start_date, end_date, node_list, tz_name)
# output: a pandas DataFrame, 2 columns per node, one for RTP and one for DAM
def get_CAISO_as(start_date=datetime.date(2019, 1, 1), 
                  end_date=datetime.date(2019, 1, 2), 
                  market_run_id='DAM', 
                  nodes=['DLAP_PGAE-APND'],
                  tz_name='UTC', 
                  raw_dir = '.'):

    # DEFAULT TIME ZONE: UTC, use pytz
    # 
    #  this function simply grabs the csv data from caiso and dumps it into a data frame with the same structure as the csv.
    # `startdate` and `enddate` have format yyyymmdd (strings). This function doesn't work for very old data. Known to be OK for 2017.
    # `market_run_id` is either "DAM" or "RTM" for day ahead or real time markets
    # `nodes` is a list of APNODES to get. The default options correspond to the PGE, SCE, and SDGE DLAP (aggregated pricing nodes)
    # `raw_dir` is a location to store unzipped .csv files. There is currently no option to automatically delete these. 

    if not isinstance(nodes, list):
        nodes = [nodes]

    dataframe = None
    for node in nodes:
        url = get_api_url(start_date, end_date, market_run_id, node, tz_name)

        filename = download_and_extract_csv(url)

        df = pd.read_csv(filename)

# Return the filename of the extracted csv file
def download_and_extract_csv(url):
    print("Getting url: ", url)
    caiso_data = requests.get(url, stream=False)

    filename = caiso_data.headers['Content-Disposition'][17:-1]
    print("Downloaded filename: ", filename)
    with open(filename, 'wb') as f:
        f.write(caiso_data.content)

    with ZipFile(filename, 'r') as zipObj:
        file_csv = zipObj.namelist()[0]
        print("Downloaded csv filename: ", file_csv)
        zipObj.extract(file_csv)

    return file_csv
    

def get_api_url(start_date, end_date, market_run_id, node, tz_name):
    #define base URL
    baseURL = 'http://oasis.caiso.com/oasisapi/SingleZip?'

    if market_run_id == 'RTM':
      market_query = 'queryname=PRC_INTVL_LMP&resultformat=6&version=1&market_run_id=RTM'

    if market_run_id == 'DAM':
      market_query = 'queryname=PRC_LMP&resultformat=6&version=1&market_run_id=DAM'

    try:
      timezone = pytz.timezone(tz_name)
    except:
      timezone = pytz.utc

    duration = end_date - start_date

    if duration.days > 31 or duration.days < 1:
      print("ERROR: duration must be at least 1 day and at most 31 days")
      return

    start_date = start_date.strftime("%Y%m%d") + "T08:00-0000"
    end_date = end_date.strftime("%Y%m%d") + "T08:00-0000"

    datetime_query = "&startdatetime=" + start_date + "&enddatetime=" + end_date
    node_query = "&node=" + node

    url = baseURL + market_query + datetime_query + node_query

    return url

# get_CAISO_as()