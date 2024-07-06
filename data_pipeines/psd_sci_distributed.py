# -*- coding: utf-8 -*-
"""
Program to make PSD of SCI distributed over LDPS particle size range

@author: alima
"""

import sys
sys.modules[__name__].__dict__.clear()

import pandas as pd
import numpy as np
exec(open(r'C:\PhD Research\Generic Codes\notion_corrections.py').read())


psd = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_qff.xlsx')) #.iloc[:,0]
psd = psd[psd["Size"] <= 1000]

df = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_sci_unstack.xlsx'))
df = df[['FP', 'Mass Perc', 'Mass Perc Error', 'Size']]

df = df.merge(psd, on ='Size', how = 'outer').sort_values('Size')
df.drop(['Mass Perc Error'], axis = 1, inplace = True)
df['Mass Perc'].fillna(method = 'ffill', inplace = True)
df['FP'].fillna(method = 'ffill', inplace = True)

count = df.groupby('FP', as_index = False).agg('count').iloc[:,:2].rename(columns = {'Mass Perc': 'Count'})
df = df.merge(count, on = 'FP', how = 'outer')
df['Mass Perc'] = df['Mass Perc'] / df['Count']

df = df.iloc[:,:3]
df = df[['Size', 'Mass Perc', 'FP']]

## Hard-coding with known PSD values of SCI
l1 = [0.251, 0.501, 1, 2.51, 10] 
l2 = [2.7272, 1.38262, 0.248422, 0.449965, 0.835937]
l3 = ['E', 'D', 'C', 'B',  'A']

add = pd.DataFrame({'Size': l1,
                 'Mass Perc': l2,
                 'FP': l3})

df = df.append(add).sort_values('FP', ascending = True).sort_values('Size')

df.to_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\psd_sci_dsitributed.xlsx'), index = False)
