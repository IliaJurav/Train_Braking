"""
Модуль расчёта тормозного пути интергрированием по скорости

    Выпускная квалификационная работа бакалавра
    Санкт-Петербургский политехнический университет Петра Великого
    Институт компьютерных наук и кибербезопасности
    Высшая школа компьютерных технологий и информационных систем
    направление 09.03.01 Информатика и вычислительная техника
    2024 год

@author: Журавский Илья Александрович

"""

import pandas as pd
import math
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import numpy as np

import models
from models.dopFunc import getFmt as getFmt
from models.dopFunc import get_eps_by_name as get_eps_by_name

import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

class modelSpeed:
    # конструктор класса
    def __init__(self, parTrain, parLoko, extCondition):
        self.parTrain = parTrain.copy()
        if 'id' in parTrain.columns:
            self.parTrain.drop(['id'], inplace=True, axis=1)
        self.parLoko = parLoko.copy()
        df = pd.DataFrame()
        df.index = extCondition.index
        df[['v0','slope','step','type']] = extCondition[['v0','slope','step','type']]
        self.extCondition = df
        self.speed = extCondition['v0'][0]
        self.interval = extCondition['step'][0]
        self.ic = extCondition['slope'][0]
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
        SKp = [0.0, 0,0, 0,0]
        SKp[parLoko['pads'][0]] = parLoko['axles'][0] * parLoko['force'][0]
        for index, row in parTrain.iterrows():
            p = int(row['pads'])
            SKp[p] = SKp[p] + row['count'] * row['force'] * row['axles']
            self.Pvag = self.Pvag + row['count'] * row['massa']
            self.nOSv = self.nOSv + row['count'] * row['axles']
        # Определяем 𝜗p по формуле (2)
        self.Teta = [x / (self.Pvag + self.Ploc) for x in SKp] # ]round(self.SKp / (self.Pvag + self.Ploc),3)

    def calcFi(self,pads,v):
        if pads == 0:
            return 0.27*(v+100.0)/(5.0*v+100.0) # чугун (6)
        elif pads == 1:
            return 0.3*(v+100.0)/(5.0*v+100.0) # чугун с фосфором (7)
        else:
            return 0.36*(v+150.0)/(2.0*v+150.0) # композит (8)
    # расчёт параметров подготовительного пути
    def calcSp(self,V0):
        bT0 = round(1000.0 * sum([self.Teta[i] * self.calcFi(i, V0) for i in range(3)]),1)
        if self.passenger: # пассажирские (50)
            tp = 4 - 5.0 * self.ic / bT0
        else: # грузовые поезда
            if self.nOSv <= 200:
                tp = 7 - 10.0 * self.ic / bT0 # для 200 осей включительно (48)
            else:
                tp = 10 - 15.0 * self.ic / bT0 # для более 200 осей (49)
        Sp = round(V0 * tp / 3.6, 1)
        return {'Sp':Sp,'tp':tp}

    def calcForSpeed(self, v = 0.0):
        if v < 0.0:
            v = 0.0
        if v == 0:
            v = self.speed
        # формулы
        # (53) основное удельное сопротивление поезда
        def calcWox(v):
           def Wo(v):
               if self.nOSv == 0:
                   return 0.0
               qo = self.Pvag / self.nOSv # средняя нагрузка оси вагона на рельсы
               if self.passenger:
               # (57) удельное сопротивление пассажирских вагонов
                   return 1.2 + 0.012 * v + 0.0002 * v * v
               else:
               # (55) удельное сопротивление грузовых вагонов
                   return 0.7 + (8 + 0.1 * v + 0.0025 * v * v) / qo
           def Wx(v): # (54) удельное сопротивление локомотива на холостом ходу
               return 2.4 + 0.011 * v + 0.00035 * v * v

           return (Wo(v) * self.Pvag + Wx(v) * self.Ploc)/(self.Ploc + self.Pvag)

# Расчитываем bт для каждого интервала по формуле (1)
        self.Fikp = round(self.calcFi(0, v),3)
# Расчитываем bт для каждого интервала по формуле (1)
#        self.bT = round(1000.0 * self.Teta * self.Fikp,1)
        self.bT = round(1000.0 * sum([self.Teta[i] *
                                      self.calcFi(i, v) for i in range(3)]),1)
        self.wox = round(calcWox(v),1)
        self.c = round(self.bT + self.wox + self.ic,1)
        return pd.DataFrame([[self.Fikp, self.bT, self.wox, self.ic, self.c]],
                            columns=['Fikp','bT','wox','ic','c'])

    # ---------------------------------------------------------------------------
    #
    #  основной расчёт
    #
    # ---------------------------------------------------------------------------
    def calculate(self):
        V0 = self.speed
        dV = self.interval
        res = pd.DataFrame(columns=['Vst','Ven','Vmid','Fikp','bT',
                                    'wox','ic','c','St','t'])
        res2 = pd.DataFrame(columns=['all_vag','all_axes','all_massa','full_massa',
            'Sp','tp','Sd','td','Sf','tf'])
        res2['all_vag'] = [self.parTrain['count'].sum()]
        res2['all_axes'] = [self.nOSv]
        res2['all_massa'] = [self.Pvag]
        res2['full_massa'] = [self.Pvag + self.Ploc]
# рассчитываем количество интервалов
        numInt = math.ceil(V0 / dV)
# получаем массив интервалов скорости
        Vint = [[min(V0, dV * (i + 1)), dV * i] for i in range(numInt)][::-1]
        res['Vst'] = [Vint[i][0] for i in range(numInt)]
        res['Ven'] = [Vint[i][1] for i in range(numInt)]
