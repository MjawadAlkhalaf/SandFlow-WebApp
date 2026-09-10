import re

import unicodedata


def cleanText(text_list):
    combined = " ".join(text_list)

    combined = unicodedata.normalize("NFKC", combined)

    cleaned = re.sub(r"[,:;#]", "", combined)

    return cleaned.lower()

def getBOL(ticket):

    ticketNumberPattern = r'(?:ticket(?:\s*no\.?|\s*number)?|bol(?:\s*no|\s*number)?|bill\s*of\s*lading\s*number)\s*([A-Za-z0-9-]+)'
        #finding ticket number using pattern defined
    ticketNumber = re.findall(ticketNumberPattern, ticket)

    #removing any words found in bol search
    ticketNumber = [t for t in ticketNumber if re.search(r'\d', t)]

    #return BOL if value is found
    if len(ticketNumber) > 0:
        return ticketNumber[0].upper()
    else:
        return "null"

#Extracting Atlas Weight
def getWeightAtlas(ticket):

    atlas_pattern = r'net\s*[\d.,]+\s*([\d.,]+)'
    weight = re.findall(atlas_pattern, ticket)
    
    
    #checking if weight was found
    if len(weight)>0:

        #stripping weight from any dots or commas found
        atlas_weight = weight[0].strip().replace(',','')
        atlas_weight = atlas_weight.replace('.','')
        atlas_weight = int(float(atlas_weight))

        return atlas_weight
    else:
        return 0

def getWeightGeneral(ticket):

    WeightPattern = r'\bnet(?:\s*weight)?\D*(\d{5})'
    weight = re.findall(WeightPattern, ticket)
    
            
    #checking if weight was found
    if len(weight)>0:

        #stripping weight from any dots or commas found
        norm_weight = weight[0].strip().replace(',','')
        norm_weight = norm_weight.replace('.','')
        norm_weight = int(float(norm_weight))

        return norm_weight
    else:
        return 0

#Find truck numbers in a ticket
def getTruckNum(ticket):

    truckPattern = r'(?:truck\s*number|truck-trailer|truck|ruck|truckid-trailerid|vehicle)\s*([A-Za-z0-9&-]+)'

    truck = re.findall(truckPattern, ticket)
    #(?:truckid|truck)
    #finding valid truck numbers from resulting tuple
    #truck_list = [val for tup in truck for val in tup if val]
    print(truck)

    truck_final = ""

    #return Valid Truck number
    if len(truck) > 0:

        final_truck = [x for x in truck if any(char.isdigit() for char in x)]

        if len(final_truck) >0:
            truck_final = final_truck[0].split("-")[0].upper()
        return truck_final
    else:
        return "null"

def getCarrier(ticket):

    carrierPattern = r'(?:carrier\s*name|carrier)\s*([A-Za-z0-9&-]+)'

    carrier = re.findall(carrierPattern, ticket)
    if len(carrier) > 0:
        return carrier[0].upper()
    else:
        return "null"

def getPO(ticket):


    #Pattern for PO Number
    POPattern = r'(?i)\b(?:sales\s*order|po\s*number|ponumber|p\.o\.|po#|po|purchase\s*order\s*\.|purchase\s*order)\s*([A-Za-z\d-]+)\b'
    
    #finding po number
    po = re.findall(POPattern, ticket)

    if "oxy" in ticket:

        oxyPo = re.findall(r'oxy-nm-\d+', ticket)
        if len(oxyPo) > 0:

            return oxyPo[0].upper()
    
    #execluding standalone words after po are found instead of po number
    if len(po) > 0:
        valid_pos = [match for match in po if any(char.isdigit() for char in match) and (any(char.isalpha() for char in match) 
        
                                                                                    or match.isdigit() or '-' in match)]
        print(valid_pos)
        #return valid po numbers 
        if len(valid_pos) > 0:
    
            return valid_pos[0].upper()
        
    return "null"


#getting facility from bol and ticket text
def getFacility(ticket, bol):
    
    if "atlas" in ticket:
        if "null" not in bol:
            if bol[0] == 'M':
                return "Atlas - Monahans"
            elif bol[0] == 'K' or bol[0] == 'E' :
                return "Atlas - Kermit"
    elif "covia" in ticket:
        if "kerm" in ticket:
            return "Covia - Kermit"
        elif "crane" in ticket:
            return "Covia - crane"
    elif "bm" in ticket:
        if "kerm" in ticket:
            return "Badger - Kermit"
        elif "crane" in ticket:
            return "Badger - crane"
    elif "STS" in bol or "SCS" in bol:
        return "Signal Peak"
    elif "black mountain" in ticket:
        return "Black Mountain"
    elif "superior silica" in ticket:
        return "Superior Silica"
    elif "arepet" in ticket:
        return "Arepet"
    elif "lonestar" in ticket:
        return "Lonestar"
    elif "us silica" in ticket:
        return "US Silica"
    elif "csp-permian" in ticket:
        return "CSP-Permian"
    else:
        return "null"


def parseTicket(ticket):

    bol = getBOL(ticket)

    facility = getFacility(ticket, bol)

    weight = getWeightGeneral(ticket)

    if "null" not in bol and len(bol) >= 3:
        if (bol[1].isdigit() or bol[2].isdigit())  and (bol[0] == "M" or bol[0] == "K" or bol[0] == 'E'):
            weight = getWeightAtlas(ticket)


    truck = getTruckNum(ticket)
    carrier = getCarrier(ticket)
    po = getPO(ticket)

    return {
        "bol": bol,
        "weight": weight,
        "truck": truck,
        "carrier": carrier,
        "po": po,
        "facility": facility
    }


def checkForInvalid(ticket):

    invalid = []

    if ticket["bol"] == "null":
        invalid.append("bol")

    if ticket["weight"] < 40000 or ticket["weight"] > 57000:
        invalid.append("weight")

    if ticket["truck"] == "null":
        invalid.append("truck")

    if ticket["po"] == "null":
        invalid.append("po")

    return invalid