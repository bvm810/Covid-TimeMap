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

print(covid_df['Country/Region'].unique().tolist())

# TO FIX
# Taiwan*
# Reunion and Jersey/Guernsey are technically France and UK, and Aruba/Curacao are Dutch
# occupied Palestinian Territory --> Israel or Palestine?
# Cruise ship -> Belongs to who?
# Diamond Princess entries
