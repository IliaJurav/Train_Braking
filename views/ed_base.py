"""
Модуль окна редактора базы данных

    Выпускная квалификационная работа бакалавра
    Санкт-Петербургский политехнический университет Петра Великого
    Институт компьютерных наук и кибербезопасности
    Высшая школа компьютерных технологий и информационных систем
    направление 09.03.01 Информатика и вычислительная техника
    2024 год

@author: Журавский Илья Александрович
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd
import re
from views.help_txt import get_help as hlp
from urllib.parse import unquote, quote
from tkinter.messagebox import showerror
from views.help_txt import pads as pads
from views.help_txt import loks as loks
from views.help_txt import vags as vags

#---------------------------------------------------------------------------
class EditBase:
    # конструктор
    # cnx - открытое подключение к базе данных
    # parent - ссылка на родительское окно (если есть)
    def __init__(self, cnx, parent=0,):
        if parent:
            tkBase = tk.Toplevel(parent)
            tkBase.geometry(f"{parent.winfo_width()}x{600}+{parent.winfo_rootx()}+{parent.winfo_rooty()}")
        else:
            tkBase = tk.Tk()
        tkBase.title("Manager of the base loko and vagons")
        tkBase.geometry("800x680")
        tkBase.minsize(800,480)
        # определение стилей
        style = ttk.Style(tkBase)
        style.theme_use("vista")

        back_color = "lightblue"
        style.configure('Fr1.TFrame', background=back_color)
        style.configure("mystyle.Treeview", highlightthickness=0, bd=2,
                        font=('Calibri', 11), background="lightyellow") # Modify the font of the body
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 12,'bold'),foreground='indigo',
                        background="skyblue", selectbackground = "skyblue",) # Modify the font of the headings
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        style.map("mystyle.Treeview.Heading",
                background = [('pressed', '!focus', "deepskyblue"),
                              ('active', "skyblue"),
                              ('disabled', '#ffffff')])
        style.map("My.TButton",
                  foreground=[('pressed', 'red'), ('active', 'blue'),('disabled', 'red')],
                  background=[('pressed', '!disabled', 'black'),
                              ('active', 'white')])

        style.configure('My.TButton', font=('Arial','11','bold'))


        forecolor = 'green'
        help_bg_color = '#FFD0E8'
        help_fg_color = 'black'
        def help_window(par,helptext):
            top = tk.Toplevel(tkBase)
            top.title(helptext[0])
            top.geometry(f"+{tkBase.winfo_rootx()+par.winfo_x()}+{par.winfo_rooty()+par.winfo_height()}")
            top['background'] = help_bg_color
            label = tk.Label(top, text=helptext[1], relief='flat',bg=help_bg_color,
                             font=('Arial','12','italic'), fg=help_fg_color)
            label.pack(fill='both',padx=10,pady=10,expand = 1)
            b1=ttk.Button(top,text="Ok",command=top.destroy,width = 10,style="My.TButton")
            b1.pack(side='bottom',padx=10,pady=10)
            top.resizable(0,0)
            top.transient(tkBase)
            top.grab_set()
            top.focus_set()
            top.wait_window(tkBase)
        bt_help_fg_color = 'white'
        bt_help_bg_color = 'skyblue'
        back_color = "lightcyan"
        def add_entry(mast,r,c,text,helptext=['Справка','Текст справки большого размера']):
            lf = tk.LabelFrame(mast,text=text,font=('Arial','11','bold'))
            sv = tk.StringVar(tkBase)
            lf.configure(labelanchor='n',background=back_color)
            action = lambda x=helptext, p=lf: help_window(par=p,
                                                    helptext=[f"{x[0]}",f"{x[1]}"])
            btn = tk.Button(lf, text="i", width=2, command=action)
            btn.configure(font=('Arial','13','bold'),fg=bt_help_fg_color,
                          bg=bt_help_bg_color,relief='flat', activebackground='yellow')
            btn.pack(side='right',fill='y',padx=(0,10),pady=(0,8))
            def is_valid(newval,nam):
                en = tkBase.nametowidget(nam)
                pattern =r'[-+]?[0-9]*\.?[0-9]*'
                if len(newval)==0 or (re.fullmatch(pattern, newval) is None) or float(newval)==0.0:
                    en.configure({"bg": "pink"})
                else:
                    en.configure({"bg": "white"})
                return True
            # валидатор url
            def is_url(code,nam):
                en = tkBase.nametowidget(nam)
                varname = en.cget("textvariable")
                value = en.getvar(varname)
                nv = unquote(value)
                if value != nv:
                    en.delete(0,tk.END)
                    en.insert(0, nv)
                #tkBase.setvar(varname, nv)
                return True
            checkNum = (lf.register(is_valid), "%P","%W")
            checkURL = (lf.register(is_url), "%d","%W")
            en = tk.Entry(lf, justify='center',font=('Arial','11','bold'),
                          relief='ridge', bd=2, borderwidth=2,
                           foreground=forecolor, textvariable=sv)
            if type(r)== str:
                en.config(validate="focusout", validatecommand=checkURL,)
                r = int(r)
            if type(c)== int:
                en.config(validate="key", validatecommand=checkNum,)
            en.pack(fill='both',expand = 1,padx=(10,10),pady=(0,8))
            if type(c)== int:
                lf.grid(row=r,column=c,sticky=tk.EW,padx=(5,5),pady=(1,4))
                mast.columnconfigure(c, weight=1)
            else:
                lf.grid(row=r,column=c[0],columnspan =c[1] , sticky=tk.EW,padx=(5,5),pady=(1,4))
            return sv,lf

        def add_combobox(mast,r,c,text,vals,helptext=['Справка','Текст\nсправки']):
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

        # общий заголовок
        label = tk.Label(tkBase, text='Работа с базой'.upper(), relief='flat',
                         font=('Arial','14','bold'), fg='yellow', bg = 'blue')
        label.pack(fill='x', padx=1, pady=1)

        pnVagon = 0
        pnLoko = 0
        # панель для кнопок переключения таблиц в базе
        fr_but = ttk.Frame(tkBase,borderwidth=1, relief='solid',style='Fr1.TFrame')# padding=[8, 10],
        btLoko = ttk.Button(fr_but, text="Локомотивы",style="My.TButton")
        btLoko.grid(row=0, column=0,padx=20,pady=10)
        btVagon = ttk.Button(fr_but, text="Вагоны", style="My.TButton")
        btVagon.grid(row=0, column=1,padx=20,pady=10)
        # для будущего
        # btRez = ttk.Button(fr_but, text="Результаты", style="My.TButton")#, command=self.open_web)
        # btRez.grid(row=0, column=2,padx=20,pady=10)
        for i in range(2):
            fr_but.columnconfigure(i, weight=1)
        fr_but.pack(fill='x')

        # главная панель на которой будут переключаться таблицы
        frMain = ttk.Frame(tkBase,borderwidth=1, relief='solid',)# padding=[8, 10],
        frMain.pack(fill='both',expand = 1)
        frMain.columnconfigure(0, weight=1)
        frMain.rowconfigure(0, weight=1)

        # загрузка dataframe в treeview
        def setTreeData(tree,df,types):
            tree.delete(*tree.get_children())
            for idx in range(df.shape[0]):
                s = 'I{0:0{1}X}'.format(idx+1,3)
                tree.insert("", "end", values=[f"{idx+1}",types[df.at[idx,'type']],df.at[idx,'name']],
                      text="edit", tags=(f'gr{idx%2}'), iid = s)

        # добавление записи
        def addRec(pn,df,tree,get_vals):
            new = get_vals()
            name = new.at[0,'name']
            if len(name)==0:
                showerror(title="Ошибка добавления записи",
                          message="Поле имени не может быть пустым!")
                return
            if new.at[0,'force'] <=0.001:
                showerror(title="Ошибка добавления записи",
                          message="Значение тормозного усилия не может быть меньше или равно нулю!")
                return
            upd = df[df['name'] == name]
            if len(upd)>1:
                showerror(title="Ошибка добавления записи",
                          message="В базе нарушена уникальность имён!")
                return
            if len(upd)==1:
                showerror(title="Ошибка добавления записи",
                          message=f"В базе уже есть такое имя '{name}'!")
                return
            if pn==1:
                tbl = 'LOKO'
                typs = loks
            else:
                tbl = 'VAGON'
                typs = vags
            if pn==1: # локомотивы
                if new.at[0,'axles'] <= 1:
                    showerror(title="Ошибка добавления записи",
                              message="Значение количества осей мало!")
                    return
                if new.at[0,'weight'] <= 1.0:
                    showerror(title="Ошибка добавления записи",
                              message="Значение веса локомотива мало!")
                    return
            idrec = max(df['id'])+1
            cols = new.columns
            vals = [f"'{new.at[0,cols[i]]}'" for i in range(len(cols))]
            sql = f"INSERT INTO {tbl} (id, {','.join(cols)}) VALUES ({idrec} , {','.join(vals)});"
            cursor = cnx.cursor()
            cursor.execute(sql)
            cnx.commit()
            df.drop(df.index,inplace=True)
            new_df = pd.read_sql_query(f"SELECT * FROM {tbl}", cnx)
            for row in new_df.iterrows():
                df.loc[len(df)] = row[1]
            setTreeData(tree, df, typs)
            elem = tree.get_children()[-1]
            tree.focus(elem)
            tree.selection_set(elem)
            tree.yview_moveto(1)

        # обновление записи
        def updRec(pn,df,tree,get_vals):
            # проверка на выбранную запись
            if len(tree.selection()) == 0:
                showerror(title="Ошибка обновления записи",
                          message="Не выбрана обновляемая запись!")
                return
            # проверка на встроенные записи
            elem = tree.selection()[0]
            idx = int(elem[1:],16)-1
            if (pn == 1 and idx<22) or (pn == 2 and idx<17):
                showerror(title=f"Ошибка обновления записи {idx+1}",
                          message="Встроенные записи нельзя обновлять!")
                return
            if pn==1:
                tbl = 'LOKO'
                typs = loks
            else:
                tbl = 'VAGON'
                typs = vags
            new = get_vals()
            upd = df[df['name'] == new.at[0,'name']]
            if len(upd)>1:
                showerror(title="Ошибка обновления записи",
                          message="В базе нарушена уникальность имён!")
                return
            if upd.at[0,'id']!=idx:
                showerror(title="Ошибка обновления записи",
                          message=f"В базе нарушена уже есть такое имя id={idx+1}!")
                return
            #UPDATE COMPANY SET ADDRESS = 'Texas' WHERE ID = 6;
            df.drop(df.index,inplace=True)
            new_df = pd.read_sql_query(f"SELECT * FROM {tbl}", cnx)
            for row in new_df.iterrows():
                df.loc[len(df)] = row[1]
            setTreeData(tree, df, typs)
            tree.focus(elem)
            tree.selection_set(elem)

        # удаление записи
        def delRec(pn,df,tree,get_vals):
            # проверка на выбранную запись
            if len(tree.selection()) == 0:
                showerror(title="Ошибка удаления записи",
                          message="Не выбрана запись!")
                return
            # проверка на встроенные записи
            idx = tree.selection()[0]
            idx = int(idx[1:],16)-1
            if (pn == 1 and idx<22) or (pn == 2 and idx<17):
                showerror(title=f"Ошибка удаления записи {idx+1}",
                          message="Встроенные записи нельзя удалять!")
                return
            if pn==1:
                tbl = 'LOKO'
                typs = loks
            else:
                tbl = 'VAGON'
                typs = vags
            sql = f"DELETE FROM {tbl} WHERE id = {df.at[idx,'id']};"
            #print(idx, sql)
            cursor = cnx.cursor()
            cursor.execute(sql)
            cnx.commit()
            df.drop(df.index,inplace=True)
            new_df = pd.read_sql_query(f"SELECT * FROM {tbl}", cnx)
            for row in new_df.iterrows():
                df.loc[len(df)] = row[1]
            setTreeData(tree, df, typs)
            item = tree.get_children()[0]
            tree.focus(item)
            tree.selection_set(item)
            tree.yview_moveto(0)

        # панель с данными для локомотивов
        def createPanelLoko():
            cols = ['id','typeLoko','nameLoko']
            frLoko = ttk.Frame(frMain,borderwidth=1, relief='solid',)# padding=[8, 10],
            tk.Label(frLoko, text='Таблица локомотивов', relief='flat',
                             font=('Arial','12','italic'), fg='yellow', bg = 'blue').pack(fill='x')
            frTable= ttk.Frame(frLoko,borderwidth=1, relief='solid',)
            trLoko = ttk.Treeview(frTable, columns=cols, show="headings", style="mystyle.Treeview",)
            trLoko.tag_configure('gr0', background='lightcyan')
            trLoko.column("#0", width=0,  stretch=tk.NO)
            trLoko.heading('#1', text='id')
            trLoko.column(cols[0], anchor="center", width=50, minwidth=10, stretch=tk.NO)
            trLoko.heading('#2', text='Тип локомотива')
            trLoko.column(cols[1], anchor="center", width=140, minwidth=70, stretch=tk.NO)
            trLoko.heading('#3', text='Название локомотива')
            trLoko.column(cols[2], anchor="w", width=40, minwidth=40, stretch=tk.YES)
            trLoko.config(height=3)
            scrollbar_object = tk.Scrollbar(frTable, orient="vertical")
            scrollbar_object.pack(side='right', fill='y')
            scrollbar_object.config(command=trLoko.yview)
            trLoko.configure(yscrollcommand=scrollbar_object.set)
            trLoko.pack(fill='both',expand=1)
            frTable.pack(fill='both',expand=1)
            frLoko.grid(row=0, column=0,sticky='nsew')

            df = pd.read_sql_query("SELECT * FROM LOKO", cnx)
            setTreeData(trLoko,df,loks)
        # +++++++++++++++
            fr2 = ttk.Frame(frLoko,borderwidth=1, relief='solid',# padding=[8, 10],
                        style= 'Fr2.TFrame')
            # текстовые переменные для Entry
            loko_type,_ = add_combobox(fr2,0,0,"Тип локомотива",
                                       loks ,hlp('loko_types'))
            loko_name,_ = add_entry(fr2,0,[1,2],"Модель локомотива",hlp('loko_name'))
            loko_desc,_ = add_entry(fr2,1,[0,2],"Описание модели",hlp('loko_desc'))
            loko_massa,_ = add_entry(fr2,2,0,"Вес локомотива, тонн",hlp('loko_massa'))
            loko_axles,_ = add_entry(fr2,2,1,"Количество осей, шт", hlp('loko_axles'))
            loko_force,_ = add_entry(fr2,3,0,"Тормозное усилие, тонн",hlp('loko_force'))
            loko_pads,_ = add_combobox(fr2,3,1,"Тип колодок",
                                       pads ,hlp('loko_pads'))
            loko_url,_ = add_entry(fr2,'4',[0,2],"URL описания",hlp('loko_url'))
            def get_loks():
                return pd.DataFrame([[loko_name.get(),loko_type.current(),float(loko_force.get()),
                                      loko_pads.current(),int(loko_axles.get()),
                                      float(loko_massa.get()),loko_desc.get(),quote(loko_url.get())]],
        				  columns=['name','type','force','pads','axles','weight','desc','URL'])
            def sel_loko(event):
                idx =trLoko.selection()[0]
                idx =int(idx[1:],16)-1
                loko_type.current(df.at[idx,'type'])
                loko_name.set(df.at[idx,'name'])
                loko_desc.set(df.at[idx,'desc'])
                loko_massa.set(df.at[idx,'weight'])
                loko_axles.set(df.at[idx,'axles'])
                loko_force.set(df.at[idx,'force'])
                loko_pads.current(df.at[idx,'pads'])
                loko_url.set(unquote(df.at[idx,'URL']))
            trLoko.bind("<<TreeviewSelect>>", sel_loko)
            fr2.pack(fill = 'x')
            fr_but = ttk.Frame(frLoko,borderwidth=1, relief='solid',style='Fr1.TFrame')
            btLoko = ttk.Button(fr_but, text="Обновить",style="My.TButton",
                                command = lambda pn=1,df=df,tree = trLoko, g = get_loks : updRec(pn,df,tree,g))
            btLoko.grid(row=0, column=0,padx=20,pady=10)
            btVagon = ttk.Button(fr_but, text="Добавить",style="My.TButton",
                                 command = lambda pn=1,df=df,tree = trLoko, g = get_loks : addRec(pn,df,tree,g))
            btVagon.grid(row=0, column=1,padx=20,pady=10)
            btRez = ttk.Button(fr_but, text="Удалить",style="My.TButton",
                               command = lambda pn=1,df=df,tree = trLoko, g = get_loks : delRec(pn,df,tree,g))
            btRez.grid(row=0, column=2,padx=20,pady=10)
            for i in range(3): fr_but.columnconfigure(i, weight=1)
            fr_but.pack(fill='x')
            return frLoko


        # панель с данными для вагонов
        def createPanelVagon():
            cols = ['id','typeVagon','nameVagon']
            frVagon = ttk.Frame(frMain,borderwidth=1, relief='solid',)# padding=[8, 10],
            tk.Label(frVagon, text='Таблица вагонов', relief='flat',
                             font=('Arial','12','italic'), fg='yellow', bg = 'blue').pack(fill='x')
            frTable= ttk.Frame(frVagon,borderwidth=1, relief='solid',)
            trVagon = ttk.Treeview(frTable, columns=cols, show="headings", style="mystyle.Treeview",)
            trVagon.tag_configure('gr0', background='lightcyan')
            trVagon.column("#0", width=0,  stretch=tk.NO)
            trVagon.heading('#1', text='id')
            trVagon.column(cols[0], anchor="center", width=50, minwidth=10, stretch=tk.NO)
            trVagon.heading('#2', text='Тип вагона')
            trVagon.column(cols[1], anchor="center", width=140, minwidth=70, stretch=tk.NO)
            trVagon.heading('#3', text='Модель вагона')
            trVagon.column(cols[2], anchor="w", width=40, minwidth=40, stretch=tk.YES)
            trVagon.config(height=3)
            scrollbar_object = tk.Scrollbar(frTable, orient="vertical")
            scrollbar_object.pack(side='right', fill='y')
            scrollbar_object.config(command=trVagon.yview)
            trVagon.configure(yscrollcommand=scrollbar_object.set)
            trVagon.pack(fill='both',expand=1)
            frTable.pack(fill='both',expand=1)
            frVagon.grid(row=0, column=0,sticky='nsew')

            dfv = pd.read_sql_query("SELECT * FROM VAGON", cnx)
            setTreeData(trVagon, dfv, vags)
        # +++++++++++++++
            fr2 = ttk.Frame(frVagon,borderwidth=1, relief='solid',# padding=[8, 10],
                        style= 'Fr2.TFrame')

            # текстовые переменные для Entry
            vag_name,_ = add_entry(fr2,0,[0,2],"Модель вагона")
            vag_type,_ = add_combobox(fr2,1,0,"Тип вагона", vags)
            vag_force,_ = add_entry(fr2,1,1,"Тормозное усилие, тонн")
            def get_vals():
                return pd.DataFrame([[vag_name.get(),vag_type.current(),float(vag_force.get())]],
        				  columns=['name','type','force'])
            def sel_vagon(event):
                sel = trVagon.selection()
                if len(sel)==0:
                    return
                idx =sel[0]
                idx =int(idx[1:],16)-1
                vag_name.set(dfv.at[idx,'name'])
                vag_type.current(dfv.at[idx,'type'])
                vag_force.set(dfv.at[idx,'force'])
            trVagon.bind("<<TreeviewSelect>>", sel_vagon)
            fr2.pack(fill = 'x')
            fr_but = ttk.Frame(frVagon,borderwidth=1, relief='solid',style='Fr1.TFrame')# padding=[8, 10],
            btChangeVagon = ttk.Button(fr_but, text="Обновить",style="My.TButton",
                    command = lambda pn=2,df=dfv,tree = trVagon, g = get_vals : updRec(pn,df,tree,g))
            btChangeVagon.grid(row=0, column=0,padx=20,pady=10)
            btAddVagon = ttk.Button(fr_but, text="Добавить", style="My.TButton",
                    command = lambda pn=2,df=dfv,tree = trVagon, g = get_vals : addRec(pn,df,tree,g))
            btAddVagon.grid(row=0, column=1,padx=20,pady=10)
            btRemVagon = ttk.Button(fr_but, text="Удалить", style="My.TButton",
                    command = lambda pn=2,df=dfv,tree = trVagon, g = get_vals : delRec(pn,df,tree,g))
            btRemVagon.grid(row=0, column=2,padx=20,pady=10)
            for i in range(3): fr_but.columnconfigure(i, weight=1)
            fr_but.pack(fill='x')
            return frVagon

        pnLoko = createPanelLoko()
        pnVagon = createPanelVagon()

        # переключение панелей
        def toggle_panel(b,fun):
            btLoko['state'] = tk.NORMAL
            btVagon['state'] = tk.NORMAL
            b['state'] = tk.DISABLED
            fun()
        toggle_panel(btLoko, pnLoko.tkraise)
        btLoko.config(command = lambda b=btLoko,f=pnLoko.tkraise: toggle_panel(b,f))
        btVagon.config(command = lambda b=btVagon,f=pnVagon.tkraise: toggle_panel(b,f))

        # при запуске из главной программы работаем в режиме модального окна
        if parent:
            tkBase.transient(parent)
            tkBase.grab_set()
            tkBase.focus_set()
            tkBase.wait_window(parent)
        else:
            tkBase.mainloop()
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
if __name__ == "__main__":
    pass