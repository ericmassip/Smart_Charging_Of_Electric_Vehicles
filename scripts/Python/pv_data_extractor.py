import urllib
import requests
import pandas as pd
import datetime
from datetime import date, timedelta
from datetime import datetime
import json
import os
import click

import azure_db_credentials

DATE_FORMAT_STR = "%Y-%m-%d"

URL = 'https://st-dev-data-api.azurewebsites.net'
invertersURL = urllib.parse.urljoin(URL, '/api/v0.1/buildings/energyville1/pv/roof/inverters/')
powerURL = urllib.parse.urljoin(URL, '/api/v0.1/buildings/energyville1/pv/roof/power/')

user = azure_db_credentials.smarthor_user
pswd = azure_db_credentials.smarthor_password


def get_time_dictionary_every_15min(days_to_be_checked_2):
    timedelta_15 = timedelta(minutes=15)

    dates = []

    for date in days_to_be_checked_2:
        date = datetime.strptime(date, DATE_FORMAT_STR)
        for i in range(96):
            dates.append(date)
            date = date + timedelta_15

    return dates


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


def get_total_power_consumption(dates, power_consumptions):
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


@click.command()
@click.option(
    '--sessions',
    type=click.STRING,
    required=True,
    help='Sessions file with the historical transactions to be used.'
)
@click.option(
    '--tpc_path',
    type=click.STRING,
    required=True,
    help='Path to the directory where the total power consumption will be saved.'
)
def extract_pv(sessions, tpc_path):
    start_day = date(2018, 8, 1)
    end_day = date(2019, 8, 1)

    delta = end_day - start_day

    days_to_be_checked = [start_day + timedelta(i) for i in range(delta.days)]

    sessions_filename = sessions
    sessions = pd.read_csv(sessions_filename, index_col='Started')
    df = sessions
    df.index = pd.to_datetime(df.index)

    days_to_be_checked_2 = []

    for day in days_to_be_checked:
        sessions_of_a_day = df[df.index.dayofyear == pd.Timestamp(day).dayofyear]

        if not sessions_of_a_day.empty:
            days_to_be_checked_2.append(pd.Timestamp(day)._date_repr)

    print('There are ' + str(len(days_to_be_checked_2)) + ' days to be checked.')

    start_time = datetime.strptime(days_to_be_checked_2[0], DATE_FORMAT_STR)
    end_time = datetime.strptime(days_to_be_checked_2[-1:][0], DATE_FORMAT_STR) + timedelta(days=1)

    dates = get_time_dictionary_every_15min(days_to_be_checked_2)
    power_consumptions = get_power_consumptions(start_time, end_time)
    total_power_consumption = get_total_power_consumption(dates, power_consumptions)

    df = pd.DataFrame(total_power_consumption)

    total_power_consumption_directory = tpc_path
    if not os.path.exists(total_power_consumption_directory):
        os.makedirs(total_power_consumption_directory)

    df.to_csv(total_power_consumption_directory + 'total_power_consumption_' + sessions_filename.split("_")[-1].split(".")[0] + '.csv')


if __name__ == '__main__':
    extract_pv()
