import pandas as pd

#Reading xiq export
def readcsv(csvFile):

    ##reading and selecting required columns
    xiq_df = pd.read_csv(csvFile, usecols=['order_id','sand_ticket_no','driver_weight',
                                         'loading_site_name','stage','po','sand_type_name','carrier_name','truck','status'])
    return xiq_df

#standerdizing the dataframes for easier comparison
def normalizer(csv_df, currTable):

    normalized_df = csv_df.copy()

    #removing white space from xiq columns
    for col in normalized_df.columns:
        if (col not in ['driver_weight','order_id','stage']):
            normalized_df[col] = csv_df[col].astype(str).str.strip().astype(str)
        else:
            normalized_df[col] = csv_df[col].astype(str).str.strip().astype(float)

    #establishing the same columns names as Tubulator Table
    normal_csv = normalized_df.rename(columns={
            'sand_ticket_no': 'BOL', 
            'driver_weight': 'Weight', 
            'sand_type_name': 'Sand Type',
            'carrier_name' : 'Carrier',
            'loading_site_name': 'Facility',
            'po' : 'PO',
            'truck' : 'Truck'
            })

    #selecting relevant features from tubulator table
    normal_currTable = currTable[['Sand Type','Carrier','Weight','BOL','Truck','PO','Facility',]]


    return [normal_csv,normal_currTable]

#Finding matched and unmatched rows in tubulator table
def matched_table(currTable, xiq_bols):

    #final return arrays
    matchedTable = []
    unmatchedTable = []

    #looping through table rows
    for row in range(0,len(currTable),1):

        #initial row dictionary for unmatched values 
        unmatchedTemp = {}

        if currTable.loc[row,'BOL'] in xiq_bols:

            #initial matched row dictionary
            currMatch = {}

            #looping through columns for matched row
            for col in currTable.columns:

                #recording matched column row value
                currMatch[col] = currTable.loc[row,col]

                
            #appending final array
            matchedTable.append(currMatch)
        else:
            #finding unmatched rows
            for col in currTable.columns:

                #recoring unmatched column row value
                unmatchedTemp[col] = currTable.loc[row,col]

            #appending final array
            unmatchedTable.append(unmatchedTemp)

    matchedTable_df = pd.DataFrame(matchedTable)
    unmatchedTable_df = pd.DataFrame(matchedTable)

    return [matchedTable_df,unmatchedTable_df]

#Finding matched and unmatched rows in xiq export
def matched_csv(csv_df,currTable_bols):

    #final return arrays
    matched_csv = []
    unmatchedcsv = []

    #looping through table rows
    for row in range(0,len(csv_df),1):

        #initial row dictionary for unmatched values 
        unmatchedTemp = {}

        if csv_df.loc[row,'BOL'] in currTable_bols:

            #initial matched row dictionary
            csvMatch = {}

            #looping through columns for matched row
            for col in csv_df.columns:

                #recording matched column row value
                csvMatch[col] = csv_df.loc[row,col]

                
            #appending final array
            matched_csv.append(csvMatch)
        else:
            #finding unmatched rows
            for col in csv_df.columns:

                #recoring unmatched column row value
                unmatchedTemp[col] = csv_df.loc[row,col]

            #appending final array
            unmatchedcsv.append(unmatchedTemp)

    matched_csv_df = pd.DataFrame(matched_csv)
    unmatchedcsv_df = pd.DataFrame(unmatchedcsv)

    return [matched_csv_df,unmatchedcsv_df]

#Adding order number and order ID to table info
def addOrder(matchedTable, matchedCSV):

    mod_table = matchedTable.copy()

    #looping through table rows
    for table_row in range(0,len(matchedTable),1):

        #Finding the location of table bols in csv table
        index =  matchedCSV.index[matchedCSV['BOL'] == matchedTable.loc[table_row,'BOL']].tolist()

        if len(index) == 1:

            mod_table.loc[table_row, 'order_id'] = matchedCSV.loc[index[0], 'order_id']
            mod_table.loc[table_row, 'stage'] = matchedCSV.loc[index[0], 'stage']

            #TODO: Handle duplicates if length is more than 1
    print(mod_table)
            

        

## Testing area
xiq_df = readcsv('C:/Users/Mohammed/Documents/SandTracker_Paddle/xiq_test.csv')
table = pd.read_csv('C:/Users/Mohammed/Documents/SandTracker_Paddle/test.csv')

normal_csv, normal_table = normalizer(xiq_df,table)

matched_table_df, unmatched_table_df = matched_table(normal_table, normal_csv['BOL'].values)
matched_csv_df, unmatched_csv_df = matched_csv(normal_csv, normal_table['BOL'].values)

addOrder(matched_table_df,matched_csv_df)

