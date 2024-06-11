# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 20:18:19 2024

@author: ILIA
"""
from models import lstModels
from views.mainWin import mainWindow
from views.ed_base import EditBase
from base.baseSQLite import get_conn_to_base

# import pickle
# data =   {
#           'models':lstModels,           # список доступных методов расчёта
#           'baseEditor':EditBase,        # окно редактирования базы данных
#           }

# with open('data.pickle', 'wb') as f:
#      pickle.dump(data, f)

# with open('data.pickle', 'rb') as f:
#      data_new = pickle.load(f)     

mainWindow(
         {
          'models':lstModels,           # список доступных методов расчёта
          'connect':get_conn_to_base(), # connection к базе данных
          'baseEditor':EditBase,        # окно редактирования базы данных
          }
         )