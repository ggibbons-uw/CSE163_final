"""
Sneh Gupta
CSE 163: Brazil Forest Fire Project
Data visualization of forest fires in Brazil
Plotted the total fires in each state over two decades
and made a video of a time lapse of forest fires per month over two decades,
by state
fires refers to forest fire dataset, data refers to geospatial dataset,
and merged is the combination of the two
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl
from matplotlib.artist import Artist
from unidecode import unidecode
import numpy as np


def process_fires(fires):
    """
    process forest fires in brazil data frame so that
    date column has datetime values (specific month and year)
    and All the state names are normalized to match the geodataframe
    """
    fires['number'] = fires['number'].astype(str)
    fires['number'] = fires['number'].str.replace('.', '')
    fires['number'] = fires['number'].astype(np.int64)
    fires['state'] = fires['state'].apply(unidecode)
    # make Piaui state names match in the datasets
    fires['state'] = fires['state'].replace('Piau', 'Piaui')
    # divide Rio forest fires by 3 - so that all three Rio states
    mask = fires['state'] == 'Rio'
    filters = fires[mask]
    fires.loc[mask, 'number'] = filters['number'] / 3
    # changing the months from Portugese to english
    fires['month'] = fires['month'].apply(unidecode)
    fires['month'] = fires['month'].replace({'Janeiro': 'January',
                                             'Fevereiro': 'February',
                                             'Marco': 'March',
                                             'Abril': 'April',
                                             'Maio': 'May',
                                             'Junho': 'June',
                                             'Julho': 'July',
                                             'Agosto': 'August',
                                             'Setembro': 'September',
                                             'Outubro': 'October',
                                             'Novembro': 'November',
                                             'Dezembro': 'December'})
    # chaning date column to match month and year of month and year column
    fires['date'] = fires['year'].apply(str) + ' ' + fires['month']
    fires['date'] = pd.to_datetime(fires['date'], format='%Y %B')
    return fires


def merge(fires, data):
    """
    process geometry data to normalize state names to match the Brazil forest
    fire dataset merge dataframe and geodataframe containing geometry of states
    in Brazil
    return merged data and processed geometry data
    """
    # normalize state names in data to remove accents
    data['nome'] = data['nome'].apply(unidecode)
    # combine three Rio states into one to accomodate original dataset
    data['nome'] = data['nome'].replace('Rio de Janeiro', 'Rio')
    data['nome'] = data['nome'].replace('Rio Grande do Norte', 'Rio')
    data['nome'] = data['nome'].replace('Rio Grande do Sul', 'Rio')
    # combine geometry for Rio
    data = data[['nome', 'geometry']]
    data = data.dissolve(by='nome', aggfunc='sum')
    merged = fires.merge(data, left_on='state', right_on='nome', how='inner')
    merged = gpd.GeoDataFrame(merged, geometry='geometry')
    return (merged, data)


def graph_tot(merged, data):
    """
    take merged data set and geometry data
    plot Brazil with visualization of the total number of forest fires
    in each state from 1998 to 2017
    """
    fig, ax = plt.subplots(1, figsize=(15, 7))
    data.plot(color='#EEEEEE', ax=ax)
    merged = merged[['state', 'geometry', 'number']]
    merged = merged.dissolve(by='state', aggfunc='sum')
    merged.plot(column='number', legend=True, ax=ax)
    plt.title('Number of Total Forest Fires in Brazil from 1998 to 2017')
    plt.savefig('tot_fires.png')


def time_lapse(merged, data):
    """
    take merged data and geometry data
    makes a video containing time lapse of the brazil forest fires at each
    month from 1998 to 2017
    """
    fig, ax = plt.subplots(1, figsize=(20, 10))
    data.plot(color='#EEEEEE', ax=ax)
    # sort and make legend
    merged = merged.sort_values(by='date')
    norm = mpl.colors.Normalize(vmin=merged['number'].min(),
                                vmax=merged['number'].max())
    cmap = cm.viridis
    fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), location='right')
    count = 0
    # loop over each month and create and image for forest fire visualization
    # for that month
    for month in merged['date'].unique():
        count += 1
        merged_month = merged[merged['date'] == month]
        merged_month.plot(column='number', ax=ax)
        text = ax.text(x=-45, y=3, s=str(merged_month['year'].unique()[0]) +
                       ' ' + str(merged_month['month'].unique()[0]),
                       fontsize=20)
        fig.savefig(f'frames/frame_{count:03d}', bbox_inches='tight')
        Artist.remove(text)
        plt.close()
    # putting together the images in a video
    # ffmpeg -framerate 5 -i /home/frame_%03d.png output.mp4