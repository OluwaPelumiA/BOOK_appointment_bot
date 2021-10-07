from re import sub
import requests
from datetime import datetime
from fuzzywuzzy import process
import pickle
import string
import re
import json

def callapi(uris):
    my_headers = {'Authorization' : 'Basic SHVuYV9BcHBfVXNyOlMzY3IzdEBIdW0+MjEwOA=='}
    allresponse = requests.get(uris, headers=my_headers).json()
    if isinstance(allresponse, dict):
        if allresponse.get("status") == 404:
            return None, {}
        else:
            allresponse = [allresponse]
    outagestatus = None
    outagetype = None
    outagecause = None
    outagerestoretime = None
    if len(allresponse) == 0:
        return None, {}
    elif len(allresponse) >= 1:
        response = allresponse[0]
        print(response)
        if response["outageStatus"] is not None:
            outagestatus = True
            outagetype = response['outageStatus']['outageType']
            outagecause = response['outageStatus']['primaryCause']
            resttime = datetime.strptime(response['outageStatus']['etrDateTime'], '%Y-%m-%dT%H:%M:%S')
            outagerestoretime = resttime.date().strftime("%m-%d-%Y") + " " + resttime.time().strftime("%I:%M%p")
        else:
            outagestatus = False
    rsolts = {
        "life_support": response.get("lifE_SUPPORT"),
        "post_code": response.get("instalL_PCODE"),
        "suburb": response.get("instalL_SUBURB"),
        "street": response.get("instalL_STREET"),
        "streetnumber": response.get("instalL_STREET_NO"),
        "nmi": response.get("nmi"),
        "confirm_nmi": "YesTrue" if response.get("nmi") is not None else False,
        "isoutage": outagestatus,
        "outagetype": outagetype,
        "outagecause": outagecause,
        "outagerestoretime": outagerestoretime,
        "allresults": allresponse
    }
    return allresponse, rsolts

def info_by_nmi(nmi):
    uris = f"https://jemoutage-uat.aegisservices.com.au/api/Customers/OutageStatusByNMI/{nmi}"
    allresponse, rsolts = callapi(uris)
    return allresponse, rsolts


def info_by_number(number):
    uris = f"https://jemoutage-uat.aegisservices.com.au/api/Customers/OutageStatusByPhone/{number}"
    allresponse, rsolts = callapi(uris)
    return allresponse, rsolts

def info_by_address(post_code, suburb, street, streetnumber):
    suburb = suburb.replace(" ", "%20")
    street = street.replace(" ", "%20")
    uris = f"https://jemoutage-uat.aegisservices.com.au/api/Customers/OutageStatusByAddress/{post_code}/{suburb}/{street}/{streetnumber}"
    allresponse, rsolts = callapi(uris)
    return allresponse, rsolts

with open("./suburb.pkl", "rb") as f:
    suburbs = pickle.load(f)

with open("./street.pkl", "rb") as f:
    streets = pickle.load(f)

with open("./postcode.pkl", "rb") as f:
    postcodes = pickle.load(f)

with open("./streets_pivot.json") as f:
    streets_dict = json.load(f)

with open("./suburbs_pivot.json") as f:
    suburbs_dict = json.load(f)

def correct_numbers(message):
    rightdict = {
        "one": "1", "two": "2", "three": "3",
        "four": "4", "five": "5", "six": "6",
        "seven": "7", "eight": "8", "nine": "9",
        "zero": "0", "for": "4", "why": "Y", "you": "u",
        "are": "r", "to": "2", "too": "2", "we": "V",
        "oblique": "/", "sex": "6", "whore": '4', "tu": "2"
    }
    message = message.split()
    return "".join([rightdict[i] if i in rightdict else i for i in message])

def get_address(cslots, message):
    message = message.translate(str.maketrans('', '', string.punctuation))
    message = correct_numbers(message)

    opost_code = cslots.get("post_code")
    ostreet = cslots.get("street")
    osuburb = cslots.get("suburb")
    ostreet_confi = cslots.get("street_confi")
    osuburb_confi = cslots.get("suburb_confi")
    ostreetnumber = cslots.get("streetnumber")

    print("len ", len(message))
    thresadion = min(2000/len(message), 60)
    thrres = 10+thresadion
    thrres = 64
    print("threshold", thrres)

    post_code = postcode_fuzzy(message)
    post_code = opost_code if post_code is None else post_code

    suburb, suburb_confi = suburb_fuzzy(message, suburbs_dict[post_code] if post_code is not None else suburbs, thrres)

    if osuburb_confi < suburb_confi:
        osuburb_confi = suburb_confi
    else:
        suburb = osuburb

    street, street_confi = street_fuzzy(message, streets_dict[suburb] if suburb is not None else streets, thrres)

    if ostreet_confi < street_confi:
        ostreet_confi = street_confi
    else:
        street = ostreet

    message = message.replace(post_code if post_code is not None else "", "")
    message = message.replace(opost_code if opost_code is not None else "", "")
    stnumber = re.findall("\d+", message)
    if len(stnumber) > 0:
        stnumber = stnumber[-1]
    else:
        stnumber = None

    return {
        "post_code": post_code,
        "street": street,
        "suburb": suburb,
        "streetnumber": stnumber if stnumber is not None else ostreetnumber,
        "street_confi ": ostreet_confi ,
        "suburb_confi ": osuburb_confi ,
    }
    # return {
    #     "post_code": opost_code if opost_code is not None else post_code,
    #     "street": ostreet if ostreet is not None else street,
    #     "suburb": osuburb if osuburb is not None else suburb,
    #     "streetnumber": ostnumber if ostnumber is not None else stnumber
    # }

def postcode_fuzzy(query):
    for i in postcodes:
        if str(i) in query:
            return str(i)
    return None

def street_fuzzy(query, masterllist, thrres):
    street = process.extractOne(query, masterllist)
    print("street", street)
    if street[1] >= thrres:
        return street[0], street[1]
    else:
        return None, 0

def suburb_fuzzy(query, masterllist, thrres):
    suburb = process.extractOne(query, masterllist)
    print("suburb", suburb)
    if suburb[1] >= thrres:
        return suburb[0], suburb[1]
    else:
        return None, 0

if __name__ == "__main__":
    print(info_by_number("0396470511"))
    print(info_by_nmi("6001314121"))
    print(info_by_address(3072, "PRESTON", "PLENTY ROAD", 340))