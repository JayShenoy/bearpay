import urllib.request, requests, json

def lambda_handler(event, context):
    if (event['session']['application']['applicationId'] != 'amzn1.ask.skill.7b0158fd-627b-4c86-899b-b947996db926'):
        raise ValueError('Invalid Application ID')
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "bearpay":
        return bear_pay(intent,session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print "Ending session."

def handle_session_end_request():
    card_title = "BearPay - Thanks"
    speech_output = "Thank you for using BearPay."
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "BearPay"
    speech_output = "Welcome to the BearPay App. You can use me to transfer money."
    reprompt_text = "Please ask me to send money."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def verify(intent, session):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    speech_output = 'What is your password?'

    if 'Password' in intent['slots']:
        pword = intent['slots']['Password']['value']
        return pword

    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

    #not sure how to check here

def bear_pay(intent, session):
    
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Amount' in intent['slots'] and 'Recipient' in intent['slots'] and 'Password' in intent['slots']:
        amount = intent['slots']['Amount']['value']
        recip = intent['slots']['Recipient']['value']
        pword = intent['slots']['Recipient']['value']
        session_attributes = requests.get("https://bear-pay.herokuapp.com/customer/" + recip, auth=(recip, pword))#function call to get new account balance
        dataTable = {'amount':amount,'recipient_name':recip,'password':pword}
        headers = {'Content-Type': 'application/json'}
        response = requests.post("https://bear-pay.herokuapp.com/email-transfer",data=json.dumps(dataTable),headers=headers)

        if response == 'Sent transfer email':
            speech_output = "Sent $" + amount + "to " + recip
        else:
            speech_output = response
        reprompt_text = "You can ask me to send five dollars to John with password password"

    elif not 'Amount' in intent['slots'] and 'Recipient' in intent['slots']:
        speech_output = "I'm not sure what the amount you're sending is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what the amount is. " \
                        "You can tell me the amount you're sending by saying, " \
                        "send five dollars to John with password password"
    elif 'Amount' in intent['slots'] and not 'Recipient' in intent['slots']:
        speech_output = "I'm not sure who the recipient is. " \
                        "Please try again."
        reprompt_text = "I'm not sure who the recipient is. " \
                        "You can tell me the recipient by saying, " \
                        "send five dollars to John with password password"
    elif not 'Password' in intent['slots']:
        speech_output = "You forgot to say your password " \
                        "Please try again."
        reprompt_text = "I'm not sure that you are who you say you are" \
                        "You can tell me " \
                        "send five dollars to John with password password"
    else:
        speech_output = "I'm not sure how much money you're sending and who the recipient is " \
                        "Please try again."
        reprompt_text = "I'm not sure how much you're sending and to whom. " \
                        "You can tell me " \
                        "send five dollars to John with password password"

    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }