import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import re
from urllib.parse import urlparse

# see https://github.com/yortos/imessage-analysis/blob/master/imessages-data-extract-and-prep.ipynb

# find chat.db and establish a connection
conn = sqlite3.connect('/Users/joemarlo/Library/Messages/chat.db')
cur = conn.cursor()

# query the database to get all the table names
cur.execute(" select name from sqlite_master where type = 'table' ")

for name in cur.fetchall():
    print(name)

# create pandas dataframe
messages = pd.read_sql_query('''select *, datetime(date/1000000000 + strftime("%s", "2001-01-01") ,"unixepoch","localtime")  as date_utc from message''', conn)
handles = pd.read_sql_query("select * from handle", conn)
chat_message_joins = pd.read_sql_query("select * from chat_message_join", conn)

# these fields are only for ease of datetime analysis (e.g., number of messages per month or year)
messages['message_date'] = messages['date']
messages['timestamp'] = messages['date_utc'].apply(lambda x: pd.Timestamp(x))
messages['date'] = messages['timestamp'].apply(lambda x: x.date())
messages['month'] = messages['timestamp'].apply(lambda x: int(x.month))
messages['year'] = messages['timestamp'].apply(lambda x: int(x.year))

# rename the ROWID into message_id, because that's what it is
messages.rename(columns={'ROWID' : 'message_id'}, inplace = True)

# rename appropriately the handle and apple_id/phone_number as well
handles.rename(columns={'id' : 'phone_number', 'ROWID': 'handle_id'}, inplace = True)

# merge the messages with the handles
merge_level_1 = pd.merge(messages[['text', 'handle_id', 'date','message_date' ,'timestamp', 'month','year','is_sent', 'message_id']], handles[['handle_id', 'phone_number']], on ='handle_id', how='left')

# and then that table with the chats
df_messages = pd.merge(merge_level_1, chat_message_joins[['chat_id', 'message_id']], on = 'message_id', how='left')

print(len(df_messages))

# save the combined table for ease of read for future analysis
df_messages.to_csv('~/Desktop/imessages.csv', index = False, encoding='utf-8')

# check range of dates
df_messages['date'].min(), df_messages['date'].max()

# number of messages per day
plt.plot(df_messages.groupby('date').size())
plt.xticks(rotation='45')

# how many messages you have sent versus received
df_messages.groupby('is_sent').size()

# number of messages per month and year
df_messages.groupby('month').size()
df_messages.groupby('year').size()

# filter to just the group chat
group_chat = df_messages[df_messages["chat_id"] == 2].reset_index()

# create lookup table of numbers to names
name_lookup = pd.DataFrame({'phone_number': group_chat.phone_number.unique(),
'contact': ['Joe', 'Doug', 'Sam', 'John', 'Travis']})

# create df of just the group chat with names instead of numbers
name_lookup['phone_number'] = name_lookup.phone_number.astype(str)
group_chat['phone_number'] = group_chat.phone_number.astype(str)
four_locos = group_chat.merge(name_lookup, on='phone_number', how='left').reset_index()

# reduce the columns to just the key connections
four_locos = four_locos[['date', 'contact', 'text']]

# find URLs
four_locos['url'] = four_locos['text'].str.extractall('(https?://[^>]+)').unstack()

# parse out the URL to just the domain name
def extract_domain(url):
    if isinstance(url, str):
        net_loc = urlparse(url).netloc
        domain = re.sub("http://|https://|www\\.", "", net_loc)
        return(domain)
    else:
        return('')

four_locos['url'] = four_locos['url'].apply(extract_domain)

# combine domains into one per site
youtube = ["youtube.com", "youtu.be", "m.youtube.com"]
google = ["google.com", "goo.gl"]
reddit = ['reddit.com', 'i.redd.it', 'v.redd.it']
nyt = ["mobile.nytimes.com", "nytimes.com", "nyti.ms"]
imgur = ['imgur.com', 'm.imgur.com']

def consolidate_domains(domain):
    if domain in youtube: return("youtube.com")
    if domain in google: return("google.com")
    if domain in reddit: return("reddit.com")
    if domain in nyt: return("nytimes.com")
    if domain in imgur: return('imgur.com')
    return(domain)

four_locos['url'] = four_locos['url'].apply(consolidate_domains)

# save to csv
four_locos.to_csv("four_locos.csv", index=False)

# close connections
cur.close()
conn.close()
