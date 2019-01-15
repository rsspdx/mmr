#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 07:09:57 2019

@author: rs
"""

import requests
import zipfile
import io
import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import seaborn as sns

os.chdir('/Users/rs/data/geo/mmr')

# download zip archives of csv data files from worldbank.org
mmr = requests.get('http://api.worldbank.org/v2/en/indicator/SH.STA.MMRT?downloadformat=csv')
lifeexp = requests.get('http://api.worldbank.org/v2/en/indicator/SP.DYN.LE00.IN?downloadformat=csv')
hiv = requests.get('http://api.worldbank.org/v2/en/indicator/SH.DYN.AIDS.ZS?downloadformat=csv')
urbpop = requests.get('http://api.worldbank.org/v2/en/indicator/SP.URB.TOTL.IN.ZS?downloadformat=csv')
gdpcap = requests.get('http://api.worldbank.org/v2/en/indicator/NY.GDP.PCAP.PP.CD?downloadformat=csv')

# unzip the relevant files to csv
mmr_zip = zipfile.ZipFile(io.BytesIO(mmr.content))
names = zipfile.ZipFile.namelist(mmr_zip)
mmr_csv = zipfile.ZipFile.extract(mmr_zip, names[1])

lifeexp_zip = zipfile.ZipFile(io.BytesIO(lifeexp.content))
names = zipfile.ZipFile.namelist(lifeexp_zip)
lifeexp_csv = zipfile.ZipFile.extract(lifeexp_zip, names[1])

hiv_zip = zipfile.ZipFile(io.BytesIO(hiv.content))
names = zipfile.ZipFile.namelist(hiv_zip)
hiv_csv = zipfile.ZipFile.extract(hiv_zip, names[1])

urbpop_zip = zipfile.ZipFile(io.BytesIO(urbpop.content))
names = zipfile.ZipFile.namelist(urbpop_zip)
urbpop_csv = zipfile.ZipFile.extract(urbpop_zip, names[1])

gdpcap_zip = zipfile.ZipFile(io.BytesIO(gdpcap.content))
names = zipfile.ZipFile.namelist(gdpcap_zip)
gdpcap_csv = zipfile.ZipFile.extract(gdpcap_zip, names[1])


# read in data to pandas and clean up
mmr = pd.read_csv(mmr_csv, header =  2)
# mmr.head()
lifeexp = pd.read_csv(lifeexp_csv, header = 2)
# lifeexp.columns
hiv = pd.read_csv(hiv_csv, header = 2)
# hiv.columns
urbpop = pd.read_csv(urbpop_csv, header = 2)
# urbpop.columns
gdpcap = pd.read_csv(gdpcap_csv, header = 2)
# gdpcap.columns

# this was downloaded outside this file
health_exp = pd.read_csv('health_exp.csv')

mmr = mmr[['Country Name', 'Country Code', '2015']]
mmr = mmr.rename(index = str, columns = {'2015': 'mmr'})

lifeexp = lifeexp[['Country Name', 'Country Code', '2015']]
lifeexp = lifeexp.rename(index = str, columns = {'2015': 'lifeexp'})

hiv = hiv[['Country Name', 'Country Code', '2015']]
hiv = hiv.rename(index = str, columns = {'2015': 'hiv'})

urbpop = urbpop[['Country Name', 'Country Code', '2015']]
urbpop = urbpop.rename(index =  str, columns = {'2015': 'urbpop'})

gdpcap = gdpcap[['Country Name', 'Country Code', '2015']]
gdpcap = gdpcap.rename(index =  str, columns = {'2015': 'gdpcap'})

mmr_merged = pd.merge(mmr, lifeexp)
mmr_merged = pd.merge(mmr_merged, hiv)
mmr_merged = pd.merge(mmr_merged, urbpop)
mmr_merged = pd.merge(mmr_merged, gdpcap)
mmr_data = pd.merge(mmr_merged, health_exp)
mmr_data.head()
mmr_data.dtypes
mmr_data.shape

# get world shapefile with country borders
world = requests.get('http://thematicmapping.org/downloads/TM_WORLD_BORDERS-0.3.zip')
world_zip = zipfile.ZipFile(io.BytesIO(world.content))
zipfile.ZipFile.namelist(world_zip)
world_zip.extractall()
world_map = gpd.read_file('TM_WORLD_BORDERS-0.3.shp')

# look at the data
world_map.columns
world_map = world_map.sort_values(by = 'ISO3')
# print(world_map['ISO3'])

# merge the two data sets
merged_map_mmr = pd.merge(world_map, mmr_data, left_on = 'ISO3', right_on = 'Country Code')
merged_map_mmr.columns
# merged_map_mmr.to_csv('merged_map_mmr.csv')

# get region concordance -- turn the excel file into csv, edit outside python
regions_excel = requests.get('https://siteresources.worldbank.org/DATASTATISTICS/Resources/CLASS.XLS')
regions = pd.read_csv('CLASS (1).csv')
regions.head()
regions.columns
regions = regions[['Code', 'Region']]
regions.head()
regions['Code'][regions['Code'] == 'ZAR'] = 'COD'

# merge with regions; this completes the data set
mmr = pd.merge(merged_map_mmr, regions, left_on = 'Country Code', right_on = 'Code')
mmr.head()
mmr.columns
mmr['gdpcap'] = mmr['gdpcap'] / 1000
mmr['gdpcap_sq'] = mmr['gdpcap']**2
mmr.csv = mmr.to_csv('mmr.csv')

# estimate a model for africa
reg1 = smf.ols(formula = 'mmr ~ gdpcap + gdpcap_sq + urbpop + hiv ', data = mmr[mmr['Region'] == 'Sub-Saharan Africa'])
reg1_results = reg1.fit(cov_type = 'HC3')
print(reg1_results.summary())

reg2 = smf.ols(formula = 'mmr ~ gdpcap + gdpcap_sq + urbpop + hiv + Region', data = mmr)
reg2_results = reg2.fit(cov_type = 'HC3')
print(reg2_results.summary())



sns.relplot('gdpcap', 'mmr',  data = mmr)

# draw a map
mmr.plot(column = mmr['gdpcap'], cmap = 'RdYlBu', scheme = 'QUANTILES', figsize = (10, 8))