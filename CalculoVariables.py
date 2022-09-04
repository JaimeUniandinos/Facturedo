import pandas as pd
import numpy as np
from datetime import date

def leeArchivo(id_cliente):
    
    data_df = pd.read_csv('https://docs.google.com/spreadsheets/d/1hm8N820bkxEY76bgkeYP6Aq34qmOhbU1/export?format=csv&gid=553941507', decimal=",")
    data_df['amount'] = data_df['amount'].astype('float')
    data_df['payment_date'] = pd.to_datetime(data_df['payment_date'], format='%d/%m/%Y')
    data_df['creation_date'] = pd.to_datetime(data_df['creation_date'], format='%d/%m/%Y')
    return data_df
    
def punto1(data_df,id_cliente):
    conteo_operaciones = data_df[data_df['id deudor'] == id_cliente].groupby('result')['operation_id'].count().to_dict()
    return conteo_operaciones
    
def punto2(data_df,id_cliente):
    pagados_df = data_df[data_df['result'] == 'Pagada'].where(data_df['id deudor'] == id_cliente)
    dias_promedio_pago_ops_pagadas = (pagados_df['payment_date'] - pagados_df['creation_date']).dt.days.mean().round()
    return dias_promedio_pago_ops_pagadas
    
def punto3(data_df):
    iqr = (data_df['amount'].quantile(.75) - data_df['amount'].quantile(.25))
    data_df[data_df['amount'] < (data_df['amount'].quantile(.75) - iqr * 1.5)]
    umbrales_outliers = {'umbral_inf': int(data_df['amount'].quantile(.25) - iqr * 1.5), 'umbral_superior': int(data_df['amount'].quantile(.75) + iqr * 1.5)}
    return umbrales_outliers
    
def punto4(data_df,id_cliente):
    tipo_pago_max_volumen = data_df.where(data_df['id deudor'] == id_cliente).groupby('payment_method')['amount'].max().astype(int).to_dict()
    return tipo_pago_max_volumen

def punto5(data_df,id_cliente,umbrales_outliers):
    operaciones_max_outliers = data_df[data_df['amount'].where(data_df['id deudor'] == id_cliente) > umbrales_outliers['umbral_superior']]
    lista_operaciones = dict(zip(operaciones_max_outliers['operation_id'], operaciones_max_outliers['amount'].astype(int)))
    return lista_operaciones
    
def punto6(data_df,id_cliente):
    last_six_moths_df = data_df.where(data_df['id deudor'] == id_cliente).copy()
    last_six_moths_df['date_today'] = date.today()
    last_six_moths_df['difference_days'] = pd.to_datetime(last_six_moths_df['date_today']) -  pd.to_datetime(last_six_moths_df['creation_date'])
    last_six_moths_df[last_six_moths_df['difference_days']/np.timedelta64(1, 'D') <=180]
    last_six_moths_df['cration_dat_year_month'] = data_df['creation_date'].dt.to_period('M')
    prom_max_ult_6_meses = last_six_moths_df.groupby('cration_dat_year_month')['amount'].max().mean()
    return prom_max_ult_6_meses
    
def punto7(data_df,id_cliente):
    dict_nulls = {}
    new_data_df = data_df.where(data_df['id deudor'] == id_cliente).copy()
    new_data_df['creation_date_formatted'] = data_df['creation_date'].dt.strftime('%Y-%m-%d')
    for column in data_df.columns:
        if column != 'creation_date':
            new_null = new_data_df[new_data_df[column].isnull()].set_index('creation_date_formatted')[column].astype(str).to_dict()
            #new_null = dict(zip(new_data_df[new_data_df[column].isnull()], column))
        #else:
        #    new_null= {date.today().strftime('%Y-%m-%d'): 'creation_date'}
        dict_nulls.update(new_null)
    return dict_nulls