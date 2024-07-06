# -*- coding: utf-8 -*-
"""
Program to calculate PSD of SCI for the sizes above 1 micron (to match the approximate range of LDPS dust PSD recorded)

@author: alima
"""

import sys
sys.modules[__name__].__dict__.clear()

import pandas as pd
import numpy as np
exec(open(r'C:\PhD Research\Generic Codes\notion_corrections.py').read())

#####################################################
### Step 1: Making fractionation of qff ldps data ###
#####################################################

psd = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_qff.xlsx')) #.iloc[:,0]
psd = psd[psd["Size"] <= 1000]

df = pd.read_excel(backslash_correct(r'C:\Career\Learning\Python Practice\Stata_Python_Booster\PhD - QFF\Processed\psd_sci_unstack.xlsx'))
psd = psd.merge(df, on = 'Size', how = 'outer').iloc[:,:-5]
psd['FP'].fillna(method = 'ffill', inplace = True)
psd['qff psd error'] = psd['qff psd error'].pow(2)

psd = psd.groupby('FP', as_index = False).agg({'qff psd' : 'sum',
                                               'qff psd error': 'sum',
                                               'Size' : 'min'}).sort_values('Size').reset_index(drop = True).iloc[3:]

psd['qff psd error'] = psd['qff psd error'].pow(0.5)
psd['qff psd'] = (psd['qff psd'] / psd['qff psd'].sum()) * 100
psd = psd.iloc[:,1:].rename(columns = {'qff psd': 'value',
                                       'qff psd error': 'error'})

psd['Method'] = 'QFF'

###########################################
### Step 2: Making fractionation of SCI ###
###########################################

df = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_sci_unstack.xlsx'))
df_large = df[df['Size'] >= 1].sort_values('Size')

a = df_large['Mass Perc Error'].pow(2).sum()
b = df_large['Mass Perc'].max()
df_large['Mass Perc Error'] = df_large['Mass Perc'] * np.sqrt(  (df_large['Mass Perc Error']/df_large['Mass Perc']).pow(2)  +   (a/b) ** 2 )

all_mass = df_large['Mass Perc'].sum()
df_large['Mass Perc'] = (df_large['Mass Perc']/all_mass) * 100

# df_large = df_large [['Mass Perc', 'Mass Perc Error', 'Size']]
df_large = df_large.iloc[:,3:6].rename(columns = {'Mass Perc': 'value',
                                                 'Mass Perc Error': 'error'})                     

df_large['Method'] = 'AB'

# all_mass_psd = 
df = psd.append(df_large).reset_index(drop = True)
df.to_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_above_1mic.xlsx'), index = False)

