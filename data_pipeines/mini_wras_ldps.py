# -*- coding: utf-8 -*-
"""
Program to adjust the size bins of PSD data between laser diffraction particle sizer (LDPS) and mini-WRAS
The program has no output but processed data are copied manually for further use in the project

@author: alima
"""

import sys
sys.modules[__name__].__dict__.clear()
import pandas as pd
import numpy as np
from scipy import stats
import math
exec(open(r'C:\PhD Research\Generic Codes\notion_corrections.py').read())

###########################################
### Step 1: Reading from Mini-WRAS Data ###
###########################################

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

######################################
### Step 2: Reading from LDPS Data ###
######################################

df_ldps = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_qff_evaluation.xlsx'))

df = df_mw.append(df_ldps).iloc[:,:-1]
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