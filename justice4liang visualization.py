
# coding: utf-8

# In[115]:

# Load data from pickle files
get_ipython().magic(u'pwd')
get_ipython().magic(u'cd "C:/Users/xxx"')

import jupyter_client
import ipykernel

import sys
import sqlite3
import time
import datetime
from pprint import pprint
import string
import itertools
import unicodedata 
import geocoder

from numpy import random, asarray, linspace, corrcoef
import pandas as pd
from pandas import Series

pd.set_option('display.max_columns', 100)
pd.set_option('max_colwidth',300)

get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot as plt
from pylab import* 

df_all = pd.read_pickle("df_all.pkl")
geo_df = pd.read_pickle("geo_df.pkl")
time_series_plot = pd.read_pickle("time_series_plot.pkl")


# In[1]:

# Load data from the raw SQLite database
get_ipython().magic(u'pwd')
get_ipython().magic(u'cd "C:/Users/XXXX"')

import jupyter_client
import ipykernel

import sys
import sqlite3
import time
import datetime
from pprint import pprint
import string
import itertools
import unicodedata 
import geocoder

from numpy import random, asarray, linspace, corrcoef
import pandas as pd
from pandas import Series

pd.set_option('display.max_columns', 100)
pd.set_option('max_colwidth',300)

get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot as plt
from pylab import* 

# connect to an existing database
con = sqlite3.connect("justice4liang.sqlite")
cur = con.cursor()
df_all = pd.read_sql_query("SELECT * FROM gfw_tweets", con)
#print("this database has:", len(df_all), "tweets.")
con.close()

df_all['created_at'] = pd.to_datetime(df_all['created_at'])
#df_all['created_at'] = df_all['created_at'].apply(lambda x: x.date())
df_all['created_at_copy'] = df_all['created_at'] 
df_all = df_all.sort(['created_at'])
df_all = df_all.set_index(['created_at'])
df_all.index = df_all.index.tz_localize('UTC').tz_convert('US/Eastern')

def rtornot(row):
    if row['retweeted_status'] == "THIS IS A RETWEET --> DOUBLE-CHECK JSON":
        return 1
    return 0

df_all['RT_or_not'] = df_all.apply(lambda row: rtornot(row), axis=1) 
#df_all    
print ("Total # of tweets in filtered PANDAS dataframe:", len(df_all))
df_all.head(2)


# In[2]:

#ones = np.ones(len(all_dates))
idx = pd.DatetimeIndex(df_all.index.strftime("%H:%M %Y/%m/%d"))
trend_df = pd.DataFrame(idx)
trend_df.columns = ['created_time']
trend_df['base_tweet_count'] = np.ones(len(df_all['created_at_copy']))
trend_df['rt_count'] = np.asarray(df_all['retweet_count'])
trend_df['follower_count'] = np.asarray(df_all['from_user_followers_count'])
trend_df['RT_or_not'] = np.asarray(df_all['RT_or_not'])
trend_df['cum_rt_count'] = trend_df.rt_count.cumsum()
trend_df['cum_follower_count'] = trend_df.follower_count.cumsum()
trend_df.head(200)


# In[39]:

hourly_cum_rt_count


# In[3]:

hourly_tweet_count = pd.Series(np.asarray(trend_df['base_tweet_count']), index=idx)
hourly_rt_count = pd.Series(np.asarray(trend_df['rt_count']), index=idx)
hourly_follower_count = pd.Series(np.asarray(trend_df['follower_count']), index=idx)
hourly_cum_rt_count = pd.Series(np.asarray(trend_df['cum_rt_count']), index=idx)
hourly_cum_follower_count = pd.Series(np.asarray(trend_df['cum_follower_count']), index=idx)

def getmax(row):
    return np.amax(row)

tweet_per_hr = hourly_tweet_count.resample('H', how="sum").fillna(0)
rt_per_hr = hourly_rt_count.resample('H', how="sum").fillna(0)
follower_per_hr = hourly_follower_count.resample('H', how="mean").fillna(0)
cum_rt_per_hr = hourly_cum_rt_count.resample('H', how=getmax)
cum_follower_per_hr = hourly_cum_follower_count.resample('H', how=getmax).fillna(0)

len(tweet_per_hr)

time_series_plot = pd.DataFrame(tweet_per_hr)
#time_series_plot = time_series_plot.append(rt_per_hr)
time_series_plot.columns = ['tweet_per_hr']
time_series_plot['rt_per_hr'] = rt_per_hr
time_series_plot['follower_per_hr'] = np.around(follower_per_hr)
time_series_plot['cum_rt_per_hr'] = cum_rt_per_hr
time_series_plot['cum_follower_per_hr'] = cum_follower_per_hr
time_series_plot


