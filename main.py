import json
import sys
from tkinter import Text, END, BOTH
from tkinter.ttk import Button, Frame

import fontawesome as fa
import websocket

from generate_form import app_values, App, update_data


def on_message(ws, message):
    form_data = json.loads(message)
    id_form = json.loads(form_data["Body"])["ID"]
    if id_form in app_values.keys():
        update_data(id_form, form_data)
    else:
        window.create_child(form_data, 300, 300, id_form)

    # message_entry.insert(END, form_data)
    for ic in fa.icons:
        message_entry.insert(END, "\n" + ic + "   " + fa.icons[ic])
    # print(message)


def on_error(ws, error):
    # app_values["main"]['data']["connect_main"]['tk']['text'] = fa.icons["hands"]
    print(error)


def send_message(ws, message):
    ws.send(app_values[message])


def connection():
    websocket.enableTrace(True)
    if len(sys.argv) < 2:
        host = "ws://127.0.0.1:8080/telephon"
    else:
        host = sys.argv[1]
    ws = websocket.WebSocketApp(host,
                                on_message=on_message,
                                on_error=on_error)
    ws.on_open = on_open
    app_values['ws'] = ws
    app_values["main"]['data']["connect_main"]['tk']['text'] = fa.icons["handshake"]
    app_values["main"]['id'] = "main"
    app_values["main"]['data']['id'] = "main"
    ws.run_forever()

    return


def on_open(ws):
    d = {"Action": "login", "Parameters": "", }
    ws.send(json.dumps(d))


def on_connect():
    import threading
    t = threading.Thread(target=connection)
    t.start()


if __name__ == "__main__":
    window = App(500, 500, "Telephone")

    tool = Frame(window.root)
    b = Button(tool, text=fa.icons["thumbs-up"], command=on_connect, width=4)
    b.pack(side="right")
    tool.pack(side="bottom", fill=BOTH)

    app_values["main"]['data']["connect_main"] = {"Param": "login", "tk": b}
    app_values["main"]['frame']["test"] = tool

    message_entry = Text(window.root)
    app_values["main"]['frame']["message_entry"] = message_entry

    message_entry.pack(side="bottom")

    window.run()
