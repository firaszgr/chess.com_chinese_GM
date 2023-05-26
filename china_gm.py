#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests


# In[2]:


#Get user names of chess.com Grand Masters
url = "https://api.chess.com/pub/titled/GM"
response = requests.get(url)
gm_list = response.json()


# In[3]:


#Since the gm_list type is dictionary, we'll convert it to a data frame using pandas
import pandas as pd
GM = pd.DataFrame(gm_list)
GM.head()


# In[4]:


#Get the number of GMs in chess.com
len(GM)


# In[5]:


#Get chess.com Chinese players usernames
url_chinese_players="https://api.chess.com/pub/country/CN/players"
response_chinese_players=requests.get(url_chinese_players)
chinese_players=response_chinese_players.json()
chinese_players=pd.DataFrame(chinese_players,columns=["players"])
chinese_players.head()


# In[6]:


#Now we need to see which ones are GM. Consequently, we'll need to create an inner join on the players (username) column
chinese_GM = pd.merge(GM, chinese_players, on="players", how="inner")
print(len(chinese_GM))


# In[7]:


#We do have now the list of Grand Masters from China on chess.com. Let's extract their profile information 
player_info_list = []

# Iterate over the dataframe rows
for index, row in chinese_GM.iterrows():
    username = row["players"]
    url = f"https://api.chess.com/pub/player/{username}"
    response = requests.get(url)
    profile = response.json()
    player_info_list.append(profile)

# Create a dataframe from the player information list
chinese_gm_info = pd.DataFrame(player_info_list)

# Print the player information dataframe
chinese_gm_info.head(20)


# In[8]:


print(chinese_gm_info.columns)


# In[9]:


player_stats_list = []

# Iterate over the DataFrame rows
for index, row in chinese_gm_info.iterrows():
    username = row["username"]
    url = f"https://api.chess.com/pub/player/{username}/stats"
    response = requests.get(url)
    stats = response.json()
    stats["username"] = username  # Add the username to the stats dictionary
    player_stats_list.append(stats)

# Create a DataFrame from the player statistics list
player_stats_df = pd.DataFrame(player_stats_list)


# In[10]:


player_stats_df.head()


# In[11]:


#We're going to work only on the popular category chess_blitz
player_stats_df = player_stats_df[['chess_blitz','username']]
player_stats_df.head()


# In[12]:


#As we can see, the data from chess_blitz appears to be in json format.
player_stats_df["chess_blitz"][0]


# In[13]:


#Let's convert it and split json data to separate columns to get a more readable format 

import json

username_column = player_stats_df["username"]

# Convert the "chess_blitz" column data to JSON
column_data = player_stats_df["chess_blitz"].tolist()
data_string = json.dumps(column_data)

# Normalize the JSON data and split it into separate columns
chinese_gm_blitz = pd.json_normalize(json.loads(data_string))

# Concatenate the "username" column with the resulting dataframe
chinese_gm_blitz["username"] = username_column

# Print the resulting dataframe
print(chinese_gm_blitz)


# In[22]:


#Now as we have two tables: chinese_gm_info containing data about chinese Grand Masters profiles on chess.com
#And chinese_gm_blitz containing data about their blitz games, let's merge the two tables together based on "username"

china_gm_data= pd.merge(chinese_gm_info, chinese_gm_blitz, on="username")

# Print the resulting merged dataframe head
china_gm_data.head()


# In[24]:


#Converting timestamps to a regular format
date_columns = ['last.date', 'best.date', 'last_online', 'joined']
china_gm_data[date_columns] = china_gm_data[date_columns].apply(lambda x: pd.to_datetime(x, unit='s'))
china_gm_data.head()


# In[25]:


#Finally, let's save our table in csv file
china_gm_data.to_csv("china_gm_data.csv",index=False)

