##############################################
 #  @filename   :   main.py                 #
 #  @brief      :   2.7inch e-paper display #
 #  @author     :   Kevin Stillman          #
##############################################



import time
import epd2in7
import requests
import json
import RPi.GPIO as GPIO
import python_weather
import asyncio
import os
from bs4 import BeautifulSoup
from PIL import Image 
from PIL import ImageFont
from PIL import ImageDraw
import wom
from datetime import datetime

 
# getting data
xpGained = 0
totalLvl = 0
lvlGained = 0
async def getData(data_type):
    # Instantiate the WOM client
    client = wom.Client()
 
    # Start the WOM client
    await client.start()
 
    # Set properties for API
    client.set_api_base_url("https://api.wiseoldman.net/v2")
    client.set_api_key("bfg8cifkm38okshnw7kea3z5")
    client.set_user_agent("@ThickJuiciness")
 
    # Data request
    if data_type == "overallData":
        result = await client.players.get_gains("ciwa", period=wom.Period.Day)
 
    elif data_type == "achievementData":
        result = await client.players.get_achievements("ciwa")
 
    # Check if the request was successful
    if result.is_ok:
        result = result.to_dict()
 
    # Close the client
    await client.close()
    return result
 
 
# Fetch overallData and achievementData
async def fetch_data():
        overallData = await getData("overallData")
        achievementData = await getData("achievementData")
 
    # Extract Achievement data (newest item)
        sortedAchievementData = sorted(achievementData["value"], key=lambda x: datetime.fromisoformat(x["createdAt"].replace("Z", "+00:00")), reverse=True)
        newestAchievement = sortedAchievementData[0]["name"]
 
    # Extract specific values from the overallData
        global xpGained
        global lvlGained
        global totalLvl
        xpGained = overallData['value']['data']['skills']['overall']['experience']['gained']
        xpGained = int(xpGained)
        lvlGained = overallData['value']['data']['skills']['overall']['level']['gained']
        lvlGained = int(lvlGained)
        totalLvl = overallData['value']['data']['skills']['overall']['level']['end']
        totalLvl = int(totalLvl)
 
# Run the fetch_data function
asyncio.run(fetch_data())


screens = ['osrs']
currentscreen = 0

def screenchanged(screen):
    if screen == 0 or screen == 'osrs':
        currentscreen = 0
    elif screen == 1 or screen == 'tbd':
        currentscreen = 1
        
bc = 1

    
def button_press(channel):
    if channel == button1_pin:
        print(f'Button 1 pressed! Refreshing..')
        buildScreen("osrs")

    if channel == button2_pin:
        print('no use yet!')
    
    if channel == button3_pin:
        print('Button 3 pressed! Clearing screen..')
        buildScreen("clear")
        print('Button 3 pressed, clearing screen.')
    
    if channel == button4_pin:
        print('Button 4 pressed! This is the quit button, goodbye!')
        quit()
        
def buildScreen(screen):
    if screen == 'osrs' or screen == 1:
            #init building to screen
        epd = epd2in7.EPD()
        epd.init()
        image = Image.new('1', (epd2in7.EPD_WIDTH, epd2in7.EPD_HEIGHT), 255)    # 255: clear the image with white
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 18)
        global totalLvl
        global xpGained
        global lvlGained
        
        
        # Title
        draw.text((2, 0), f'Ciwa - {totalLvl}/2277', font = font, fill = 0) #Title Text
        
        #data (Section 1)
        draw.text((15, 25), "24 Hour Gains", font = font, fill = 0)
        draw.line((0, 40, 180, 40), fill = 0)#horizontal bar under title text
        
        draw.text((50, 75), f"{str(xpGained)}", font = font, fill = 0)
        draw.text((20, 100), "XP Acquired ", font = font, fill = 0)
        
        draw.text((85, 150), f"{lvlGained}", font = font, fill = 0)
        draw.text((10, 175), "Levels Gained", font = font, fill = 0)


        
        
  
        

        epd.display_frame(epd.get_frame_buffer(image))
        print('Draw Executed via BuildScreen command')
        
    if screen == "clear" or screen == 2:
        epd = epd2in7.EPD()
        epd.init()
        image = Image.new('1', (epd2in7.EPD_WIDTH, epd2in7.EPD_HEIGHT), 255)    # 255
        draw = ImageDraw.Draw(image)
        
    if screen == 'weather' or screen == 3:
            #init building to screen and clearing
        epd = epd2in7.EPD()
        epd.init()
        image = Image.new('1', (epd2in7.EPD_WIDTH, epd2in7.EPD_HEIGHT), 255)    # 255
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 18)
        
#       epd.display_frame(epd.get_frame_buffer(image)) # 125 to 129 clear hte screen
        
        #prepare weather data and weather screen frame
    
        draw.text((35, 5), 'Norfolk, Va', font = font, fill = 0)
        draw.text((105, 40), 'F', font = font, fill = 0)
        draw.text((10, 60), 'Chichester PA', font = font, fill = 0)
        draw.text((105, 80), 'F', font = font, fill = 0)
        
        epd.display_frame(epd.get_frame_buffer(image)) # draw non-live data
        print('line 162 draw executed')
        time.sleep(3)
        
        # data
        try:
            nfktemp = str(asyncio.run(getweather('Norfolk VA')))
            try:
                chitemp = str(asyncio.run(getweather('Chichester PA')))
            except:
                weatherbroken = True
                print('aw bud the chi temp is fucked')
                
        except:
            weatherbroken = True
            print('aw bud the nfk temp is fucked')
        
        
        
        else:
            draw.text((80, 80), chitemp, font = font, fill = 0, size = 40)
            draw.text((80, 40), nfktemp, font = font, fill = 0, size = 40)
            epd.display_frame(epd.get_frame_buffer(image))
            print('line 181 draw executed')
            
        if weatherbroken:
            image = Image.new('1', (epd2in7.EPD_WIDTH, epd2in7.EPD_HEIGHT), 255)    # clear screen
            draw = ImageDraw.Draw(image)                                            # clear screen
            epd.display_frame(epd.get_frame_buffer(image))                          # clear screen
            draw.text((5, 5), 'Weather broken', font = font, fill = 0)
            
            epd.display_frame(epd.get_frame_buffer(image))
        
# WEATHER

async def getweather(loc):
    async with python_weather.Client(format=python_weather.IMPERIAL) as client:
        weather = await client.get(loc)
        temp = weather.current.temperature
        return temp
        

# BUTTONS
GPIO.setmode(GPIO.BCM)

button1_pin = 5
button2_pin = 6
button3_pin = 13
button4_pin = 19

# set the input pins as pull-downs to avoiud false inputs

GPIO.setup(button1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button3_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button4_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(button1_pin, GPIO.FALLING, callback = button_press, bouncetime = 200)
GPIO.add_event_detect(button2_pin, GPIO.FALLING, callback = button_press, bouncetime = 200)
GPIO.add_event_detect(button3_pin, GPIO.FALLING, callback = button_press, bouncetime = 200)
GPIO.add_event_detect(button4_pin, GPIO.FALLING, callback = button_press, bouncetime = 200)





buildScreen(1)


run = True

while run:
    break
    
    
    
if __name__ == "__main__":
    asyncio.run(main())
