import json
from tkinter import StringVar, Toplevel, HORIZONTAL, Tk
from tkinter.ttk import Style, Button, Label, Entry, Frame, PanedWindow

# import fontawesome as fa

# app_values
# Представляет собой словарь ключом которого является id  формы
# Значение представляет собой список form(ОписаниеФормы), design(Описание дизайна), Данные
#   Описание формы:  title, icon, tip, buttons
#   Описание дизайна: Форма состоит из  Блоков(menu, tool, main(left, center, right), status).
#       Каждый блок состоит из списка элементов дизайна - Части part->(block : part ).
#          Каждая Часть состоит из Части или Элементов дизайна  elem->(part : (value, tip(part, block, elem))).
#   Данные и Элементы тесно связаны data -> (elem  : (old, new))
#  formID : form(стуктура) , block(словарь), part(словарь), data(словарь)
from Table import table

app_values = {}


# key - вызываемая функция,  data - данные хранящие параметры для функции
def send_message(key, data):
    # Получим список параметров
    parm = data[key]["Param"].split(',')
    # Подготовим структуру для отправки
    # Action - функция, Sender - объект который содержит эту функцию
    # data['id'] - id  формы отправителя
    mes = {'Action': key, "Sender": data['id'], }
    pp = {}
    if parm[0] != '':
        for p in parm:
            pp[p] = data[p]['GuiValue'].get()
    # pp - параметры со значениями
    mes['parameters'] = pp
    ws = app_values['ws']
    ws.send(json.dumps(mes, indent=4))


# Создаем(помещаем) tool_bar  в указанном блоке(frame) - fr
# but  - описание кнопок
# data - словарь с данными
def gen_but(but, fr, data, side='right'):
    for bt in but:
        #  Сохраним параметры для функции
        if bt["Name"] in data:
            w = data[bt["Name"]]['tk']
        else:
            w = Button(fr, text=bt["Title"], command=lambda m=bt["Name"], d=data: send_message(m, d))
        data[bt["Name"]] = {"Param": bt["Param"], "tk": w}
        w.pack(side=side)


def gen_fields(fields, fr, nom_str, col, data):
    Label(fr, text=fields["Title"]).grid(row=nom_str, column=col)
    if fields["Name"] not in data:
        v1 = StringVar()
        data[fields["Name"]] = {"Title": fields["Title"], "Value": fields["Value"], "GuiValue": v1, }
        Entry(fr, text=fields["Value"], textvariable=data[fields["Name"]]["GuiValue"]).grid(row=nom_str, column=col + 1)


def create_frame(parent, width):
    bar = Frame(parent, width=width)
    bar['borderwidth'] = 5
    bar['relief'] = 'groove'
    parent.add(bar)
    return bar


def delete_frames(id_form):
    block = app_values[id_form]["frame"]
    if len(block) > 0:
        for fr in block:
            block[fr].forget()
    # del block[fr]
    # app_values[id_form] = copy.deepcopy(app_values[id_form])


def update_data(id_form, form_data):
    form = app_values[id_form]
    block = app_values[id_form]["frame"]
    data = app_values[id_form]["data"]
    root = form['form'].root
    root.title(json.loads(form_data["Body"])['Title'])
    nom_str = 0
    for el in form_data["Child"]:

        if el["Name"].startswith("tool"):
            if "tool_bar" in block:
                tool_bar = block["tool_bar"]
            else:
                tool_bar = Frame(root)
                block["tool_bar"] = tool_bar
                tool_bar.pack(side="top", fill="x")
            gen_but(json.loads(el["Body"]), tool_bar, data)
        if el["Name"].startswith("fields"):
            if "main_bar" in block:
                main_bar = block["main_bar"]
            else:
                main_bar = PanedWindow(root, orient=HORIZONTAL)
                main_bar.pack(fill="both", expand=True)
                block["main_bar"] = main_bar
                main_bar.pack()
            fields = json.loads(el["Body"])
            col = 0
            for str_f in fields:
                gen_fields(str_f, main_bar, nom_str, col, data)
                col = col + 2
            nom_str = nom_str + 1
        if el["Name"].startswith("table"):
            table(form['form'].root, json.loads(el["Body"]))

class ChildWindow:
    def __init__(self, parent, form_data, width, height, id_form, icon=None):
        self.style = Style()
        self.style.theme_use("default")
        self.style.configure("my.TFrame", borderwidth=5, relief='flat')
        self.id_form = id_form
        app_values[id_form] = {"form": self, "data": {}, "frame": {}, }
        data = app_values[id_form]["data"]
        data["id"] = id_form

        self.root = Toplevel(parent)
        self.root.geometry(f"{width}x{height}+200+200")

        if icon:
            self.root.iconbitmap(icon)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        update_data(id_form, form_data)
        self.root.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.grab_focus()

    def grab_focus(self):
        self.root.grab_set()
        # self.root.focus_set()
        # self.root.wait_window()

    def on_closing(self):
        del app_values[self.id_form]
        self.root.destroy()

    # def confirm_delete(self):
    #     message = "Вы уверены, что хотите закрыть это окно?"
    #     if askyesno(message=message, parent=self):
    #         del app_values[self.id_form]
    #         self.close()


class App:
    def __init__(self, width, height, title="MyWindow", icon=None):
        self.root = Tk()
        self.root.title(title)

        v1 = StringVar().set(title)
        app_values["main"] = {"form": self, "title": v1, "data": {}, "frame": {}, }
        if icon:
            self.root.iconbitmap(icon)

    def run(self):
        self.root.mainloop()

    def create_child(self, data, width, height, id_form, icon=None):
        ChildWindow(self.root, data, width, height, id_form, icon)
