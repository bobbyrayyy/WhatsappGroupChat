from flask import Flask, request, jsonify
from pyngrok import ngrok
import requests
import sys
from datetime import datetime
import json
import re

# create app instance
app = Flask(__name__)

# --- Replace the values here with your own Maytapi details and tokens. ---
INSTANCE_URL = "https://api.maytapi.com/api"
PRODUCT_ID = "2c77bf87-2f3f-4d4b-a61a-11affe273046"
PHONE_ID = "8592"
API_TOKEN = "76e86522-3c47-4f90-a250-28f98a2f7401"
MANAGER_GROUP = "6599999999-1608439226@g.us"
USER_GROUPS = ["6599998888-1608438727@g.us", "6599997777-1608438751@g.us"]
# --- ---- ---- ---- ---- --- ---- ---- ----


# Create list to store open incidents
# (makeshift database just for this POC)
incidents_list = [
    # {'id': 0,
    #  'response_time': 00000000000000,
    #  'property': '6582698370-1606722491@g.us', 
    #  'status': 'open'},
    # {'id': 1,
    # 'response_time': 00000000000000,
    # 'property': '6582698370-1606722491@g.us', 
    # 'status': 'closed'}
]


@app.route('/webhook', methods=['GET'])
def front_end():

    # Find Total incidents
    total_incidents = len(incidents_list)

    # Find number of open incidents
    num_open = 0
    for incident in incidents_list:
        if incident["status"] == 'open':
            num_open += 1

    # Find number of closed incidents
    num_closed = total_incidents - num_open
    

    # Find avg response time
    total_response_time = -1
    for incident in incidents_list:
        total_response_time += incident["response_time"]
    
    avg_response_time = (total_response_time/num_closed)//60     # we want to get a whole number, and in minutes

    # Find total incidents per property
    total_incidents_per_property_per_month = []  

    for group in USER_GROUPS:
        for month in range(11):
            total_incidents_this_month = 0
            for incident in incidents_list:
                if incident["property"] == group:
                    this_month = incident["id"][4:5]    #slicing to get the month
                    if month == this_month:
                        total_incidents_this_month += 1

            # total_incidents_per_property is a list of dictionaries, each dictionary contains info on total number of incidents per property
            total_incidents_per_property_per_month.append({"month": month, "property": group, "total_incidents_here": total_incidents_this_month})    

    print(total_incidents_per_property_per_month)
    # final output 
    results = [
        {
            "total_incidents": total_incidents,
            "num_open": num_open,
            "num_closed": num_closed,
            "avg_response_time": avg_response_time,
            "total_incidents_per_property_per_month": total_incidents_per_property_per_month
        }
    ]
    print("\n\n\n Results are here:\n" + results)
    return jsonify(results)


@app.route("/")
def hello():
    return app.send_static_file("index.html")

def send_response(body):
    print("Request Body", body, file=sys.stdout, flush=True)
    url = INSTANCE_URL + "/" + PRODUCT_ID + "/" + PHONE_ID + "/sendMessage"
    headers = {
        "Content-Type": "application/json",
        "x-maytapi-key": API_TOKEN, #need to send 'x-maytapi-key':'YOUR_TOKEN' header with every request.
    }
    response = requests.post(url, json=body, headers=headers)
    print("Response", response.json(), file=sys.stdout, flush=True)
    return


