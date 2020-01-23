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
rMail           = '1080486@ucn.dk' # Mikkels studiemail

# Variabler for afsending af sms alarm
accountSID      = 'AC00f16cee6bdebbac72f4da3d7b8a819f'
authToken       = '4766fbfeb6871003e79d0752db2cdaaa'
smsMessage      = 'Der er registreret vandspild på din enhed.'
sNum            = '+12564459376'
rNum            = '+4522355213' # Nummeret skal være verified på Twilio.

# Variabler til fejl-logning
filePath        = '/home/pi/Documents/project1/Vandspil/errorlog.txt'

try:
    
    MCP3008 = aws.initADC(1)

    while True:
        
        roomTemp  = round(aws.readADC(MCP3008,roomTempChannel,vref),1)
        pipeTemp  = round(aws.readADC(MCP3008,pipeTempChannel,vref),1)
        print(f'Rum temp: {roomTemp} | Rør temp: {pipeTemp}')
            
        aws.thingspeakTransfer(channelID, writeKey, roomTemp, pipeTemp)
    
        trigger,counter,timeTrigger  = aws.checkTempState(roomTemp, pipeTemp, counter, timeTrigger)
        
        if trigger:
            aws.emailAlert(smtpHost, smtpPort, sMail, sPass, rMail)
            aws.smsAlert(accountSID, authToken, smsMessage, sNum, rNum)
except KeyboardInterrupt:
    counter = 0
    timeTrigger = 10*100
except Exception as errorMsg:
    aws.errorLog(filePath, errorMsg)
    aws.restart()
    counter = 0
    timeTrigger = 10*100