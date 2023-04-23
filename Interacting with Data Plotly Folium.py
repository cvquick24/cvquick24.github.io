#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium


# In[ ]:





# In[2]:


##Part 1


# In[3]:


vote_data = pd.read_csv('vote_subset.csv')
vote_data.head()


# In[4]:


vote_data['voter_cat'].value_counts()


# In[5]:


vote_data['income_cat'].unique()


# In[ ]:





# In[6]:


income_dim = go.parcats.Dimension(
    values=vote_data['income_cat'],
    categoryorder = 'array',
    categoryarray = ['$125k or more', '$75-125k', '$40-75k', 'Less than $40k'],
    label='Income'
)

educ_dim = go.parcats.Dimension(
    values = vote_data['education'],
    label ='Education'
)

freq_dim = go.parcats.Dimension(
    values = vote_data['voter_cat'],
    categoryorder = 'array',
    categoryarray = ['always', 'sporadic', 'rarely/never'],
    ticktext = ['Always', 'Sporadic', 'Rarely/Never'],
    label = 'Voting Frequency'
)
                       
vote_data['voter_cat_dicot'] = vote_data['voter_cat'].apply(
    lambda x:2 if x == 'always' else (1 if x == 'sporadic' else 0))


fig = go.Figure(data = [go.Parcats(dimensions=[freq_dim, educ_dim, income_dim],
                                  line = {'color':vote_data['voter_cat_dicot'], 'colorscale':'Spectral', 'shape':'hspline'},
                                  hoverinfo = 'count',
                                  labelfont = {'size':20, 'family': 'Arial'},
                                  tickfont = {'size':16, 'family': 'Arial'})])

fig.write_image('categories.png')
fig.write_html('categories.html')
fig.show()



# In[ ]:





# In[7]:


##Part 2


# In[8]:


elect_data = pd.read_csv('election_data.csv')
elect_data.head()


# In[9]:


elect_data = elect_data[elect_data['ActiveRegisteredVoters'] > 0]
elect_data.head()


# In[10]:


elect_data['pct_absentee'] = (elect_data['absentee_ballots']/elect_data['TotalVoteTurnout'])*100
elect_data['pct_turnout'] = (elect_data['TotalVoteTurnout']/elect_data['ActiveRegisteredVoters'])*100
elect_data.head()


# In[11]:


elect_data['region'].unique()


# In[12]:


elect_data['region'] = elect_data['region'].replace({'eastern':'Eastern', 
                                                     'central':'Central',
                                                     'northern': 'Northern',
                                                     'valley': 'Valley',
                                                     'west_central':'West Central',
                                                     'southwest':'Southwest', 
                                                     'southside':'Southside',
                                                     'hampton_roads':'Hampton Roads'})
elect_data


# In[ ]:





# In[13]:


elect_data.loc[elect_data['pct_turnout'] == elect_data['pct_turnout'].max()]


# In[ ]:





# In[14]:


min_x,max_x = elect_data['pct_turnout'].min(), elect_data['pct_turnout'].max()
min_y,max_y = elect_data['pct_absentee'].min(), elect_data['pct_absentee'].max()

print("min_x:", min_x)
print("max_x:", max_x)


# In[15]:


min_y = min_y - 0.1*(max_y - min_y)
max_y = max_y + 0.1*(max_y - min_y)
print("min_x:", min_x - 0.1*(max_x - min_x))
print("min_y:", min_y)
print("max_x:", max_x + 0.1*(max_x - min_x))
print("max_y:", max_y)


# In[16]:


min_x = 30
max_x = 100

fig = px.scatter(elect_data, x='pct_turnout', y='pct_absentee', 
                 color = 'region',
                 color_discrete_sequence = px.colors.qualitative.Prism,
                 size = 'TotalRegisteredVoters', size_max = 30,
                 labels = {'locality':'Locality','pct_turnout':'Percent Turnout', 
                           'pct_absentee':'Percentage of Absentee Votes',
                           'region':'Region', 'TotalRegisteredVoters':'Total Registered Voters'},
                 hover_data = {'locality':True, 'region':False, 'year':False,
                              'pct_turnout':':.2f','pct_absentee':':.2f'},
                 animation_frame = 'year',
                 category_orders = {'year' : [2014, 2016, 2018, 2020, 2022]},
                 range_x = [min_x,max_x], range_y = [min_y,max_y],
                 height = 600
               )
fig.update_layout(sliders=[{"currentvalue": {"prefix": "Year: ",'xanchor':'right'}}])
fig.write_html('bubble.html')
fig.write_image('bubble.png')
fig.show()


# In[ ]:





# In[17]:


##Part 3


# In[18]:


elect_data_2022 = elect_data[elect_data['year'] == 2022]
elect_data_2022.head()


# In[19]:


elect_data_2022['pct_turnout'] = (elect_data_2022['TotalVoteTurnout']/elect_data_2022['ActiveRegisteredVoters'])*100
elect_data_2022.head()


# In[20]:


elect_data_2022['locality'] = elect_data_2022['locality'].str.lower()
elect_data_2022['locality'] = elect_data_2022['locality'].str.title()
elect_data_2022['locality']


# In[21]:


for value in elect_data_2022['locality']:
    if ' And' in value:
        print(value)


# In[22]:


for value in elect_data_2022['locality']:
    if ' Of' in value:
        print(value)


# In[23]:


elect_data_2022['locality'] = elect_data_2022['locality'].replace('King And Queen County', 'King and Queen County')
elect_data_2022.loc[elect_data_2022['locality'] == 'King and Queen County']


# In[24]:


elect_data_2022['locality'] = elect_data_2022['locality'].replace('Isle Of Wight County', 'Isle of Wight County')
elect_data_2022.loc[elect_data_2022['locality'] == 'Isle of Wight County']


# In[ ]:





# In[25]:


VA_CENTER = [37.9, -79.2]
m = folium.Map(VA_CENTER, zoom_start=7, tiles = None)
geo_json = 'counties_VA.json'
c = folium.Choropleth(geo_json, data = elect_data_2022, columns = ['locality', 'pct_turnout'],
                     key_on='properties.NAME', highlight = True, fill_color = 'BuGn',
                     legend_name = 'Percent of Voter Turnout in 2022', bins = 8).add_to(m)

folium.GeoJsonTooltip(fields = ['NAME'], labels = False).add_to(c.geojson )

title_html = '''
             <h3 align="center" style="font-size:24px"><b>{}</b></h3>
             '''.format('2022 General Election Voter Turnout in Virginia')

svg_style = '<style>svg#legend {font-size:medium;}</style>'
m.get_root().header.add_child(folium.Element(svg_style))
m.get_root().html.add_child(folium.Element(title_html))
m.save('map.html')
m


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