# In[4]:

mpl.style.use('fivethirtyeight')

time_series_plot_public = time_series_plot["tweet_per_hr"].plot(kind='line', label = "# of tweets", color = "red",lw=1.5, alpha=0.75,legend=True, x_compat=True, figsize=(18, 14))
xticks(fontsize = 14, rotation = -25, ha ="center")                  #USE THE CUSTOM TICKS
time_series_plot_public.set_xlabel('Time', weight = 'bold', labelpad=15)  #SET X-AXIS LABEL, ADD PADDING TO TOP OF X-AXIS LABEL
time_series_plot_public.set_ylabel('Tweet sent per hour', weight='bold', labelpad=15) #SET Y-AXIS LABEL, ADD PADDING TO RIGHT OF Y-AXIS LABEL
time_series_plot_public.set_title('Tweet sent per hour', fontsize = 14, weight = 'bold')
#xticks(fontsize = 9, rotation = 0, ha= "center")                          #SET FONT SIZE FOR X-AXIS TICK LABELS
yticks(fontsize = 12)                                                      #SET FONT SIZE FOR Y-AXIS TICK LABELS
time_series_plot_public.tick_params(axis='x', pad=55)                                   #SET PADDING ABOVE X-AXIS LABELS
legend(fontsize='medium',loc=1,labelspacing=0.1, frameon=False)#.draggable()
#cumlike_plot.plot(figsize=(100,600))
#cumlike_plot.legend_ = True    
savefig('tweet_count.jpg', bbox_inches='tight', dpi=400, format='jpg')   #SAVE PLOT IN PNG FORMAT


# In[5]:

# Plot for tweet volume by hour
import plotly.plotly as py
from plotly.graph_objs import *
import cufflinks as cf
py.sign_in('YOUR PLOT.LY USERNAME', 'YOUR PLOT.LY API KEY') #More at https://plot.ly/python/user-guide/

from datetime import datetime

time_series_hourly_tweet_volume = time_series_plot[["tweet_per_hr"]]

layout = Layout(
    title="#justice4liang Hourly Tweet Volume as of" + " " + time_series_plot.index[-1].strftime("%H:%M %Y/%m/%d") + " (EST)",
   
    titlefont=Font(
        family='Arial, sans-serif',
        size=22,
        color='black'
    ),
    
    font=Font(
        family='"Droid Sans", sans-serif',
        size=12
    ),
    
    showlegend=False,
    autosize=False,
    width=850,
    height=430,
    xaxis=XAxis(
        title='',
        titlefont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        range=[1440388800000, 1442462400000],
        type='date',
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=True,
        nticks=5,
        ticks='inside',
        ticklen=6,
        tickcolor='rgba(0, 0, 0, 0)',
        tickfont=Font(
            family='"Verdana", monospace',
            size=12,
            color='grey'
        ),
        
        mirror=False,
        gridcolor='white',
        gridwidth=1,
        zerolinecolor='#F6F6F6',
        zerolinewidth=1,
        linecolor='rgba(152, 0, 0, 0.5)',
        linewidth=1.5
    ),
    yaxis=YAxis(
        title='# of tweets',
        titlefont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        range=[-32.55555555555556, 638.5555555555555],
        type='linear',
        autorange=True,
        showgrid=True,
        zeroline=False,
        showline=True,
        nticks=5,
        ticks='',
        ticklen=6,
        tickcolor='rgba(0, 0, 0, 0)',
        tickfont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        mirror=False,
        gridcolor='white',
        gridwidth=1,
        zerolinecolor='#F6F6F6',
        zerolinewidth=1,
        linecolor='rgba(152, 0, 0, 0.5)',
        linewidth=1.5
    ),
    legend=Legend(
        x=0.9013254786450663,
        y=1.132,
        traceorder='normal',
        font=Font(
            family='Arial, sans-serif',
            size=12,
            color='#666666'
        ),
        bgcolor='rgb(240, 240, 240)',
        bordercolor='grey',
        borderwidth=0,
        xref='paper',
        yref='paper',
        xanchor='left',
        yanchor='top'
    ),
    paper_bgcolor='rgb(240, 240, 240)',
    plot_bgcolor='rgb(240, 240, 240)',
    bargap=0.2
)

