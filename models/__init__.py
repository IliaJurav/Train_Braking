"""
Модуль инициализации пакета "models"

    Выпускная квалификационная работа бакалавра
    Санкт-Петербургский политехнический университет Петра Великого
    Институт компьютерных наук и кибербезопасности
    Высшая школа компьютерных технологий и информационных систем
    направление 09.03.01 Информатика и вычислительная техника
    2024 год

@author: Журавский Илья Александрович
"""

# подключение модулей с методами расчёта
import models.modelSpeed
import models.modelTime
import models.modelTimeRKF
import models.modelInvert
# подключение дополнительных модулей
import models.write2docx
import models.rkf
import models.dopFunc

# список описателей реализованных методов 
lstModels = (models.modelSpeed.metodDescription,
             models.modelTime.metodDescription,
             models.modelTimeRKF.metodDescription,
             models.modelInvert.metodDescription
             )