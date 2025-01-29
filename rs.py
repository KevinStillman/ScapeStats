import asyncio
import wom
import requests
import json
from datetime import datetime
 
# getting data
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
	xpGained = overallData['value']['data']['skills']['overall']['experience']['gained']
	lvlGained = overallData['value']['data']['skills']['overall']['level']['gained']
	totalLvl = overallData['value']['data']['skills']['overall']['level']['end']
 
	print(f"XP Gained: {xpGained} \nLevels Gained: {lvlGained} \nTotal Level: {totalLvl}")
	print(f"Latest Achievement: {newestAchievement}")
 
# Run the fetch_data function
asyncio.run(fetch_data())
