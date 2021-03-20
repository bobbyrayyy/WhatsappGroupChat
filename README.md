# Whatsapp Groupchat via Maytapi

- In this example we demo a building management use case.

- We use ngrok to create temporary https reverse proxy so whatsapp can reach our demo api.

- Because ngrok public url changes everytime we also change webhook settings in our instance at boot. This should not be used like this in production environments.

- NOTE: Before testing the demo you need to create your phone instance and connect an active WhatsApp account to instance in [Phones Page](https://console.maytapi.com/). (Create a trial Maytapi Whatsapp API account and register the test phone via Whatsapp Web QR code)


  Link to full Maytapi docs for more details: https://maytapi.com/whatsapp-api-documentation

# Installation

### Installing python libraries

`pip install -r requirements.txt`

### Configure Tokens

You need to change PRODUCT_ID, PHONE_ID, API_TOKEN, MANAGER_GROUP and USER_GROUPS (list of strings) values in app.py file. 

You can find your Product ID and Token in [Settings Token Page](https://console.maytapi.com/settings/token). 
Phone Id can be found in [Phones Page](https://console.maytapi.com/) or with `/listPhones` endpoint.

MANAGER_GROUP and USER_GROUPS are the conversation IDs of each respective Whatsapp groupchat. 
They can be obtained from your Maytapi Developer account dashboard -> Developers -> Logs, find value of "conversation" in the JSON data logs. (e.g. "6582698370-1606900617@g.us")

  

# Start The Api
## Mac/Linux
```

export FLASK_APP=app.py

flask run --host 0.0.0.0 --port 9000 --no-debugger --no-reload

```

## Windows Cmd

```

set FLASK_APP=app.py

flask run --host 0.0.0.0 --port 9000 --no-debugger --no-reload

```

## Windows PowerShell

```

$env:FLASK_APP = "app.py"

flask run --host 0.0.0.0 --port 9000 --no-debugger --no-reload

```
# Description of Use Case
This project serves as a demo for use case:
<img src="https://i.ibb.co/LYZKqs3/Screenshot-2020-12-04-at-11-13-53-AM.png" alt="Screenshot-2020-12-04-at-11-13-53-AM" border="0">
<img src="https://i.ibb.co/gSz7v7J/Screenshot-2020-12-04-at-11-13-57-AM.png" alt="Screenshot-2020-12-04-at-11-13-57-AM" border="0">

There are 3 main whatsapp groups created:
1. **WA Group 1 - Republic Plaza:**
	This groupchat is for building staff to send updates on *incident report* and *incident resolved* for Republic Plaza. This groupchat includes the building staff (end user) and the bot. 
2. **WA Group 2 - City Square Mall:**
	Similarly, this groupchat is for building staff to send updates on *incident report* and *incident resolved* for City Square Mall. This groupchat includes the building staff (end user) and the bot. 
3. **WA Group 3 - CDL Ops Manager Groupchat:**
	This groupchat acts as a log and receives message updates from the bot whenever there is a *incident report* or *incident resolved* from any one of the buildings. This groupchat includes the manager and the bot. Thus, the manager does not need to be in every single building groupchat, he only needs to be in this one.

The Operations Dashboard is done in Vue (similar to Yoobot) and gets JSON data from the backend (app.py) via its GET method.


# How to Demo Use Case
### 1. Create the Whatsapp groups and add users
Create the 3 seperate Whatsapp groups and make sure the correct members are in each group (as mentioned above).

### 2. To report an incident
In any one of the building chatgroups, start the text message with '@6582698370 ' or '@saved_contact_name_of_bot ' (a list of suggestions should automatically appear). 
<img src="https://i.ibb.co/qCvmj1L/IMB-24v-Po-S.gif" alt="IMB-24v-Po-S" border="0">

Once this message is sent, the bot will reply with a confirmation message. 
<img src="https://i.ibb.co/Kx24KM4/IMG-8248.jpg" alt="IMG-8248" border="0">

A message will also be sent to the manager groupchat to log the incident.
<img src="https://i.ibb.co/DCXKRY4/IMG-8253.png" alt="IMG-8253" border="0">


### 3. To resolve/close an incident
Reply *'Incident resolved'* to the bot-generated 'incident received' message that has the corresponding incident number as the incident you wish to resolve.
This can be done by swiping the message to the right, or pressing and holding -> select 'reply'.

Once done, the bot will send a confirmation message that the incident is closed. 
<img src="https://i.ibb.co/hXbRsVB/IMG-8250.jpg" alt="IMG-8250" border="0">

A message will also be sent to the manager groupchat to log the closure of the incident.
<img src="https://i.ibb.co/Fz6dr7b/IMG-8254.jpg" alt="IMG-8254" border="0">




### Additional Message:
This project can be replicated to serve many use cases:
- management of delivery fleet, where constant updates/actions to the central controller might be needed
- management of incident reporting (maintainene/crime/information gathering/etc)
- large scale amazing race events (central controller can act as the manager group, while many teams each have a phone that can log direct updates to the central controller, who then can monitor the situation live)
