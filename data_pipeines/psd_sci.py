# -*- coding: utf-8 -*-
"""
Program to calculate Sioutas Cascade Impactor (SCI) size distribution

@author: alima
"""

import sys
sys.modules[__name__].__dict__.clear()

import pandas as pd
import numpy as np
exec(open(r'C:\PhD Research\Generic Codes\notion_corrections.py').read())

Pm25_cor_factor = 1.061952   # from PEM to SCI PM2.5 ratios

##########################################
### Step 1: Reading gravimetric errors ###
##########################################

## reading PTFE mass error
df = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Des\Filter_Master_v21_200206_am.xlsx'))
mass_err = df[df['Visit_#'] == 'Visit 0']['PM Mass'].describe()['50%']

## reading MCE mass error
df = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\filter_gravimetric_master.xlsx'))
tsp_mass_err = df[(df['Pilot/Field/Travel'] == 'Travel') & (df['Filter Material'] == 'MCE')]['PM Mass'].abs().describe()['50%']

##########################################################
### Step 2: Calculating gravimetric size distributions ###
##########################################################

df = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\filter_gravimetric_master.xlsx'))
df = df[(df['Filter Position'].str[0:3] == 'PEM')| 
        (df['Filter Position'].str[0:3] == 'SCI')|
        (df['Filter Position'].str[0:3] == 'FC1')|
        (df['Filter Position'].str[0:3] == 'FC2')|
        (df['Filter Position'].str[0:3] == 'FC3')]

df.loc[df['Filter Position'].str[0:2] == 'FC', 'Filter Position'] = df['Filter Position'].str[0:2]
df.loc[df['Filter Position'].str[0:3] == 'SCI', 'Filter Position'] = df['Filter Position'].str[0:3]

df = df.groupby('Filter Position', as_index = False)['Average Flow', 'PM Mass'].agg('sum')
df.loc[df['Filter Position'] == 'SCI'  ,'Average Flow'] = df['Average Flow']/5
df.loc[df['Filter Position'] == 'FC'  ,'Average Flow'] = df['Average Flow']/3
df.loc[df['Filter Position'] == 'FC'  ,'PM Mass'] = df['PM Mass']/3

df.loc[df['Filter Position'] == 'SCI'  ,'PM Mass'] = df['PM Mass'] * Pm25_cor_factor
df.sort_values('Filter Position', inplace = True)

mass_10_inf = df.loc[2,'Average Flow'] * ((df.loc[0,'PM Mass']/df.loc[0,'Average Flow']) - (df.loc[2,'PM Mass'] / df.loc[2,'Average Flow']))
mass_10_inf_error = 0.433373 ## Haal nadashtam formoll bezanam dasti as STATA gereftam

df = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\filter_gravimetric_master.xlsx'))
df = df[(df['Filter Position'].str[0:3] == 'SCI')]
df['Filter Position'] = df['Filter Position'].str[-1:]
df = df[['Filter Position', 'PM Mass']]

df = df.groupby('Filter Position')['PM Mass'].sum()  
df['a'] = mass_10_inf
df = df.reset_index()
df = pd.concat([df, pd.Series([0] * 6)], axis = 1)

df.loc[5, 0] = mass_10_inf_error
df.loc[:4, 0] = mass_err
df.columns = ['FP', 'PM Mass', 'Error']

df['Error'] = df['Error'].pow(2)
sum_error = df['Error'].sum()**0.5
sum_mass = df['PM Mass'].sum()
df['Mass Perc'] = df['PM Mass'] / sum_mass
df['Mass Perc Error'] = df['Mass Perc'] * np.sqrt( (mass_err/df['PM Mass']).pow(2) + (sum_error/sum_mass)**2 )
df[['Mass Perc', 'Mass Perc Error']] = df[['Mass Perc', 'Mass Perc Error']] * 100

min_size = [2.51, 1, 0.501, 0.251, 0.1, 10]
max_size = [10, 2.51, 1, 0.501, 0.251, 3500]
df.columns

df = pd.concat([df, pd.Series(min_size), pd.Series(max_size)], axis = 1)
df.columns = ['FP', 'PM Mass', 'Error', 'Mass Perc', 'Mass Perc Error', 'Size', 'Max Size']


for col in ['FP', 'PM Mass', 'Error', 'Mass Perc', 'Mass Perc Error']:
    df[col].fillna(method='ffill', inplace = True)

df.to_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_sci_unstack.xlsx'), index = False)