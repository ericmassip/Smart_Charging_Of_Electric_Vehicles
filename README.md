# Smart_Charging_Of_Electric_Vehicles

Eric Massip - Master's in Artificial Intelligence student of the KU Leuven



## Azure and Smarthor API credentials

In order to extract data of EnergyVille either from the Azure database or through the Smarthor API, it will be necessary that you specify the credentials. The easiest way to handle this is to generate a file *azure_db_credentials.py* with the following lines:

```python
storage_account_name = 'storage_account_name'  # Specify the storage_account_name
sas_token = 'sas_token'  # Specify the sas_token here

smarthor_user = 'your_smarthor_user'  # Insert your smarthor user here
smarthor_password = 'your_smarthor_password'  # Insert your smarthor password here
```



## Download the charging transactions from the EnergyVille database

The electric vehicle charging transactions at the parking lot of EnergyVille are being recorded in an Azure database. You must extract this data to train your network. Make sure to have created the file *azure_db_credentials.py*, mentioned above, with your credentials.

The file *extract_historical_transactions.py* is the one in charge of extracting this data. It outputs a csv file with the already preprocessed historical transactions almost ready for training. It has 2 required arguments that need to be specified when running the script.

* *--filter_query* (required): Azure DB query to extract records from the HistoricalTransactions table. This query has to be extracted from the Microsoft Azure Storage Explorer executing the following steps:
  1. Open the Microsoft Azure Storage Explorer
  2. Go to Storage Accounts -> SmartChargingDevSa -> Tables -> HistoricalTransactions
  3. On the top left of the toolbar, click on Query
  4. Define the query that you want, either loaded from memory or added manually
  5. Execute the query and make sure it is querying what you wanted
  6. Click on the top left icon that says ‘Text editor’
  7. Your filter_query will appear as a string sequence

* *--ht_path* (required): Path to the directory where the historical transactions csv file will be saved.

Example:
```console
python extract_historical_transactions.py --filter_query "deployment eq 'production' and stopTime ne '' and chg3phase ne '' and maxPowerDetermined eq true and chargingStationId ne 'BLUEC3' and PartitionKey ne '1970-01-01'" --ht_path '../../../datasets/Transactions/'
```
The command above generates the file *historical_transactions_2019-05-05.csv* in the directory *~/Projects/MAI/Thesis/datasets/Transactions/*.

REMARK: *We prune the transactions longer than Hmax, because we consider transactions longer than one working day as outliers. Similarly, we prune transactions shorter than half an hour, cuz they are usually used for testing purposes.*



## Download the PV data generated on the EnergyVille roof top

Training the network requires taking into account the PV data generated at EnergyVille for each timeslot. We must extract this data from the Smarthor API. Make sure to have created the file *azure_db_credentials.py*, mentioned above, with your credentials.

The file *pv_data_extractor.py* is the one in charge of extracting this PV data. It ouputs a file with the PV data generated every 15 minutes during the days specified on the historical transactions input file. It has 2 required arguments that need to be specified when running the script.

* *--sessions* (required): Csv file extracted with historical transactions to be used.
* *--tpc_path* (required): Path to the directory where the total power consumption csv file will be saved.

Example:
```console
python pv_data_extractor.py --sessions '~/Projects/MAI/Thesis/datasets/Transactions/historical_transactions_2019-05-05.csv' --tpc_path '../../../datasets/PV/'
```
The command above generates the file *total_power_consumption_2019-05-05.csv* in the directory *~/Projects/MAI/Thesis/datasets/PV/*.