cf.set_config_file(offline=False, world_readable=True, theme='ggplot')

time_series_hourly_tweet_volume.iplot(kind='scatter', layout = layout, filename='justice4liang_hourly_tweet_volume')


# In[6]:

# Plot for retweet per hour
import plotly.plotly as py
from plotly.graph_objs import *
import cufflinks as cf
py.sign_in('xxx', 'xxx')

from datetime import datetime


time_series_hourly_rt_volume = time_series_plot[["rt_per_hr"]]
layout = Layout(
    title="#justice4liang Hourly Retweet Volume as of" + " " + time_series_plot.index[-1].strftime("%H:%M %Y/%m/%d") + " (EST)",
    titlefont=Font(
        family='Arial, sans-serif',
        size=22,
        color='black'
    ),
    font=Font(
        family='"Droid Sans", sans-serif',
        size=12
    ),
    showlegend=False,
    autosize=False,
    width=850,
    height=430,
    xaxis=XAxis(
        title='',
        titlefont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        range=[1440388800000, 1442462400000],
        type='date',
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=True,
        nticks=5,
        ticks='inside',
        ticklen=6,
        tickcolor='rgba(0, 0, 0, 0)',
        tickfont=Font(
            family='"Verdana", monospace',
            size=12,
            color='grey'
        ),
        mirror=False,
        gridcolor='white',
        gridwidth=1,
        zerolinecolor='#F6F6F6',
        zerolinewidth=1,
        linecolor='rgba(152, 0, 0, 0.5)',
        linewidth=1.5
    ),
    yaxis=YAxis(
        title='# of retweets',
        titlefont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        range=[-32.55555555555556, 638.5555555555555],
        type='linear',
        autorange=True,
        showgrid=True,
        zeroline=False,
        showline=True,
        nticks=5,
        ticks='',
        ticklen=6,
        tickcolor='rgba(0, 0, 0, 0)',
        tickfont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        mirror=False,
        gridcolor='white',
        gridwidth=1,
        zerolinecolor='#F6F6F6',
        zerolinewidth=1,
        linecolor='rgba(152, 0, 0, 0.5)',
        linewidth=1.5
    ),
    legend=Legend(
        x=0.9013254786450663,
        y=1.132,
        traceorder='normal',
        font=Font(
            family='Arial, sans-serif',
            size=12,
            color='#666666'
        ),
        bgcolor='rgb(240, 240, 240)',
        bordercolor='grey',
        borderwidth=0,
        xref='paper',
        yref='paper',
        xanchor='left',
        yanchor='top'
    ),
    paper_bgcolor='rgb(240, 240, 240)',
    plot_bgcolor='rgb(240, 240, 240)',
    bargap=0.2
)

cf.set_config_file(offline=False, world_readable=True, theme='ggplot')

time_series_hourly_rt_volume.iplot(kind='scatter', layout = layout, filename='justice4liang_hourly_rt_volume')


# In[7]:

# Plot for audience size per hour
import plotly.plotly as py
from plotly.graph_objs import *
import cufflinks as cf
py.sign_in('xxx', 'xxx')

from datetime import datetime


time_series_hourly_audience = time_series_plot[["follower_per_hr"]]
layout = Layout(
    title="#justice4liang Hourly Audience Size as of" + " " + time_series_plot.index[-1].strftime("%H:%M %Y/%m/%d") + " (EST)",
    titlefont=Font(
        family='Arial, sans-serif',
        size=22,
        color='black'
    ),
    font=Font(
        family='"Droid Sans", sans-serif',
        size=12
    ),
    showlegend=False,
    autosize=False,
    width=850,
    height=430,
    xaxis=XAxis(
        title='',
        titlefont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        range=[1440388800000, 1442462400000],
        type='date',
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=True,
        nticks=5,
        ticks='inside',
        ticklen=6,
        tickcolor='rgba(0, 0, 0, 0)',
        tickfont=Font(
            family='"Verdana", monospace',
            size=12,
            color='grey'
        ),
        mirror=False,
        gridcolor='white',
        gridwidth=1,
        zerolinecolor='#F6F6F6',
        zerolinewidth=1,
        linecolor='rgba(152, 0, 0, 0.5)',
        linewidth=1.5
    ),
    yaxis=YAxis(
        title='avg. follower count of tweeters',
        titlefont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        range=[-32.55555555555556, 638.5555555555555],
        type='linear',
        autorange=True,
        showgrid=True,
        zeroline=False,
        showline=True,
        nticks=5,
        ticks='',
        ticklen=6,
        tickcolor='rgba(0, 0, 0, 0)',
        tickfont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        mirror=False,
        gridcolor='white',
        gridwidth=1,
        zerolinecolor='#F6F6F6',
        zerolinewidth=1,
        linecolor='rgba(152, 0, 0, 0.5)',
        linewidth=1.5
    ),
    legend=Legend(
        x=0.9013254786450663,
        y=1.132,
        traceorder='normal',
        font=Font(
            family='Arial, sans-serif',
            size=12,
            color='#666666'
        ),
        bgcolor='rgb(240, 240, 240)',
        bordercolor='grey',
        borderwidth=0,
        xref='paper',
        yref='paper',
        xanchor='left',
        yanchor='top'
    ),
    paper_bgcolor='rgb(240, 240, 240)',
    plot_bgcolor='rgb(240, 240, 240)',
    bargap=0.2
)

