# -*- coding: utf-8 -*-
"""
Created on Wed May 22 20:29:29 2024

@author: ILIA
"""
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
import re
import webbrowser
import pandas as pd
from views.help_txt import get_help as hlp
from views.help_txt import pads as pads
from views.help_txt import loks as loks
from views.help_txt import vags as vags
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class mainWindow:
    def open_web(self):
        if len(self.wwwLoko)>0:
            webbrowser.open_new_tab(self.wwwLoko)

    def __init__(self,params=[['не заданы методы']]):
        tkMain=tk.Tk()
        tkMain.title("Calculations of the braking distance of the train")
        tkMain.geometry("1000x680")
        tkMain.minsize(800,480)
        self.tkMain = tkMain
        self.params = params
        # ------------------------------------------------------------------------
        style = ttk.Style(tkMain)
        style.theme_use("vista")
        style.configure("Big.TLabel", foreground = 'yellow', background="blue",
                        font=('Arial','19','bold'), justify='center',borderwidth=2, relief="groove")

        style.map("My.TButton",
                  foreground=[('pressed', 'red'), ('active', 'blue')],
                  background=[('pressed', '!disabled', 'black'),
                              ('active', 'white')])

        style.configure('My.TButton', font=('Arial','11','bold'))
        # список панелей для активизации при выборе метода
        pans = [m[2] for m in params['models']]

        # ------------------------------------------------------------------------
        # переключение панелей при смене выбора combobox
        def cbSelected(event):
            #print(event)
            cur = pans[comboMetod.current()]
            for p in cur:
                if p.upper() == 'L':
                    fWay.tkraise()
                if p.upper() == 'DL':
                    fdWay.tkraise()
                if p.upper() == 'V':
                    fSpeed.tkraise()
                if p.upper() == 'DV':
                    fdSpeed.tkraise()
                if p.upper() == 'DT':
                    fdTime.tkraise()
        # --------------------------------------------------------------------            
        # create panel 1
        back_color = "lightblue"
        style.configure('Fr1.TFrame', background=back_color)
        l1 = ttk.Label(tkMain, text="Выбор метода расчёта".upper(),
                       style="Big.TLabel", anchor='center')#, background=back_color)
        l1.pack(fill="x")
        fr1 = ttk.Frame(tkMain,borderwidth=1, relief='solid', padding=[8, 10],
                        style= 'Fr1.TFrame')
        self.metod = tk.StringVar(tkMain)
        metods = [m[0] for m in params['models']]
        comboMetod = ttk.Combobox(fr1, values=metods, width=40,font=("Arial",12,'bold'), #height=18,
                              textvariable=self.metod)
                              #style = 'My.TCombobox')
        popdown = tkMain.tk.call("ttk::combobox::PopdownWindow", comboMetod)
        tkMain.tk.call(f"{popdown}.f.l", "configure", "-font", "Arial 10")
        self.metod.set(metods[0])
        comboMetod['state'] = 'readonly'
        comboMetod.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        fr1.columnconfigure(0, weight=1)

        comboMetod.bind("<<ComboboxSelected>>",cbSelected)

        # функция загрузки тестовых значений
        def setTestData():
            self.slope.set("-10")
            #self.wayType.current(0)
            self.Speed0.set("68")
            self.IntSpeed.set("10")
            self.IntTime.set("0.1")
            self.airTemperature.set(25)
            trVagGroups.delete(*trVagGroups.get_children())
            trVags.delete(*trVags.get_children())
            lok_name = "Электровоз серии ВЛ23"
            self.paramsLoko = pd.DataFrame([[lok_name, 138.0, 6, 11.0, 0]],
        				  columns=['name','massa','axles','force','pads'])
            dfl = self.paramsLoko

            lok_name = f"{dfl.at[0,'name']}\nОсей - {dfl.at[0,'axles']}, вес - {dfl.at[0,'massa']} тонн, тормозное усилие - {dfl.at[0,'force']}"
            self.wwwLoko = r'https://ru.wikipedia.org/wiki/%D0%92%D0%9B23'
            labLoko['text'] = lok_name.upper()
            self.lokoVes = dfl.at[0,'massa']
            vg_name = 'Четырёхосные и двухосные грузовые вагоны при включении "нагруженный режим"'
            self.paramsTrain = pd.DataFrame([[vg_name, 20, 82.0, 4, 7.0, 0, 8],
                                             [vg_name, 10, 82.0, 4, 7.0, 0, 8],
                                             [vg_name, 20, 82.0, 4, 7.0, 0, 8],
                                             ],
        	   	      columns=['name', 'count','massa','axles','force','pads','id'])
            ids = set()
            df = self.paramsTrain
            for idx in range(df.shape[0]):
                vals =[df.at[idx,'count'],int(df.at[idx,'id']),df.at[idx,'massa'],
                       df.at[idx,'axles'], pads[int(df.at[idx,'pads'])],df.at[idx,'force']]
                if not df.at[idx,'id'] in ids:
                    ids.add(df.at[idx,'id'])
                    self.trVagGroups.insert("", "end", values=[df.at[idx,'id'],df.at[idx,'name']],
                       text="edit", tags=(f'gr{len(self.trVagGroups.get_children())%2}',))
                self.trVags.insert("", "end", values=vals,
                       text="edit", tags=(f'gr{len(self.trVags.get_children())%2}',))
            self.calcVagsData()
        # функция вызова расчёта по выбранному методу
        def calcMetod():
            pnt = comboMetod.current()
            cur = pans[pnt]
            startCondition = pd.DataFrame()
        # начальные условия
            startCondition['type'] = [self.trainType.current()]
            startCondition['way'] = [self.wayType.current()]
            try:
                 startCondition['slope'] = [float(self.slope.get())]
            except ValueError:
                 showerror(title="Ошибка выбора уклона",
                          message="Не задан уклон или неверные значения")
                 return
            try:
                 startCondition['air'] = [float(self.airTemperature.get())]
            except ValueError:
                 showerror(title="Ошибка выбора температуры",
                          message="Не задан уклон или неверные значения")
                 return
            if 'L' in cur:
                try:
                     startCondition['lenWay'] = [float(self.LenWay.get())]
                except ValueError:
                     showerror(title="Ошибка выбора длины тормозного пути",
                                message="Не задана или неверные значения")
                     return
            if 'dL' in cur:
                try:
                     startCondition['stepL'] = [float(self.accWay.get())]
                except ValueError:
                     showerror(title="Ошибка выбора точности расчёта",
                                message="Не задан параметр или неверное значение")
                     return
            if 'V' in cur:
                try:
                     v0 = float(self.Speed0.get())
                     if v0 < 1.0 or v0 > 160.0:
                         showerror(title="Ошибка выбора начальной скорости",
                                    message="Начальная скорость должна быть в диапазоне от 1 км/ч до 160 км/ч")
                         return
                     startCondition['v0'] = [v0]
                except ValueError:
                     showerror(title="Ошибка выбора начальной скорости",
                                message="Не задана начальная скорость или неверные значения")
                     return
            if 'dV' in cur:
                try:
                     startCondition['step'] = [float(self.IntSpeed.get())]
                except ValueError:
                     showerror(title="Ошибка выбора шага скорости",
                                message="Не задан параметр или неверное значение")
                     return
            if 'dt' in cur:
                try:
                     startCondition['dt'] = [float(self.IntTime.get())]
                except ValueError:
                     showerror(title="Ошибка выбора интервала времени",
                                message="Не задан параметр или неверное значение")
                     return

            data = params['models'][pnt][1](self.paramsTrain, self.paramsLoko, startCondition)
            data.calculate()

            rezWin = tk.Tk()

            rezWin.geometry("1100x650")
            rezWin.minsize(1000,350)
            rezWin.title(comboMetod.get())

            data.putReport(rezWin)

            rezWin.mainloop()

        # функция вызова окна редактора базы данных
        def editBase():
            params['baseEditor'](params['connect'],tkMain)

        # кнопка вызова выбранного метода расчета
        calc_btn = ttk.Button(fr1, text="Расчитать",
                              style="My.TButton", command = calcMetod)
        calc_btn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        # кнопка загрузки тестовых данных
        tst_btn = ttk.Button(fr1, text="Тест данные",
                             style="My.TButton", command = setTestData)
        tst_btn.grid(row=0, column=2, padx=5, pady=5, sticky=tk.EW)

        # кнопка вызова окна редактора базы данных
        base_btn = ttk.Button(fr1, text="Работа с базой данных",
                              style="My.TButton", command=editBase)
        base_btn.grid(row=0, column=3, padx=5, pady=5, sticky=tk.EW)

        fr1.pack(fill="x")
        # ------------------------------------------------------------------------
        # create panel 2
        back_color = "lightcyan"
        style.configure('Fr2.TFrame', background=back_color)
        style.configure('My.TLabelFrame',anchor='center', background=back_color)
        l2 = ttk.Label(tkMain, text="Внешние условия".upper(),
                       style="Big.TLabel", anchor='center')#,background=back_color)
        l2.pack(fill="x",pady = (2,0))
        fr2 = ttk.Frame(tkMain,borderwidth=1, relief='solid',# padding=[8, 10],
                        style= 'Fr2.TFrame')
        forecolor = 'green'
        # +++++++++++++++
        # цвета для окна со справкой
        help_bg_color = '#FFD0E8'
        help_fg_color = 'black'
        # функция отображения окна со справкой
        def help_window(par,helptext):
            # создаём модальное окно
            top = tk.Toplevel(tkMain)
            # задаём заголовок окна
            top.title(helptext[0])
            # задаём расположение окна в привязке к объеку справки
            top.geometry(f"+{tkMain.winfo_rootx()+par.winfo_x()}+{par.winfo_rooty()+par.winfo_height()}")
            top['background']=help_bg_color
            # текст подсказки/справки
            tk.Label(top, text=helptext[1], relief='flat',bg=help_bg_color,
                             font=('Arial','12','italic'),
                             fg=help_fg_color).pack(fill='both',
                                                padx=10,pady=10,expand = 1)
            # кнопка закрытия окна со справкой
            ttk.Button(top,text="Ok",command=top.destroy,
                    width = 10,style="My.TButton").pack(side='bottom',
                                                        padx=10,pady=10)
            # запрет изменения размеров
            top.resizable(0,0)
            # блокировка родительского окна
            top.transient(tkMain)
            top.grab_set()
            top.focus_set()
            top.wait_window(tkMain)

        # +++++++++++++++
        # цвета кнопки вызова справки
        bt_help_fg_color = 'white'
        bt_help_bg_color = 'skyblue'
        # добавление панели с полем текстового ввода
        def add_entry(mast,r,c,text,helptext=['Справка','Текст справки большого размера']):
            lf = tk.LabelFrame(mast,text=text,font=('Arial','11','bold'))
            sv = tk.StringVar(mast)
            lf.configure(labelanchor='n',background=back_color)
            action = lambda x=helptext, p=lf: help_window(par=p,
                                                    helptext=[f"{x[0]}",f"{x[1]}"])
            btn = tk.Button(lf, text="i", width=2, command=action)
            btn.configure(font=('Arial','13','bold'),fg=bt_help_fg_color,
                          bg=bt_help_bg_color,relief='flat', activebackground='yellow')
            btn.pack(side='right',fill='y',padx=(0,10),pady=(0,8))
            # функция проверки на валидность введённого значения
            def is_valid(newval,nam):
                en = tkMain.nametowidget(nam)
                pattern =r'[-+]?[0-9]*\.?[0-9]*'
                if len(newval)==0 or re.fullmatch(pattern, newval) is None:
                    en.configure({"bg": "pink"})
                else:
                    en.configure({"bg": "white"})
                #print(newval,nam, en['bg'])
                return True
            # параметры передаваемые функции проверки на валидность
            # check = (lf.register(is_valid), "%P","%W")
            en = tk.Entry(lf, justify='center',font=('Arial','11','bold'),
                          relief='ridge', bd=2, borderwidth=2,
                           validate="key",
                           validatecommand=(lf.register(is_valid), "%P","%W"),
                           foreground=forecolor, textvariable=sv)
            en.pack(fill='both',expand = 1,padx=(10,10),pady=(0,8))
            lf.grid(row=r,column=c,sticky=tk.EW,padx=(5,5),pady=(1,4))
            mast.columnconfigure(c, weight=1)
            return sv,lf

        # +++++++++++++++
        # Creating a photoimage object to use image
        #self.photo = PhotoImage(file = r".\icons\icons8-информация-48.png")

        # Resizing image to fit on button
        #self.photoimage = self.photo.subsample(3, 3)
        def add_combobox(mast,r,c,text,vals,helptext=['Справка','Текст справки']):
            lf = tk.LabelFrame(mast,text=text,font=('Arial','11','bold'))
            lf.configure(labelanchor='n',background=back_color)
            action = lambda x=helptext,p=lf: help_window(par=p,
                                                    helptext=[f"{x[0]}",f"{x[1]}"])
            btn = tk.Button(lf, text="i", width=2, command=action,)# image="::tk::icons::information")
            btn.configure(font=('Arial','13','bold'),fg=bt_help_fg_color,
                          bg=bt_help_bg_color,
                          relief='flat', activebackground='yellow')
            btn.pack(side='right',fill='y',padx=(0,10),pady=(0,8))
            cmb = ttk.Combobox(lf, values=vals,font=('Arial','11','bold'),# width=40,font=("Arial",12), #height=18,
                              justify='center',foreground=forecolor,
                              background='yellow')
            cmb['state']='readonly'
            cmb.current(0)
            cmb.pack(fill='both',expand = 1,padx=(10,10),pady=(0,10))
            lf.grid(row=r,column=c,sticky=tk.EW,padx=(5,5),pady=(1,4))
            mast.columnconfigure(c, weight=1)
            return cmb,lf
        # -----------------------------------------
        # текстовые переменные для Entry
        self.slope,_ = add_entry(fr2,0,0,"Уклон, ‰", hlp('slope'))
        self.LenWay,fWay = add_entry(fr2,0,1,"Тормозной путь, м", hlp('break_way'))
        self.Speed0,fSpeed = add_entry(fr2,0,1,"Начальная скорость, км/ч", hlp('speed0'))
        self.accWay,fdWay = add_entry(fr2,0,2,"Точность расчёта, м", hlp('acc_way'))
        self.IntTime,fdTime = add_entry(fr2,0,2,"Интервалы времени, сек", hlp('int_time'))
        self.IntSpeed,fdSpeed = add_entry(fr2,0,2,"Интервалы скорости, км/ч", hlp('int_speed'))
        self.wayType,_ = add_combobox(fr2,1,0,'Тип пути',['звеньевой','бесстыковой'], hlp('type_way'))
        self.trainType,_ = add_combobox(fr2,1,1,'Тип состава',vags, hlp('type_train'))
        self.airTemperature,_ = add_entry(fr2,1,2,'Температура воздуха, ºС', hlp('air'))
        fr2.pack(fill = 'x')
        #====================================================================
        # начальные значения
        self.slope.set("-10")
        self.LenWay.set("950.0")
        self.accWay.set("0.2")
        self.Speed0.set("68")
        self.IntSpeed.set("10")
        self.IntTime.set("1")
        self.airTemperature.set("25")
        # ------------------------------------------------------------------------
        # create panel 3
        back_color = "#D0E0A2" # "thistle"
        style.configure('Fr3.TFrame', background=back_color)
        style.configure('My.TLabelFrame',anchor='center')#, background=back_color)
        l2 = ttk.Label(tkMain, text="Локомотив".upper(),
                       style="Big.TLabel", anchor='center')#,background=back_color)
        l2.pack(fill="x",pady = (2,0))
        fr3 = ttk.Frame(tkMain,borderwidth=1, relief='solid',# padding=[8, 10],
                        style= 'Fr3.TFrame')
        labLoko = ttk.Label(fr3, text="ВЛ43\nОсей - 4, вес - 137 тонн, тормозное усилие - 11".upper(),font=('Arial','11','bold'),
                       style="Info.TLabel", anchor='center',
                       background='ivory',
                       borderwidth=2, relief="groove")
        self.lokoVes = 137.0
        labLoko.grid(row=0,column=0,sticky=tk.EW,pady = 5,padx = 5,ipady=3)
        self.labLoko = labLoko
        fr3.columnconfigure(0, weight=1)
        bt = ttk.Button(fr3, text="Выбор",style="My.TButton", command=self.SelLokoClick)
        bt.grid(row=0, column=1,padx=20,pady=10)
        bt = ttk.Button(fr3, text="WWW",style="My.TButton", command=self.open_web)
        bt.grid(row=0, column=2,padx=20,pady=10)
        self.wwwLoko = ''


        fr3.pack(fill = 'x')
        # ------------------------------------------------------------------------
        # create panel 4
        back_color = "lavender"
        style.configure('Fr4.TFrame', background=back_color)
        style.configure('My.TLabelFrame',anchor='center')#, background=back_color)
        l2 = ttk.Label(tkMain, text="группы вагонов".upper(),
                       style="Big.TLabel", anchor='center')#,background=back_color)
        l2.pack(fill="x",pady = (2,0))

        fr7 = ttk.Frame(tkMain,borderwidth=1, relief='solid',# padding=[8, 10],
                        style= 'Fr4.TFrame')
        btnAddVags = ttk.Button(fr7, text="Добавить группу вагонов",
                                style="My.TButton", command = self.AddVagsClick)
        btnAddVags.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
        btnDelVags = ttk.Button(fr7, text="Удалить группу вагонов",
                                style="My.TButton", command = self.DelVagsClick)
        btnDelVags.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        fr7.columnconfigure(0, weight=1)
        fr7.columnconfigure(1, weight=1)
        fr7.pack(fill="x")

        fr4 = ttk.Frame(tkMain,borderwidth=1, relief='solid',# padding=[8, 10],
                        style= 'Fr4.TFrame')
        def addlb(mast,r,c,text):
            lf = tk.LabelFrame(mast,text=text,font=('Arial','11','bold'))
            sv = tk.StringVar(mast)
            lf.configure(labelanchor='n',background=back_color)
            lb = ttk.Label(lf,anchor='center',font=('Arial','11','bold'),textvariable=sv,
                           background='white',borderwidth=2, relief="groove",
                           foreground='teal')
            lb.pack(fill='both',expand = 1,padx=(10,10),pady=(0,10))
            lf.grid(row=r,column=c,sticky=tk.EW,padx=(5,5),pady=(1,4))
            mast.columnconfigure(c, weight=1)
            return sv
        # текстовые переменные для Labels
        self.allGroup =  addlb(fr4,0,0,"Всего групп, шт")
        self.allAxes =   addlb(fr4,0,1,"Всего осей, шт")
        self.allVags =   addlb(fr4,0,2,"Всего вагонов, шт")
        self.vagMassa =  addlb(fr4,0,3,"Вес вагонов, т")
        self.fullMassa = addlb(fr4,0,4,'Вес поезда, т')

        self.allGroup.set("0")
        self.allAxes.set("0")
        self.allVags.set("0")
        self.vagMassa.set("0")
        self.fullMassa.set(self.lokoVes)

        style.configure("mystyle.Treeview", highlightthickness=0, bd=2,
                        font=('Calibri', 11), background="lightyellow") # Modify the font of the body
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 12,'bold'),foreground='indigo',
                        background="skyblue", selectbackground = "skyblue",) # Modify the font of the headings
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        style.map("mystyle.Treeview.Heading",
                background = [('pressed', '!focus', "deepskyblue"),
                              ('active', "skyblue"),
                              ('disabled', '#ffffff')])

        fr5 = ttk.Frame(fr4,borderwidth=1, relief='solid',# padding=[8, 10],
                        style= 'Fr4.TFrame')
        fr5.grid(row=1, column=0,columnspan=5,padx=2,sticky='ew')


        cols = ['id','value']
        trVagGroups = ttk.Treeview(fr5, columns=cols, show="headings", style="mystyle.Treeview")
        trVagGroups.tag_configure('gr0', background='lightcyan')
        trVagGroups.column("#0", width=0,  stretch=tk.NO)
        trVagGroups.heading('#1', text='id')
        trVagGroups.column(cols[0], anchor="center", width=100, minwidth=10, stretch=tk.NO)
        trVagGroups.heading('#2', text='Тип группы вагонов')
        trVagGroups.column(cols[1], anchor="center", width=40, minwidth=40, stretch=tk.YES)
        #trVagGroups.insert("", "end", values=['Add'], tags=(f'gr{len(trVagGroups.get_children())%2}',))
        #trVagGroups.config(height=len(trVagGroups.get_children()))
        trVagGroups.config(height=3)
        scrollbar_object = tk.Scrollbar(fr5, orient="vertical")
        scrollbar_object.pack(side='right', fill='y')
        scrollbar_object.config(command=trVagGroups.yview)
        trVagGroups.configure(yscrollcommand=scrollbar_object.set)
        trVagGroups.pack(padx=2,fill='x')
        self.trVagGroups = trVagGroups


        fr6 = ttk.Frame(fr4,borderwidth=1, relief='solid',# padding=[8, 10],
                        style= 'Fr4.TFrame')
        fr6.grid(row=2, column=0,columnspan=5,padx=2,sticky='nsew')
        fr4.rowconfigure(2, weight = 1)
        cols = ["cnt","id","weight","axis","pads","kt"]
        trVags = ttk.Treeview(fr6, columns=cols, show="headings", style="mystyle.Treeview")
        trVags.tag_configure('gr0', background='lightcyan')
        trVags.column("#0", width=0,  stretch=tk.NO)
        trVags.heading('#1', text='Количество')
        trVags.column(cols[0], anchor="center", width=100, minwidth=100, stretch=tk.NO)
        trVags.heading('#2', text='id')
        trVags.column(cols[1], anchor="center", width=100, minwidth=100, stretch=tk.NO)
        trVags.heading('#3', text='Вес, т')
        trVags.column(cols[3], anchor="center", width=100, minwidth=100, stretch=tk.NO)
        trVags.heading('#4', text='Оси, шт')
        trVags.column(cols[2], anchor="center", width=100, minwidth=100, stretch=tk.NO)
        trVags.heading('#5', text='Колодки')
        trVags.column(cols[4], anchor="center", width=100, minwidth=100, stretch=tk.NO)
        trVags.heading('#6', text='Усилие нажима, т')
        trVags.column(cols[5], anchor="center", width=100, minwidth=100, stretch=tk.YES)
        trVags.config(height=1)
        scrollbar_object = tk.Scrollbar(fr6, orient="vertical")
        scrollbar_object.pack(side='right', fill='y')
        scrollbar_object.config(command=trVags.yview)
        trVags.configure(yscrollcommand=scrollbar_object.set)
        trVags.pack(padx=2,fill='both',expand=1)
        self.trVags = trVags
        fr4.pack(fill = 'both',expand=1)

        tkMain.update()
        # ------------------------------------------------------------------------
        self.win = tkMain
        self.frvag = fr4
        #tkMain.eval('tk::PlaceWindow . center')
        tkMain.mainloop()
        params['connect'].close() # закрыть подключение к базе
    # ----------------------------------------------------------------------------
    # ----------------------------------------------------------------------------
    # подсчёт параметров состава и удаление ненужных записей
    def calcVagsData(self, remId=0):
        a_cnt = 0
        a_axes = 0
        a_massa = 0.0
        remGrp = True
        df = pd.DataFrame(columns=['name', 'count','massa','axles','force','pads','id'])
        idx = 0
        for row in self.trVags.get_children():
            cnt = int(self.trVags.item(row)['values'][0])
            ax = int(self.trVags.item(row)['values'][3])
            mas = float(self.trVags.item(row)['values'][2])
            if remId == self.trVags.item(row)['values'][1]:
                remGrp = False
            a_cnt += cnt
            a_axes += cnt * ax
            a_massa = a_massa + cnt*mas
            df.at[idx,'count'] = cnt
            df.at[idx,'massa'] = mas
            df.at[idx,'axles'] = ax
            df.at[idx,'force'] = float(self.trVags.item(row)['values'][5])
            df.at[idx,'pads'] = pads.index(self.trVags.item(row)['values'][4])
            idg = self.trVags.item(row)['values'][1]
            for row in self.trVagGroups.get_children():
                if self.trVagGroups.item(row)['values'][0] == idg:
                    df.at[idx,'name'] = self.trVagGroups.item(row)['values'][1]
                    df.at[idx,'id'] = idg
                    break
            idx += 1

        if remId>0 and remGrp:
            for row in self.trVagGroups.get_children():
                if self.trVagGroups.item(row)['values'][0] == remId:
                    self.trVagGroups.delete(row)
                    break
        self.paramsTrain = df
        self.vagMassa.set(a_massa)
        self.fullMassa.set(a_massa + self.lokoVes)
        self.allAxes.set(a_axes)
        self.allVags.set(a_cnt)
        self.allGroup.set(len(self.trVags.get_children()))
    # ----------------------------------------------------------------------------
    # удаление строки записи о группе вагонов
    def DelVagsClick(self):
        sel = self.trVags.selection()
        if len(sel) == 0:
            return
        remId = self.trVags.item(sel[0])['values'][1]
        self.trVags.delete(sel[0])
        self.calcVagsData(remId)
    # ----------------------------------------------------------------------------
    def AddVagsClick(self):
        tkMain = self.win
        top = tk.Toplevel(tkMain)
        top.title('Выбор группы вагонов')
        top.geometry(f"{tkMain.winfo_width()}x{600}+{tkMain.winfo_rootx()}+{tkMain.winfo_rooty()}")
        top['background']='blue'
        label = tk.Label(top, text='Выберите тип группы вагонов и задайте параметры', relief='flat',
                         font=('Arial','12','italic'), fg='black', bg = 'aqua')
        label.pack(fill='x',padx=1,pady=1)
        cols = ['id','typeVagons']
        fr5 = ttk.Frame(top,borderwidth=1, relief='solid',)# padding=[8, 10],
        fr5.pack(fill='both',expand = 1)
        trVagGroups = ttk.Treeview(fr5, columns=cols, show="headings", style="mystyle.Treeview",
                                   )
        trVagGroups.tag_configure('gr0', background='lightcyan')

        trVagGroups.column("#0", width=0,  stretch=tk.NO)
        trVagGroups.heading('#1', text='id')
        trVagGroups.column(cols[0], anchor="center", width=50, minwidth=10, stretch=tk.NO)
        trVagGroups.heading('#2', text='Тип группы вагонов')
        trVagGroups.column(cols[1], anchor="w", width=40, minwidth=40, stretch=tk.YES)
        trVagGroups.config(height=3)
        scrollbar_object = tk.Scrollbar(fr5, orient="vertical")
        scrollbar_object.pack(side='right', fill='y')
        scrollbar_object.config(command=trVagGroups.yview)
        trVagGroups.configure(yscrollcommand=scrollbar_object.set)
        df = pd.read_sql_query("SELECT * FROM VAGON", self.params['connect'])

        for idx in range(df.shape[0]):
            trVagGroups.insert("", "end", values=[f"{idx+1}",df.at[idx,'name']],
                      text="edit", tags=(f'gr{idx%2}',))

        trVagGroups.pack(padx=2,fill='both',expand = 1)
        #-------------------
        # +++++++++++++++
        fr2 = ttk.Frame(top,borderwidth=1, relief='solid',# padding=[8, 10],
                        style= 'Fr2.TFrame')
        forecolor = 'green'
        help_bg_color = '#FFD0E8'
        help_fg_color = 'black'
        def help_window(par,helptext):
            top = tk.Toplevel(tkMain)
            top.title(helptext[0])
            top.geometry(f"+{tkMain.winfo_rootx()+par.winfo_x()}+{par.winfo_rooty()+par.winfo_height()}")
            top['background'] = help_bg_color
            label = tk.Label(top, text=helptext[1], relief='flat',bg=help_bg_color,
                             font=('Arial','12','italic'), fg=help_fg_color)
            label.pack(fill='both',padx=10,pady=10,expand = 1)
            b1=ttk.Button(top,text="Ok",command=top.destroy,width = 10,style="My.TButton")
            b1.pack(side='bottom',padx=10,pady=10)
            top.resizable(0,0)
            top.transient(tkMain)
            top.grab_set()
            top.focus_set()
            top.wait_window(tkMain)
        bt_help_fg_color = 'white'
        bt_help_bg_color = 'skyblue'
        back_color = "lightcyan"
        def add_entry(mast,r,c,text,helptext=['Справка','Текст справки большого размера']):
            lf = tk.LabelFrame(mast,text=text,font=('Arial','11','bold'))
            sv = tk.StringVar(top)
            lf.configure(labelanchor='n',background=back_color)
            action = lambda x=helptext, p=lf: help_window(par=p,
                                                    helptext=[f"{x[0]}",f"{x[1]}"])
            btn = tk.Button(lf, text="i", width=2, command=action)
            btn.configure(font=('Arial','13','bold'),fg=bt_help_fg_color,
                          bg=bt_help_bg_color,relief='flat', activebackground='yellow')
            btn.pack(side='right',fill='y',padx=(0,10),pady=(0,8))
            def is_valid(newval,nam):
                en = tkMain.nametowidget(nam)
                pattern =r'[-+]?[0-9]*\.?[0-9]*'
                if len(newval)==0 or (re.fullmatch(pattern, newval) is None) or float(newval)==0.0:
                    en.configure({"bg": "pink"})
                else:
                    en.configure({"bg": "white"})
                return True
            check = (lf.register(is_valid), "%P","%W")
            en = tk.Entry(lf, justify='center',font=('Arial','11','bold'),
                          relief='ridge', bd=2, borderwidth=2,
                           validate="key", validatecommand=check,
                           foreground=forecolor, textvariable=sv)
            en.pack(fill='both',expand = 1,padx=(10,10),pady=(0,8))
            lf.grid(row=r,column=c,sticky=tk.EW,padx=(5,5),pady=(1,4))
            mast.columnconfigure(c, weight=1)
            return sv,lf
        def add_combobox(mast,r,c,text,vals,helptext=['Справка','Текст справки']):
            lf = tk.LabelFrame(mast,text=text,font=('Arial','11','bold'))
            lf.configure(labelanchor='n',background=back_color)
            action = lambda x=helptext,p=lf: help_window(par=p,
                                                    helptext=[f"{x[0]}",f"{x[1]}"])
            btn = tk.Button(lf, text="i", width=2, command=action,)# image="::tk::icons::information")
            btn.configure(font=('Arial','13','bold'),fg=bt_help_fg_color,
                          bg=bt_help_bg_color,
                          relief='flat', activebackground='yellow')
            btn.pack(side='right',fill='y',padx=(0,10),pady=(0,8))
            cmb = ttk.Combobox(lf, values=vals,font=('Arial','11','bold'),# width=40,font=("Arial",12), #height=18,
                              justify='center',foreground=forecolor)
            cmb['state']='readonly'
            cmb.current(0)
            cmb.pack(fill='both',expand = 1,padx=(10,10),pady=(0,10))
            lf.grid(row=r,column=c,sticky=tk.EW,padx=(5,5),pady=(1,4))
            mast.columnconfigure(c, weight=1)
            return cmb,lf
        # -----------------------------------------


        # текстовые переменные для Entry
        vag_count,_ = add_entry(fr2,0,0,"Количество, шт", hlp('vag_count'))
        vag_massa,_ = add_entry(fr2,0,1,"Вес вагона, тонн", hlp('vag_massa'))
        vag_axes,_ = add_entry(fr2,0,2,"Количество осей, шт", hlp('vag_axles'))
        vag_force,_ = add_entry(fr2,1,0,"Тормозное усилие, тонн", hlp('vag_force'))
        vag_pads,_ = add_combobox(fr2,1,1,"Тип колодок", pads, hlp('vag_pads'))
        vag_mode,_ = add_combobox(fr2,1,2,"Режим", ['гружёный','порожний'], hlp('vag_mode'))
        #trVagGroups.selection_set("I001")
        def sel_vagon(event):
            idx =trVagGroups.selection()[0]
            idx =int(idx[1:],16)-1
            vag_count.set(1)
            vag_massa.set(50)
            vag_axes.set(4)#df.at[idx,'axles'])
            vag_force.set(df.at[idx,'force'])
            vag_pads.current(0)
            vag_mode.current(0)
        trVagGroups.bind("<<TreeviewSelect>>", sel_vagon)
        #self.wayType,_ = add_combobox(fr2,1,0,'Тип пути',['звеньевой','бесстыковой'])
        #self.trainType,_ = add_combobox(fr2,1,1,'Тип состава',['грузовой','пассажирский'])
        #vag_type,_ = add_entry(fr2,1,2,'Тип состава2')
        fr2.pack(fill = 'x')
        #
        def press_ok():
            grp = -1
            id_grp = trVagGroups.item(trVagGroups.selection()[0])['values'][0]
            for row in self.trVagGroups.get_children():
                if self.trVagGroups.item(row)['values'][0] == id_grp:
                    grp = id_grp
                    break
            if grp<0:
                self.trVagGroups.insert("", "end", values=[id_grp, trVagGroups.item(trVagGroups.selection()[0])['values'][1]],
                      text="edit", tags=(f'gr{len(self.trVagGroups.get_children())%2}',))
                grp = id_grp
            #cols = ["cnt","id","weight","axis","pads","kt"]
            vals =[vag_count.get(),id_grp,vag_massa.get(),vag_axes.get(),vag_pads.get(),vag_force.get()]
            self.trVags.insert("", "end", values=vals,
                       text="edit", tags=(f'gr{len(self.trVags.get_children())%2}',))
            self.calcVagsData()
            top.destroy()

        b1=ttk.Button(top,text="Ok",command=press_ok,width = 10,style="My.TButton")
        #b1.grid(row=2, column=0, padx=(2, 35), sticky="ew")
        b1.pack(side='bottom',padx=10,pady=10)
        #top.protocol("WM_DELETE_WINDOW", top.close)
        #top.bind("<FocusOut>", top.focus_force)
        #top.attributes('-topmost', True)
        #top.resizable(0,0)
        top.transient(tkMain)
        top.grab_set()
        top.focus_set()
        top.wait_window(tkMain)

    # ----------------------------------------------------------------------------
    def SelLokoClick(self):
        tkMain = self.win
        top = tk.Toplevel(tkMain)
        top.title('Выбор локомотива')
        top.geometry(f"{tkMain.winfo_width()}x{600}+{tkMain.winfo_rootx()}+{tkMain.winfo_rooty()}")
        top['background']='blue'
        #l1=tk.Label(top, image="::tk::icons::information")
        #l1.grid(row=0, column=0, pady=(7, 0), padx=(10, 30), sticky="e")
        #l1.pack(side="left")
        label = tk.Label(top, text='Выберите локомотив', relief='flat',
                         font=('Arial','12','italic'), fg='black', bg = 'aqua')
        label.pack(fill='x',padx=1,pady=1)
        cols = ['id','typeLoko']
        fr5 = ttk.Frame(top,borderwidth=1, relief='solid',)# padding=[8, 10],
        fr5.pack(fill='both',expand = 1)
        trLoko = ttk.Treeview(fr5, columns=cols, show="headings", style="mystyle.Treeview",
                                   )
        trLoko.tag_configure('gr0', background='lightcyan')

        trLoko.column("#0", width=0,  stretch=tk.NO)
        trLoko.heading('#1', text='id')
        trLoko.column(cols[0], anchor="center", width=50, minwidth=10, stretch=tk.NO)
        trLoko.heading('#2', text='Название локомотива')
        trLoko.column(cols[1], anchor="w", width=40, minwidth=40, stretch=tk.YES)
        #trLoko.insert("", "end", values=['Add'], tags=(f'gr{len(trLoko.get_children())%2}',))
        #trLoko.config(height=len(trLoko.get_children()))
        trLoko.config(height=3)
        scrollbar_object = tk.Scrollbar(fr5, orient="vertical")
        scrollbar_object.pack(side='right', fill='y')
        scrollbar_object.config(command=trLoko.yview)
        trLoko.configure(yscrollcommand=scrollbar_object.set)
        #-------------------------------------------------------------
        df = pd.read_sql_query("SELECT * FROM LOKO", self.params['connect'])
        for idx in range(df.shape[0]):
            trLoko.insert("", "end", values=[f"{idx+1}",f"{loks[df.at[idx,'type']]} {df.at[idx,'name']}"],
                      text="edit", tags=(f'gr{idx%2}',))

        trLoko.pack(padx=2,fill='both',expand = 1)
        #-------------------
        # +++++++++++++++
        fr2 = ttk.Frame(top,borderwidth=1, relief='solid',# padding=[8, 10],
                        style= 'Fr2.TFrame')
        forecolor = 'green'
        help_bg_color = '#FFD0E8'
        help_fg_color = 'black'
        def help_window(par,helptext):
            top = tk.Toplevel(tkMain)
            top.title(helptext[0])
            top.geometry(f"+{tkMain.winfo_rootx()+par.winfo_x()}+{par.winfo_rooty()+par.winfo_height()}")
            top['background'] = help_bg_color
            label = tk.Label(top, text=helptext[1], relief='flat',bg=help_bg_color,
                             font=('Arial','12','italic'), fg=help_fg_color)
            label.pack(fill='both',padx=10,pady=10,expand = 1)
            b1=ttk.Button(top,text="Ok",command=top.destroy,width = 10,style="My.TButton")
            b1.pack(side='bottom',padx=10,pady=10)
            top.resizable(0,0)
            top.transient(tkMain)
            top.grab_set()
            top.focus_set()
            top.wait_window(tkMain)
        bt_help_fg_color = 'white'
        bt_help_bg_color = 'skyblue'
        back_color = "lightcyan"
        def add_entry(mast,r,c,text,helptext=['Справка','Текст справки большого размера']):
            lf = tk.LabelFrame(mast,text=text,font=('Arial','11','bold'))
            sv = tk.StringVar(top)
            lf.configure(labelanchor='n',background=back_color)
            action = lambda x=helptext, p=lf: help_window(par=p,
                                                    helptext=[f"{x[0]}",f"{x[1]}"])
            btn = tk.Button(lf, text="i", width=2, command=action)
            btn.configure(font=('Arial','13','bold'),fg=bt_help_fg_color,
                          bg=bt_help_bg_color,relief='flat', activebackground='yellow')
            btn.pack(side='right',fill='y',padx=(0,10),pady=(0,8))
            def is_valid(newval,nam):
                en = tkMain.nametowidget(nam)
                pattern =r'[-+]?[0-9]*\.?[0-9]*'
                if len(newval)==0 or (re.fullmatch(pattern, newval) is None) or float(newval)==0.0:
                    en.configure({"bg": "pink"})
                else:
                    en.configure({"bg": "white"})
                return True
            check = (lf.register(is_valid), "%P","%W")
            en = tk.Entry(lf, justify='center',font=('Arial','11','bold'),
                          relief='ridge', bd=2, borderwidth=2,
                           validate="key", validatecommand=check,
                           foreground=forecolor, textvariable=sv)
            en.pack(fill='both',expand = 1,padx=(10,10),pady=(0,8))
            lf.grid(row=r,column=c,sticky=tk.EW,padx=(5,5),pady=(1,4))
            mast.columnconfigure(c, weight=1)
            return sv,lf
        def add_combobox(mast,r,c,text,vals,helptext=['Справка','Текст справки']):
            lf = tk.LabelFrame(mast,text=text,font=('Arial','11','bold'))
            lf.configure(labelanchor='n',background=back_color)
            action = lambda x=helptext,p=lf: help_window(par=p,
                                                    helptext=[f"{x[0]}",f"{x[1]}"])
            btn = tk.Button(lf, text="i", width=2, command=action,)# image="::tk::icons::information")
            btn.configure(font=('Arial','13','bold'),fg=bt_help_fg_color,
                          bg=bt_help_bg_color,
                          relief='flat', activebackground='yellow')
            btn.pack(side='right',fill='y',padx=(0,10),pady=(0,8))
            cmb = ttk.Combobox(lf, values=vals,font=('Arial','11','bold'),# width=40,font=("Arial",12), #height=18,
                              justify='center',foreground=forecolor)
            cmb['state']='readonly'
            cmb.current(0)
            cmb.pack(fill='both',expand = 1,padx=(10,10),pady=(0,10))
            lf.grid(row=r,column=c,sticky=tk.EW,padx=(5,5),pady=(1,4))
            mast.columnconfigure(c, weight=1)
            return cmb,lf
        # -----------------------------------------

        # текстовые переменные для Entry
        loko_massa,_ = add_entry(fr2,0,0,"Вес локомотива, тонн", hlp('loko_massa'))
        loko_axes,_ = add_entry(fr2,0,1,"Количество осей, шт", hlp('loko_axles'))
        loko_force,_ = add_entry(fr2,1,0,"Тормозное усилие, тонн", hlp('loko_force'))
        loko_pads,_ = add_combobox(fr2,1,1,"Тип колодок", pads, hlp('loko_pads'))
        #
        def sel_loko(event):
            idx =trLoko.selection()[0]
            idx =int(idx[1:],16)-1
            loko_massa.set(df.at[idx,'weight'])
            loko_axes.set(df.at[idx,'axles'])#df.at[idx,'axles'])
            loko_force.set(df.at[idx,'force'])
            loko_pads.current(0)
        trLoko.bind("<<TreeviewSelect>>", sel_loko)
        fr2.pack(fill = 'x')
        #
        def press_ok():
            idx =trLoko.selection()[0]
            idx =int(idx[1:],16)-1
            lok_name = f"{loks[df.at[idx,'type']]} {df.at[idx,'name']}"
            self.labLoko['text'] = f"{lok_name} {df.at[idx,'desc']}\nОсей - {loko_axes.get()}, вес - {loko_massa.get()} тонн, тормозное усилие - {loko_force.get()}"
            self.wwwLoko = df.at[idx,'URL']
            if type(self.wwwLoko) != str:
                nn = df.at[idx,'name']
                self.wwwLoko = f'https://www.google.com/search?q="{nn}"'
            self.lokoVes = df.at[idx,'weight']
            self.calcVagsData()
            self.paramsLoko = pd.DataFrame([[lok_name, df.at[idx,'weight'], df.at[idx,'axles'], df.at[idx,'force'], 0]],
        				  columns=['name','massa','axles','force','pads'])
            top.destroy()

        b1=ttk.Button(top,text="Ok",command=press_ok,width = 10,style="My.TButton")
        b1.pack(side='bottom',padx=10,pady=10)
        top.transient(tkMain)
        top.grab_set()
        top.focus_set()
        top.wait_window(tkMain)
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
if __name__ == "__main__":
    lstMetods=[["Тормоза. Расчёт по скорости","Тормоза. Расчёт по времени",
       "Тормоза. Обратный расчёт"],[]]
    mainWindow(lstMetods)