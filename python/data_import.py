# -*- coding: utf-8 -*-
# Requirements: pyjstat, sqlalchemy, pyodbc, json, requests, iterdools, pandas, numpy, statsmodels
"""
Created on Thu May  6 14:12:31 2021
"""
from pyjstat import pyjstat
import json
import requests
import itertools
import sqlalchemy as sal
import pandas as pd
import numpy as np
import statsmodels.api as sm



# Getting environment information from one level up
exec(open("../env_config.py").read())

# Connection string to your reporting database (parameters read from env_config.py just above)
engine = sal.create_engine("mssql+pyodbc://" + servername + "/" + databasename + "?driver=SQL Server?Trusted_Connection=yes")

# Fetch mortality information

URL = 'https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/StatFin/vrm/kuol/statfin_kuol_pxt_12ap.px'

post_data = {
  "query": [
    {
      "code": "Vuosi",
      "selection": {
        "filter": "item",
        "values": [
          "2019","2009"
        ]
      }
    },
    {
      "code": "Sukupuoli",
      "selection": {
        "filter": "item",
        "values": [
          "SSS",
          "1",
          "2"
        ]
      }
    },
    {
      "code": "Tiedot",
      "selection": {
        "filter": "item",
        "values": [
          "kvaara"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}


response = requests.post(URL, data=json.dumps(post_data))
kuolleisuus = pyjstat.from_json_stat(response.json())[0]
kuolleisuus= kuolleisuus.rename({'value': 'kuolleisuus'}, axis='columns')
kuolleisuus=kuolleisuus.astype({"Ikä": int})

kuolleisuus_2009=kuolleisuus.loc[kuolleisuus["Vuosi"]=='2009']
kuolleisuus_2009=kuolleisuus_2009.drop(columns=['Tiedot','Vuosi']).ffill(axis=0)

kuolleisuus_2019=kuolleisuus.loc[kuolleisuus["Vuosi"]=='2019']
kuolleisuus_2019=kuolleisuus_2019.drop(columns=['Tiedot','Vuosi']).ffill(axis=0)


# Fetch information about movements between municipalities

URL = 'https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/StatFin/vrm/muutl/statfin_muutl_pxt_11a2.px'

post_data = {
  "query": [
    {
      "code": "Alue",
      "selection": {
        "filter": "item",
        "values": [
          "KU837"
        ]
      }
    },
    {
      "code": "Sukupuoli",
      "selection": {
        "filter": "item",
        "values": [
          "SSS"
        ]
      }
    },
    {
      "code": "Ikä",
      "selection": {
        "filter": "item",
        "values": [
          "SSS",
          "0-4",
          "5-9",
          "10-14",
          "15-19",
          "20-24",
          "25-29",
          "30-34",
          "35-39",
          "40-44",
          "45-49",
          "50-54",
          "55-59",
          "60-64",
          "65-69",
          "70-74",
          "75-"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

response = requests.post(URL, data=json.dumps(post_data))
muutto_suomessa = pyjstat.from_json_stat(response.json())[0]




# Fecth birthrate information

URL = 'https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/StatFin/vrm/synt/statfin_synt_pxt_12ds.px'

post_data = {
  "query": [
    {
      "code": "Vuosi",
      "selection": {
        "filter": "item",
        "values": [
          "2020","2010"
        ]
      }
    },
    {
      "code": "Äidin ikä",
      "selection": {
        "filter": "item",
        "values": [
          "SSS",
          "15-19",
          "20-24",
          "25-29",
          "30-34",
          "35-39",
          "40-44",
          "45-49"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

response = requests.post(URL, data=json.dumps(post_data))
syntyvyys = pyjstat.from_json_stat(response.json())[0]
syntyvyys= syntyvyys.rename({'value': 'Syntyvyys' , 'Äidin ikä': 'Ikäluokka'}, axis='columns')
syntyvyys['Sukupuoli']='Naiset'


syntyvyys_2010=syntyvyys.loc[syntyvyys["Vuosi"]=='2010']
syntyvyys_2010=syntyvyys_2010.drop(columns=['Tiedot','Vuosi']).ffill(axis=0)

syntyvyys_2020=syntyvyys.loc[syntyvyys["Vuosi"]=='2020']
syntyvyys_2020=syntyvyys_2020.drop(columns=['Tiedot','Vuosi']).ffill(axis=0)



# Fetch immigration information

URL = 'https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/StatFin/vrm/muutl/statfin_muutl_pxt_11a7.px'

post_data = {
  "query": [
    {
      "code": "Alue",
      "selection": {
        "filter": "item",
        "values": [
          "KU837"
        ]
      }
    },
    {
      "code": "Sukupuoli",
      "selection": {
        "filter": "item",
        "values": [
          "SSS",
          "1",
          "2"
        ]
      }
    },
    {
      "code": "Ikä",
      "selection": {
        "filter": "item",
        "values": [
          "SSS",
          "0-4",
          "5-9",
          "10-14",
          "15-19",
          "20-24",
          "25-29",
          "30-34",
          "35-39",
          "40-44",
          "45-49",
          "50-54",
          "55-59",
          "60-64",
          "65-69",
          "70-74",
          "75-"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

response = requests.post(URL, data=json.dumps(post_data))
maahanmuutto = pyjstat.from_json_stat(response.json())[0]


# Current population

vaesto = pd.read_excel('../tilastokeskus_väestötilastopalvelu.xlsx',sheet_name="001_12nh_2020",skiprows=[0,2]).ffill(axis=0)
vaesto.columns=['Osa-Alue','Ikä','Kieli','Tiedot','Sukupuoli','Asukasluku']
vaesto['Vuosi']=2020
vaesto=vaesto.drop(columns=['Tiedot'])
analyysivaesto=vaesto.loc[(vaesto['Osa-Alue']=='837 Tampere') & (vaesto['Kieli']!='Yhteensä') & (vaesto['Sukupuoli']!='Yhteensä') & (vaesto['Ikä']!='Yhteensä')]
analyysivaesto.loc[analyysivaesto['Ikä'] == '100-', 'Ikä'] = '100'
analyysivaesto=analyysivaesto.astype({"Ikä": int})

#Prepared data for first year in analysis
lahtodata=analyysivaesto[['Kieli','Ikä','Sukupuoli','Asukasluku','Vuosi']]


# Create support variables for births 

ikaluokat= pd.cut(analyysivaesto['Ikä'].astype(int),bins=[0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75, 111],labels=['0 - 4', '5 - 9' ,'10 - 14','15 - 19','20 - 24','25 - 29','30 - 34','35 - 39','40 - 44','45 - 49','50 - 54', '55 - 59', '60 - 64' , '65 - 69' , '70 - 74' , '75 -'],right=False)
analyysivaesto.insert(3,'Ikäluokka',ikaluokat)

syntyvyys_ikavuosittain=analyysivaesto[['Ikä','Ikäluokka','Sukupuoli']].drop_duplicates()
syntyvyys_sukupuolittain = pd.DataFrame(data={'Sukupuoli': ['Miehet','Naiset'], 'syntyvien_osuus': [0.51, 0.49]})

tarkennettu_syntyvyys=pd.merge(syntyvyys_ikavuosittain,syntyvyys_2020,how='left',on=["Sukupuoli","Ikäluokka"])
tarkennettu_syntyvyys=tarkennettu_syntyvyys.drop(columns=['Ikäluokka']).astype({"Ikä": int})

# Create support variables for migration - proportion of total migration for each age and sex

def calculate_migration_proportion(migration_year):
    #Suppose that 99.5 % of net migration within Finland is Finnish speaking and 0.5 % Swedish speaking . 
    #Suppose that net migration within Finland is Finnish/Swedish speaking and net migration from/to abroad speak foreign languages
    nettomuutto_suomi=muutto_suomessa.loc[(muutto_suomessa['Vuosi']==migration_year) & 	( muutto_suomessa['Tiedot']=="Kuntien välinen nettomuutto") & 	( muutto_suomessa['Ikä']!="Yhteensä") ].copy()
    nettomuutto_suomi['Kieli']='suomi'
    nettomuutto_suomi['value']=nettomuutto_suomi['value']*0.995
    
    nettomuutto_ruotsi=muutto_suomessa.loc[(muutto_suomessa['Vuosi']==migration_year) & 	( muutto_suomessa['Tiedot']=="Kuntien välinen nettomuutto") & 	( muutto_suomessa['Ikä']!="Yhteensä") ].copy()
    nettomuutto_ruotsi['Kieli']='ruotsi'
    nettomuutto_ruotsi['value']=nettomuutto_ruotsi['value']*0.005
    
    nettomuutto_vieraskieliset=maahanmuutto.loc[(maahanmuutto['Vuosi']==migration_year) & 	( maahanmuutto['Tiedot']=="Nettomaahanmuutto") & ( maahanmuutto['Ikä']!="Yhteensä") & ( maahanmuutto['Sukupuoli']=="Yhteensä") ].copy()
    nettomuutto_vieraskieliset['Kieli']='VIERASKIELISET YHTEENSÄ'
    
    nettomuutto_osuus=nettomuutto_suomi.append(nettomuutto_vieraskieliset).append(nettomuutto_ruotsi)
    
    ikaluokka_n = nettomuutto_osuus.groupby(['Kieli', 'Ikä']).agg({'value': 'sum'})
    kieli_n = nettomuutto_osuus.groupby(['Kieli']).agg({'value': 'sum'})
    
    muutto_osuus=ikaluokka_n.div(kieli_n, level='Kieli') 
    muutto_osuus.reset_index(inplace=True)
    muutto_osuus = muutto_osuus.rename(columns = {'Ikä':'Ikäluokka'})
    muutto_osuus =pd.merge(muutto_osuus,syntyvyys_ikavuosittain,on='Ikäluokka',how='right')
    muutto_osuus['muutto_osuus']=np.where((muutto_osuus['Ikäluokka']=="75 -"), muutto_osuus['value']/52, muutto_osuus['value']/10)
    muutto_osuus=muutto_osuus[['Kieli','Ikä','Sukupuoli','muutto_osuus']]
    return muutto_osuus, kieli_n

muutto_osuus, kieli_n = calculate_migration_proportion("2020")

# Create support variables for migration - predicted total migration amount
# In the Tampere city väestösuunnite, net migration is 3071 at 2020 and increases 1.38 % per year

kieli_osuus=kieli_n/sum(kieli_n['value'])
kieli_osuus.reset_index(inplace=True)
muutto_maara= pd.DataFrame({ 'Vuosi' : range(2021, 2072 ,1)})
muutto_maara=pd.merge(muutto_maara,kieli_osuus,how="cross")
muutto_maara['nettomuuttosumma']=3071* 1.0138 ** (muutto_maara['Vuosi']-2021) *muutto_maara['value']
muutto_maara=muutto_maara[['Kieli','Vuosi','nettomuuttosumma']]


# Function to calculate population for next year
def calculate_next_population(lahtodata,kuolleisuus, tarkennettu_syntyvyys,muutto_osuus,muutto_maara):
    laskuvuosi=lahtodata['Vuosi'].max()
    
    # Join changes to baseline
    vuoden_muutot=muutto_maara.loc[(muutto_maara['Vuosi']==laskuvuosi+1),['nettomuuttosumma','Kieli']]
    vuoden_muutot=pd.merge(vuoden_muutot,muutto_osuus,how="right",on="Kieli")
    vuoden_muutot['Nettomuutto']=vuoden_muutot['nettomuuttosumma']*vuoden_muutot['muutto_osuus']

    analyysivaesto2=pd.merge(lahtodata,kuolleisuus,how='left',on=["Sukupuoli","Ikä"])
    analyysivaesto3=pd.merge(analyysivaesto2,tarkennettu_syntyvyys,how='left',on=["Sukupuoli","Ikä"])
    analyysivaesto4=pd.merge(analyysivaesto3,vuoden_muutot,how='left',on=["Sukupuoli","Ikä","Kieli"])
       
    analyysivaesto4['Syntyvat']=analyysivaesto4['Syntyvyys']*analyysivaesto4['Asukasluku']/1000
    
    #Calculate births for next year
    
    ika0=analyysivaesto4.groupby(['Kieli'],as_index=False)['Syntyvat'].agg('sum')
    ika0['Ikä']=0
    ika0=pd.merge(ika0,syntyvyys_sukupuolittain,how='cross')
    ika0['Asukasluku']=ika0['Syntyvat']*ika0['syntyvien_osuus']
    ika0=ika0[['Kieli','Ikä','Sukupuoli','Asukasluku']]
    
    #Calculate population for next year    
    seuraava_vuosi=analyysivaesto4
    seuraava_vuosi['Ikä']=pd.to_numeric(seuraava_vuosi['Ikä'])+1
    seuraava_vuosi.loc[seuraava_vuosi['Ikä']>100,'Ikä']=100
    seuraava_vuosi['Asukasluku']=seuraava_vuosi['Asukasluku']*(1000-seuraava_vuosi['kuolleisuus'])/1000+seuraava_vuosi['Nettomuutto']

    seuraava_vuosi_summa=seuraava_vuosi.groupby(['Kieli','Ikä','Sukupuoli'],as_index=False)['Asukasluku'].agg('sum')

    valitulos=seuraava_vuosi_summa.append(ika0)
    valitulos['Vuosi']=laskuvuosi+1
    valitulos['Asukasluku']=valitulos['Asukasluku'].round()
    valitulos['Asukasluku']= np.where(valitulos['Asukasluku'] < 0, 0, valitulos['Asukasluku'])

    return valitulos


#Use function to loop through i years


tulokset = []
valitulos=lahtodata

i = 1
while i < 51:
  valitulos=calculate_next_population(lahtodata=valitulos,kuolleisuus=kuolleisuus_2019, tarkennettu_syntyvyys=tarkennettu_syntyvyys,muutto_osuus=muutto_osuus,muutto_maara=muutto_maara )
  tulokset.append(valitulos)
  i += 1

tulokset = pd.concat(tulokset)


#Use ARIMA to predict migration amount


nettomuutto_suomi_historia=muutto_suomessa.loc[( muutto_suomessa['Tiedot']=="Kuntien välinen nettomuutto") & 	( muutto_suomessa['Ikä']=="Yhteensä") ].copy()
nettomuutto_suomi_historia.Vuosi=pd.to_datetime(nettomuutto_suomi_historia.Vuosi, format='%Y')
nettomuutto_suomi_historia = nettomuutto_suomi_historia.set_index('Vuosi')


y = nettomuutto_suomi_historia['value']


#Find optimal hyperparameter value for ARIMA

def find_optimal_ARIMA_hyperparameters(y):
    p = d = q = range(0, 3)
    pdq = list(itertools.product(p, d, q))
    parameters = []
    for param in pdq:
        try:
            model = sm.tsa.statespace.SARIMAX(y,method='css',
                                            order=param,
                                            enforce_stationarity=False,
                                            enforce_invertibility=False)
            results = model.fit()
        except:
            continue
        aic = results.aic
        parameters.append([param,aic])
    result_table = pd.DataFrame(parameters)
    result_table.columns = ['parameters','aic']
        # sorting in ascending order, the lower AIC is - the better
    return result_table.sort_values(by='aic', ascending=True).reset_index(drop=True)


hyperparameter_result_table=find_optimal_ARIMA_hyperparameters(y)

#Fit best model

mod = sm.tsa.statespace.SARIMAX(y,
                                order=hyperparameter_result_table["parameters"][0],                          
                                enforce_stationarity=False,
                                enforce_invertibility=False)

results = mod.fit()

print(results.summary().tables[1])

#Plot Model Diagnostics
results.plot_diagnostics(figsize=(16, 8))

#Plot predicted one step ahead vs observed
pred = results.get_prediction(start=pd.to_datetime('2000-01-01'), dynamic=False)
ax = y['1990':].plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))


# Forecast next steps and save results
pred_uc = results.get_forecast(steps=80)
pred_ci = pred_uc.conf_int()

ax = y.plot(label='observed', figsize=(14, 7))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.25)
ax.set_xlabel('Date')
ax.set_ylabel('Forecasted Migration')

aikasarjaennuste=pred_uc.predicted_mean.to_frame()
aikasarjaennuste.reset_index(inplace=True)
aikasarjaennuste['Vuosi']=pd.DatetimeIndex(aikasarjaennuste['index']).year

aikasarjaennuste_suomi=aikasarjaennuste.copy()
aikasarjaennuste_suomi['Kieli']='suomi'
aikasarjaennuste_suomi['nettomuuttosumma']=aikasarjaennuste_suomi['predicted_mean']*0.995

aikasarjaennuste_ruotsi=aikasarjaennuste.copy()
aikasarjaennuste_ruotsi['Kieli']='ruotsi'
aikasarjaennuste_ruotsi['nettomuuttosumma']=aikasarjaennuste_suomi['predicted_mean']*0.005



# Repeat same steps time series forecasting steps for international migration

#Use ARIMA to predict migration amount


nettomaahanmuutto_historia=maahanmuutto.loc[( maahanmuutto['Tiedot']=="Nettomaahanmuutto") & 	( maahanmuutto['Ikä']=="Yhteensä")  & 	( maahanmuutto['Sukupuoli']=="Yhteensä") ].copy()
nettomaahanmuutto_historia.Vuosi=pd.to_datetime(nettomaahanmuutto_historia.Vuosi, format='%Y')
nettomaahanmuutto_historia = nettomaahanmuutto_historia.set_index('Vuosi')

y = nettomaahanmuutto_historia['value']


#Find optimal hyperparameter value for ARIMA

hyperparameter_result_table=find_optimal_ARIMA_hyperparameters(y)

#Fit best model

mod = sm.tsa.statespace.SARIMAX(y,
                                order=hyperparameter_result_table["parameters"][0],                          
                                enforce_stationarity=False,
                                enforce_invertibility=False)

results = mod.fit()

print(results.summary().tables[1])

#Plot Model Diagnostics
results.plot_diagnostics(figsize=(16, 8))

#Plot predicted one step ahead vs observed
pred = results.get_prediction(start=pd.to_datetime('2000-01-01'), dynamic=False)
ax = y['1990':].plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))


# Forecast next steps and save results
pred_uc = results.get_forecast(steps=80)
pred_ci = pred_uc.conf_int()

ax = y.plot(label='observed', figsize=(14, 7))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.25)
ax.set_xlabel('Date')
ax.set_ylabel('Forecasted Migration')

aikasarjaennuste_vieraskieliset=pred_uc.predicted_mean.to_frame()
aikasarjaennuste_vieraskieliset.reset_index(inplace=True)
aikasarjaennuste_vieraskieliset['Vuosi']=pd.DatetimeIndex(aikasarjaennuste_vieraskieliset['index']).year
aikasarjaennuste_vieraskieliset['Kieli']='VIERASKIELISET YHTEENSÄ'
aikasarjaennuste_vieraskieliset['nettomuuttosumma']=aikasarjaennuste_vieraskieliset['predicted_mean']

muutto_maara_aikasarja=aikasarjaennuste_suomi.append(aikasarjaennuste_vieraskieliset).append(aikasarjaennuste_ruotsi)
muutto_maara_aikasarja=muutto_maara_aikasarja[["Kieli", "Vuosi","nettomuuttosumma"]]




#WIP repeat the whole calculation using time series forecast as migration amount



tulokset_aikasarja = []
valitulos=lahtodata

i = 1
while i < 51:
  valitulos=calculate_next_population(lahtodata=valitulos,kuolleisuus=kuolleisuus_2019, tarkennettu_syntyvyys=tarkennettu_syntyvyys,muutto_osuus=muutto_osuus,muutto_maara=muutto_maara_aikasarja )
  tulokset_aikasarja.append(valitulos)
  i += 1

tulokset_aikasarja = pd.concat(tulokset_aikasarja)




#Validation:  repeat time series forecast approach starting from year 2010 and compare the results to 2020 


# Fetch population from 2010

URL = 'https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/StatFin/vrm/vaerak/statfin_vaerak_pxt_11rz.px'

post_data = {
  "query": [
    {
      "code": "Alue",
      "selection": {
        "filter": "item",
        "values": [
          "KU837"
        ]
      }
    },
    {
      "code": "Sukupuoli",
      "selection": {
        "filter": "item",
        "values": [
          "SSS",
          "1",
          "2"
        ]
      }
    },
    {
      "code": "Ikä",
      "selection": {
        "filter": "item",
        "values": [
          "SSS",
          "000",
          "001",
          "002",
          "003",
          "004",
          "005",
          "006",
          "007",
          "008",
          "009",
          "010",
          "011",
          "012",
          "013",
          "014",
          "015",
          "016",
          "017",
          "018",
          "019",
          "020",
          "021",
          "022",
          "023",
          "024",
          "025",
          "026",
          "027",
          "028",
          "029",
          "030",
          "031",
          "032",
          "033",
          "034",
          "035",
          "036",
          "037",
          "038",
          "039",
          "040",
          "041",
          "042",
          "043",
          "044",
          "045",
          "046",
          "047",
          "048",
          "049",
          "050",
          "051",
          "052",
          "053",
          "054",
          "055",
          "056",
          "057",
          "058",
          "059",
          "060",
          "061",
          "062",
          "063",
          "064",
          "065",
          "066",
          "067",
          "068",
          "069",
          "070",
          "071",
          "072",
          "073",
          "074",
          "075",
          "076",
          "077",
          "078",
          "079",
          "080",
          "081",
          "082",
          "083",
          "084",
          "085",
          "086",
          "087",
          "088",
          "089",
          "090",
          "091",
          "092",
          "093",
          "094",
          "095",
          "096",
          "097",
          "098",
          "099",
          "100-"
        ]
      }
    },
    {
      "code": "Vuosi",
      "selection": {
        "filter": "item",
        "values": [
          "1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020"
        ]
      }
    },
    {
      "code": "Kieli",
      "selection": {
        "filter": "item",
        "values": [
          "SSS",
          "01",
          "02"
        ]
      }
    },
    {
      "code": "Siviilisääty",
      "selection": {
        "filter": "item",
        "values": [
          "SSS"
        ]
      }
    }
  ],
  "response": {
    "format": "json-stat2"
  }
}

response = requests.post(URL, data=json.dumps(post_data))
vaestohistoria = pyjstat.from_json_stat(response.json())[0]



analyysivaesto_2010=vaestohistoria.loc[ (vaestohistoria['Kieli']!='Yhteensä') & (vaestohistoria['Sukupuoli']!='Yhteensä') & (vaestohistoria['Ikä']!='Yhteensä') & (vaestohistoria['Vuosi']=='2010')]
analyysivaesto_2010.loc[analyysivaesto_2010['Ikä'] == '100 -', 'Ikä'] = '100'
analyysivaesto_2010.loc[analyysivaesto_2010['Kieli'] == 'KOTIMAISET KIELET YHTEENSÄ', 'Kieli'] = 'suomi'
analyysivaesto_2010=analyysivaesto_2010.astype({"Ikä": int,"Vuosi": int})
analyysivaesto_2010.rename(columns = {'value' : 'Asukasluku'}, inplace = True)

lahtodata_2010=analyysivaesto_2010[['Kieli','Ikä','Sukupuoli','Asukasluku','Vuosi']].copy()




#Fetch other needed information

tarkennettu_syntyvyys_2010=pd.merge(syntyvyys_ikavuosittain,syntyvyys_2010,how='left',on=["Sukupuoli","Ikäluokka"])
tarkennettu_syntyvyys_2010=tarkennettu_syntyvyys_2010.drop(columns=['Ikäluokka']).astype({"Ikä": int})

muutto_osuus_2010, kieli_n_2010 = calculate_migration_proportion("2010")


#Create time series forecasts for 2010

y = nettomuutto_suomi_historia.loc[nettomuutto_suomi_historia.index < '2010-01-01','value']


#Find optimal hyperparameter value for ARIMA


hyperparameter_result_table=find_optimal_ARIMA_hyperparameters(y)


#Fit best model

mod = sm.tsa.statespace.SARIMAX(y,
                                order=hyperparameter_result_table["parameters"][0],                          
                                enforce_stationarity=False,
                                enforce_invertibility=False)

results = mod.fit()

print(results.summary().tables[1])

#Plot Model Diagnostics
results.plot_diagnostics(figsize=(16, 8))

#Plot predicted one step ahead vs observed
pred = results.get_prediction(start=pd.to_datetime('2000-01-01'), dynamic=False)
ax = y['1990':].plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))


# Forecast next steps and save results
pred_uc = results.get_forecast(steps=80)
pred_ci = pred_uc.conf_int()

ax = y.plot(label='observed', figsize=(14, 7))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.25)
ax.set_xlabel('Date')
ax.set_ylabel('Forecasted Migration')

aikasarjaennuste=pred_uc.predicted_mean.to_frame()
aikasarjaennuste.reset_index(inplace=True)
aikasarjaennuste['Vuosi']=pd.DatetimeIndex(aikasarjaennuste['index']).year

aikasarjaennuste_suomi_2010=aikasarjaennuste.copy()
aikasarjaennuste_suomi_2010['Kieli']='suomi'
aikasarjaennuste_suomi_2010['nettomuuttosumma']=aikasarjaennuste_suomi_2010['predicted_mean']



# Repeat same steps time series forecasting steps for international migration

#Use ARIMA to predict migration amount

y = nettomaahanmuutto_historia.loc[nettomuutto_suomi_historia.index < '2010-01-01','value']


#Find optimal hyperparameter value for ARIMA

hyperparameter_result_table=find_optimal_ARIMA_hyperparameters(y)

#Fit best model

mod = sm.tsa.statespace.SARIMAX(y,
                                order=hyperparameter_result_table["parameters"][0],                          
                                enforce_stationarity=False,
                                enforce_invertibility=False)

results = mod.fit()

print(results.summary().tables[1])

#Plot Model Diagnostics
results.plot_diagnostics(figsize=(16, 8))

#Plot predicted one step ahead vs observed
pred = results.get_prediction(start=pd.to_datetime('2000-01-01'), dynamic=False)
ax = y['1990':].plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='One-step ahead Forecast', alpha=.7, figsize=(14, 7))


# Forecast next steps and save results
pred_uc = results.get_forecast(steps=80)
pred_ci = pred_uc.conf_int()

ax = y.plot(label='observed', figsize=(14, 7))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.25)
ax.set_xlabel('Date')
ax.set_ylabel('Forecasted Migration')

aikasarjaennuste_vieraskieliset_2010=pred_uc.predicted_mean.to_frame()
aikasarjaennuste_vieraskieliset_2010.reset_index(inplace=True)
aikasarjaennuste_vieraskieliset_2010['Vuosi']=pd.DatetimeIndex(aikasarjaennuste_vieraskieliset_2010['index']).year
aikasarjaennuste_vieraskieliset_2010['Kieli']='VIERASKIELISET YHTEENSÄ'
aikasarjaennuste_vieraskieliset_2010['nettomuuttosumma']=aikasarjaennuste_vieraskieliset_2010['predicted_mean']

muutto_maara_aikasarja_2010=aikasarjaennuste_suomi_2010.append(aikasarjaennuste_vieraskieliset_2010)
muutto_maara_aikasarja_2010=muutto_maara_aikasarja_2010[["Kieli", "Vuosi","nettomuuttosumma"]]

#Run the validation forecast

tulokset_validointi = []
valitulos=lahtodata_2010

i = 1
while i < 51:
  valitulos=calculate_next_population(lahtodata=valitulos,kuolleisuus=kuolleisuus_2009, tarkennettu_syntyvyys=tarkennettu_syntyvyys_2010,muutto_osuus=muutto_osuus_2010,muutto_maara=muutto_maara_aikasarja_2010 )
  tulokset_validointi.append(valitulos)
  i += 1

tulokset_validointi = pd.concat(tulokset_validointi)






# Write to db

kuolleisuus.to_sql("kuolleisuus",engine,if_exists="replace",method="multi",chunksize=200,index=False)
muutto_suomessa.to_sql("muutto_suomessa",engine,if_exists="replace",method="multi",chunksize=200,index=False)
syntyvyys.to_sql("syntyvyys",engine,if_exists="replace",method="multi",chunksize=200,index=False)
maahanmuutto.to_sql("maahanmuutto",engine,if_exists="replace",method="multi",chunksize=200,index=False)
tulokset.to_sql("vaestoennuste",engine,if_exists="replace",method="multi",chunksize=200,index=False)
tulokset_aikasarja.to_sql("vaestoennuste_aikasarja",engine,if_exists="replace",method="multi",chunksize=200,index=False)
tulokset_validointi.to_sql("vaestoennuste_validointi",engine,if_exists="replace",method="multi",chunksize=200,index=False)
vaestohistoria.to_sql("vaestohistoria",engine,if_exists="replace",method="multi",chunksize=200,index=False)


#tulokset.to_csv("vaestoennuste.csv")
#tulokset_aikasarja.to_csv("vaestoennuste_aikasarja.csv")
#tulokset_validointi.to_csv("vaestoennuste_validointi.csv")
#vaestohistoria.to_csv("vaestohistoria.csv")