@app.route("/webhook", methods=["POST"])
def webhook():
    # This part is just extracting the useful parameters from json
    json_data = request.get_json()
    message = json_data.get("message")
    if message != None:
        _type = message.get("type")
    else:
        print(json_data)
    conversation = json_data.get("conversation")
    
    ##### Here is where we start handling message content #####
    if message == None:
        print("Ignoring ack message...")
        return

    if message != None and message.get("fromMe"):
        return

    if message != None and _type == "text":
        # get content of the message as variable 'text'
        text = message.get("text")
        text = text.lower()
        print("Type:", _type, "Text:", text, file=sys.stdout, flush=True)
       
        # If conversation is from 'Group 1...' or 'Group 2...', then have response for messages
        if conversation in USER_GROUPS:

            # serialized starts with 'true' if it is a reply message, starts with 'false' if not
            replyMessage = json_data.get("quoted") 
            if replyMessage != None:
                serialized = replyMessage.get("_serialized")
                incidentText = replyMessage.get("text")

            # get user number
            user_data = json_data.get("user")
            if user_data != None:
                external_user_number = user_data.get("phone")
            
            # Getting location name based on conversation ID
            if json_data.get("conversation") == "6582698370-1608438751@g.us":
                conversation_name = "Republic Plaza"
            elif json_data.get("conversation") == "6582698370-1608438727@g.us":
                conversation_name = "City Square"
            
            # ONLY if message starts with '@6582698370 ' (with the space) then bot will acknowledge!
            if text.startswith('@6582698370 '):
                # create an incident ID based on current time
                incidentId = datetime.now().strftime('%Y%m%d%H%M%S')

                # append to list that keeps track of open incidents
                incidents_list.append({'id': incidentId,'response_time': 00000000000000,'property': conversation, 'status': 'open'})
                print(incidents_list)
                
                # Reply acknowledgement message in the same group chat
                body = {"type": "text", "message": "@" + external_user_number + ",\nYour incident report has been received! \nAlerting cleaners, facility manager, and operations manager.\n\nIncident Number: #" + incidentId}
                body.update({"to_number": conversation})
                send_response(body)

                # Forward the notification message to Manager's chat too
                description = text.replace('@6582698370 ', '')
                managerBody = {"type": "text", "message": "*Incident Report*\nLocation: " + conversation_name + "\nReporting Employee: " + external_user_number + "\nIncident Description: '" + description + "'\nIncident Number: #" + incidentId}
                managerBody.update({"to_number": MANAGER_GROUP})
                send_response(managerBody)

            # this is for handling 'incident resolved' messages, aka a reply message
            elif replyMessage != None and serialized.startswith('true'):    #only if it is a message replying to something
                if "incident resolved" in text:
                    # retreive the ID of incident we want to close
                    try:
                        foundId = re.search(r'\d\d\d\d\d\d\d\d\d\d\d\d\d\d', incidentText).group(0)
                    except AttributeError:
                        print("Not replying to an incident reporting message...", type,  file=sys.stdout, flush=True)
                        return jsonify({"success": True}), 200

                    # open text file in read mode
                    print("HELLO CAN U SEE THIS111")
                    print("\n")
                    print(foundId)
                    for incident in incidents_list:
                        if incident["id"] == foundId and incident["status"] == 'open':
                            # updating status to 'closed'
                            incident["status"] = 'closed'

                            # updating response_time
                            start = datetime.strptime(foundId, '%Y%m%d%H%M%S')
                            end = datetime.strptime(datetime.now().strftime('%Y%m%d%H%M%S'), '%Y%m%d%H%M%S')
                            incident["response_time"] = (end - start).total_seconds     #in seconds!

                            # crafting reply message
                            replyBody = {"type": "text", "message": " @" + external_user_number + "\nClosing incident #" + foundId + " Thank you."}
                            replyBody.update({"to_number": conversation})
                            send_response(replyBody)
                            print("Reporting to manager now...")
                            # Forward the notification message to Manager's chat too
                            managerBody = {"type": "text", "message": "*Incident Resolved*\nLocation: " + conversation_name + "\nResolving Employee: " + external_user_number + "\nIncident Number: #" + foundId}
                            managerBody.update({"to_number": MANAGER_GROUP})
                            send_response(managerBody)
                        elif incident["id"] == foundId and incident["status"] == 'closed':
                            replyBody = {"type": "text", "message": " @" + external_user_number + "\nIncident #" + foundId + " has already been closed."}
                            replyBody.update({"to_number": conversation})
                            send_response(replyBody)
                        else:
                            print("Incident id doesn't exist...")
      
            else:
                print("Bot is not concerned with the internal chitchat...", type,  file=sys.stdout, flush=True)
        else:
            print("Bot is not concerned with the other chats...", type,  file=sys.stdout, flush=True)
    else:
        print("Ignored Message Type:", type,  file=sys.stdout, flush=True)
    return jsonify({"success": True}), 200


def setup_webhook():
    if PRODUCT_ID == "" or PHONE_ID == "" or API_TOKEN == "":
        print(
            "You need to change PRODUCT_ID, PHONE_ID and API_TOKEN values in app.py file.", file=sys.stdout, flush=True
        )
        return
    tunnel = ngrok.connect(9000)
    public_url = tunnel.public_url
    public_url = public_url.replace("http", "https", 1)
    
    print("Public Url " + public_url, file=sys.stdout, flush=True)
    url = INSTANCE_URL + "/" + PRODUCT_ID + "/setWebhook"
    headers = {
        "Content-Type": "application/json",
        "x-maytapi-key": API_TOKEN,
    }
    body = {"webhook": public_url + "/webhook"}
    response = requests.post(url, json=body, headers=headers)
    print(response.json(), file=sys.stdout, flush=True)


# Do not use this method in your production environment
setup_webhook()


