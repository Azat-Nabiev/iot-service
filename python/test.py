# Write
import urllib.request
import serial
from threading import Thread
import requests
import smtplib
import imaplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from matplotlib import pyplot as plt
import datetime
import numpy as np
import time
import math
import schedule

PORT = ''
BAUD_RATE = 9600

CHANNEL_ID = ''
API_KEY_WRITE = ''
API_KEY_READ = ''

BASE_URL = 'https://api.thingspeak.com'

WRITE_URL = '{}/update?api_key={}'.format(BASE_URL, API_KEY_WRITE)
READ_CHANNEL_RUL = '{}/channels/{}/feeds.json?api_key={}'.format(BASE_URL, CHANNEL_ID, API_KEY_READ)

READ_FIELD1_URL = '{}/channels/{}/fields/{}.json?api_key={}&results={}'.format(BASE_URL, CHANNEL_ID, 1, API_KEY_READ, 10)
READ_FIELD2_URL = '{}/channels/{}/fields/{}.json?api_key={}&results={}'.format(BASE_URL, CHANNEL_ID, 2, API_KEY_READ, 10)
READ_FIELD3_URL = '{}/channels/{}/fields/{}.json?api_key={}&results={}'.format(BASE_URL, CHANNEL_ID, 3, API_KEY_READ, 20)

temp = requests.get(READ_FIELD1_URL)
illum = requests.get(READ_FIELD2_URL)
activity = requests.get(READ_FIELD3_URL)

dataJsonT = temp.json()
dataJsonI = illum.json()
dataJsonA = activity.json()

light_time = []
secure_time = []

end_time_light = None
start_time_light = None

end_time_security = None
start_time_security = None

feeds = dataJsonT["feeds"]
temperature = []
for x in feeds:
    x = float(x["field1"])
    temperature.append(x)


feeds_illum = dataJsonI["feeds"]
illumination = []
for x in feeds_illum:
    x = float(x["field2"])
    illumination.append(x)


feeds_activity = dataJsonA["feeds"]
activity = []
for x in feeds_activity:
    x = float(x["field3"])
    activity.append(x)


