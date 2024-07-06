# -*- coding: utf-8 -*-
"""
Program to measure HVAC flow rate needed for QFF estimation of PM and trace metals

@author: alima
"""

import sys
sys.modules[__name__].__dict__.clear()
import pandas as pd
import numpy as np
exec(open(r'C:\PhD Research\Generic Codes\notion_corrections.py').read())


##################################################
### Step 1: Reading TFSOP values for later use ###
##################################################

df = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Des\Pressure_Flow_v09_191114_am.xlsx'))
TFP_p = round(df.iloc[0,12],2)
TFP_flow = round(df.iloc[0,13],2)

df = df[(df['Pressure_Type'] == 'TFSOP_return') | (df['Pressure_Type'] == 'TFSOP_supply')]
TFSOP_p_supply = df.iloc[0,12]
TFSOP_p_return = df.iloc[1,12]

#############################################################
### Step 2: Flow calculations based on TFSOP and pressure ###
#############################################################

df = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Des\Pressure_Flow_v09_191114_am.xlsx'))
df = df[(df['Pressure_Type'].str[0:4] == 'NSOP') & (df['Pressure_Type'].str[-4:] != 'down')]

df.loc[df['Pressure_Type'].str[-6:] == 'supply', 'Flow'] = np.sqrt(df['Average_Pressure']/TFSOP_p_supply) * TFP_flow
df.loc[df['Pressure_Type'].str[-6:] == 'return', 'Flow'] = np.sqrt(df['Average_Pressure']/TFSOP_p_return) * TFP_flow

df = df[['Visit_#', 'Date', 'Pressure_Type', 'System_Mode', 'Average_Pressure', 'Flow']]
df_ratio = df[df['Visit_#'] == 7]
df_ratio.sort_values(['Pressure_Type', 'System_Mode'], inplace = True)
df_ratio.reset_index(inplace= True)

ret_ratio = df_ratio.loc[0,'Flow']/df_ratio.loc[1,'Flow']
sup_ratio = df_ratio.loc[2,'Flow']/df_ratio.loc[3,'Flow']

df = df.iloc[:-2,:][['Visit_#', 'Pressure_Type', 'Flow']]
df['Pressure_Type'] = df['Pressure_Type'].str[-6:]
df.set_index(['Visit_#', 'Pressure_Type'], inplace = True)

df = df.unstack(level = -1)
df.columns = ['Flow Fan Return','Flow Fan Supply']

'''
# This didn't work'
df.rename(columns = {('Flow', 'return'): 'Flow Fan Return',
                     ('Flow', 'supply'): 'Flow Fan Supply'}, inplace = True)
'''

df['Flow Compressor Return'] = df['Flow Fan Return'] * ret_ratio
df['Flow Compressor Supply'] = df['Flow Fan Supply'] * sup_ratio

df = df * 1.699

df['Flow Fan'] = df[['Flow Fan Return', 'Flow Fan Supply']].mean(axis = 1)
df['Flow Compressor'] = df[['Flow Compressor Return', 'Flow Compressor Supply']].mean(axis = 1)

df['Flow Fan Error'] = df[['Flow Fan Return', 'Flow Fan Supply']].std(axis = 1)
df['Flow Compressor Error'] = df[['Flow Compressor Return', 'Flow Compressor Supply']].std(axis = 1)

df = df.iloc[:,-4:]

for i in range(1,len(df)):
    for col in df.columns:
        j = i + 1
        df.loc[i,col] = (df.loc[i,col] + df.loc[j,col]) / 2

df['Flow Fan Error'] = np.sqrt(df['Flow Fan Error'].pow(2) + (0.07 * df['Flow Fan']).pow(2))
df['Flow Compressor Error'] = np.sqrt(df['Flow Compressor Error'].pow(2) + (0.07 * df['Flow Compressor']).pow(2))
df = df.iloc[:-1,:]
df.rename(columns = {'visit_#': 'visit'}, inplace = True)
df.reset_index(inplace = True)

df.to_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\flow_rates.xlsx'), index = False)

