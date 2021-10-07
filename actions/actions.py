
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormValidationAction, REQUESTED_SLOT
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet
from .dbutils import *
from typing import Any, Text, Dict, List, Optional
from datetime import datetime, timedelta
import string
import re

class ValidateoutageForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_outage_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: Dict,
    ) -> Optional[List[Text]]:
        return slots_mapped_in_domain

    async def extract_is_life_threat(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        # print("tracker state metadata")
        # import json
        # with open("./trackerdump.json", "w") as fp:
        #     fp.write(json.dumps(tracker.current_state()))
        # print(tracker.current_state())
        return {}
    
    async def validate_is_life_threat(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if slot_value is True:
            dispatcher.utter_message("Please wait while we transfer you to one of our team members.#JEN_faults_life_threat#")
            rdic = {}
            cslots = tracker.current_state()["slots"]
            for sname in cslots:
                if cslots[sname] is None:
                    rdic[sname] = " "
            return rdic
        return {}

    async def extract_purposeofcall(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if tracker.get_slot(REQUESTED_SLOT) == "purposeofcall":
            intent_name = tracker.latest_message.get("intent").get("name")
            return {"purposeofcall": intent_name}
        return {}

    async def validate_purposeofcall(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        intent_name = tracker.latest_message.get("intent").get("name")
        switcher = {
                "lifethreat": "#JEN_faults_life_threat#",
                "priority": "#JEN_faults_priority#",
                "general": "#JEN_faults_general#",
                "other_general": "#JEN_Gen_Enq#"
            }
        if intent_name in switcher:
            dispatcher.utter_message("Please wait while we transfer you to one of our team members"+switcher.get(intent_name, ""))
        return {}

    async def extract_nmi(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if tracker.get_slot(REQUESTED_SLOT) == "nmi":
            intent_name = tracker.latest_message.get("intent").get("name")
            user_message = tracker.latest_message.get("text").lower()
            user_message = user_message.replace(' ','') 
            nmis = re.findall("\d{10}", user_message)
            if len(nmis) > 0:
                nmis = nmis[-1]
            else:
                nmis = None
            if nmis is not None:
                return {"nmi": nmis}
            if intent_name == 'deny' and nmis is None:
                return {
                    "nmi": False
                }
        return {}
    
    async def validate_nmi(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if slot_value is False:
            return {
                "nmi": False,
                "confirm_nmi": "NA"
            }
        else:
            speak_nmi = " ".join([i for i in str(slot_value)])
            return {
                "speak_nmi": speak_nmi
            }

    async def extract_confirm_nmi(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if tracker.get_slot(REQUESTED_SLOT) == "confirm_nmi":
            intent_name = tracker.latest_message.get("intent").get("name")
            user_message = tracker.latest_message.get("text").lower()
            user_message = user_message.replace(' ','') 
            nmis = re.findall("\d{10}", user_message)
            if len(nmis) > 0:
                nmis = nmis[-1]
            else:
                nmis = None
            if nmis is not None:
                return {"nmi": nmis}
        return {}
    
    async def validate_confirm_nmi(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if slot_value is True:
            allres, info = info_by_nmi(tracker.get_slot("nmi"))
            if allres is None:
                dispatcher.utter_message(text="Invalid N M I number.")
                return {
                    "nmi": None,
                    "confirm_nmi": None
                }
            else:
                return info
        elif slot_value is False:
            return {
                "nmi": None,
                "confirm_nmi": None
            }
        return {}

    async def extract_post_code(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if tracker.get_slot(REQUESTED_SLOT) == "post_code":
            user_message = tracker.latest_message.get("text").lower()
            return get_address(tracker.current_slot_values(), user_message)
        return {}
    
    async def validate_post_code(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        return {}
    
    async def extract_suburb(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if tracker.get_slot(REQUESTED_SLOT) == "suburb":
            user_message = tracker.latest_message.get("text").lower()
            return get_address(tracker.current_slot_values(), user_message)
        return {}
    
    async def validate_suburb(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        return {}

    async def extract_street(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if tracker.get_slot(REQUESTED_SLOT) == "street":
            user_message = tracker.latest_message.get("text").lower()
            return get_address(tracker.current_slot_values(), user_message)
        return {}
    
    async def validate_street(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        return {}
    
    async def extract_streetnumber(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if tracker.get_slot(REQUESTED_SLOT) == "streetnumber":
            intent_name = tracker.latest_message.get("intent").get("name")
            user_message = tracker.latest_message.get("text").lower()
            user_message = user_message.replace(' ','') 
            streetnumbers = re.findall("\d+", user_message)
            if len(streetnumbers) > 0:
                streetnumbers = streetnumbers[-1]
            else:
                streetnumbers = None
            if streetnumbers is not None:
                return {"streetnumber": streetnumbers}
            if intent_name == 'deny' and streetnumbers is None:
                return {
                    "streetnumber": False
                }
        return {}
    
    async def validate_streetnumber(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        alresp = tracker.get_slot("allresults")
        # if alresp is not None:
        #     for i in alresp:
        #         f1 = i["instalL_PCODE"] == tracker.get_slot("post_code")
        #         f2 = i["instalL_SUBURB"] == tracker.get_slot("suburb")
        #         f3 = i["instalL_STREET"] == tracker.get_slot("street")
        #         f4 = i["instalL_STREET_NO"] == tracker.get_slot("streetnumber")
        #         if f1 and f2 and f3 and f4:

        return {}
    
    async def extract_confirm_address(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if tracker.get_slot(REQUESTED_SLOT) == "confirm_address":
            intent_name = tracker.latest_message.get("intent").get("name")
            if intent_name != "affirm":
                user_message = tracker.latest_message.get("text").lower()
                return get_address(tracker.current_slot_values(), user_message)
        return {}
    
    async def validate_confirm_address(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if slot_value is True and tracker.get_slot("nmi") is False:
            allres, info = info_by_address(tracker.get_slot("post_code"),
                                           tracker.get_slot("suburb"),
                                           tracker.get_slot("street"),
                                           tracker.get_slot("streetnumber"))
            if allres is None:
                dispatcher.utter_message(text="Can't find a NMI against your address")
                return {
                    "post_code": None,
                    "suburb": None,
                    "street": None,
                    "streetnumber": None,
                    "confirm_address": None,
                    "isoutage": None,
                    "outagetype": None,
                    "outagecause": None,
                    "outagerestoretime": None
                }
            else:
                return info
        elif slot_value is False:
            return {
                "post_code": None,
                "suburb": None,
                "street": None,
                "streetnumber": None,
                "confirm_address": None,
                "isoutage": None,
                "outagetype": None,
                "outagecause": None,
                "outagerestoretime": None
            }
        return {}

    async def extract_receive_updates(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        if tracker.get_slot(REQUESTED_SLOT) == "receive_updates":
            return {}
        return {}
    
    async def validate_receive_updates(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        return {}

class Actionsubmitoutage(Action):
    def name(self) -> Text:
        return "action_submitoutage"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slots = tracker.current_slot_values()
        if slots.get("is_life_threat") is True:
            dispatcher.utter_message(text="Transfer to Agent#JEN_faults_life_threat#")
            return []
        elif slots.get("isoutage") is False and slots.get("receive_updates") is True:
            dispatcher.utter_message(text="Transfer to agent#JEN_faults_priority#")
            return []
        elif slots.get("isoutage") is True and slots.get("receive_updates") is True:
            dispatcher.utter_message(text="Sure we will keep you updated by SMS")
            return []
        return []

class ActionSetNumber(Action):
    def name(self) -> Text:
        return "action_setnumber"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #transfer on life support
        return [SlotSet("phonenumber", "402330333")]#, SlotSet("is_life_threat", False), SlotSet("purposeofcall", "outage"), SlotSet("nmi", False)]



class ActionCheckLifeSupport(Action):
    def name(self) -> Text:
        return "action_checklifesupport"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        phnnumber = tracker.get_slot("phonenumber")
        allres, info = info_by_number(phnnumber)
        #call external api with phone number and check life support
        return [SlotSet(x, j) for x, j in info.items()]+[SlotSet("allresults", allres)]


class ActionTransferLifeSupport(Action):
    def name(self) -> Text:
        return "action_transferlifesupport"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("life_support") is True:
            dispatcher.utter_message("Please wait while we transfer you to one of our team members.#JEN_faults_life_threat#")
            rdic = {}
            cslots = tracker.current_state()["slots"]
            for sname in cslots:
                if cslots[sname] is None:
                    rdic[sname] = " "
            return [SlotSet(x, j) for x, j in rdic.items()]
        return []