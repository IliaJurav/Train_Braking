"""
Модуль с дополнительными структурами и функциями

    Выпускная квалификационная работа бакалавра
    Санкт-Петербургский политехнический университет Петра Великого
    Институт компьютерных наук и кибербезопасности
    Высшая школа компьютерных технологий и информационных систем
    направление 09.03.01 Информатика и вычислительная техника
    2024 год

@author: Журавский Илья Александрович
"""

import numpy as np

# структура для указания названия и формата отображения параметров
dic_str = {'v0':['Начальная скорость, км/ч',1],'slope':['Уклон, ‰',1],
           'step':['Интервал, км/ч',1],'type':['Тип поезда',-1,['Грузовой','Пассажирский']],
           'air':['Температура воздуха, ºС',1],'way':['Тип пути',-1,['Звеньевой','Бесстыковой']],
           'Vst':['Vнач, км/ч',1],'Ven':['Vкон, км/ч',1],'Vmid':['Vср, км/ч',1],
           'dt':['Интервал времени, с',1],'Fikp':['ϑкр',3],'bT':['bT, кг/т',1],
           'wox':['ωox, кг/т',1],'ic':['Уклон, ‰',1],
           'c':['c, кг/т',1],'St':['Длина, м',1],'t':['Время, с',1],
           'count':['Кол-во, шт',0],'massa':['Вес, т',1],
           'axles':['Оси, шт',0],'force':['Сила, т',1],
           'pads':['Колодки',-1,['Чугун','Чугун+F','Композит']],
           'Sp':['Длина подготовительного пути (Sп),м',1],'tp':['Время подготовки, с',1],
           'Sd':['Длина тормозного пути (Sд),м',1],'td':['Время торможения, с',1],
           'Sf':['Полный тормозной путь (Sп),м',1],'tf':['Полное время торможения, с',1],
           'lenWay':['Реальный тормозной путь (Sп),м',1],
           'stepL':['Точность расчётов пути ,м',1],
           'vс0':['Расчётная начальная скорость, км/ч',1],
           'all_vag':['Количество вагонов в составе, шт',0],
           'all_axes':['Количество осей в составе, шт',0],
           'all_massa':['Суммарая масса всех вагонов, т',1],
           'full_len':['Длина состава, м',1],
           'full_massa':['Полная масса поезда, т',1],
           'name':['Название',-1],
           }

# поиск описания в структуре
def getFmt(a):
    if not(a in dic_str.keys()):
        # если нет, то возвращаем "заглушку"
        return [a,1]
    else:
        # если есть, то возвращаем описание
        return dic_str[a]

# Таблицы для расчёта методом интервалов времени

# градации длины состава
kPressLen = [0.0,500.0,800.0,1200.0,1600.0]

# таблица наполнения тормозных цилиндров (стр.14 таблица 5 jpg)
kPress = [
    [ 0.0, [  0,  0,  0,  0,  0]],
    [ 3.0, [ 15,  0,  0,  0,  0]],
    [ 6.0, [ 62, 20, 15,  2,  0]],
    [ 9.0, [ 87, 45, 35, 20, 10]],
    [12.0, [ 97, 65, 50, 35, 25]],
    [15.0, [100, 80, 65, 50, 35]],
    [18.0, [100, 90, 75, 60, 45]],
    [21.0, [100, 95, 85, 70, 55]],
    [24.0, [100, 98, 95, 80, 62]],
    [27.0, [100,100, 98, 85, 70]],
    [30.0, [100,100,100, 90, 75]],
    [33.0, [100,100,100, 94, 80]],
    [36.0, [100,100,100, 96, 85]],
    [39.0, [100,100,100, 98, 90]],
    [42.0, [100,100,100,100, 92]],
    [45.0, [100,100,100,100, 95]],
    [50.0, [100,100,100,100, 98]],
    [55.0, [100,100,100,100,100]]
    ];
