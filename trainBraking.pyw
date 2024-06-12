"""
Запуск главного окна приложения без создания консольного окна python

    Выпускная квалификационная работа бакалавра
    Санкт-Петербургский политехнический университет Петра Великого
    Институт компьютерных наук и кибербезопасности
    Высшая школа компьютерных технологий и информационных систем
    направление 09.03.01 Информатика и вычислительная техника
    2024 год

@author: Журавский Илья Александрович
"""

from models import lstModels
from views.mainWin import mainWindow
from views.ed_base import EditBase
from base.baseSQLite import get_conn_to_base

mainWindow(
         {
          'models':lstModels,           # список доступных методов расчёта
          'connect':get_conn_to_base(), # connection к базе данных
          'baseEditor':EditBase,        # окно редактирования базы данных
          }
         )