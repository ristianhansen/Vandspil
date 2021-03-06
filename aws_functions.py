# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 11:35:16 2019

@authors:
    Christian Hansen,
    Kasper Griebel Mogensen,
    Birita Mortensen, 
    Jan Nielsen,
    Mikkel Vardinghus.
"""

import spidev
from time import time, sleep, ctime
import requests
import smtplib
from twilio.rest import Client #Twilio skal installeres (pip install twilio)
import pytz
from datetime import datetime
from subprocess import Popen, PIPE

# Filstil til fejlskrivning
filePath        = '/home/pi/Documents/project1/Vandspil/errorlog.txt'

###############################################################################
# Funktion til initialisering af ADC'en.

def initADC(SSn=0):
    """
    Initialiserer ADC chippen. SSn = Slave Select number.
    """
    spi = spidev.SpiDev()
    spi.open(0,SSn)
    spi.max_speed_hz = 50000

    return spi
    
###############################################################################
# Læs data fra ADC funktion

def readADC(ADC, channel, vref):
    """
    Sender 3 bytes, forespørgsel om data fra slave.
    Første indeks i listen signalerer vi vil læse data.
    Andet indeks specificerer hvilken kanal.
    Tredje indeks er ligegyldig data, som dog stadig skal sendes.
    """
    reply       =    ADC.xfer2([0b00000001,channel, 0b00000000])
    roomValue   =    ((reply[1]&3) << 8) + reply[2]
    roomVolts   =    (roomValue*vref)/1024
    roomTemp    =    roomVolts/(10.0/1000)
    
    return roomTemp

###############################################################################
# Thingspeak overførselsfunktion

def thingspeakTransfer(channelID, writeKey, temp1, temp2):
    """
    Denne funktion tager som input Thingspeak kanal ID, Thingspeak write key,
    og 2 temperaturer. Dataen bliver herefter gemt i en dictionary, 
    og sendes herefter til Thingspeak som json-data.
    """

    try:
        url = f"https://api.thingspeak.com/channels/{channelID}/bulk_update.json"
        
        timeStamp = datetime.now(tz = pytz.timezone('CET')).isoformat()
        data = {
                "write_api_key" : writeKey,
                "updates"       : [{
                        "created_at"    : timeStamp,
                        "field1"        : temp1,
                        "field2"        : temp2
                        }]}
        
        requests.post(url,json=data)
        #response = requests.post(url,json=data)
        #status = response.status_code
        
    except Exception as errorMsg:
        errorLog(filePath, errorMsg)
        pass
        
    return

###############################################################################
# Trigger-funktion

def checkTempState(roomTemp, pipeTemp, counter, timeTrigger):
    """
    Modtager som input rumtemperatur, rørtemperatur, counter og et tidsstempel.
    
    De to temperaturer sammenlignes, og såfremt der er forskel på mere end 1
    grad, samtidig med at counteren er 0, skabes et nyt tidsstempel,
    og der bliver lagt 1 til counteren.
    
    Normaliserer temperaturforskellen sig nulstiller tidsstempel og counter.
    
    Tidsstemplet bliver herefter sammenlignet med nuværende tid,
    og såfremt differencen vedvarer i et døgn returnerer funktionen True på
    trigger variablen.
    """
    trigger = False
    tempDiff = roomTemp-pipeTemp
    
    if (tempDiff < -1 or tempDiff > 1):
        tempTrigger = True
    else:
        tempTrigger = False
        
    if tempTrigger and counter == 0:
        timeTrigger = time() + 60*1440
        counter += 1
    
    if not tempTrigger:
        counter = 0
        timeTrigger = 10**100
            
    if time() >= timeTrigger:
        print("Der er sendt besked")
        trigger = True
        counter = 0

    return trigger, counter, timeTrigger

###############################################################################
# E-mail alarm funktion
    
def emailAlert(smtpHost, smtpPort, sMail, sPass, rMail):
    """
    Funktion til at give besked om vandspild over email.
    """
    timeStamp = ctime()
    try:
        # Laver en SMTP session
        s = smtplib.SMTP(smtpHost, smtpPort)
         
        # Starter tls (transport layer security) for sikkerhed.
        s.starttls()
         
        #  afsenders credidentials
        s.login(sMail, sPass)
         
        # Variabel med besked.
        textmessage = f"Du har vandspild. Sendt {timeStamp}"
        message = 'Subject: {}\n\n{}'.format('VANDSPILD!', textmessage)
        
        # send emailen
        s.sendmail(sMail, rMail, message)
        
        # lukker smtp sessionen igen.
        s.quit()
    except Exception as errorMsg:
        errorLog(filePath, errorMsg)
        pass
    return

###############################################################################
# SMS alarm funktion (Husk at lav ny demo bruger)

def smsAlert(accountSID,authToken,messageBody,sNum,rNum):
    """
    Funktion til at give besked om vandspild over sms.
    
    Hej Ib og/eller Henning. Læser i det her?
    """
    try:
        client = Client(accountSID, authToken)
        
        #Danner beskeden
        message = client.messages \
                        .create(
                             body=messageBody,
                             from_=sNum,
                             to=rNum
                         )
        print(message)
    except Exception as errorMsg:
        errorLog(filePath, errorMsg)
        pass
    return

###############################################################################
# Funktion til at genstarte Raspberry Pi'en. Brugt i tilfælde af fejl.

def restart():
    """
    Funktion til at genstarte Raspberry Pi'en. Bliver anvendt i tilfælde af
    at programmet crasher.
    """
    sleep(60)
    command = "/usr/bin/sudo /sbin/shutdown -r now"
    process = Popen(command.split(), stdout=PIPE)
    output = process.communicate()[0]
    print(output)
    return

###############################################################################
# Funktion til at logge fejlkoder.

def errorLog(filePath, errorMsg):
    """
    
    """
    try:
        timeStamp = ctime()
        logMsg = timeStamp + ":" + "\t" + str(errorMsg) + "\n"
        with open(filePath, mode="a") as f:
            f.write(str(logMsg))
    except FileNotFoundError:
        pass
    except PermissionError:
        pass
    finally:
        f.close()
    return