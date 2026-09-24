import pandas as pd
from difflib import SequenceMatcher

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
        
        normalized_df[col] = (csv_df[col].astype(str).str.strip().str.replace(r'\.0$', '', regex=True))

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

    #handling numeric values in xiq export csv
    normal_csv['Weight'] = pd.to_numeric(normal_csv['Weight'], errors='coerce').astype('Int64')
    normal_csv['order_id'] = pd.to_numeric(normal_csv['order_id'], errors='coerce').astype('Int64')
    normal_csv['stage'] = pd.to_numeric(normal_csv['stage'], errors='coerce').astype('Int64')

    
    #selecting relevant features from tubulator table
    normal_currTable = currTable[['Sand Type','Carrier','Weight','BOL','Truck','PO','Facility','Source']].copy()

    #handling type mismatch in current table
    for i in normal_currTable.columns:

        if i != 'Weight':
            normal_currTable[i] = normal_currTable[i].astype(str)


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
    unmatchedTable_df = pd.DataFrame(unmatchedTable)

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
    duplicates = []

    #initializing new columns
    mod_table['order_id'] = pd.NA
    mod_table['stage'] = pd.NA

    #looping through table rows
    for table_row in range(0,len(matchedTable),1):


        #Finding the location of table bols in csv table
        index =  matchedCSV.index[matchedCSV['BOL'] == matchedTable.loc[table_row,'BOL']].tolist()
        
        if len(index) == 1:

            mod_table.loc[table_row, 'order_id'] = matchedCSV.loc[index[0], 'order_id']
            mod_table.loc[table_row, 'stage'] = matchedCSV.loc[index[0], 'stage']

        #having more than one index means we have a duplicate BOL
        else:

            #find duplicate bols
            for i in index:
                duplicates.append({
                "BOL": matchedCSV.loc[i, "BOL"],
                "order_id": int(matchedCSV.loc[i, "order_id"]),
                "stage": int(matchedCSV.loc[i, "stage"])
            })

    return(mod_table,duplicates)

#finding likely candidates of unmatched rows using gastalt pattern matching            
def likeyCandidate(unmatchedTable, CSVTable):

    #final list to be returned
    candidates = []

    #loop through unmatched values from table
    for row in range(0,len(unmatchedTable),1):

        #loop through unmatched csv table
        for csvRow in range(0,len(CSVTable),1):

            tempCandidate = {}

            #finding similarity ratio
            similarity = SequenceMatcher(None,unmatchedTable.loc[row,'BOL'],CSVTable.loc[csvRow,'BOL']).ratio()
            
            #similarity threshold
            if (similarity >= 0.8):

                score = similarity

                #weight matching adds one to the score
                if(unmatchedTable.loc[row,'Weight'] == CSVTable.loc[csvRow,'Weight']):

                    score += 1

                #truck matching adds 1 to the score
                if(unmatchedTable.loc[row,'Truck'] == CSVTable.loc[csvRow,'Truck']):

                    score += 1

                
                for col in CSVTable.columns:

                    tempCandidate[col] = CSVTable.loc[csvRow,col]

                #keeping original bol being matched to sort in app.js
                tempCandidate['source_bol'] = unmatchedTable.loc[row, 'BOL']

                tempCandidate['score'] = round(score,2)
                candidates.append(tempCandidate)


    return(candidates)

def compare_df(matched_table, matched_csv):

    

    #Final matched table to modify
    matched_final = matched_table.copy()

    #looping through both tables to compate
    for row in range(0,len(matched_table),1):
        
        for csv_row in range(0,len(matched_csv),1):

            #find the matched row
            if(matched_table.loc[row,'BOL'] == matched_csv.loc[csv_row,'BOL']):
                  
                #flag difference values for truck, po, weight
                matched_final.loc[row,'truck_bool'] = (matched_table.loc[row,'Truck'] == matched_csv.loc[csv_row,'Truck'])
                matched_final.loc[row,'po_bool'] = (matched_table.loc[row,'PO'] == matched_csv.loc[csv_row,'PO'])
                matched_final.loc[row,'weight_bool'] = (matched_table.loc[row,'Weight'] == matched_csv.loc[csv_row,'Weight'])

    return matched_final

def match_xiq(csvFile, currTable):

    xiq_df = readcsv(csvFile)

    normal_csv, normal_table = normalizer(xiq_df, currTable)

    matched_table_df, unmatched_table_df = matched_table(
        normal_table,
        normal_csv['BOL'].values
    )

    matched_csv_df, unmatched_csv_df = matched_csv(
        normal_csv,
        normal_table['BOL'].values
    )

    compared_table = compare_df(
            matched_table_df,
            matched_csv_df
        )

    new_table, duplicates = addOrder(
        compared_table,
        matched_csv_df
    )
    
    

    #checking if matches are found
    if not new_table.empty:

        # Get the original full SandFlow rows for matched BOLs
        matched_full = currTable[ currTable['BOL'].astype(str).isin(new_table['BOL'].astype(str))].copy()
        
        # Add xIQ match information to the original rows
        matched_full = matched_full.merge(new_table[['BOL','order_id','stage','truck_bool','po_bool','weight_bool']],on='BOL',how='left')
        matched_json = (matched_full.astype(object).where(pd.notna(matched_full), None).to_dict(orient="records"))
        
    #fallback in case no order id matches were found
    else:
        matched_full = None
        matched_json = None

    

    candidates = likeyCandidate(
        unmatched_table_df,
        unmatched_csv_df
    )

    #removing np.int64 text from candidate table
    if len(candidates) > 0:

        candidates_df = pd.DataFrame(candidates)

        candidates_json = (candidates_df.astype(object).where(pd.notna(candidates_df), None).to_dict(orient="records"))

    else:

        candidates_json = []

    matched_csv_json = (matched_csv_df.astype(object).where(pd.notna(matched_csv_df), None).to_dict(orient="records"))
    
    

    unmatched_json = (unmatched_table_df.astype(object).where(pd.notna(unmatched_table_df), None).to_dict(orient="records"))

    return {
        "candidates": candidates_json,
        "duplicates": duplicates,
        "matched_with_order": matched_json,
        "matched_csv": matched_csv_json,
        "unmatched_table_tickets": unmatched_json
    }