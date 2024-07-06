# -*- coding: utf-8 -*-
"""
Program to calculate filtration volume of HVAC visit by visit 

@author: alima
"""

import sys
sys.modules[__name__].__dict__.clear()
import pandas as pd
import numpy as np
exec(open(r'C:\PhD Research\Generic Codes\notion_corrections.py').read())

### Reading runtime (in hours) and flow rate in m3/h to calculation filtration volume (Q*t)

df1 = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\runtime_hr.xlsx'))
df2 = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\flow_rates.xlsx'))
df2.rename(columns = {'Visit_#': 'visit'}, inplace = True)

df = df1.merge(df2, on = 'visit')

df['FV C'] = df['Compressor'] * df['Flow Compressor']
df['FV F'] = df['Fan Only'] * df['Flow Fan']
df['FV All'] = df['FV C'] + df['FV F']

df['FV C Error'] = df['Compressor'] * df['Flow Compressor Error']
df['FV F Error'] = df['Fan Only'] * df['Flow Fan Error']
df['FV All Error'] = np.sqrt(df['FV C Error'].pow(2) + df['FV F Error'].pow(2))
df = df[['FV C', 'FV F', 'FV All', 'FV C Error', 'FV F Error', 'FV All Error']]

df.to_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\filtration_volume.xlsx'))
