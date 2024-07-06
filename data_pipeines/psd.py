# -*- coding: utf-8 -*-
"""
Program to measure PSD of filter dust samples and the adujsted PSD of airborne particles using filter efficiency

@author: alima
"""

import sys
sys.modules[__name__].__dict__.clear()

import pandas as pd
import numpy as np
from scipy import stats
import math
exec(open(r'C:\PhD Research\Generic Codes\notion_corrections.py').read())
exec(open(r'C:\PhD Research\Generic Codes\mastersizer_all.py').read())


#################################################
### Step 1: Reading filter forensics (FF) PSD ###
#################################################

path_in = backslash_correct(r'C:\PhD Research\QFF Evaluation\Raw\\')
path_out = backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\\') 

psd = mastersizer_input_v3(path_in, path_out, 'psd_qff_evaluation', 'psd_qff_evaluation')
psd = psd[['Size'] + [col for col in psd.columns if (('mean' in col) | ('std' in col)) & (col[13:14] == 'D') & ('r2' not in col)]]

psd.to_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_ff.xlsx'), index = False)


#######################################################################################
### Step 2: Calculating QFF PSD Using FF PSD and LDPS Size Efficiency from Mini-WRAS ##
#######################################################################################

df_mw = pd.read_excel(backslash_correct('C:\PhD Research\QFF Evaluation\Processed\mini_wras_eff.xlsx'))

for col in [col for col in df_mw.columns if 'Overall' in col]:
    i = 0
    N = len(df_mw) - 1
    while i < N:
        j = 1 + 1
        df_mw.loc[i, 'Sl_' + col] = (df_mw.loc[j,col]  - df_mw.loc[i,col])/(np.log(df_mw.loc[j,'Size'] - np.log(df_mw.loc[i,'Size'])))
        df_mw.loc[i, 'xic_' + col] = np.log(df_mw.loc[i,'Size'])
        df_mw.loc[i, 'yic_' + col] = df_mw.loc[i,col]
        i += 1

df_mw = df_mw[['Size'] + [col for col in df_mw.columns if 'Overall' in col]]
df_mw['Eq'] = 'MW'


df_ldps = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_ff.xlsx'))

df = df_mw.append(df_ldps).iloc[:,:-2]
df.drop_duplicates('Size', inplace = True)
df.sort_values('Size', inplace = True)
df.loc[df['Eq'] != 'MW', 'Eq'] = 'LDPS'
df = df[~(df['Size'] > 35.15)]

df.columns


for col in ['Sl_Overall', 'Sl_Overall Error', 'xic_Overall', 'yic_Overall', 'xic_Overall Error', 'yic_Overall Error']:
    df[col].fillna(method="ffill", inplace = True)


for col in ['Overall', 'Overall Error']:
    df[col].fillna(0, inplace = True)
    
    df[col] = df['yic_' + col] + df['Sl_' + col]  * (np.log(df['Size']) - df['xic_' + col])

df.loc[0,'Eq'] = 'LDPS'
df = df[df['Eq'] == 'LDPS']
df.loc[df['Overall'] > 100, 'Overall'] = 100
df = df.iloc[:,0:3]

df = df.merge(psd, on = 'Size', how = 'outer')
df['Overall'].fillna(100, inplace = True)
df['Overall Error'].fillna(0, inplace = True)

df['qff psd'] = df.iloc[:,3] / (df['Overall']/100)
df['qff psd'] = df['qff psd'] / (df['qff psd'].sum()/100)
df['qff psd error'] = df['qff psd'] * np.sqrt( (df['Overall Error']/df['Overall']).pow(2) + (df.iloc[:,4]/df.iloc[:,3]).pow(2) )
df['qff psd error'].fillna(0, inplace = True)
df = df[['Size', 'qff psd', 'qff psd error']]

df.to_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_qff.xlsx'), index = False)
