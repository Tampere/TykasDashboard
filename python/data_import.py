# -*- coding: utf-8 -*-
# Requirements: pyjstat, sqlalchemy, pyodbc, json, requests
"""
Created on Thu May  6 14:12:31 2021
"""
from pyjstat import pyjstat
import json
import requests
import sqlalchemy as sal

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
          "2019"
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
          "2020"
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







# Write to db

kuolleisuus.to_sql("kuolleisuus",engine,if_exists="replace",method="multi",chunksize=20,index=False)
muutto_suomessa.to_sql("muutto_suomessa",engine,if_exists="replace",method="multi",chunksize=20,index=False)
syntyvyys.to_sql("syntyvyys",engine,if_exists="replace",method="multi",chunksize=20,index=False)
maahanmuutto.to_sql("maahanmuutto",engine,if_exists="replace",method="multi",chunksize=20,index=False)



