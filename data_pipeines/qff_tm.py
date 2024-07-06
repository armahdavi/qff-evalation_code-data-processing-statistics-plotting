# -*- coding: utf-8 -*-
"""
Program to calculate qff-integrated trace metal concentration from HVAC filter dust

@author: alima
"""

import sys
sys.modules[__name__].__dict__.clear()

import pandas as pd
import numpy as np
import re
exec(open(r'C:\PhD Research\Generic Codes\notion_corrections.py').read())

elem_list = stata_varlist_split('Pb As Cd Cu Zn Ni K Ti V Fe Sr Sb')

##########################################################
### Step 1: Calculation of the integrated airborne TMs ###
##########################################################

df = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\tm_mass.xlsx'))

a = df.iloc[:,1].sum()
tm = df.iloc[:,2:14].sum().reset_index(drop = True)
tm_error = df.iloc[:,-12:].pow(2).sum().pow(0.5).reset_index(drop = True)
b = (tm / ( a * ( (7*24*60)/1000) )   ) * 1000
c = b * np.sqrt(  (tm_error/tm).pow(2)  +  0.025**2  +  ((0.1*6**0.5)/a) **2 )

df = pd.concat([pd.Series(elem_list), b, c], axis = 1)

df.columns = ['Element', 'Concentration', 'Error']
df['measure'] = 'ab'

#############################################
### Step 2: Calculating TMS form QFF HVAC ###
#############################################

## M: Mass of dust on filter
mass = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Des\lds_extraction_qff_F00_00_190927_am.xlsx'), sheet_name = 'Filter_mass').iloc[0:5,0:2]
M = mass.iloc[4,1] - mass.iloc[0:2,1].mean()
M_error = np.sqrt( mass.iloc[-3:,1].std()**2 + mass.iloc[0:2,1].std()**2 + 1.3 ** 2)

## V: Filtration volume
volume = pd.read_excel(backslash_correct(r'C:\Career\Learning\Python Practice\Stata_Python_Booster\PhD - QFF\Processed\filtration_volume.xlsx'))
volume = volume[['FV All', 'FV All Error']]
volume['FV All Error'] = volume['FV All Error'].pow(2)
V = volume['FV All'].sum()
V_error = volume['FV All Error'].sum()**0.5

## f: concentration in dust (ug/g)
# Uncertainty error
uc_error = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Des\Chemicals\Metals_UC.xlsx'))
# uc_error = uc_error[0]
uc_error.rename(columns = {'Unnamed: 0': 'Filter S/N'}, inplace = True)

pattern = '\D+'
a = dict(zip([col for col in uc_error.columns][1:], [re.findall(pattern,col)[0] for col in uc_error.columns][1:]))

uc_error.rename(columns = a, inplace = True)
uc_error = uc_error[elem_list]
uc_error = uc_error.iloc[0,:].reset_index()
uc_error.rename(columns = {'index': 'Element',
                           0: 'Dev UC'}, inplace = True)

# MDL error
mdl_error = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\tm_mdl_errors.xlsx')).iloc[0,:-1].reset_index()
mdl_error[0] = mdl_error[0].astype(float)
mdl_error.rename(columns = {'index': 'Element',
                            0: 'MDL UC'}, inplace = True)

# Combining as an overall uncertainty
tm_error = uc_error.merge(mdl_error, on = 'Element', how = 'outer')
tm_error['overall uc'] = np.sqrt(tm_error['Dev UC'].pow(2) + tm_error['MDL UC'].pow(2))
tm_error.drop(['Dev UC', 'MDL UC'], axis = 1, inplace = True)

# f 
f = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Des\Chemicals\Metals Results_Alireza.xlsx'), sheet_name = 'raw')
f = f.loc[2,elem_list].reset_index()
f.rename(columns = {'index': 'Element',
                    2: 'f'}, inplace = True)
f['f']=f['f'].astype(float)

# bringing all parameters into a signle df
df_qff = tm_error.merge(f, on = 'Element')
df_qff['Concentration'] = ((M * df_qff['f'])/V) * 1000
df_qff['Error'] = df_qff['Concentration'] * np.sqrt(  (M_error/M)**2  +  0.07**2  +  (df_qff['overall uc']/df_qff['f']).pow(2)  +  0.003**2  )
df_qff['measure'] = 'qff'
df = df.append(df_qff).iloc[:,:-2].reset_index(drop = True)

df.to_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\\Processed\tm_qff.xlsx'), index = False)