cf.set_config_file(offline=False, world_readable=True, theme='ggplot')

time_series_hourly_audience.iplot(kind='scatter', layout = layout, filename='justice4liang_hourly_audience_size')


# In[8]:

# Plot for cumulative rt count 
import plotly.plotly as py
from plotly.graph_objs import *
import cufflinks as cf
py.sign_in('xxx', 'xxx')

from datetime import datetime


time_series_hourly_audience = time_series_plot[["cum_rt_per_hr"]]
time_series_hourly_audience = time_series_hourly_audience.dropna()
layout = Layout(
    title="#justice4liang Cumulative Retweet Count as of" + " " + time_series_plot.index[-1].strftime("%H:%M %Y/%m/%d") + " (EST)",
    titlefont=Font(
        family='Arial, sans-serif',
        size=22,
        color='black'
    ),
    font=Font(
        family='"Droid Sans", sans-serif',
        size=12
    ),
    showlegend=False,
    autosize=False,
    width=850,
    height=430,
    xaxis=XAxis(
        title='',
        titlefont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        range=[1440388800000, 1442462400000],
        type='date',
        autorange=True,
        showgrid=False,
        zeroline=False,
        showline=True,
        nticks=5,
        ticks='inside',
        ticklen=6,
        tickcolor='rgba(0, 0, 0, 0)',
        tickfont=Font(
            family='"Verdana", monospace',
            size=12,
            color='grey'
        ),
        mirror=False,
        gridcolor='white',
        gridwidth=1,
        zerolinecolor='#F6F6F6',
        zerolinewidth=1,
        linecolor='rgba(152, 0, 0, 0.5)',
        linewidth=1.5
    ),
    yaxis=YAxis(
        title='# of retweets',
        titlefont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        range=[-32.55555555555556, 638.5555555555555],
        type='linear',
        autorange=True,
        showgrid=True,
        zeroline=False,
        showline=True,
        nticks=5,
        ticks='',
        ticklen=6,
        tickcolor='rgba(0, 0, 0, 0)',
        tickfont=Font(
            family='"Verdana", monospace',
            size=12,
            color='black'
        ),
        mirror=False,
        gridcolor='white',
        gridwidth=1,
        zerolinecolor='#F6F6F6',
        zerolinewidth=1,
        linecolor='rgba(152, 0, 0, 0.5)',
        linewidth=1.5
    ),
    legend=Legend(
        x=0.9013254786450663,
        y=1.132,
        traceorder='normal',
        font=Font(
            family='Arial, sans-serif',
            size=12,
            color='#666666'
        ),
        bgcolor='rgb(240, 240, 240)',
        bordercolor='grey',
        borderwidth=0,
        xref='paper',
        yref='paper',
        xanchor='left',
        yanchor='top'
    ),
    paper_bgcolor='rgb(240, 240, 240)',
    plot_bgcolor='rgb(240, 240, 240)',
    bargap=0.2
)

cf.set_config_file(offline=False, world_readable=True, theme='ggplot')

time_series_hourly_audience.iplot(kind='scatter', layout = layout, filename='justice4liang_cumulative_rt_volume')


# In[23]:

geo_df[1:50]


# In[ ]:

# create a separate dataframe for visualization
geo_df = df_all[['from_user_location', 'content', 'coordinates','from_user_followers_count', 'RT_or_not']]


# In[51]:

