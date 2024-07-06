# -*- coding: utf-8 -*-
"""
Complemetary: Program to integrate and caluclate concentration of PM using QFF (HVAC filter meta data and dust mass collected on the filter)

@author: alima
"""

import sys
sys.modules[__name__].__dict__.clear()

import pandas as pd
import numpy as np

exec(open(r'C:\PhD Research\Generic Codes\notion_corrections.py').read())
exec(open(r'C:\PhD Research\Generic Codes\mastersizer_all.py').read())


####################################################
### Step 1: Calculation of Mastersizer fractions ###
####################################################

df = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_qff.xlsx'))
df['qff psd error 2'] = df['qff psd error'].pow(2)

s_pm1 = pd.Series([df['qff psd'].iloc[:20].sum() , df['qff psd error 2'].iloc[:19].sum() ** 0.5])/100
s_pm25 = pd.Series([df['qff psd'].iloc[:28].sum() , df['qff psd error 2'].iloc[:28].sum() ** 0.5])/100
s_pm10 = pd.Series([df['qff psd'].iloc[:40].sum() , df['qff psd error 2'].iloc[:40].sum() ** 0.5])/100
s_pm1_25 = pd.Series([df['qff psd'].iloc[20:28].sum() , df['qff psd error 2'].iloc[20:28].sum() ** 0.5])/100
s_pm25_10 = pd.Series([df['qff psd'].iloc[28:40].sum() , df['qff psd error 2'].iloc[28:40].sum() ** 0.5])/100

s = pd.concat([s_pm10, s_pm25, s_pm1, s_pm25_10, s_pm1_25], axis = 1).T
s.rename(columns = {0: 'Fraction', 1: 'Error'}, inplace = True)

###########################################
### Step 2: Combination with efficiency ###
###########################################

eff = pd.read_excel(backslash_correct('C:\PhD Research\QFF Evaluation\Processed\mini_wras_eff_pm.xlsx'))
eff['Efficiency'] = (eff['Initial'] + eff['Final'])/2
eff['Efficiency Error'] = (1/2) * np.sqrt(eff['Initial Error'].pow(2) + eff['Final Error'].pow(2))

eff = eff[['PM', 'Efficiency', 'Efficiency Error']]

df = pd.concat([s, eff], axis = 1)
df = df[['PM', 'Fraction', 'Error', 'Efficiency', 'Efficiency Error']]


##########################################
### Step 3: Reading HVAC data: M and V ###
##########################################

mass = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Des\lds_extraction_qff_F00_00_190927_am.xlsx'), sheet_name = 'Filter_mass').iloc[0:4,0:2]
# mass2 = pd.read_excel(backslash_correct(r'C:\Career\Learning\Python Practice\Stata_Python_Booster\PhD - QFF\Des\lds_extraction_qff_F00_00_190927_am.xlsx'), sheet_name = 'Filter_mass').iloc[0:5,0:2]
# M.dropna(subset = ['stat'], axis = 1, inplace = True)
M = mass.groupby('stat', as_index = False)['mass'].agg('mean').iloc[0,1] - mass.groupby('stat', as_index = False)['mass'].agg('mean').iloc[1,1]
M_error = (mass.groupby('stat', as_index = False)['mass'].agg('std').iloc[0,1]**2 + mass.groupby('stat', as_index = False)['mass'].agg('std').iloc[1,1]**2 + 1.3 **2)**0.5

volume = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\filtration_volume.xlsx'))
volume = volume[['FV All', 'FV All Error']]
volume['FV All Error'] = volume['FV All Error'].pow(2)

V = volume['FV All'].sum()
V_error = volume['FV All Error'].sum()**0.5

###############################################################
### Step 4: Calculating QFF TSP and other PM concnetrations ###
###############################################################

df['Concentration'] = (M * df['Fraction'])/((df['Efficiency']/100) * V) * 1000000
df['C Error'] = df['Concentration'] * np.sqrt(  (M_error/M)**2  +   (df['Error']/df['Fraction']).pow(2)  +  (df['Efficiency Error']/df['Efficiency']).pow(2)  +  (V_error/V)**2  )
df.drop(['Fraction', 'Error', 'Efficiency', 'Efficiency Error'], inplace = True, axis = 1)
df.rename(columns = {'C Error' : 'Error'}, inplace = True)

tsp = M/V * 1000000
tsp_error = tsp * (  (M_error/M)**2  +  (V_error/V)**2   )**0.5

zeros = [ [0] * 3 for _ in range(4)]

df_new = pd.DataFrame(np.array(zeros), columns = ['PM', 'Concentration', 'Error'])
df_new.iloc[0] = ['TSP', tsp, tsp_error]
df_new.iloc[1] = ['PM10_inf', tsp - df.iloc[0,1], (tsp_error ** 2 + df.iloc[0,2]**2)**0.5]
df_new.iloc[2] = ['PM2.5_inf', tsp - df.iloc[1,1],  (tsp_error ** 2 + df.iloc[1,2]**2)**0.5]
df_new.iloc[3] = ['PM1_inf', tsp - df.iloc[2,1],  (tsp_error ** 2 + df.iloc[2,2]**2)**0.5]

df = df.append(df_new)
df['Measure'] = 'qff'

df.to_excel(backslash_correct('C:\PhD Research\QFF Evaluation\Processed\qff_pm.xlsx'), index = False)
