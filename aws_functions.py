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

#import spidev
from time import time, ctime, sleep
import requests
import smtplib
from twilio.rest import Client #Twilio skal installeres (pip install twilio)


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

def thingSpeakTransfer(channelID, writeKey, temp1, temp2):
    """
    Denne funktion tager som input Thingspeak kanal ID, Thingspeak write key,
    og 2 temperaturer. Dataen bliver herefter gemt i en dictionary, 
    og sendes herefter til Thingspeak som json-data.
    """
    #time = find ud af hvordan den finder ud af det, tid?
    try:
        url = f"https://api.thingspeak.com/channels/{channelID}/bulk_update.json"
        
        timestamp = datetime.now(tz = pytz.timezone('CET')).isoformat()
        data = {
                "write_api_key" : writeKey,
                "updates"       : [{
                        "created_at"    : timestamp,
                        "field1"        : temp1,
                        "field2"        : temp2
                        }]}
        
        response = requests.post(url,json=data)
        status = response.status_code
        
    except:
        print("ThingSpeak transfer failed.")
    return

###############################################################################
# Trigger-funktion

def checkTempState(roomTemp, pipeTemp):
    """
    Denne funktion modtager som input rumtemperatur og rørtemperatur,
    sammenligner de to, og returnerer en booleansk værdi afhængigt af
    differencen. Hvis der er en difference på mere end 1 grad over en
    periode på 1 døgn, returnerer funktionen True, hvis ikke, False.
    """
    tempDiff = roomTemp-pipeTemp
    trigger = False
    timeTrigger = 90000000*5
    if tempDiff < -1 or tempDiff > 1:
        timeTrigger = time.time() + 5
#        timeTrigger = time.time() + 60*1440 Original
    if time.time() >= timeTrigger:
        trigger = True

    return trigger

###############################################################################
# E-mail alarm funktion
    
def AlarmEmail(smtpHost, smtpPort, sMail, sPass, rMail):
    """
    Hvad glor du på?
    """
    # Laver en SMTP session
    s = smtplib.SMTP(smtpHost, smtpPort)
     
    # Starter tls for sikkerhed.
    s.starttls()
     
    #  afsenders credidentials
    s.login(sMail, sPass)
     
    # Variabel med besked.
    textmessage = "Du har vandspild."
    message = 'Subject: {}\n\n{}'.format('VANDSPILD!', textmessage)
    
     
    # send emailen
    s.sendmail(sMail, rMail, message)
     
    # lukker smtp sessionen igen.
    s.quit()
    return

###############################################################################
# SMS alarm funktion (Husk at lav ny demo bruger)

def SMSMsg(accountSID,authToken,messageBody,sNum,rNum):
    """
    Kommentar tekst
    """
    client = Client(accountSID, authToken)
    
    #Danner beskeden
    message = client.messages \
                    .create(
                         body=messageBody,
                         from_=sNum,
                         to=rNum
                     )
    return

###############################################################################
# Test funktion
    
def timeTest():
    f = datetime.now()
    print(f)
    return