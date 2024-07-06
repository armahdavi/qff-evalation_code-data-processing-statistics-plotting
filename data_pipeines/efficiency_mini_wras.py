# -*- coding: utf-8 -*-
"""
Program to calculate mass-based filtration efficiency of HVAC filter using mini-WRAS particle monitoring sensor

@author: alima
"""

import sys
sys.modules[__name__].__dict__.clear()
import pandas as pd
import numpy as np
import glob
import os
exec(open(r'C:\PhD Research\Generic Codes\notion_corrections.py').read())

###############################################################
### Step 1: Reading start and end times of sensor recording ###
###############################################################

df = pd.read_excel(r'C:\PhD Research\QFF Evaluation\Des\mini_wras_time_cutoff.xlsx')
df['start'] = pd.to_datetime(df['start'])
df['end'] = pd.to_datetime(df['end'])

match_dict = {}

for v in df['visit'].unique():
    for loc in df['location'].unique():
        locals()['start_%s_%s' %(v,loc)] = df.loc[(df['visit'] == v) & (df['location'] == loc), 'start']
        locals()['end_%s_%s' %(v,loc)] = df.loc[(df['visit'] == v) & (df['location'] == loc), 'end']
        match_dict['%s_%s' %(v,df.loc[(df['visit'] == v) & (df['location'] == loc), 'sn'].iloc[0])] = loc

#########################################################################
### Step 2: Reading all Mini-WRAS PSD data and refine based on Step 1 ###
#########################################################################

os.chdir(backslash_correct('C:\PhD Research\QFF Evaluation\Raw\mini_wras'))

j = 1
for file in glob.glob('*.xlsx'):
    df = pd.read_excel(file, sheet_name= 'Mass values', skiprows = 4)
    df['date & time'] = df['date & time'].str[:-2] + '00'
    
    df['date & time'] = pd.to_datetime(df['date & time'])
    key_indicator = file[15:16] + '_' + file[24:27]
    
    # t = file[15:16]
    t = file[15:16] + '_' +  match_dict[key_indicator]
    a = locals()['start_%s' %t].iloc[0]
    b = locals()['end_%s' %t].iloc[0]
    
    df = df[(df['date & time'] >= a) & (df['date & time'] <= b)]
    df = df.iloc[:,2:]
    df = df.T
    
    for i in range(1,4):
        if i == 1:
            df['%s_mean_%s' %(t,i)] = df.iloc[:,:4].mean(axis = 1)
            df['%s_stdev_%s' %(t,i)] = df.iloc[:,:4].std(axis = 1)
        elif i == 2:
            df['%s_mean_%s' %(t,i)] = df.iloc[:,5:9].mean(axis = 1)
            df['%s_stdev_%s' %(t,i)] = df.iloc[:,5:9].std(axis = 1)
        elif i == 3:
            df['%s_mean_%s' %(t,i)] = df.iloc[:,10:].mean(axis = 1)
            df['%s_stdev_%s' %(t,i)] = df.iloc[:,10:].std(axis = 1)
        
    df = df.iloc[:, -6:]
    
    if j == 1:
        df_mw_psd = df
        j += 1
    else:
        df_mw_psd = pd.merge(df_mw_psd, df, left_index=True, right_index=True)

#######################################################################################
### Step 3: Calculating efficiency using the upstream and downstream concentrations ###
#######################################################################################

for i in range(1,4):
    eff = df
    eff['initial_%s' %i] = (1 - df_mw_psd['1_down_mean_%s' %i]/df_mw_psd['1_return_mean_%s' %i]) * 100
    eff['initial_error_%s' %i] = (df_mw_psd['1_down_mean_%s' %i]/df_mw_psd['1_return_mean_%s' %i]) * 100 * np.sqrt((df_mw_psd['1_down_stdev_%s' %i]/df_mw_psd['1_down_mean_%s' %i]).pow(2) + (df_mw_psd['1_return_stdev_%s' %i]/df_mw_psd['1_return_mean_%s' %i]).pow(2))
    
    eff['final_%s' %i] = (1 - df_mw_psd['7_down_mean_%s' %i]/df_mw_psd['7_return_mean_%s' %i]) * 100
    eff['final_error_%s' %i] = df_mw_psd['7_down_mean_%s' %i]/df_mw_psd['7_return_mean_%s' %i] * 100 * np.sqrt((df_mw_psd['7_down_stdev_%s' %i]/df_mw_psd['7_down_mean_%s' %i]).pow(2) + (df_mw_psd['7_return_stdev_%s' %i]/df_mw_psd['7_return_mean_%s' %i]).pow(2))


eff = eff.iloc[:,-12:]
   
eff['Initial'] = (1/3) * (eff['initial_1'] + eff['initial_2'] + eff['initial_3'])
eff['Initial Error'] = (1/3) * np.sqrt(eff['initial_error_1'].pow(2) + eff['initial_error_2'].pow(2) + eff['initial_error_3'].pow(2))

eff['Final'] = (1/3) * (eff['final_1'] + eff['final_2'] + eff['final_3'])
eff['Final Error'] = (1/3) * np.sqrt(eff['final_error_1'].pow(2) + eff['final_error_2'].pow(2) + eff['final_error_3'].pow(2))

eff = eff.iloc[:,-4:]

eff['Overall'] = (1/2) * (eff['Initial'] + eff['Final'])
eff['Overall Error'] = (1/2) * np.sqrt(eff['Initial Error'].pow(2) + eff['Final Error'].pow(2))

eff.reset_index(inplace = True)
eff.rename(columns = {'index': 'Size'}, inplace = True)

eff['Size'] = eff['Size'].astype(float) / 1000
eff = eff[eff['Size'] >= 0.1]

eff.to_excel(backslash_correct('C:\PhD Research\QFF Evaluation\Processed\mini_wras_eff.xlsx'), index = False)

