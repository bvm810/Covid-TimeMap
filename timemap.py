"""
Script for creating time map with all cases of Covid-19 since 22/01/2020
"""

import wget
import pandas as pd

# Get data from Github

# Data urls
urls = ['https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv',
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv']

# Local filenames for csvs
filenames = ['covid-confirmed.csv',
             'covid-deaths.csv',
             'covid-recovered.csv']
# Download data
for idx in range(len(urls)):
    wget.download(urls[idx], filenames[idx])

# Read CSVs corresponding to confirmed, deaths, and recovered cases
confirmed_df = pd.read_csv('covid-confirmed.csv')
deaths_df = pd.read_csv('covid-deaths.csv')
recovered_df = pd.read_csv('covid-recovered.csv')

# Data has each date as a column. In order to plot it more easily later we convert to single column called Date
confirmed_df = pd.melt(confirmed_df, id_vars = ['Province/State', 'Country/Region', 'Lat', 'Long'],
                       value_vars = confirmed_df.columns[4:],
                       var_name = 'Date',
                       value_name = 'Confirmed')

deaths_df = pd.melt(deaths_df, id_vars = ['Province/State', 'Country/Region', 'Lat', 'Long'],
                       value_vars = deaths_df.columns[4:],
                       var_name = 'Date',
                       value_name = 'Deaths')

recovered_df = pd.melt(recovered_df, id_vars = ['Province/State', 'Country/Region', 'Lat', 'Long'],
                       value_vars = recovered_df.columns[4:],
                       var_name = 'Date',
                       value_name = 'Recovered')

# Concatenating all three datasets in a single dataframe
covid_df = pd.concat([confirmed_df, deaths_df['Deaths'], recovered_df['Recovered']], axis = 1)

# In the U.S cases are counted by state and by county, so there are duplicates. We remove them by eliminating
# rows containing ',' in the Province/State column, because counties are states as 'County, State'
covid_df = covid_df[covid_df['Province/State'].str.contains(',') != True]

# For some reason, Congo cases are listed with same lat/long but with different country entries (Congo (Kinshasa) and
# Congo (Brazzaville)). I joined both of these entries in a single Congo entry for each date with the code below
for date in covid_df.Date.unique():
    conf = covid_df[(covid_df['Country/Region']=='Congo (Kinshasa)') & (covid_df['Date'] == date)]['Confirmed'].values[0] + covid_df[(covid_df['Country/Region']=='Congo (Brazzaville)') & (covid_df['Date'] == date)]['Confirmed'].values[0]
    dead = covid_df[(covid_df['Country/Region']=='Congo (Kinshasa)') & (covid_df['Date'] == date)]['Deaths'].values[0] + covid_df[(covid_df['Country/Region']=='Congo (Brazzaville)') & (covid_df['Date'] == date)]['Deaths'].values[0]
    recov = covid_df[(covid_df['Country/Region']=='Congo (Kinshasa)') & (covid_df['Date'] == date)]['Recovered'].values[0] + covid_df[(covid_df['Country/Region']=='Congo (Brazzaville)') & (covid_df['Date'] == date)]['Recovered'].values[0]
    new_row = {'Country/Region': 'Congo', 'Lat': -4.0383, 'Long': 21.7587, 'Date': date, 'Confirmed': conf, 'Deaths': dead, 'Recovered': recov}
    covid_df = covid_df.append(new_row, ignore_index=True)

# This line drops the undesired columns after the merge because only these entries have '(' in the name
covid_df = covid_df[covid_df['Country/Region'].str.contains('\(')!=True]

# Taiwan had an asterisk next to its name because it is considered by many to be a part of China. Since it is
# disputed anyway, since Chinese cases are separated by province and since it is the Taiwaneese government that
# decided how to handle Covid-19 cases, I decided to consider it as a separate country
# So I only removed the asterisk in the name
covid_df = covid_df.replace({'Country/Region': {'Taiwan*': 'Taiwan'}})

# Adding Reunion to France
covid_df.loc[covid_df['Country/Region'] == 'Reunion','Province/State'] = 'Reunion'
covid_df = covid_df.replace({'Country/Region': {'Reunion': 'France'}})

# Adding Aruba to the Netherlands
covid_df.loc[covid_df['Country/Region'] == 'Aruba','Province/State'] = 'Aruba'
covid_df = covid_df.replace({'Country/Region': {'Aruba': 'Netherlands'}})

# Jersey/Guernsey are Channel Islands, and so their cases are already counted, like those from U.S counties
covid_df = covid_df[covid_df['Country/Region'].str.contains('Jersey')!=True]
covid_df = covid_df[covid_df['Country/Region'].str.contains('Guernsey')!=True]

# Entries marked with occupied Palestinian territory are governed by the Palestinian Authority, so I will mark them as
# Palestine.
covid_df = covid_df.replace({'Country/Region': {'occupied Palestinian territory': 'Palestine'}})

# Cruise Ship/Diamond Princess/Grand Princess entries are cases of Covid that appeared on the Princess Cruise Ships during the
# outbreak of the virus. I did not find information as to where those passengers disembarked, and moreover it seems
# that like the counties in the U.S case, they are double counted for cases in the U.S, Canada and Australia.
# Since they represent a small percentage of the total cases (0.4%), and since passengers will eventually desembark,
# thus updating the data sources, I decided to neglect those cases in the map.
covid_df = covid_df[covid_df['Country/Region'].str.contains('Cruise')!=True]
covid_df = covid_df[covid_df['Province/State'].str.contains('Princess')!=True]


# Data visualization

