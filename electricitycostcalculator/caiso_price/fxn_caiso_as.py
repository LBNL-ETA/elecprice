# fetch CAISO LMP data from OASIS (see "Interface Specification for OASIS API)

import datetime
import pytz
import requests

# fn_name(start_date, end_date, node_list, tz_name)
# output: a pandas DataFrame, 2 columns per node, one for RTP and one for DAM
def get_CAISO_as(start_date=datetime.date.today(), 
                  end_date=datetime.date.today(), 
                  market_run_id='DAM', 
                  nodes=['DLAP_PGAE-APND', 'DLAP_SCE-APND', 'DLAP_SDGE-APND'],
                  tz_name='UTC', 
                  raw_dir = '.'): 

# DEFAULT TIME ZONE: UTC, use pytz
  # 
  #  this function simply grabs the csv data from caiso and dumps it into a data frame with the same structure as the csv.
  # `startdate` and `enddate` have format yyyymmdd (strings). This function doesn't work for very old data. Known to be OK for 2017.
  # `market_run_id` is either "DAM" or "RTM" for day ahead or real time markets
  # `nodes` is a list of APNODES to get. The default options correspond to the PGE, SCE, and SDGE DLAP (aggregated pricing nodes)
  # `raw_dir` is a location to store unzipped .csv files. There is currently no option to automatically delete these. 
  
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

  start_date = start_date.strftime("%Y%m%d") + "T08:00-0000"
  end_date = end_date.strftime("%Y%m%d") + "T08:00-0000"

  datetime_query = "&startdatetime=" + start_date + "&enddatetim=" + end_date

  for node in nodes:
    node_query = "&node=" + node
    url = baseURL + market_query + datetime_query + node_query

    caiso_data = requests.get(url)
   
  
  # for(i in 1:nrow(get_options)){
    
  # getURL <- paste0(get_options[i,base], get_options[i,market], get_options[i,date], get_options[i,node])
    
  
  # temp <- tempfile() #create temp file
  # try(download.file(getURL,temp)) # get data into temp
  # try(newdata <- read.csv(unzip(temp, exdir = raw_dir))) # unzip and read csv, dump into data
  # unlink(temp)
  
  # if(i == 1){data <- newdata}
  # if(i > 1){ try(data <- rbind(data,newdata))}#append new data to existing
  
  #   Sys.sleep(5.1) # wait 5.1 seconds so CAISO doesn't send HTTP error
  # }
 
  # return(as.data.table(data))
# }
    
