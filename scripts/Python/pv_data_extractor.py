import urllib
import requests
import pandas as pd
import datetime
from datetime import timedelta
from datetime import datetime
import json

URL = 'https://st-dev-data-api.azurewebsites.net'
invertersURL = urllib.parse.urljoin(URL, '/api/v0.1/buildings/energyville1/pv/roof/inverters/')
powerURL = urllib.parse.urljoin(URL, '/api/v0.1/buildings/energyville1/pv/roof/power/')
user = 'eric_massip'
pswd = 'ssCpoDC3uHF4ssHJtvMf'

DATE_FORMAT_STR = "%Y-%m-%d"

start_time = datetime(2017, 12, 1)
end_time = datetime(2017, 12, 16)


def get_inverter_ids():
    inverter_ids_json_response = json.loads(requests.get(invertersURL, auth=(user, pswd)).text)['data']
    inverter_ids = []
    for i in range(len(inverter_ids_json_response)):
        inverter_ids.append(inverter_ids_json_response[i]['InverterId'])
    return inverter_ids


def get_params(inverter_id, start, end):
    return {'start': start.strftime(DATE_FORMAT_STR),
            'end': end.strftime(DATE_FORMAT_STR),
            'time_zone': 'Central European Standard Time',
            'inverter_ids': inverter_id}


def get_power_consumption(inverter_id, start, end):
    return json.loads(requests.get(powerURL, params=get_params(inverter_id, start, end), auth=(user, pswd)).text)['data']


def get_power_consumptions(start, end):
    return [get_power_consumption(inverter_id, start, end) for inverter_id in get_inverter_ids()]


power_consumptions = get_power_consumptions(start_time, end_time)


def get_time_dictionary_every_5min(start_time, end_time):
    timedelta_5 = timedelta(minutes=5)
    
    dates = []
    date = start_time
    while date != end_time:
        dates.append(date)
        date = date + timedelta_5
        
    return dates


dates = get_time_dictionary_every_5min(start_time, end_time)


def get_total_power_consumption():
    total_power_consumption = []
    for date_to_be_checked in dates:
        date_to_be_checked_str = date_to_be_checked.strftime("%Y-%m-%d %H:%M:%S")
        power_sum = 0
        for inverter_consumption in power_consumptions:
            for i in range(len(inverter_consumption)):
                this_inverter_consumption = inverter_consumption[i]
                log_generation_power = this_inverter_consumption['GenerationPower']
                if log_generation_power != 0:
                    log_datetime = datetime.fromisoformat(this_inverter_consumption['DateTimeMeasurement']).strftime("%Y-%m-%d %H:%M:%S")
                    if log_datetime == date_to_be_checked_str:
                        if log_generation_power != 0:
                            power_sum += log_generation_power
        print(date_to_be_checked_str)
        total_power_consumption.append({'date': date_to_be_checked_str, 'power_sum': power_sum})
    return total_power_consumption


total_power_consumption = get_total_power_consumption()


df = pd.DataFrame(total_power_consumption)

df.to_csv('pv/total_power_consumption_12_1_2017.csv')
