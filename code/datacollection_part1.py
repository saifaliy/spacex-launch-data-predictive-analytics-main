# Import requests for handling HTTP requests
# Import pandas for data manipulation and analysis
# Import numpy for numerical operations
# Import datetime for handling date and time operations

import requests
import pandas as pd
import numpy as np
import datetime

# Set pandas display options to show all columns and full content of each column
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

# Initialize an empty list to store booster version names
def getBoosterVersion(data):
    for x in data['rocket']:
        if x:
            response = requests.get("https://api.spacexdata.com/v4/rockets/"+str(x)).json()
            BoosterVersion.append(response['name'])

# Initialize empty lists to store launch site information
def getLaunchSite(data):
    for x in data['launchpad']:
        if x:
            response = requests.get("https://api.spacexdata.com/v4/launchpads/"+str(x)).json()
            Longitude.append(response['longitude'])
            Latitude.append(response['latitude'])
            LaunchSite.append(response['name'])


# Initialize empty lists to store payload information
def getPayloadData(data):
    for load in data['payloads']:
        if load:
            response = requests.get("https://api.spacexdata.com/v4/payloads/"+str(load)).json()
            PayloadMass.append(response['mass_kg'])
            Orbit.append(response['orbit'])


# Initialize empty lists to store core information
def getCoreData(data):
    for core in data['cores']:
        if core['core']:
            response = requests.get("https://api.spacexdata.com/v4/cores/"+str(core['core'])).json()
            Block.append(response['block'])
            ReusedCount.append(response['reuse_count'])
            Serial.append(response['serial'])
        else:
            Block.append(None)
            ReusedCount.append(None)
            Serial.append(None)
        Outcome.append(str(core['landing_success']) +' '+ str(core['landing_type']))
        Flights.append(core['flight'])
        GridFins.append(core['gridfins'])
        Reused.append(core['reused'])
        Legs.append(core['legs'])
        LandingPad.append(core['landpad'])

# Request rocket launch data from SpaceX API
spacex_url = "https://api.spacexdata.com/v4/launches/past"
response = requests.get(spacex_url)
print(response.content)

# Request and parse the SpaceX launch data (JSON) using the GET request
static_json_url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/API_call_spacex_api.json'

# Should get 200 status response code for the request to be successful
response = requests.get(static_json_url)
response.status_code

# Converting the JSON response into a Pandas DataFrame
from pandas import json_normalize
# Decode the response content as JSON
spacex_url = response.json()
# Convert the JSON result into a dataframe
spacex_df = json_normalize(spacex_url)
# Display the first 5 rows
spacex_df.head()

# Lets take a subset of our dataframe keeping only the features we want and the flight number, and date_utc.
data = spacex_df[['flight_number', 'date_utc', 'rocket', 'launchpad', 'payloads', 'cores']]

# Remove rows with multiple cores because those are falcon rockets with 2 extra rocket boosters and rows that have multiple payloads in a single rocket
data = data[data['cores'].map(len) == 1]
data = data[data['payloads'].map(len) == 1]

# Payloads and cores are lists of size 1, we need to convert them to just their single values
data['payloads'] = data['payloads'].map(lambda x: x[0])
data['cores'] = data['cores'].map(lambda x: x[0])

# Convert the date_utc column to datetime format
data['date_utc'] = pd.to_datetime(data['date_utc']).dt.date

# Using the date_utc, we will restrict the launch dates
data = data[data['date_utc'] <= datetime.date(2020, 11, 13)]

# From the rocket we would like to learn the booster name
# From the payload we would like to learn the mass of the payload and the orbit that it is going to
# From the launchpad we would like to know the name of the launch site being used, the longitude, and the latitude.
# From cores we would like to learn the outcome of the landing, the type of the landing, number of flights with that core, whether gridfins were used, whether the core is reused, whether legs were used, the landing pad used, the block of the core which is a number used to seperate version of cores, the number of times this specific core has been reused, and the serial of the core.
# The data from these requests will be stored in lists and will be used to create a new dataframe.

#Global variables 
BoosterVersion = []
PayloadMass = []
Orbit = []
LaunchSite = []
Outcome = []
Flights = []
GridFins = []
Reused = []
Legs = []
LandingPad = []
Block = []
ReusedCount = []
Serial = []
Longitude = []
Latitude = []

# Call the functions to fill the lists
getBoosterVersion(data)
getLaunchSite(data)
getPayloadData(data)
getCoreData(data)

# Create a new dataframe with the information collected
launch_dict = {'FlightNumber': list(data['flight_number']),
'Date': list(data['date_utc']),
'BoosterVersion':BoosterVersion,
'PayloadMass':PayloadMass,
'Orbit':Orbit,
'LaunchSite':LaunchSite,
'Outcome':Outcome,
'Flights':Flights,
'GridFins':GridFins,
'Reused':Reused,
'Legs':Legs,
'LandingPad':LandingPad,
'Block':Block,
'ReusedCount':ReusedCount,
'Serial':Serial,
'Longitude': Longitude,
'Latitude': Latitude}

# Create a dataframe from launch_dict
launch_df = pd.DataFrame(launch_dict)

# Show the head of the dataframe
launch_df.head()

# Filter the dataframe to only include Falcon 9 launches
data_falcon9 = launch_df[launch_df['BoosterVersion'] != 'Falcon 1']

# Reset FlgihtNumber to start from 1 and increase sequentially
data_falcon9.loc[:,'FlightNumber'] = list(range(1, data_falcon9.shape[0]+1))
data_falcon9

# Data Wrangling
# Missing rows
data_falcon9.isnull().sum()
# The LandingPad column will retain None values to represent when landing pads were not used.

# Calculate the mean value of the PayloadMass column
payload_mass_mean = data_falcon9['PayloadMass'].mean()

# Replace the np.nan values with its mean value
data_falcon9['PayloadMass'].replace(np.nan, payload_mass_mean, inplace=True)

# Verify that there are no missing values left in PayloadMass
data_falcon9['PayloadMass'].isnull().sum()
# Now we should have no missing values in our dataset except for in LandingPad

data_falcon9.to_csv('dataset_part_1.csv', index=False)