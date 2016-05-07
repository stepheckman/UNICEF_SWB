#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import time
import csv
import numpy as np
import shapely.geometry as geometry
from shapely.geometry import Point
from shapely.geometry import MultiPoint
import pprint
import pandas as pd

DEBUG = True

def read_data(fname):
    df = pd.read_csv(fname) 
    print 'Processing data from dataset ' + fname
    remapped_column_names = {
        'team_num':'team',
        'EAsize':'huct',
        '_gps_latitude':'lat',
        '_gps_longitude':'lon',
        '_gps_precision':'precision'
    }
    df.rename(columns= remapped_column_names, inplace=True)
    
    # delete columns
    for v in ['metainstanceid','_uuid', '_merge','deviceid','gps',
        'endtime', 'starttime', '_gps_altitude', 'form_consent', 'EA_Name',
        'cluster_name', '_submission_time']:
        del df[v]

    # drop imprecise GPS coordinates 
    for index, row in df.iterrows():
        if df.loc[index, 'precision'] > 10:
            df.loc[index, 'lon'] = np.nan
            df.loc[index, 'lat'] = np.nan
            df.loc[index, 'precision'] = np.nan

    df['coord'] = df[['lat', 'lon']].apply(tuple, axis=1)
    return df

def cluster_dt(df):
    dfG = df.groupby(['cluster'], as_index=False)
    dfG = dfG.agg( {'huct' : { 'minct':  'min'},
                    'team': { 'minteam' : 'min',
                                'maxteam':  'max'},
                    'lga': { 'minlga' : 'min',
                                'maxlga':  'max'},
                    'state': { 'minstate' : 'min',
                                'maxstate':  'max'}} )
    dfG['area'] = float(0)
    for index, row in dfG.iterrows():
        # get points in this cluster
        subset = pd.DataFrame(df.loc[df['cluster'] == int(row['cluster'])])
        # area of points in this cluster -- in square degrees
        area = float(hull_area(tuple(subset['coord'])))
        # convert to square km (approx)
        dfG.loc[index,'area'] = area*12.3
    print df.columns
    print df.dtypes
    return dfG

def hull_area(tup):
    try:
        points = MultiPoint(tup)
        return points.convex_hull.area
    except Exception,e:
        print e

def main():
    dt = read_data('NGR_GPS_Data.csv')
    sumdt = cluster_dt(dt)
    print sumdt['area'].describe()
    sumdt.to_csv('csv_export.csv')
    
if __name__ == '__main__':
    main()