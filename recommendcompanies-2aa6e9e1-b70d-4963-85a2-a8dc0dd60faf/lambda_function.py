### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
from botocore.vendored import requests


def get_forecast(ticker):
    
    response = requests.get(f"https://ethicallysourced.azurewebsites.net/forecasts/{ticker}")
    data = response.json()
    message = data.get('ticker_id') + " is forecasted to go " + data.get('forecast') + " with an uncertainty of " + str(data.get('mape'))
    return message
    
def validate_data(values, intent_request):
    """
    Validates the data provided by the user.
    """
    # Validate the retirement age based on the user's current age.
    # An retirement age of 65 years is considered by default.
    if values is None:
        return build_validation_result(
            False,
            "values",
            "Please choose a value from the list",
        )
    return build_validation_result(True, None, None)

def rec_companies(values):
    """
    Defines each risk level
    """
    recommend= "none"
    if values == "Human Rights Support":
        recommend = "D, EPHYU, GTEC, LM, PRAX, NBO, EDU, PAXYF, STNL, SPY"
    elif values == "Environmentally Friendly":
        recommend = "D, EPHYU, GUT, GTEC, IGAP, LM, PRAX, NBO, EDU, PAXYF, STNL, FLEX"
    elif values == "Unaffiliated with Defense/Weapons":
        recommend = "ACEZ, D, GUT, PRAX, NBO, EDU, PAXYF, SPY, FLEX, VWO"
    elif values == "Cruelty Free":
        recommend = "EDU, SPY, FLEX, VWO"

    return recommend
    
def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response
    
    
def recommend_stocks(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """
    #final_rec = get_forecast(ticker)
    values = get_slots(intent_request)["values"]
    source = intent_request["invocationSource"]
    ticker= get_slots(intent_request)["ticker"]
    initial_recommendation = rec_companies(values)
    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.
        slots = get_slots(intent_request)
        validation_result = validate_data(values, intent_request)
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None  # Cleans invalid slot
            # Returns an elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"]
            )
        if ticker is None:
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                "ticker",
                {"contentType": "PlainText", "content": """Thank you for your information;
                based on the value you selected, my recommendation is to choose a stock from this list: {}. 
                Enter a ticker to see the two week projection""".format(initial_recommendation)}
            )
        
        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]
        return delegate(output_session_attributes, get_slots(intent_request))   
    # Get the initial investment recommendation
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###
    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{}
            """.format(get_forecast(ticker))
        }
    )

### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendStocks":
        return recommend_stocks(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
        