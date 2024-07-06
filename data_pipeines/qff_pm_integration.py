# -*- coding: utf-8 -*-
"""
Program to integrate and caluclate concentration of PM using QFF (HVAC filter meta data and dust mass collected on the filter)

@author: alima
"""

import sys
sys.modules[__name__].__dict__.clear()

import pandas as pd
import numpy as np
from scipy import stats
import math
exec(open(r'C:\PhD Research\Generic Codes\notion_corrections.py').read())


pm25_cor_factor = 1.061952
df = pd.read_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\pm_master_all_error.xlsx'))
df.columns

df_mass = df[['TSP Mass', 'PM10 SCI Mass', 'PM2.5 SCI Mass', 'PM1 SCI Mass']].sum().reset_index(drop=True)
df_mass_error = df[['TSP Mass Error', 'PM10 SCI Mass Error', 'PM2.5 SCI Mass Error', 'PM1 SCI Mass Error']].pow(2).sum().pow(0.5).reset_index(drop=True)


df_flow = df[['Average Flow FC', 'Average Flow SCI']].sum()

df_pm_conc = pd.Series([0,0,0,0])

df_pm_conc.iloc[0] = (df_mass.iloc[0] / (df_flow.iloc[0] * (7*24*60))) * 1000000
df_pm_conc.iloc[1:] = ((df_mass.iloc[1:]) / (df_flow.iloc[1] * (7*24*60))) * 1000000 

df_conc_error = pd.Series([0,0,0,0])

df_conc_error.iloc[0] = df_pm_conc.iloc[0] * np.sqrt(  (df_mass_error.iloc[0]/df_mass.iloc[0])**2   +   ((0.5 * math.sqrt(6)) / (df_flow.iloc[0])) ** 2  +   0.025 ** 2  )
# df_conc_error.iloc[0] = df_pm_conc.iloc[0] * np.sqrt(  (df_mass_error.iloc[0]/df_mass.iloc[0])**2   +   ((0.1 * math.sqrt(6)) / (df_flow.iloc[0])) ** 2  +   0.025 ** 2  )
df_conc_error.iloc[1:] = df_pm_conc.iloc[1:] * np.sqrt(  (df_mass_error.iloc[1:]/df_mass.iloc[1:]).pow(2)   +   ((0.5 * math.sqrt(6)) / (df_flow.iloc[1])) ** 2  +   0.025 ** 2  )

df_pm_conc[1:] = df_pm_conc[1:] * pm25_cor_factor
df_conc_error.iloc[1:] = df_conc_error.iloc[1:] * pm25_cor_factor

df_pm_conc_compl = pd.Series([0,0,0,0,0])
df_pm_conc_compl.iloc[0] = df_pm_conc.iloc[0] - df_pm_conc.iloc[1] # PM10_inf
df_pm_conc_compl.iloc[1] = df_pm_conc.iloc[0] - df_pm_conc.iloc[2] # PM2.5_inf
df_pm_conc_compl.iloc[2] = df_pm_conc.iloc[0] - df_pm_conc.iloc[3] # PM1_inf
df_pm_conc_compl.iloc[3] = df_pm_conc.iloc[1] - df_pm_conc.iloc[2] # PM2.5_10
df_pm_conc_compl.iloc[4] = df_pm_conc.iloc[2] - df_pm_conc.iloc[3] # PM1_2.5

df_pm_error_compl = pd.Series([0,0,0,0,0])
df_pm_error_compl.iloc[0] = (df_conc_error.iloc[0]**2 + df_conc_error.iloc[1]**2)**0.5 # PM10_inf Error
df_pm_error_compl.iloc[1] = (df_conc_error.iloc[0]**2 + df_conc_error.iloc[2]**2)**0.5 # PM2.5_inf Error
df_pm_error_compl.iloc[2] = (df_conc_error.iloc[0]**2 + df_conc_error.iloc[3]**2)**0.5 # PM1_inf Error
df_pm_error_compl.iloc[3] = (df_conc_error.iloc[1]**2 + df_conc_error.iloc[2]**2)**0.5 # PM2.5_10 Error
df_pm_error_compl.iloc[4] = (df_conc_error.iloc[2]**2 + df_conc_error.iloc[3]**2)**0.5 # PM1_2.5 Error

df_pm_conc = df_pm_conc.append(df_pm_conc_compl).reset_index(drop = True)
df_conc_error = df_conc_error.append(df_pm_error_compl).reset_index(drop = True)
pm_name = pd.Series(['TSP', 'PM10', 'PM2.5', 'PM1', 'PM10_inf', 'PM2.5_inf', 'PM1_inf', 'PM2.5_10', 'PM1_2.5'])
df = pd.concat([ pm_name, df_pm_conc,df_conc_error], axis = 1)
df.columns = ['PM', 'Concentration', 'Error']
df['Measure'] = 'ab'

df.to_excel(backslash_correct(r'C:\PhD Research\QFF Evaluation\Processed\ab_pm_integ.xlsx'), index = False)
