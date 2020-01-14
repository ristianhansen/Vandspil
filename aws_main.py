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

##############################################################################
"""
To do:
    - E-mail og SMS funktioner skal kun kunne køre 1 gang i døgnet
    - Kommentarer
    - Exception handling
    - Github synkronisering
"""
##############################################################################

import aws_functions as aws

# Variabler til trigger-funktion
counter = 0
timeTrigger = 10**100

# Variabler for kommunikation med ADC over SPI.
vref = 5
roomTempChannel = 0b10110000
pipeTempChannel = 0b11000000

# Variabler for afsending af data til ThingSpeak.
channelID       = 917419
writeKey        = 'EBUYTMJKFLG4934Z'

# Variabler for afsending af e-mail alarm
smtpHost        = 'smtp.gmail.com'
smtpPort        = 587
sMail           = 'avoidwaterpillage@gmail.com'
sPass           = 'vand12345'
rMail           = '1080486@ucn.dk'

# Variabler for afsending af sms alarm
accountSID      = 'ACb46169ce269feae4771b07bbcc18746a'
authToken       = 'baba7a7f332fb1fbc2431744804e2f76'
smsMessage      = 'Der er registreret vandspild på din enhed.'
sNum            = '+19726395292'
rNum            = '+4593886999' # Nummeret skal være verified på Twilio.

# PROGRAM KODE STARTER HER

running = True
MCP3008 = aws.initADC(1)

try:
    while running:
        
        roomTemp  = round(aws.readADC(MCP3008,roomTempChannel,vref),1)
        pipeTemp  = round(aws.readADC(MCP3008,pipeTempChannel,vref),1)
        print(f'Rum temp: {roomTemp} | Rør temp: {pipeTemp}')
            
        aws.thingSpeakTransfer(channelID, writeKey, roomTemp, pipeTemp)
    
        trigger,counter,timeTrigger  = aws.checkTempState(roomTemp, pipeTemp, counter, timeTrigger)
        
        if trigger:
            aws.AlarmEmail(smtpHost, smtpPort, sMail, sPass, rMail)
            aws.SMSMsg(accountSID, authToken, smsMessage, sNum, rNum)
except:
    aws.restart()