for index, row in geo_df[50001:].iterrows():
    a = row['from_user_location']
    if a!='':
        try:
            g = geocoder.arcgis(a)
            #print g, '\n', '\n', '\n'
            k = abs(g.lat)+abs(g.lng) #used to minimize errors in geodecoding process
            if k >0:
                print ("currently processing index number:", index)
                print ([unicode(g.lat)], [unicode(g.lng)])
                #geo_df.ix[index,'lat'] = g.lat
                geo_df.loc[index,'lat'] = g.lat
                #geo_df.ix[index,'lng'] = g.lng
                geo_df.loc[index, 'lng'] = g.lng
        except: pass
        


# In[ ]:

for index, row in geo_df.iterrows():
    coords = str(row['lat']) + ', ' + str(row['lng'])
    print (coords)
    #coords.replace(' ,', ',')
    coords.replace(', ', ',')
    print (coords)
    geo_df.ix[index, 'coords_from_user_location'] = coords
    
geo_df['coords_combined'] = geo_df['coords_from_user_location']


# In[3]:

for index, row in geo_df.iterrows():  
    print (row['coords_combined'])
    #if row['coords_combined']!='':
    if row['coordinates']!='':
        geo_df.ix[index,'coords_combined']=row['coordinates']
    if row['coordinates']=='0,0, 0.0':
        geo_df.ix[index,'coords_combined']=row['coords_from_user_location']
     
    #df['coords_from_user_location'] = df['lat'] + df['lng']
    #df.head(2)
geo_df['coords_combined'] = geo_df['coords_combined'].replace('0.0, 0.0', np.nan)


# In[ ]:

for index, row in geo_df.iterrows():  
    geo_df.ix[index,'geoloc_lat'] = row['coords_combined'].split(",")[0]
    temp_lng = row['coords_combined'].split(",")[1]
    temp_lng = temp_lng.replace(' ', '')
    print (temp_lng)
    geo_df.ix[index,'geoloc_lng'] = temp_lng
    
geo_df = geo_df[geo_df.coords_combined != "nan, nan"]


# In[2]:

geo_df


# In[12]:

import folium

justice4liang_map = folium.Map(location = [39.828175, -98.5795], zoom_start = 3)
for index, row in geo_df.iterrows():
    justice4liang_map.simple_marker(location = [row['geoloc_lat'], row['geoloc_lng']], popup='I tweeted')

justice4liang_map


# In[116]:

ds = pd.Timestamp('2016-02-22 00:02:07-05:00')
df_for_show.index.get_loc(ds)


# In[123]:

import plotly.plotly as py
py.sign_in('xxx', 'xxx')
df_for_show = geo_df[['geoloc_lat','geoloc_lng','from_user_followers_count','content', 'RT_or_not']]
df_for_show.columns = ['lat', 'lon','from_user_followers_count','content', 'retweet or not']

limits = [(0,30), (31, 189), (190, 789), (790,1305), (1306, 12983), (12984,17250), (17251, 17645)]
colors = ["rgb(0,116,217)","rgb(178,57,162)","rgb(133,20,75)","rgb(255,133,27)","rgb(220,211,147)", "rgb(6,39,96)", "rgb(32,248,183)"]
location = []
names = ['2-16-2016','2-17-2016','2-18-2016','2-19-2016', '2-20-2016', '2-21-2016', '2-22-2016']
scale = 5000

for i in range(len(limits)):
    lim = limits[i]
    df_sub = df_for_show[lim[0]:lim[1]]
    locale = dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        lon = df_sub['lon'],
        lat = df_sub['lat'],
        text = df_sub['content'],
        marker = dict(
            size = (df_sub['from_user_followers_count'])/85+9,
            #size = 5,
            color = colors[i],
            line = dict(width=0.5, color='rgb(40,40,40)'),
            sizemode = 'area'
        ),
    
        #name = '{0} - {1}'.format(lim[0],lim[1]) )
        name = names[i])
    location.append(locale)

layout = dict(
        title = 'Mapping #justice4liang',
        showlegend = True,
        geo = dict(
            scope='usa',
            projection=dict( type='albers usa' ),
            showland = True,
            landcolor = 'rgb(217, 217, 217)',
            subunitwidth=1,
            countrywidth=1,
            subunitcolor="rgb(255, 255, 255)",
            countrycolor="rgb(255, 255, 255)"
        ),
    )

fig = dict( data=location, layout=layout )
url = py.plot( fig, validate=False, filename='d3-bubble-map-justice4liang' )


# In[5]:

df_all.to_pickle('df_all.pkl')
geo_df.to_pickle('geo_df.pkl')
time_series_plot.to_pickle('time_series_plot.pkl')

