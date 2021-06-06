"""
Sneh Gupta and Gracie Gibbons
Brazil Forest Fires Project
Visualizing forest fires from 1998 to 2017 in Brazil via
geospatial visualizations and regression line.
Also making predictive machine learning models.
"""

import pandas as pd
import geopandas as gpd
import data_visualization as dv
import ml


def main():
    fires = pd.read_csv(
        '/Users/graciegibbons/UW/Sophomore/Spring/CSE_163/amazon.csv',
        encoding='cp1252')
    fires = dv.process_fires(fires)
    data = gpd.read_file(
        '/Users/graciegibbons/UW/Sophomore/Spring/CSE_163/br-states.json')
    merged, data = dv.merge(fires, data)
    dv.graph_tot(merged, data)
    dv.time_lapse(merged, data)
    ml.trend(fires)
    ml.fit_model(fires)
    # ml.fit_model_2(fires)


if __name__ == '__main__':
    main()
