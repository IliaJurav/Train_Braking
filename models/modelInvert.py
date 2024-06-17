"""
Модуль обратного расчёта
выполняется поиск начальной скорости поезда по известному тормозному пути
метод интервалов скорости интегрирование ведётся RKF45

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

from models.dopFunc import getFmt as getFmt
from models.dopFunc import get_eps_by_name as get_eps_by_name
from models.dopFunc import CalcPress as CalcPress
from models.dopFunc import calcKnt as calcKnt
from models.rkf import rkf as rkf
from models.write2docx import putDocFile as putDocFile


from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)



class modelInvertTimeRKF:
    # конструктор класса
    def __init__(self, parTrain, parLoko, extCondition):
        self.parTrain = parTrain.copy()
        if 'id' in parTrain.columns:
            self.parTrain.drop(['id'], inplace=True, axis=1)
        self.parLoko = parLoko.copy()
        df = pd.DataFrame()
        df.index = extCondition.index # 'lenWay','stepL'
        df[['lenWay','slope','stepL','type','way','air']] = extCondition[['lenWay','slope','stepL','type','way','air']]
        self.extCondition = df
        self.brakeWay = extCondition['lenWay'][0]
        self.accWay = extCondition['stepL'][0]
        self.ic = extCondition['slope'][0]
        self.way = extCondition['way'][0]
        self.air = extCondition['air'][0]
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
        if self.passenger:
            self.lenght = (parTrain['count'].sum()+1)*24.0
        else:
            self.lenght = (parTrain['count'].sum()+1)*12.0
    # расчет фи
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
        lenWay = self.brakeWay

        # (53) основное удельное сопротивление поезда
        def calcWox(v):
           qo = self.Pvag / self.nOSv # средняя нагрузка оси вагона на рельсы
           def Wo(v):
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


        def forces(t,v):
            w = calcWox(v)
            bT = 1000.0 * sum([self.Teta[i] *
                           self.calcFi(i, v) for i in range(3)])
            kk = CalcPress(t, self.lenght)
            return w, bT*kk/100.0

        # функция для интергирования в rkf45
        def myF(t,u):
            x,v = u
            dx = v / 3.6 # км/ч => m/c
            w, bT = forces(t,v)
            dv = - self.eps*(bT+w+self.ic)/3600.0 # m/с^2 => (км/ч)/c
            return np.array([dx,dv], dtype='f8')

        res = pd.DataFrame(columns=['Tst','Ten','Vst','Ven','Vmid','Fikp','bT',
                                    'wox','ic','c','St','t'])
        res2 = pd.DataFrame(columns=['all_vag','all_axes','all_massa','full_massa','full_len',
            'vс0','Sf','tf'])
        res2['all_vag'] = [self.parTrain['count'].sum()]
        res2['all_axes'] = [self.nOSv]
        res2['all_massa'] = [self.Pvag]
        res2['full_len'] = [self.lenght]
        res2['full_massa'] = [self.Pvag + self.Ploc]
        # учетные параметры
        Vcur = 160.0

        x0=[0.0, Vcur] #  начальные условия
        rrr  = rkf(f=myF, a=0, b=1000, x0=x0, atol=1e-8, rtol=1e-6,
                       hmax=5.0, hmin=0.001)
        t, sv = rrr.solve()

        v0 = 0.0
        v1 = Vcur
        l0 = 0.0
        l1 = sv[-1][0]
        for k in range(20):
            Vcur = np.interp(lenWay, [l0, l1], [v0 * v0, v1 * v1],left = (v0-1.0)**2, right= (v1+1.0)**2) ** 0.5
            x0=[0.0, Vcur] #  начальные условия
            rrr  = rkf(f=myF, a=0, b=1000, x0=x0, atol=1e-8, rtol=1e-6,
                       hmax=1.0, hmin=0.001)
            t, sv = rrr.solve()
            l = sv[-1][0]
            if l>lenWay:
                v1 = Vcur
                l1 = l
            else:
                v0 = Vcur
                l0 = l
            if abs(l - lenWay)<self.accWay:
                break

        Vcur = np.interp(lenWay, [l0, l1], [v0 * v0, v1 * v1], left = v0**2, right= v1**2) ** 0.5
        x0=[0.0, Vcur] #  начальные условия
        rrr  = rkf(f=myF, a=0, b=1000, x0=x0, atol=1e-8, rtol=1e-6,
                   hmax=1.0, hmin=0.001)
        t, sv = rrr.solve()
        s, v = sv.T

        Vst = Vcur # скорость
        Vwt = int(Vcur / 10) * 10.0
        if Vst - Vwt < 0.1:
            Vwt = Vwt - 10.0
        if Vwt<0.0:
            Vwt = 0.0
        #Scur = 0.0
        tWt = 10.0
        iRez = 0
        iSt = 0
        for idx in range(t.size):
            if t[idx] >= tWt:
                res.at[iRez,'Tst'] = round(t[iSt],1)
                res.at[iRez,'Ten'] = round(t[idx],1)
                res.at[iRez,'Vst'] = round(v[iSt],1)
                res.at[iRez,'Ven'] = round(v[idx],1)
                Vmid = np.average(v[iSt:idx])
                res.at[iRez,'Vmid'] = round(Vmid,1)
                res.at[iRez,'St'] = round(s[idx] - s[iSt],1)
                res.at[iRez,'t'] = round(t[idx] - t[iSt],1)
                res.at[iRez,'Fikp'] = sum([self.calcFi(i, Vmid) for i in range(3)])
                res.at[iRez,'bT'] = round(1000.0 * sum([self.Teta[i] *
                           self.calcFi(i, Vmid) for i in range(3)])/100.0*
                           CalcPress(np.average(t[iSt:idx]), self.lenght),1)
                res.at[iRez,'wox'] = calcWox(Vmid)
                res.at[iRez,'ic'] = self.ic
                res.at[iRez,'c'] = res.at[iRez,'wox'] + res.at[iRez,'ic'] + res.at[iRez,'bT']
                tWt = min(tWt+10.0,t[-1])
                iSt = idx
                iRez += 1


        Sit = s
        Vit = v
        tCur = t

        res2['vс0'] = [round(v[0],1)]
        res2['Sf'] =[s[-1]]
        res2['tf'] =[t[-1]]

        def generatePlot():
            x = Sit
            y = Vit
            w = [0.0]
            for i in range(len(x)-1):
                w.append(x[i+1]-x[i])
            colors = cm.rainbow(np.linspace(0.9, 0.1, len(w))).tolist()
            #colors.insert(0,"gainsboro")
            for dl in [50,100,200,250,500,1000]:
                xticks=[i*dl for i in range(int(x[-1]/float(dl))+1)]
                if len(xticks)<8:
                    break
            xticks.append(float('{:2.1f}'.format(x[-1])))

            plt.style.use('default')
            fig = plt.figure(figsize=(8.0, 6.0))
            plt.bar(x, height = y, width = w, color = colors, alpha = 0.9)
            plt.plot(x, y, 'k',linewidth=2.0,alpha=0.9)
            _ = plt.xticks(xticks, xticks)#, rotation=45)
            font1 = {'family':'serif','color':'navy','size':13}
            font2 = {'family':'serif','color':'k','size':12}
            plt.title('Определение начальной скорости по длине тормозного пути\nс использованием RKF45',
                      fontdict = font1)
            plt.xlabel(f'Полный тормозной путь {round(Sit[-1],1)} м\nпри начальной скорости {round(Vit[0],1)} км/ч', fontdict = font2)
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
        putDocFile('Расчёт начальной скорости по длине тормозного пути\n(обратная задача)', tabls, [self.plt_rezult])

# описатель класса для возможности обращения к нему
metodDescription = ('Расчёт скорости по длине тормозного пути (обратная задача)',
                    modelInvertTimeRKF, ['L','dL'])

if __name__ == "__main__":
    print(metodDescription[0])