def checkMail(email, serialCommunication):
    email.select('inbox')

    while True:
        retcode, response = email.search(None, '(SUBJECT "SEND REPORT" UNSEEN)')

        retcode, responseLightOn = email.search(None, '(SUBJECT "LIGHT ON" UNSEEN)')
        retcode, responseLightOff = email.search(None, '(SUBJECT "LIGHT OFF" UNSEEN)')
        retcode, responseLightAuto = email.search(None, '(SUBJECT "LIGHT AUTO" UNSEEN)')

        retcode, responseSecureOn = email.search(None, '(SUBJECT "SECURE ON" UNSEEN)')
        retcode, responseSecureOff = email.search(None, '(SUBJECT "SECURE OFF" UNSEEN)')

        retcode, responseHeatingOn = email.search(None, '(SUBJECT "HEATING ON" UNSEEN)')
        retcode, responseHeatingOff = email.search(None, '(SUBJECT "HEATING OFF" UNSEEN)')
        retcode, responseHeatingAuto = email.search(None, '(SUBJECT "HEATING AUTO" UNSEEN)')

        retcode, responseCoolingOn = email.search(None, '(SUBJECT "COOLING ON" UNSEEN)')
        retcode, responseCoolingOff = email.search(None, '(SUBJECT "COOLING OFF" UNSEEN)')
        retcode, responseCoolingAuto = email.search(None, '(SUBJECT "COOLING AUTO" UNSEEN)')


        if len(response[0]) > 0:
            emailIds = response[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')
            sendReport()

        if len(responseLightOn[0]) > 0:
            text = "on"

            end_time_light = time.time()
            if start_time_light is not None:
                light_time.append(end_time_light - start_time_light)

            start_time_light = None

            serialCommunication.write(text.encode('ascii'))
            emailIds = responseLightOn[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        if len(responseLightOff[0]) > 0:
            text = "off"

            end_time_light = time.time()
            if start_time_light is not None:
                light_time.append(end_time_light - start_time_light)

            start_time_light = None

            serialCommunication.write(text.encode('ascii'))
            emailIds = responseLightOff[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        if len(responseLightAuto[0]) > 0:
            text = "auto"
            start_time_light = time.time()
            serialCommunication.write(text.encode('ascii'))
            emailIds = responseLightAuto[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        if len(responseSecureOn[0]) > 0:
            text = "motion_on"
            start_time_security = time.time()
            serialCommunication.write(text.encode('ascii'))
            emailIds = responseSecureOn[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        if len(responseSecureOff[0]) > 0:
            text = "motion_off"

            end_time_security = time.time()
            if start_time_security is not None:
                secure_time.append(end_time_security - start_time_security)

            serialCommunication.write(text.encode('ascii'))
            emailIds = responseSecureOff[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        if len(responseHeatingOn[0]) > 0:
            text = "lamp_on"
            serialCommunication.write(text.encode('ascii'))
            emailIds = responseHeatingOn[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')


        if len(responseHeatingOff[0]) > 0:
            text = "lamp_off"
            serialCommunication.write(text.encode('ascii'))
            emailIds = responseHeatingOff[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        if len(responseHeatingAuto[0]) > 0:
            text = "lamp_auto"
            serialCommunication.write(text.encode('ascii'))
            emailIds = responseHeatingAuto[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')


        if len(responseCoolingOn[0]) > 0:
            text = "cooling_on"
            serialCommunication.write(text.encode('ascii'))
            emailIds = responseCoolingOn[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        if len(responseCoolingOff[0]) > 0:
            text = "cooling_off"
            serialCommunication.write(text.encode('ascii'))
            emailIds = responseCoolingOff[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        if len(responseCoolingAuto[0]) > 0:
            text = "cooling_auto"
            serialCommunication.write(text.encode('ascii'))
            emailIds = responseCoolingAuto[0].split()
            for id in emailIds:
                email.store(id, '+FLAGS', '\\Seen')

        time.sleep(5)


def sendNotification():
    message = MIMEMultipart()
    message['Subject'] = 'Report from our arduino'

    plt.ioff()
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, 'Some activity were found!', fontsize=15, ha='center')
    plt.axis('off')

    fileName = 'report-activity-{}.png'.format(datetime.date.today())
    filePath = 'C:\\Users\\Azat\\Desktop\\Reports\\' + fileName
    plt.savefig(filePath, bbox_inches='tight')

    tempGraph = open(filePath, 'rb')
    msgTempGraph = MIMEImage(tempGraph.read())
    tempGraph.close()
    message.attach(msgTempGraph)

    server = smtplib.SMTP('', 587)
    server.starttls()
    r = server.login('', '')
    r = server.sendmail('', '', message.as_string())
    server.quit()
    print('Report sent')


def sendReport():
    message = MIMEMultipart()
    message['Subject'] = 'Report from our arduino'
    # Daily temperature
    plt.ioff()
    x = np.linspace(0, 23, (1 * 10))
    fig = plt.figure()
    plt.title("Daily temperature")
    plt.xlabel("Hours")
    plt.ylabel("Temperature (C)")
    plt.plot(x, temperature)
    fileName = 'report-temperature-{}.png'.format(datetime.date.today())
    plt.savefig('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName)

    tempGraph = open('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName, 'rb')
    msgTempGraph = MIMEImage(tempGraph.read())
    tempGraph.close()
    message.attach(msgTempGraph)

    # Daily illumination
    plt.ioff()
    x = np.linspace(0, 23, (1 * 10))
    fig = plt.figure()
    plt.title("Daily illumination")
    plt.xlabel("Hours")
    plt.ylabel("Illumination (%)")
    plt.plot(x, illumination)
    fileName = 'report-illumination-{}.png'.format(datetime.date.today())
    plt.savefig('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName)

    illumGraph = open('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName, 'rb')
    msgIllumGraph = MIMEImage(illumGraph.read())
    illumGraph.close()
    message.attach(msgIllumGraph)

    # Temperature max/min/average
    plt.ioff()
    max_temp = max(temperature)
    min_temp = min(temperature)
    avg_temp = np.mean(temperature)

    plt.figure()
    plt.bar(['Max', 'Min', 'Average'], [max_temp, min_temp, avg_temp])
    plt.title('Tempo report')
    plt.ylabel('Tempo (°C)')

    fileName = 'report-tempo-state-{}.png'.format(datetime.date.today())
    plt.savefig('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName)

    tempo_state = open('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName, 'rb')
    msgTempoState = MIMEImage(tempo_state.read())
    tempo_state.close()
    message.attach(msgTempoState)

    # Illumination max/min/average
    plt.ioff()
    max_illum = max(illumination)
    min_illum = min(illumination)
    avg_illum = np.mean(illumination)

    plt.figure()
    plt.bar(['Max', 'Min', 'Average'], [max_illum, min_illum, avg_illum])
    plt.title('Illumination report')
    plt.ylabel('Illumination')

    fileName = 'report-illum-state-{}.png'.format(datetime.date.today())
    plt.savefig('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName)

    illum_state = open('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName, 'rb')
    msgIllumState = MIMEImage(illum_state.read())
    illum_state.close()
    message.attach(msgIllumState)

    # Activity detector total count
    plt.ioff()
    max_activity = activity.count(1)

    plt.ioff()
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, max_activity, fontsize=15, ha='center')
    plt.axis('off')

    fileName = 'report-activity-state-{}.png'.format(datetime.date.today())
    plt.savefig('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName)

    activity_state = open('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName, 'rb')
    msgActivityState = MIMEImage(activity_state.read())
    activity_state.close()
    message.attach(msgActivityState)


    # Daily activity

    plt.ioff()
    x = np.linspace(0, 23, (1 * 20))
    fig = plt.figure()
    plt.title("Daily activity")
    plt.xlabel("Hours")
    plt.ylabel("Activity (%)")
    plt.plot(x, activity)
    fileName = 'report-activity-daily-{}.png'.format(datetime.date.today())
    plt.savefig('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName)

    activity_daily = open('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName, 'rb')
    msgActivityDailyGraph = MIMEImage(activity_daily.read())
    activity_daily.close()
    message.attach(msgActivityDailyGraph)


    # Secure mode active period

    plt.ioff()

    plt.ioff()
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, format_seconds_to_time(secure_time) + ' secure auto', fontsize=15, ha='center')
    plt.axis('off')

    fileName = 'report-secure-active-period-{}.png'.format(datetime.date.today())
    plt.savefig('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName)

    secure_mode_active_period = open('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName, 'rb')
    msgSecureModeActive = MIMEImage(secure_mode_active_period.read())
    secure_mode_active_period.close()
    message.attach(msgSecureModeActive)

    # Light auto mode active period

    plt.ioff()

    plt.ioff()
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, format_seconds_to_time(light_time) + ' light auto', fontsize=15, ha='center')
    plt.axis('off')

    fileName = 'report-light-auto-active-period-{}.png'.format(datetime.date.today())
    plt.savefig('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName)

    light_auto_mode_active_period = open('C:\\Users\\Azat\\Desktop\\Reports\\' + fileName, 'rb')
    msgLightAutoModeActive = MIMEImage(light_auto_mode_active_period.read())
    light_auto_mode_active_period.close()
    message.attach(msgLightAutoModeActive)



    server = smtplib.SMTP('', )
    server.starttls()
    r = server.login('', '')
    r = server.sendmail('', '', message.as_string())
    server.quit()
    print('Report sent')


def processData(data):
    processedData = {}
    dataList = data.split()
    print(dataList)
    processedData["activity"] = 0

    if "ALERT" in dataList:
        sendNotification()
        processedData["activity"] = 1
        dataList.remove("ALERT")
        print("ALERT")

    if len(dataList) >= 2:
        processedData["temp_value"] = dataList[0]
        processedData["illum_value"] = dataList[1]
        sendTS(processedData)


def sendTS(data):
    print(data)
    # if len(data) == 2:
    #     resp = urllib.request.urlopen("{}&field1={}&field2={}".format(WRITE_URL, data["temp_value"], data["illum_value"]))

    if len(data) == 3:
        resp = urllib.request.urlopen("{}&field1={}&field2={}&field3={}".format(WRITE_URL, data["temp_value"], data["illum_value"], data["activity"]))


def receive(serialCom):
    receivedMessage = ""
    while True:
        if serialCom.in_waiting > 0:
            receivedMessage = serialCom.read(size=serialCom.in_waiting).decode('ascii')
            processData(receivedMessage)

        schedule.run_pending()

        time.sleep(10)


def format_seconds_to_time(seconds_list):
    if not seconds_list:
        return "None"

    total_seconds_sum = sum(seconds_list)

    whole_seconds = math.floor(total_seconds_sum)
    milliseconds = total_seconds_sum - whole_seconds

    hours = whole_seconds // 3600
    minutes = (whole_seconds % 3600) // 60
    seconds = whole_seconds % 60

    formatted_time = f"{hours} hours, {minutes} minutes, {seconds + milliseconds:.3f} seconds"

    return formatted_time


schedule.every().day.at("23:23").do(sendReport)


serialCommunication = serial.Serial(PORT, BAUD_RATE)

email = imaplib.IMAP4_SSL('')
email.login('', '')

checkEmailThread = Thread(target=checkMail, args=(email, serialCommunication,))
checkEmailThread.start()

receivingThread = Thread(target=receive, args=(serialCommunication,))
receivingThread.start()
