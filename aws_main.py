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
    - Ændrer crontab fra aws_source.py til aws_main.py
    - Exceptions
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

# Variabler til fejl-logning
filePath        = '/home/pi/Documents/project1/Vandspil/errorlog.txt'


# PROGRAM KODE STARTER HER
try:
    
    running = True
    MCP3008 = aws.initADC(1)

    while running:
        
        roomTemp  = round(aws.readADC(MCP3008,roomTempChannel,vref),1)
        pipeTemp  = round(aws.readADC(MCP3008,pipeTempChannel,vref),1)
        print(f'Rum temp: {roomTemp} | Rør temp: {pipeTemp}')
            
        aws.thingspeakTransfer(channelID, writeKey, roomTemp, pipeTemp)
    
        trigger,counter,timeTrigger  = aws.checkTempState(roomTemp, pipeTemp, counter, timeTrigger)
        
        if trigger:
            aws.emailAlert(smtpHost, smtpPort, sMail, sPass, rMail)
            aws.smsAlert(accountSID, authToken, smsMessage, sNum, rNum)
except Exception as errorMsg:
    aws.errorLog(filePath, errorMsg)
    aws.restart()