import pandas as pd
import numpy as np

import azure_db_service

historical_transactions = azure_db_service.get_data_from_historical_transactions()

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    max_power_seens = historical_transactions[historical_transactions['maxPowerSeen'] > 50]['maxPowerSeen']
    print('Mean: ' + str(np.mean(max_power_seens)))
    print('Median: ' + str(np.median(max_power_seens)))