# Расчитываем среднюю скорость на интервале
        Vmid = [(Vint[i][0] + Vint[i][1]) /  2 for i in range(numInt)]
       	res['Vmid'] = Vmid
        for idx, row in res.iterrows():
           stp = self.calcForSpeed(row['Vmid'])
           res.at[idx,'Fikp'] = stp.at[0,'Fikp']
           res.at[idx,'bT'] = stp.at[0,'bT']
           res.at[idx,'wox'] = stp.at[0,'wox']
           res.at[idx,'ic'] = stp.at[0,'ic']
           res.at[idx,'c'] = stp.at[0,'c']
           St = round(500.0 / self.eps *(row['Vst']**2 - row['Ven']**2)/stp.at[0,'c'] ,1)
           res.at[idx,'St'] = St
           res.at[idx,'t'] = round(St/row['Vmid']*3.6,1)
        stp = self.calcSp(V0)
        res2['Sp'] =[stp['Sp']]
        res2['tp'] =[stp['tp']]
        res2['Sd'] =[res['St'].sum()]
        res2['td'] =[res['t'].sum()]
        res2['Sf'] =[res2.at[0,'Sd']+res2.at[0,'Sp']]
        res2['tf'] =[res2.at[0,'td']+res2.at[0,'tp']]
        def generatePlot():
            x = ["Подготовка"]
            y = [res.at[0,'Vst']]
            w = [res2.at[0,'Sp']]
            if (round(dV, 0)-dV) != 0.0:
                fmt = r'{:2.1f}-{:2.1f}  км/ч'
            else:
                fmt = r'{:1.0f}-{:1.0f}  км/ч'
            for idx, row in res.iterrows():
                x.append(fmt.format(row['Vst'],row['Ven']))
                #x.append(f"{int(row['Vmid'])} км/ч")
                y.append(row['Vmid'])
                w.append(row['St'])

            colors = cm.rainbow(np.linspace(0.9, 0.1, len(w))).tolist()
            colors.insert(0,"gainsboro")

            xticks=[0,round(w[0],1), round(sum(w),1)]
            xline = [0]
            yline = [res.at[0,'Vst']]
            xpos = []
            a = 0
            for n, c in enumerate(w):
                a = a + w[n]
                if n == 0:
                    yline.append(res.at[0,'Vst'])
                    xline.append(w[n])
                    xpos.append(w[n]/2)
                else:
                    yline.append(res.at[n-1,'Vmid'])
                    xline.append(sum(w[:n]) + w[n]/2)
                    xpos.append(a - w[n]/2)
            xline.append(sum(w))
            yline.append(0.0)

            plt.style.use('default')
            fig = plt.figure(figsize=(8.0, 5.0))
            a = plt.bar(xpos, height = y, width = w, color = colors, alpha = 0.9,edgecolor = "black")
            plt.plot(xline, yline, 'k-o',linewidth=3.0,alpha=0.5)
            _ = plt.xticks(xticks, xticks)
            font1 = {'family':'serif','color':'navy','size':15}
            font2 = {'family':'serif','color':'k','size':12}
            plt.title(f'Расчёт тормозного пути методом интервалов скорости\nначальная скорось {V0} км/ч, шаг {dV} км/ч',
                      fontdict = font1)
            plt.xlabel('Полный тормозной путь, м', fontdict = font2)
            plt.ylabel('Скорость состава, км/ч', fontdict = font2)
            if numInt<21:
                plt.legend(a.patches, x)
            plt.grid(True)
            return fig
        self.df_rezult = res2 # ['all_vag','all_axes','all_massa','full_massa','Sp','tp','Sd','td','Sf','tf']
        self.df_rezTable = res # ['Vst','Ven','Vmid','Fikp','bT','wox','ic','c','St','t']
        self.plt_rezult = generatePlot()
        return
    # ---------------------------------------------------------------------------
    #
    #  заполнение окна результатами
    #
    # ---------------------------------------------------------------------------
    # root - ссылка на окно для заполнения
    def putReport(self, root):
        def onCanvasConfigure(e):
            canvas.itemconfig('frame', width=canvas.winfo_width())

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


        fr3 = tk.Frame(root)
        l3 = tk.Label(fr3, text="Результаты расчёта".upper())
        l3.configure(font='Arial 19 bold', justify='center', anchor='center',
                     foreground = 'teal', background="whitesmoke")
        l3.pack(expand=1)
        fr3.pack(fill="x")

        fr2 = tk.Frame(root, background="whitesmoke")
        # bt = ttk.Button(fr2, text="Добавить в базу данных",width=45,
        #                style="My.TButton",)
        # bt.grid(row=0, column=0, pady=(0, 10),padx=(10, 10))
        bt2 = ttk.Button(fr2, text="Экспортировать в doc-файл",width=45,
                         style="My.TButton",
                         command = self.putResult2docx)#putDocFile)
        bt2.grid(row=0, column=0,pady=(0, 10),padx=(10, 10))
        fr2.pack()


        canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
        frame= tk.Frame(canvas, background="dodgerblue")
        vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(fill= tk.BOTH, expand=1)

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
        models.write2docx.putDocFile('Расчёт длины тормозного пути поезда\nметод расчёта по интервалам скорости (Гребенюк 1969г)', tabls, [self.plt_rezult])


# описатель класса для возможности обращения к нему
metodDescription = ('Метод расчёта по интервалам скорости (Гребенюк 1969г)',
                    modelSpeed, ['V','dV'])

if __name__ == "__main__":
    print(metodDescription[0])