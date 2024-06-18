"""
Модуль расчёта длины тормозного пути методом интервалов скорости
интегрирование ведётся методом прямоугольников

    Выпускная квалификационная работа бакалавра
    Санкт-Петербургский политехнический университет Петра Великого
    Институт компьютерных наук и кибербезопасности
    Высшая школа компьютерных технологий и информационных систем
    направление 09.03.01 Информатика и вычислительная техника
    2024 год

@author: Журавский Илья Александрович
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import numpy as np

import tkinter as tk
from tkinter import ttk
import models
from models.dopFunc import getFmt as getFmt
from models.dopFunc import get_eps_by_name as get_eps_by_name
from models.dopFunc import CalcPress as CalcPress
from models.dopFunc import calcKnt as calcKnt

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

# описание класса
class modelTime:
    # конструктор класса
    def __init__(self, parTrain, parLoko, extCondition):
        # создаём копии исходных данных, чтобы никто не испортил
        self.parTrain = parTrain.copy()
        self.parLoko = parLoko.copy()
        # правим их под нужды модуля
        if 'id' in parTrain.columns:
            self.parTrain.drop(['id'], inplace=True, axis=1)
        df = pd.DataFrame()
        df.index = extCondition.index
        df[['v0','slope','dt','type','way','air']] = extCondition[['v0','slope','dt','type','way','air']]
        self.extCondition = df
        self.speed = extCondition['v0'][0]
        self.interval = extCondition['dt'][0]
        self.ic = extCondition['slope'][0]
        self.way = extCondition['way'][0]
        self.air = extCondition['air'][0]
        # создаём переменные
        self.bT = 0.0
        self.passenger = extCondition['type'][0] > 0
        self.Fikp = 0.0
        self.wox = 0.0
        self.c = 0.0
        self.Ploc = parLoko['massa'][0]
        self.eps = get_eps_by_name(parLoko['name'][0])
        self.Pvag = 0.0
        self.nOSv = 0
        self.df_rezult = 0
        self.df_rezTable= 0
        self.plt_rezult = 0
        self.tables = []
        self.lab_names=['Условия расчёта', 'Параметры локомотива', 'Параметры состава по группам вагонов',
                   'Таблица результатов', 'Таблица по интервалам','График']
        # рассчитываем разные параметры, чтобы потом не отвлекаться
        SKp = [0.0, 0,0, 0,0]
        SKp[parLoko['pads'][0]] = parLoko['axles'][0] * parLoko['force'][0]
        for index, row in parTrain.iterrows():
            p = int(row['pads'])
            SKp[p] = SKp[p] + row['count'] * row['force'] * row['axles']
            self.Pvag = self.Pvag + row['count'] * row['massa']
            self.nOSv = self.nOSv + row['count'] * row['axles']
        # Определяем 𝜗p по формуле (2)
        self.Teta = [x / (self.Pvag + self.Ploc) for x in SKp] # ]round(self.SKp / (self.Pvag + self.Ploc),3)
        if self.passenger:
            self.lenght = (parTrain['count'].sum()+1)*24.0
        else:
            self.lenght = (parTrain['count'].sum()+1)*12.0
    # расчет фи
    # pads - тип тормозных колодок (0,1,2)
    # v - скорость км/ч
    def calcFi(self,pads,v):
        if pads == 0:
            return 0.27*(v+100.0)/(5.0*v+100.0) # чугун
        elif pads == 1:
            return 0.3*(v+100.0)/(5.0*v+100.0) # чугун с фосфором
        else:
            return 0.36*(v+150.0)/(2.0*v+150.0) # композит

    # ---------------------------------------------------------------------------
    #
    #  основной расчёт
    #
    # ---------------------------------------------------------------------------
    def calculate(self):
        # начальная скорость км/ч
        v = self.speed

        # (53) основное удельное сопротивление поезда
        # v - скорость км/ч
        def calcWox(v):
           def Wo(v):
               if self.nOSv == 0:
                   return 0.0
               qo = self.Pvag / self.nOSv # средняя нагрузка оси вагона на рельсы
               if self.passenger:
               # (стр 5) удельное сопротивление пассажирских вагонов
                   if self.way == 0:
                       # (13) удельное сопротивление пассажирских вагонов на звеньевом пути
                       res = 6.9 + (78.5 + 1.76 * v + 0.03 * v * v) / qo
                   else:
                       # (14) удельное сопротивление пассажирских вагонов на бесстыковом пути
                       res = 6.9 + (78.5 + 1.57 * v + 0.022 * v * v) / qo
               else:
               # (стр 5) удельное сопротивление грузовых вагонов
                   if self.way == 0:
                       # (1) удельное сопротивление грузовых вагонов на звеньевом пути
                       res = 5.2 + (35.4 + 0.785 * v + 0.027 * v * v) / qo
                   else:
                       # (7) удельное сопротивление грузовых вагонов на бесстыковом пути
                       res = 5.2 + (34.2 + 0.732 * v + 0.022 * v * v) / qo
#                   return 0.7 + (8 + 0.1 * v + 0.0025 * v * v) / qo
               return res / 9.8 # kH => ton
           def Wx(v): # (54) удельное сопротивление локомотива на холостом ходу
               if self.way == 0:
                   # –электровозы и тепловозы на звеньевом пути
                   res = 18.6 + 0.1 * v + 0.0029 * v * v # (15)
               else:
                   # –электровозы и тепловозы на бесстыковом пути
                   res = 18.6 + 0.08 * v + 0.0024 * v * v # (17)
               return res / 9.8 # kH => ton
           return (Wo(v) * self.Pvag + Wx(v) * self.Ploc)/(self.Ploc + self.Pvag) * calcKnt(self.air, v, self.way)
        # инициализация локальных переменных
        tCur = 0.0
        Scur = 0.0
        Vcur = v
        dt = self.interval
        # подготовка таблиц с результатами
        res = pd.DataFrame(columns=['Vst','Ven','Vmid','Fikp','bT',
                                    'wox','ic','c','St','t'])
        res2 = pd.DataFrame(columns=['all_vag','all_axes','all_massa','full_massa','full_len',
            'Sf','tf'])
        res2['all_vag'] = [self.parTrain['count'].sum()]
        res2['all_axes'] = [self.nOSv]
        res2['all_massa'] = [self.Pvag]
        res2['full_len'] = [self.lenght]
        res2['full_massa'] = [self.Pvag + self.Ploc]
        Sit = [Scur]
        Vit = [Vcur]
        # учетные параметры
        Vst = Vcur # скорость
        Vwt = int(Vcur / 10) * 10.0
        if Vst - Vwt < 0.1:
            Vwt = Vwt - 10.0
        if Vwt<0.0:
            Vwt = 0.0
        Lst = 0.0 # путь
        Tst = 0 # время
        # цикл пока скорость больше нуля
        while Vcur>0.0:
           w = calcWox(Vcur)
           bT = round(1000.0 * sum([self.Teta[i] *
                          self.calcFi(i, Vcur) for i in range(3)]),1)
           kk = CalcPress(tCur+dt/2.0, self.lenght)
           dV = self.eps*(bT*kk/100.0+w+self.ic)/3600.0*dt
           if dV > Vcur:
               dt = dt * Vcur / (Vcur + dV)
               dV = Vcur
           dS = (Vcur - dV/2) * dt / 3.6
           Vcur = Vcur - dV
           Scur = Scur + dS
           # фиксация промежуточных данных
           if Vcur<=Vwt:
               idx = len(res)
               res.at[idx,'Vst'] = Vst
               res.at[idx,'Ven'] = Vwt
               Vmid = (Vst + Vwt) / 2.0
               res.at[idx,'Vmid'] = Vmid
               res.at[idx,'Fikp'] = sum([self.calcFi(i, Vmid) for i in range(3)])
               res.at[idx,'bT'] = round(1000.0 * sum([self.Teta[i] *
                          self.calcFi(i, Vmid) for i in range(3)]),1)
               res.at[idx,'wox'] = calcWox(Vmid)
               res.at[idx,'ic'] = self.ic
               res.at[idx,'c'] = res.at[idx,'wox'] + res.at[idx,'ic'] + res.at[idx,'bT']
               res.at[idx,'St'] = Scur - Lst
               Lst = Scur
               res.at[idx,'t'] = tCur - Tst
               Tst = tCur
               Vst = Vwt
               Vwt = Vwt - 10.0
               if Vwt<0.0:
                   Vwt = 0.0

           Sit.append(Scur)
           Vit.append(Vcur)
           tCur = tCur+dt

        res2['Sf'] =[Scur]
        res2['tf'] =[tCur - dt]

        # создание графика
        def generatePlot():
            x = Sit
            y = Vit
            w = [0.0]
            for i in range(len(x)-1):
                w.append(x[i+1]-x[i])
            colors = cm.rainbow(np.linspace(0.9, 0.1, len(x))).tolist()
            colors.insert(0,"gainsboro")
            xticks=[i*100 for i in range(int(x[-1]/100.0)+1)]
            xticks.append(float('{:2.1f}'.format(x[-1])))

            plt.style.use('default')
            fig = plt.figure(figsize=(8.0, 5.0))
            plt.bar(x, height = y, width = w, color = colors, alpha = 0.9)
            plt.plot(x, y, 'k',linewidth=2.0,alpha=0.9)
            _ = plt.xticks(xticks, xticks)#, rotation=45)
            font1 = {'family':'serif','color':'navy','size':15}
            font2 = {'family':'serif','color':'k','size':12}
            plt.title('Расчёт тормозного пути методом интервалов времени',
                      fontdict = font1)
            plt.xlabel('Полный тормозной путь, м', fontdict = font2)
            plt.ylabel('Скорость состава, км/ч', fontdict = font2)
            plt.grid(True)
            return fig

        self.df_rezult = res2 # ['all_vag','all_axes','all_massa','full_massa','Sp','tp','Sd','td','Sf','tf']
        self.df_rezTable = res # ['Vst','Ven','Vmid','Fikp','bT','wox','ic','c','St','t']
        self.plt_rezult = generatePlot()
        return [Vit,Sit,tCur]

    # ---------------------------------------------------------------------------
    #
    #  заполнение окна результатами
    #
    # ---------------------------------------------------------------------------
    # root - ссылка на окно для заполнения
    def putReport(self, root):
        def onCanvasConfigure(e):
            canvas.itemconfig('frame', width=canvas.winfo_width())
        # вывод панели с таблицей
        def create_table(pan, df, tran=False):
            tree = ttk.Treeview(pan, style="mystyle.Treeview")
            tree.tag_configure('gr0', background='lightcyan')

            rcnt, ccnt = df.shape
            if tran & rcnt==1:
                cols = ['Параметр','Значение']
                tree["columns"] = cols
                tree.column("#0", width=0,  stretch=tk.NO)
                tree.heading('#1', text=cols[0])
                tree.column(cols[0], anchor="center", width=30, minwidth=30, stretch=tk.YES)
                tree.heading('#2', text=cols[1])
                tree.column(cols[1], anchor="center", width=10, minwidth=10, stretch=tk.YES)
                pars = list(df.columns)
                idx = 0
                for par in pars:
                    idx += 1
                    fmt = getFmt(par)
                    if fmt[1]<0:
                        if len(fmt)>2:
                            val = fmt[2][int(df.at[0,par])]
                        else:
                            val = df.at[0,par]
                    else:
                        val = "{:1.{}f}".format(df.at[0,par],fmt[1])
                        #round(df.at[0,par],fmt[1])
                    values = [fmt[0], val]
                    tree.insert("", "end", values=values, tags=(f'gr{idx%2}',))

            else:

                tree["columns"] = list(df.columns)
                tree.column("#0", width=0,  stretch=tk.NO)
                idx = 0
                fmts = []
                for col in df.columns:
                    idx += 1
                    fmt = getFmt(col)
                    fmts.append(fmt)
                    tree.heading(f'#{idx}', text=fmt[0])
                    tree.column(col, anchor="center", width=30, minwidth=30, stretch=tk.YES)

                # Добавление данных в таблицу
                for index, row in df.iterrows():
                    values = []
                    for col in df.columns:
                        idx = len(values)
                        val = row[col]
                        if fmts[idx][1]<0:
                            if fmts[idx][1]<0:
                                if len(fmts[idx])>2:
                                    val = fmts[idx][2][int(val)]
                        else:
                            val = "{:1.{}f}".format(val,fmts[idx][1])
                        values.append(val)
                    #values = [row[col] for col in df.columns]
                    tree.insert("", "end", values=values, tags=(f'gr{index%2}',))

            tree.config(height=len(tree.get_children()))
            tree.pack(fill=tk.X, expand=0, padx=(10,10),pady=(3,10))

            tree.tag_configure('gr0', background='lightcyan')

            self.tables.append(tree)
        # -- - - - - - - - - - - -  - - - - - - -
        # определяем стили
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("mystyle.Treeview", highlightthickness=0,
                        bd=2, font=('Calibri', 12),
                        background="lightyellow") # Modify the font of the body
        style.configure("mystyle.Treeview.Heading",
                        font=('Calibri', 14,'bold'),foreground='indigo',
                        background="deepskyblue") # Modify the font of the headings
        style.layout("mystyle.Treeview",
                     [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        style.map("My.TButton",
          foreground=[('pressed', 'red'), ('active', 'blue')],
          background=[('pressed', '!disabled', 'black'),
                      ('active', 'white')])

        style.configure('My.TButton', font=('Arial','11','bold'))


        # панель заголовка
        fr3 = tk.Frame(root)
        l3 = tk.Label(fr3, text="Результаты расчёта".upper())
        l3.configure(font='Arial 19 bold', justify='center', anchor='center',
                     foreground = 'teal', background="whitesmoke")
        l3.pack(expand=1)
        fr3.pack(fill="x")

        # панель с кнопками
        fr2 = tk.Frame(root, background="whitesmoke")
        # bt = ttk.Button(fr2, text="Добавить в базу данных",width=45,
        #                style="My.TButton",)
        # bt.grid(row=0, column=1, pady=(0, 10),padx=(10, 10))
        bt2 = ttk.Button(fr2, text="Экспортировать в doc-файл",width=45,
                         style="My.TButton",
                         command = self.putResult2docx)#putDocFile)
        bt2.grid(row=0, column=0, pady=(0, 10),padx=(10, 10))
        fr2.pack()

        # панель на которой будут результаты и которую можно будет прокручивать
        canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
        frame= tk.Frame(canvas, background="dodgerblue")
        vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill= tk.BOTH, expand=1)

        # выводим таблички поочереди
        m = [self.extCondition,self.parLoko,self.parTrain,self.df_rezult,self.df_rezTable]
        self.tables = []
        for i in range(6):
            lbl = ttk.Label(frame, text=self.lab_names[i], relief="groove")
            lbl.configure(font='Arial 17 bold', justify='center',
                          foreground = 'yellow',anchor='center',background="darkblue")
            lbl.pack(fill= tk.X, expand=1, anchor='center')
            if i == 5:
                break
            create_table(frame, m[i], i in [0,1,3])

        # добавляем график
        fig = self.plt_rezult
        frmpic = tk.Frame(frame)
        frmpic.pack(fill=tk.X,expand=1)
        canvas2 = FigureCanvasTkAgg(fig, frmpic)
        toolbar = NavigationToolbar2Tk(canvas2, frmpic)
        toolbar.update()
        canvas2._tkcanvas.pack(fill=tk.X, expand=1)

        canvas.create_window((4, 4), window=frame, anchor="nw", tags="frame")
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind("<Configure>", onCanvasConfigure)
    # ---------------------------------------------------------------------------
    #
    #  Экспорт результатов в doc файл
    #
    # ---------------------------------------------------------------------------
    def putResult2docx(self):
        tabls = []
        for tree in self.tables:
            nam_col = 0
            rows = []
            #print('---------------------------------')
            for row_id in tree.get_children():
                row = tree.item(row_id)['values']
                if nam_col == 0:
                    nam_col = [tree.heading(f'#{i}')['text'] for i in range(1,len(row)+1) ]
                rows.append(row)
            tabls.append({'name':self.lab_names[len(tabls)],'cols':nam_col,'rows':rows})
        models.write2docx.putDocFile('Расчёт длины тормозного пути поезда\nметод расчёта по интервалам времени (Мугинштейн 2014г)', tabls, [self.plt_rezult])

# описатель класса для возможности обращения к нему
metodDescription = ('Метод расчёта по интервалам времени (Мугинштейн 2014г)',
                    modelTime, ['V','dt'])

if __name__ == "__main__":
    print(metodDescription[0])