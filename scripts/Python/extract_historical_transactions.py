import pandas as pd
import azure_db_service
import datetime
from session_helper import Hmax

historical_transactions = azure_db_service.get_data_from_historical_transactions()
clean_historical_transactions = historical_transactions[['idTag', 'startTime', 'stopTime']]


# The pure version of get_max_charging_timestamp sends back the charging times without tweeks
def get_max_charging_timestamp_pure(power_data):
    maxChargingTimestamp = power_data.iat[len(power_data) - 1, 0]

    found = False
    i = 1  # Start at 1 because normally the first value is 0
    while i < len(power_data) and not (found):
        value = power_data.iat[i, 1]
        if value == 0:
            if power_data.iloc[i:i + 91, 1].sum() == 0:
                maxChargingTimestamp = power_data.iat[i, 0]
                found = True
        i += 1

    return maxChargingTimestamp


def get_charging_time(transactionId):
    power_data = azure_db_service.get_power_data_from_meter_values(transactionId)

    power_data.drop(['PartitionKey', 'chargingStationId', 'connectorId'], axis=1, inplace=True)
    power_data.sort_values(by='timestampMeasurement', inplace=True)
    power_data['timestampMeasurement'] = pd.to_datetime(power_data['timestampMeasurement'])
    power_data['value'] = pd.to_numeric(power_data['value'])

    maxChargingTimestamp = get_max_charging_timestamp_pure(power_data)
    minChargingTimestamp = power_data.iat[0, 0]
    diff = maxChargingTimestamp - minChargingTimestamp

    return diff.seconds / 3600


def get_connection_time(start_time, end_time):
    return (end_time - start_time).seconds / 3600


transactions_cleaned = []

for i in range(len(clean_historical_transactions)):
    transactionId = clean_historical_transactions.index[i]
    started = pd.to_datetime(clean_historical_transactions.iat[i, 1])
    ended = pd.to_datetime(clean_historical_transactions.iat[i, 2])
    connected_time = round(get_connection_time(started, ended), 2)

    # We prune the transactions longer than Hmax, because we consider transactions longer than one working day
    # as outliers. Similarly, we prune transactions shorter than half an hour, cuz they are usually used for testing
    # purposes.
    if 0.5 < connected_time < Hmax and \
            started.year == ended.year and \
            started.month == ended.month and \
            started.day == ended.day:

        charge_time = round(get_charging_time(transactionId), 2)
        idTag = clean_historical_transactions.iat[i, 0]

        transactions_cleaned.append(
            {'transactionId': transactionId, 'Started': started, 'Ended': ended, 'ConnectedTime': connected_time,
             'ChargeTime': charge_time, 'idTag': idTag})

    print('Transaction: ' + str(i))

df = pd.DataFrame(transactions_cleaned)
df.to_csv('historical_transactions_' + str(datetime.date.today()) + '.csv')
