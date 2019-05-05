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



## Downloading the PV data generated on the EnergyVille roof top

Training the network requires taking into account the PV data generated at EnergyVille for each timeslot. We must extract this data from the Smarthor API. Make sure to have created the file *azure_db_credentials.py*, mentioned above, with your credentials.

The file *pv_data_extractor.py* is the one in charge of extracting this PV data. It ouputs a file with the PV data generated every 15 minutes during the days specified on the historical transactions input file. It has 2 required arguments that need to be specified when running the script.

* *--sessions* (Required): Csv file extracted with historical transactions to be used.
* *--tpc_path* (Required): Path to the directory where the total power consumption csv file will be saved.

Example:
```console
python pv_data_extractor.py --sessions '~/Projects/MAI/Thesis/datasets/Transactions/historical_transactions_2019-04-25.csv' --tpc_path '../../../datasets/PV/'
```
The command above generates the file *total_power_consumption_2019-04-25.csv* in the directory *~/Projects/MAI/Thesis/datasets/PV/*.