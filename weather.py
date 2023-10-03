from tkinter import *
import tkinter as tk
from functools import partial
from geopy.geocoders import Nominatim
from tkinter import ttk, messagebox
from timezonefinder import TimezoneFinder
from datetime import datetime
import requests
import pytz
from lunarcalendar import Converter, Solar, Lunar, DateNotExist
from googletrans import Translator
import time
from pathlib import Path
from configparser import ConfigParser

root = Tk()
root.title("Weather App")
root.geometry("900x500+300+200")
root.resizable(False,False)

global load, long,lati, update, counter
global LOCATION, WEATHERAPI, ROOT_PATH
load = False
update = False

def loadConfig():
    global LOCATION, WEATHERAPI, ROOT_PATH
    parser = ConfigParser()
    ROOT_PATH = Path(__file__).parent / 'config.ini'
    print(ROOT_PATH)
    parser.read(ROOT_PATH)
    LOCATION = parser.get('config', 'location') 
    WEATHERAPI = parser.get('config', 'WeatherApi')


def enter(event1):
    global load, LOCATION
    # print (event1.char)
    # print (event1)
    if load == False and event1.keysym == "Return":
        LOCATION=textfield.get()
        print("save")
        load = True
        getWeather(LOCATION)
        save_ini('config', 'location', LOCATION)

def key(event):
    print("key:", event.char)
    


from threading import Thread, Lock
global start
start = True



def polling_thread():
    """Modbus polling thread."""
    global update, LOCATION , start, once
    once = True
    counters = 0
    # polling loop
    while True:
        if start:
            start = False
            loadConfig()
            getWeather(LOCATION)

        if once:
            once = False 
            print("updated :", update)
        counters = counters + 1
        if counters > 60 and load == False:
            counters = 0
            try:
                print("Load")
                getWeather(LOCATION)
            except KeyError:
                print("error: " , KeyError)
        if update:
            obj = TimezoneFinder()
            results = obj.timezone_at(lng=long, lat=lati)
            # print(results)
            home = pytz.timezone(results)
            local_time = datetime.now(home)
            current_time = local_time.strftime("%I:%M %p")
            clock.config(text=current_time)
            current_date = local_time.strftime("%d/%m/%Y")
            date.config(text=current_date)
            name.config(text="In " + LOCATION)
            solar = Solar(int(local_time.strftime("%Y")), int(local_time.strftime("%m")), int(local_time.strftime("%d")))
            lunar = Converter.Solar2Lunar(solar)
            lunardate.config(text="Lunar: " + str(lunar.day) + "/" + str(lunar.month) + "/" + str(lunar.year))
            # print("updated time")
        time.sleep(1)
        

t = Thread(target=polling_thread)
# t.setDaemon(True)
t.start()

def save_ini(tab, pos, value):
    global ROOT_PATH
    # Config file
    parser = ConfigParser()
    parser.read(ROOT_PATH)
    # Set the color change
    parser.set(tab, pos, value)
    # Save the config file
    with open(ROOT_PATH, 'w') as configfile:
        parser.write(configfile)

