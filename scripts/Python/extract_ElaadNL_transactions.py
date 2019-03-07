import pandas as pd
from datetime import datetime


elaad_nl_dataset = pd.read_excel('Charging_profiles.xlsx')
elaad_nl_dataset = elaad_nl_dataset[['Started', 'Ended', 'ConnectedTime', 'ChargeTime']]


def get_sojourn_time(start, end):
    return round((end - start).seconds / 3600, 2)


# 6.00 and 9.00 arrival times
start_arrival_times = datetime(2017, 1, 1, 6, 0, 0)
end_arrival_times = datetime(2017, 1, 1, 10, 0, 0)

# 13.00 and 18.00 departure times
start_departure_times = datetime(2017, 1, 1, 13, 0, 0)
end_departure_times = datetime(2017, 1, 1, 18, 0, 0)

charge_near_work_transactions = []

for i in range(len(elaad_nl_dataset)):
    started = datetime.strptime(str(elaad_nl_dataset.loc[i, 'Started']), "%Y-%m-%d %H:%M:%S")
    ended = datetime.strptime(str(elaad_nl_dataset.loc[i, 'Ended']), "%Y-%m-%d %H:%M:%S")

    sojourn_time = get_sojourn_time(started, ended)

    if sojourn_time < 24:
        if start_arrival_times.hour <= started.hour < end_arrival_times.hour and start_departure_times.hour <= ended.hour < end_departure_times.hour:
            charge_near_work_transactions.append(elaad_nl_dataset.loc[i])
    print(i)


df = pd.DataFrame(charge_near_work_transactions)
df.to_csv('charge_near_work_transactions_ElaadNL.csv')