# расчёт наполнености (%) тормозной системы в зависимости
# от t - времени от начала тормржения
# от ln - длины состава
def CalcPress(t,ln):
    if t>=55.0:
        return 100.0
    pcur = 1
    while kPress[pcur][0]<t:
        pcur += 1
    lcur = 1
    if ln<1600:
        while kPressLen[lcur]<ln:
            lcur += 1
    else:
       lcur = 5
    # Билинейная интерполяция
    pSt = (kPress[pcur-1][1][lcur-1] +
     (kPress[pcur][1][lcur-1] - kPress[pcur-1][1][lcur-1]) /
     (kPress[pcur][0]-kPress[pcur-1][0])*(t-kPress[pcur-1][0]))
    pEn = (kPress[pcur-1][1][lcur]+
     (kPress[pcur][1][lcur]-kPress[pcur-1][1][lcur])/
     (kPress[pcur][0]-kPress[pcur-1][0])*(t-kPress[pcur-1][0]))
    Result = pSt+(pEn-pSt)/(kPressLen[lcur]-kPressLen[lcur-1])*(ln - kPressLen[lcur-1])
    # подстраховка от выхода за пределы
    if Result > 100.0:
        Result = 100.0
    if Result < 0.0:
        Result = 0.0
    return Result


# Коэффициент Кнт стр 10
# , учитывающий низкую температуру наружного воздуха v, км/ч
tKnt = [-20.0, -30.0,-35.0,-40.0,-45.0,-50.0,-60.0]
# скорости
vKnt = [0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0]
# Грузовые вагоны при t ºС
valKntCargo = [
#t= -20.0,-30.0,-35.0,-40.0,-45.0,-50.0,-60.0
    [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00],# 0 км/ч
    [1.00, 1.01, 1.01, 1.01, 1.01, 1.01, 1.01],# 20 км/ч
    [1.00, 1.03, 1.03, 1.04, 1.04, 1.05, 1.06],# 40 км/ч
    [1.00, 1.05, 1.06, 1.07, 1.07, 1.08, 1.09],# 60 км/ч
    [1.00, 1.07, 1.08, 1.09, 1.10, 1.11, 1.12],# 80 км/ч
    [1.00, 1.09, 1.10, 1.12, 1.13, 1.14, 1.15],# 100 км/ч
    [1.00, 1.11, 1.12, 1.13, 1.14, 1.15, 1.16],# 120 км/ч
    [1.00, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18],# 140 км/ч
    [1.00, 1.15, 1.16, 1.17, 1.18, 1.19, 1.20],# 160 км/ч
    ]
#  Пассажирские вагоны при t ºС
valKntPassenger = [
#t= -20.0,-30.0,-35.0,-40.0,-45.0,-50.0,-60.0
    [1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00],# 0 км/ч
    [1.00, 1.01, 1.01, 1.01, 1.01, 1.01, 1.01],# 20 км/ч
    [1.00, 1.02, 1.02, 1.03, 1.03, 1.03, 1.04],# 40 км/ч
    [1.00, 1.03, 1.04, 1.04, 1.05, 1.06, 1.07],# 60 км/ч
    [1.00, 1.04, 1.05, 1.06, 1.07, 1.08, 1.09],# 80 км/ч
    [1.00, 1.05, 1.06, 1.07, 1.09, 1.10, 1.11],# 100 км/ч
    [1.00, 1.06, 1.07, 1.09, 1.10, 1.11, 1.12],# 120 км/ч
    [1.00, 1.07, 1.08, 1.09, 1.11, 1.12, 1.13],# 140 км/ч
    [1.00, 1.07, 1.09, 1.10, 1.12, 1.13, 1.15],# 160 км/ч
    ]

valKnt = [valKntCargo, valKntPassenger]

# Расчёт коэффициента Кнт стр 10
# t - температура воздуха, С
# v - скорость состаава км/ч
# typ - тип вагонов, 0 - груз, 1 - пасс
def calcKnt(t,v,typ):
    if t>-20.0 or v<=0.0:
        return 1.0
    if t<-60.0 or v>120.0:
        return 1.2
    tcur = 1
    while tKnt[tcur]>t:
        tcur += 1
    vcur = 1
    while vKnt[vcur]<v:
        vcur += 1
    val = valKnt[typ]
    # Билинейная интерполяция через линейную
    kSt = np.interp(t, tKnt[::-1], val[vcur-1][::-1])
    kEn = np.interp(t, tKnt[::-1], val[vcur][::-1])
    Result = np.interp(v, vKnt[vcur-1:vcur+1], [kSt, kEn])
    # на всякий случай
    if Result < 1.0:
        Result = 1.0
    return Result