from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity

import azure_db_credentials

import pandas as pd

storage_account_name = azure_db_credentials.storage_account_name
sas_token = azure_db_credentials.sas_token


def query_azure_db(filterQuery, selectQuery, tableName, rowKeyColumnName):
    
    ## Setup the table service
    table_service = TableService(account_name=storage_account_name, sas_token=sas_token)
    
    ## Get the data from the Storage Account
    transactions = list(table_service.query_entities(tableName, filter=filterQuery, select=selectQuery))
    
    ## Store data in a Pandas dataframe in a neat way
    df = pd.DataFrame(transactions)
    df.rename(columns={'RowKey': rowKeyColumnName}, inplace=True)
    df.set_index(rowKeyColumnName, inplace=True)
    df.drop(['etag'], axis=1, inplace=True)

    return df


def get_data_from_historical_transactions():
    filterQuery = "deployment eq 'production' and stopTime ne '' and chg3phase ne '' and maxPowerDetermined eq true"
    selectQuery = 'RowKey, chargingStationId, chg3phase, connectorId, idTag, energy, finished, lastSeen, curPower, maxPowerSeen, meterStart, meterStop, startTime, stopTime'
    tableName = "HistoricalTransactions"
    rowKeyColumnName = "transactionId"
    
    return query_azure_db(filterQuery, selectQuery, tableName, rowKeyColumnName)



def get_power_data_from_meter_values(partitionKey):
    filterQuery = "PartitionKey eq '" + str(partitionKey) + "' and measurand eq 'Power.Active.Import'"
    selectQuery = 'PartitionKey, RowKey, chargingStationId, connectorId, timestampMeasurement, value'
    tableName = "MeterValues"
    rowKeyColumnName = "meterValueId"
    
    return query_azure_db(filterQuery, selectQuery, tableName, rowKeyColumnName)