def getWeather(locations):
    global load, long, lati, update
    if locations is None:
        city=textfield.get()
    else:city=locations
    loadConfig()
    # geolocator = Nominatim(user_agent="geoapiExercises")
    # geocode = partial(geolocator.geocode, language="en")
    # print("geolocator",geocode(city, timeout=10, exactly_one=False))
    # location = geolocator.geocode(city)
    # print("local",location.raw)


    #weather api
    api = "https://api.openweathermap.org/data/2.5/weather?q="+city+"&appid=" + WEATHERAPI
    json_data = requests.get(api).json()
    # print(json_data)
    condition = json_data['weather'][0]['main']
    description = json_data['weather'][0]['description']
    temp = int(json_data['main']['temp']-273.15)
    temp_feels = int(json_data['main']['feels_like']-273.15)
    pressure = json_data['main']['pressure']
    humidity = json_data['main']['humidity']
    wind = json_data['wind']['speed']               
    # print(json_data['coord']['lon'])
    # print(json_data['weather'][0]['main'])
    
    t.config(text=(temp,"°C"))
    c.config(text=(condition,"|","FEELS","LIKE",temp_feels,"°C"))
    d.config(text=description)
    w.config(text=(wind , "m/s"))
    h.config(text=(humidity , "%"))
    p.config(text=pressure)
    obj = TimezoneFinder()
    long = json_data['coord']['lon']
    lati = json_data['coord']['lat']
    results = obj.timezone_at(lng=long, lat=lati)
    # print(results)
    home = pytz.timezone(results)
    local_time = datetime.now(home)
    current_time = local_time.strftime("%I:%M %p")
    clock.config(text=current_time)
    current_date = local_time.strftime("%d/%m/%Y")
    date.config(text=current_date)
    name.config(text="In " + LOCATION)
    solar = Solar(int(local_time.strftime("%Y")), int(local_time.strftime("%m")), int(local_time.strftime("%d")))
    lunar = Converter.Solar2Lunar(solar)
    lunardate.config(text="Lunar: " + str(lunar.day) + "/" + str(lunar.month) + "/" + str(lunar.year))
    print("Load Done")
    load = False
    update = True


#search box
Search_image = PhotoImage(file="Weatherapp/search.png")
myimage = Label(image=Search_image)
myimage.place(x=20,y=20)

textfield = tk.Entry(root, justify="center", width=17, font=("poppins",25,"bold"),bg="#101010",border=0,borderwidth=0,fg="white")
textfield.place(x=50,y=40)
textfield.focus()


Search_icon = PhotoImage(file="Weatherapp/search_icon1.png")
myimage_icon = Button(image=Search_icon, borderwidth=0,cursor="hand2",bg="#101010",command=getWeather)
# myimage_icon.place(x=450,y=34)

# logo
Logo_image = PhotoImage(file="Weatherapp/logo.png")
logo=Label(image=Logo_image)
logo.place(x=150,y=100)

#bottom box
Frame_image =PhotoImage(file="Weatherapp/box.png")
frame_myimage = Label(image=Frame_image)
frame_myimage.pack(padx=5,pady=5,side=BOTTOM)

#time
name=Label(root,font=("arial",20,"bold"),justify="center", fg="#e89f3f")
name.place(x=400,y=120)
clock=Label(root,font=("Helvetica",20))
clock.place(x=30,y=130)

date=Label(root,font=("Helvetica",15))
date.place(x=30,y=165)

lunardate=Label(root,font=("Helvetica",15))
lunardate.place(x=30,y=185)

color_tray = "#0b9ed4"
#lable
lablel1 = Label(root,text="WIND",font=("Helvetica",15,"bold"),bg=color_tray)
lablel1.place(x=120,y=400)

lablel2 = Label(root,text="HUMIDITY",font=("Helvetica",15,"bold"),bg=color_tray)
lablel2.place(x=250,y=400)


lablel3 = Label(root,text="DESCRIPTION",font=("Helvetica",15,"bold"),bg=color_tray)
lablel3.place(x=430,y=400)

lablel4 = Label(root,text="PRESSURE",font=("Helvetica",15,"bold"),bg=color_tray)
lablel4.place(x=650,y=400)


t=Label(font=("arial",70,"bold"),fg="#ee666d")
t.place(x=400,y=150)
c=Label(font=("arial",15,"bold"))
c.place(x=400,y=250)

w=Label(text="...",font=("arial",20,"bold"),fg="#000000",bg=color_tray)
w.place(x=120,y=430)

h=Label(text="...",font=("arial",20,"bold"),fg="#000000",bg=color_tray)
h.place(x=250,y=430)

d=Label(text="...",font=("arial",20,"bold"),fg="#000000",bg=color_tray)
d.place(x=420,y=430)

p=Label(text="...",font=("arial",20,"bold"),fg="#000000",bg=color_tray)
p.place(x=670,y=430)


root.bind("<Key>", enter)
    # root.bind("<key>", key)

root.mainloop()