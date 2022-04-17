
import sqlite3
import requests
import tkinter as tk
from tkinter import ttk
import datetime
from datetime import datetime
from PIL import Image, ImageTk
from colors import pickColor


class WeatherWithAccuweather(tk.Tk):
    def __init__(self):
        super().__init__()
        self.APIkey = 'your API key goes here'
        # initial geometry----------------------------------------------------------------------------------------------
        self.title('Weather forecasts')
        self.attributes('-zoomed', True) # full screen
        self.state('normal')
        self.resizable(width=True, height=True)
        self.config(background='antique white')
        # variables-----------------------------------------------------------------------------------------------------
        self.timeNow = tk.StringVar()
        self.dateNow = tk.StringVar()
        self.city = tk.StringVar()
        self.forecastType = tk.StringVar()
        self.forecastType.set('12-hour')
        self.selectedCity = tk.StringVar()
        # call counter variables----------------------------------------------------------------------------------------
        self.calls = tk.IntVar()
        # canvas for input----------------------------------------------------------------------------------------------
        canvasInput = tk.Canvas(self, highlightthickness=0, background='antique white')
        canvasInput.pack(side='left', anchor='nw', padx=10, pady=10)
        # canvas for date and calls-------------------------------------------------------------------------------------
        canvasDateCalls = tk.Canvas(canvasInput, highlightthickness=0, background='antique white')
        canvasDateCalls.pack(anchor='nw', padx=10, pady=10)
        # canvas type of forecast & city--------------------------------------------------------------------------------
        canvasTypeForecastCity = tk.Canvas(canvasInput, highlightthickness=0, background='antique white')
        canvasTypeForecastCity.pack(anchor='nw', padx=10, pady=10)
        # canvas for the acknowledgements-------------------------------------------------------------------------------
        canvasAcknowledgement = tk.Canvas(canvasInput, highlightthickness=0, background='antique white')
        canvasAcknowledgement.pack(anchor='nw', padx=10, pady=10)
        # canvas for all types of forecast------------------------------------------------------------------------------
        self.canvasAnswer = tk.Canvas(self, highlightthickness=0, background='antique white')
        self.canvasAnswer.pack(side='left', anchor='ne', padx=10, pady=10, fill='both')
        self.canvasForecast = tk.Canvas(self.canvasAnswer, highlightthickness=0, width=1000, height=600,
                                        background='antique white')
        self.canvasForecast.pack(side='left', fill='both', expand=True)
        # date & time---------------------------------------------------------------------------------------------------
        timeNowLabel = tk.LabelFrame(canvasDateCalls, text='Today\'s date:', background='antique white')
        timeNowLabel.grid(column=0, row=0, padx=10, pady=5)
        dateShow = tk.Label(timeNowLabel, textvariable=self.dateNow, background='antique white')
        dateShow.pack(side='left', padx=10)
        timeShow = tk.Label(timeNowLabel, textvariable=self.timeNow, bg='white')
        timeShow.pack(side='right', padx=10)
        # calls---------------------------------------------------------------------------------------------------------
        callsLabel = tk.LabelFrame(canvasDateCalls, text='Daily calls', background='antique white')
        callsLabel.grid(column=1, row=0, padx=5, pady=5)
        callsShow = tk.Label(callsLabel, textvariable=self.calls, background='antique white')
        callsShow.pack()
        # type of forecast----------------------------------------------------------------------------------------------
        choiceOfForecast = tk.LabelFrame(canvasTypeForecastCity, text='Select your type of forecast:',
                                         background='antique white')
        choiceOfForecast.grid(column=0, row=2, sticky='nsew', padx=10, pady=5)
        current_conditions = tk.Radiobutton(choiceOfForecast, text='Current', variable=self.forecastType,
                                            value='Current conditions', indicatoron=0)
        current_conditions.pack(side='left', padx=5, pady=5)

        twelve_hours = tk.Radiobutton(choiceOfForecast, text='12-hour', variable=self.forecastType,
                                      value='12-hour', indicatoron=0)
        twelve_hours.pack(side='left', padx=5, pady=5)

        five_day = tk.Radiobutton(choiceOfForecast, text='5-day', variable=self.forecastType,
                                  value='5-day', indicatoron=0)
        five_day.pack(side='left', padx=5, pady=5)
        # city autocomplete---------------------------------------------------------------------------------------------
        choiceOfCity = tk.LabelFrame(canvasTypeForecastCity, text='Find your city:', background='antique white')
        choiceOfCity.grid(column=0, row=3, sticky='nsew', padx=10, pady=5)
        cityEntry = tk.Entry(choiceOfCity, width=28, textvariable=self.city, background='antique white')
        cityEntry.bind("<Return>", self.autoComplete)
        cityEntry.grid(column=0, row=0, sticky='w')

        cityEntry.focus()

        pickYourCity = tk.Label(choiceOfCity, text='Select your city:', background='antique white')
        pickYourCity.grid(column=0, row=1, sticky='w')
        self.listboxCity = tk.Listbox(choiceOfCity, width=40, selectmode='single', height=5, background='antique white')
        self.listboxCity.grid(column=0, row=2)
        self.listboxCity.bind("<<ListboxSelect>>", self.selection)
        # date stuff----------------------------------------------------------------------------------------------------
        today = datetime.utcnow()
        self.todayDate = today.strftime('%d %m %Y')
        self.dateNow.set(today.strftime('%d/%m/%Y'))
        self.timeNow.set(today.strftime('%H:%M'))
        # db stuff------------------------------------------------------------------------------------------------------
        self.connexion = sqlite3.connect('call_counter.db')
        self.cur = self.connexion.cursor()
        cmd = "SELECT DATE, CALLS from call_counter WHERE DATE=" + '"' + self.todayDate + '"'
        self.cur.execute(cmd)
        data = self.cur.fetchall()
        if not data:
            newRow = "INSERT INTO call_counter (DATE, CALLS) VALUES(" + '"' + self.todayDate + '"' + ',' + '0' + ')'
            self.cur.execute(newRow)
            self.connexion.commit()
            self.calls.set(0)
            self.count = 0
        else:
            fullList = []
            for row in data:
                fullList.append(row)
            self.count = fullList[0][1]
            self.calls.set(self.count)
        # acknowledgements----------------------------------------------------------------------------------------------
        acknowledgementLabel = tk.Label(canvasAcknowledgement, text='Weather data graciously provided by:',
                                        background='antique white')
        acknowledgementLabel.pack(anchor='center', padx=10, pady=5)
        self.accuPic = ImageTk.PhotoImage(Image.open('AW_Stack_RGB_resized.png'))
        self.accuPic.image = self.accuPic  # must use 'self' to prevent garbage collection
        accuPicx = tk.Canvas(canvasAcknowledgement, height=153, width=169)
        accuPicx.pack(anchor='center', padx=5, pady=5)
        accuPicx.create_image((169 // 2, 153 // 2), image=self.accuPic.image, anchor='center')
        # stuff for labels----------------------------------------------------------------------------------------------
        self.labels = ['forecast +1 hour', 'forecast +2 hours', 'forecast +3 hours', 'forecast +4 hours',
                       'forecast +5 hours', 'forecast +6 hours', 'forecast +7 hours', 'forecast +8 hours',
                       'forecast +9 hours', 'forecast +10 hours', 'forecast +11 hours', 'forecast +12 hours']
        self.weatherStuff = ['date', 'temp', 'feels', 'wind', 'cloud', 'rain', 'humidity']

    def createLabels12Hours(self, forecast12):
        for child in self.canvasForecast.winfo_children():  # erases the canvas in case of update
            child.destroy()
        i = 1  # numbers the different items of a labelFrame (temp, feel, ...)
        col = 0  # numbers the column placing of the different items of a labelFrame (temp, feel, ...)
        row = 0  # row number for the labelFrame, updated automatically with the column number
        countLabelFrame = 0  # counts the number of vertical LabelFrames to split them in several columns
        j = 0  # row reference for the placing of the LabelFrames
        k = 0  # row reference for the placing of the LabelFrames
        rowXLabel = 1  # row reference for the placing of the Labels
        rowdataLabel = 2  # row reference for the placing of the Labels displaying data
        count = 0
        for e in range(12):  # creates the LabelFrames length hardcoded because of dictionary's structure
            keyDate = 'date' + str(e + 1)
            xFrame = tk.LabelFrame(self.canvasForecast, text=forecast12.get(keyDate))
            countLabelFrame += 1
            if countLabelFrame <= 4:  # first column
                xFrame.grid(column=0, row=row, padx=5, pady=5)
                row += 1
            elif 4 < countLabelFrame <= 8:  # second column
                xFrame.grid(column=1, row=j, padx=5, pady=5)
                j += 1
            elif countLabelFrame > 8:  # third column
                xFrame.grid(column=2, row=k, padx=5, pady=5)
                k += 1

            canvasForecastDetails = tk.Canvas(xFrame)
            canvasForecastDetails.grid(column=0, row=0)

            for w in self.weatherStuff:  # creates the Labels and puts them in the canvas
                if w == 'date':
                    pass
                else:
                    xLabel = tk.Label(canvasForecastDetails, text=w, width=8)
                    xLabel.grid(column=col, row=rowXLabel, sticky='nsew')
                    key = w + str(i)
                    dataLabel = tk.Label(canvasForecastDetails, text=forecast12.get(key), width=8)
                    dataLabel.grid(column=col, row=rowdataLabel, sticky='nsew')
                    if count < 2:
                        sv1 = ttk.Separator(canvasForecastDetails, orient='vertical')
                        sv1.grid(column=col + 1, row=0, rowspan=3, sticky='ns')
                        count += 1
                        rowXLabel = 1
                        rowdataLabel = 2
                        col += 2
                    elif count == 2:  # resets the column number to 0 for the next LabelFrame
                        count += 1
                        col = 0
                        rowXLabel = 4
                        rowdataLabel = 5
                        sh1 = ttk.Separator(canvasForecastDetails, orient='horizontal')
                        sh1.grid(column=0, row=0, columnspan=6, sticky='ew')
                        sh2 = ttk.Separator(canvasForecastDetails, orient='horizontal')
                        sh2.grid(column=0, row=3, columnspan=6, sticky='ew')
                    elif count == 3:  # resets the column number to 0 for the next LabelFrame
                        sv2 = ttk.Separator(canvasForecastDetails, orient='vertical')
                        sv2.grid(column=col + 1, row=3, rowspan=3, sticky='ns')
                        count += 1
                        col = 2
                        rowXLabel = 4
                        rowdataLabel = 5
                    elif count == 4:  # resets the column number to 0 for the next LabelFrame
                        sv3 = ttk.Separator(canvasForecastDetails, orient='vertical')
                        sv3.grid(column=col + 1, row=3, rowspan=3, sticky='ns')
                        count += 1
                        col = 4
                        rowXLabel = 4
                        rowdataLabel = 5
                        sh3 = ttk.Separator(canvasForecastDetails)
                        sh3.grid(column=0, row=6, columnspan=6, sticky='ew')
                    else:
                        count = 0
                        col = 0
                        rowXLabel = 1
                        rowdataLabel = 2
            i += 1

        c = 0
        for child in self.canvasForecast.winfo_children():  # creates the canvas to support the icons
            path = self.pathList[c]
            canvasForIcon = tk.Canvas(child)
            canvasForIcon.grid(column=0, row=8)
            iconPlace = tk.Canvas(canvasForIcon, width=50, height=50, bg='white')
            iconPlace.grid(column=0, row=0)
            iconPlace.create_image(25, 25, image=self.getIcon(path))
            labelPlace = tk.Canvas(canvasForIcon)
            labelPlace.grid(column=1, row=0)
            iconPhraseLabel = tk.Label(labelPlace, wraplength=250, justify='left',
                                       text=forecast12.get('iconPhrase' + str(c + 1)))
            iconPhraseLabel.grid(column=0, row=0)
            c += 1

    def createLabels5Days(self, forecast):
        listOfLabels = forecast.get('List of stuff to create')
        for child in self.canvasForecast.winfo_children():  # erases the canvas in case of update
            child.destroy()
        rowXLabel = 0  # row reference for the placing of the Labels
        rowdataLabel = 1  # row reference for the placing of the Labels displaying data
        rowXLabelDN = 0  # row reference for the placing of the Labels Day/Night
        rowdataLabelDN = 0  # row reference for the placing of the Labels displaying data Day/Night
        row = 0  # for LabelFrame place in main canvas
        col = 0  # for placement of temperature data
        col2 = 0  # for placement of temperature data
        count = 0  # for placement of temperature data
        day = 0
        night = 0
        d = 0
        n = 0

        for w in listOfLabels:  # creates the Labels and puts them in the canvas
            if w[:-1] == 'dateConcerned':
                xFrame = tk.LabelFrame(self.canvasForecast, text=forecast.get(w), foreground=pickColor(),
                                       background='white')
                xFrame.pack(fill='x', pady=2)

                row += 1

                canvasForecastDetails = tk.Canvas(xFrame)
                canvasForecastDetails.pack(fill='x')

                canvasTemperatures = ttk.LabelFrame(canvasForecastDetails, text='Temperatures:')
                canvasTemperatures.grid(column=0, row=0, sticky='nsew', padx=10, pady=8)

                separatorVertical = ttk.Separator(canvasTemperatures, orient='vertical')
                separatorVertical.grid(column=1, row=0, sticky='ns', rowspan=5)
                separatorHorizontal = ttk.Separator(canvasTemperatures, orient='horizontal')
                separatorHorizontal.grid(column=0, row=2, sticky='ew', columnspan=4)

                canvasDay = tk.Canvas(canvasForecastDetails)
                canvasDay.grid(column=1, row=0, sticky='nsew', padx=10, pady=8)

                dayFrame = ttk.LabelFrame(canvasDay, text='Day:', width=80)
                dayFrame.grid(column=0, row=0, sticky='nsew')

                canvasNight = tk.Canvas(canvasForecastDetails)
                canvasNight.grid(column=2, row=0, sticky='nsew', padx=10, pady=3)

                nightFrame = ttk.LabelFrame(canvasNight, text='Night:', width=80)
                nightFrame.grid(column=0, row=0, sticky='nsew')
            else:
                if 'Day' in w:
                    xLabel = ttk.Label(dayFrame, text=w.split(' ')[0])
                    xLabel.grid(column=0, row=rowXLabelDN, sticky='w')
                    dataLabel = ttk.Label(dayFrame, text=forecast.get(w))
                    dataLabel.grid(column=1, row=rowdataLabelDN, sticky='e')
                    rowXLabelDN += 1
                    rowdataLabelDN += 1
                    day += 1
                    if day == 3:
                        day = 0
                        pathDay = forecast.get('IconDay')[d]
                        canvasForIconDay = tk.Canvas(canvasDay, width=200)
                        canvasForIconDay.grid(column=3, row=0, sticky='nsew')
                        iconDay = self.getIcon(pathDay)
                        iconPlaceDay = tk.Canvas(canvasForIconDay, width=50, height=50, bg='white')
                        iconPlaceDay.grid(column=0, row=0)
                        iconPlaceDay.create_image(25, 25, image=iconDay)
                        iconPhraseLabelDay = tk.Label(canvasForIconDay, text=forecast.get('Comments Day')[d],
                                                      width=30, wraplength=200, justify='left')
                        iconPhraseLabelDay.grid(column=0, row=1, sticky='nsew')
                        d += 1
                elif 'Night' in w:
                    xLabel = ttk.Label(nightFrame, text=w.split(' ')[0])
                    xLabel.grid(column=0, row=rowXLabelDN, sticky='w')
                    dataLabel = ttk.Label(nightFrame, text=forecast.get(w))
                    dataLabel.grid(column=1, row=rowdataLabelDN, sticky='e')
                    rowXLabelDN += 1
                    rowdataLabelDN += 1
                    night += 1
                    if night == 3:
                        night = 0
                        pathNight = forecast.get('IconNight')[n]
                        canvasForIconNight = tk.Canvas(canvasNight, width=200)
                        canvasForIconNight.grid(column=4, row=0, sticky='nsew')
                        iconNight = self.getIcon(pathNight)
                        iconPlaceNight = tk.Canvas(canvasForIconNight, width=50, height=50, bg='white')
                        iconPlaceNight.grid(column=0, row=0)
                        iconPlaceNight.create_image(25, 25, image=iconNight)
                        iconPhraseLabelNight = tk.Label(canvasForIconNight, text=forecast.get('Comments Night')[n],
                                                        width=30, wraplength=200, justify='left')
                        iconPhraseLabelNight.grid(column=0, row=1, sticky='nsew')
                        n += 1

                else:  # temp & feel
                    if count < 2:
                        xLabel = tk.Label(canvasTemperatures, text=w[:-1])
                        xLabel.grid(column=col, row=rowXLabel, sticky='nsew')
                        dataLabel = tk.Label(canvasTemperatures, text=forecast.get(w))
                        dataLabel.grid(column=col, row=rowdataLabel, sticky='nsew')
                        col += 2
                        count += 1
                    else:
                        rowXLabel = 3
                        rowdataLabel = 4
                        xLabel = tk.Label(canvasTemperatures, text=w[:-1])
                        xLabel.grid(column=col2, row=rowXLabel, sticky='nsew')
                        dataLabel = tk.Label(canvasTemperatures, text=forecast.get(w))
                        dataLabel.grid(column=col2, row=rowdataLabel, sticky='nsew')
                        count += 1
                        col2 += 2
                        if count > 3:
                            count = 0
                            rowXLabel = 0
                            rowdataLabel = 1
                            col = 0
                            col2 = 0

    def createLabelsCurrent(self, current):
        for child in self.canvasForecast.winfo_children():  # erases the canvas in case of update
            child.destroy()

        xFrame = tk.LabelFrame(self.canvasForecast, text=current.get('dateConcerned'))
        xFrame.grid(column=0, row=0, padx=5, pady=5)

        description = ttk.Label(xFrame, text='Weather:')
        description.grid(column=0, row=0, sticky='w')
        descriptionValue = ttk.Label(xFrame, text=current.get('description'))
        descriptionValue.grid(column=0, row=0)

        temp = ttk.Label(xFrame, text='Temperature (°C):')
        temp.grid(column=0, row=1, sticky='w')
        tempValue = ttk.Label(xFrame, text=current.get('temp'))
        tempValue.grid(column=0, row=1)

        wind = ttk.Label(xFrame, text='Wind (km/h):')
        wind.grid(column=0, row=2, sticky='w')
        windValue = ttk.Label(xFrame, text=current.get('wind'))
        windValue.grid(column=0, row=2)

        realFeel = ttk.Label(xFrame, text='Real feel (°C):')
        realFeel.grid(column=0, row=3, sticky='w')
        realFeelValue = ttk.Label(xFrame, text=current.get('realFeel'))
        realFeelValue.grid(column=0, row=3)

        humidity = ttk.Label(xFrame, text='Humidity:')
        humidity.grid(column=0, row=4, sticky='w')
        humidityValue = ttk.Label(xFrame, text=current.get('humidity'))
        humidityValue.grid(column=0, row=4)

        precipitation = ttk.Label(xFrame, text='Precipitation:')
        precipitation.grid(column=0, row=5, sticky='w')
        precipitationValue = ttk.Label(xFrame, text=current.get('precipitation'))
        precipitationValue.grid(column=0, row=5)

        iconCurrent = self.getIcon(current.get('path'))
        canvas_for_icon = tk.Canvas(xFrame)
        canvas_for_icon.grid(column=0, row=6)
        canvas_for_icon.create_image(25, 25, image=iconCurrent)

    def autoComplete(self, event):
        url = 'http://dataservice.accuweather.com/locations/v1/cities/autocomplete?apikey=' + self.APIkey + "&q=" + self.city.get()
        response = requests.get(url).json()
        self.CallCounter()
        self.listboxCity.delete(0, 'end')  # clears the list in case of a previous call
        for child in self.canvasForecast.winfo_children():  # erases the canvas in case of update
            child.destroy()

        listOfCities = []
        self.citiesKeys = {}
        for e in range(len(response)):
            listOfCities.append(
                '{0}, {1}, {2}'.format(response[e].get('LocalizedName'), response[e].get('Country').get('LocalizedName'),
                                       response[e].get('AdministrativeArea').get('LocalizedName')))

        for e in range(len(response)):
            name = str(response[e].get('LocalizedName'))
            country = str(response[e].get('Country').get('LocalizedName'))
            area = str(response[e].get('AdministrativeArea').get('LocalizedName'))
            city = name + ', ' + country + ', ' + area
            self.citiesKeys.setdefault(city, response[e].get('Key'))
        for i in listOfCities:
            self.listboxCity.insert('end', i)

    def selection(self, event):  # identifies the element selected in ListBox
        caller = event.widget
        idx = caller.curselection()
        if not idx:  # to avoid error msg
            pass
        else:
            value = caller.get(idx)
            self.selectedCity.set(value)
            self.cityCode = self.citiesKeys.get(self.selectedCity.get())
            if self.forecastType.get() == '12-hour':
                self.createLabels12Hours(self.twelve_hours_forecast())
            elif self.forecastType.get() == '5-day':
                self.createLabels5Days(self.five_day_forecast())
            elif self.forecastType.get() == 'Current conditions':
                self.createLabelsCurrent(self.currentWeather())

    def twelve_hours_forecast(self):
        url12hours = 'http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/' + self.cityCode + '?apikey=' + \
                     self.APIkey + '&language=en&details=true&metric=true'
        forecast_12 = requests.get(url12hours).json()
        self.CallCounter()
        twelveHoursDic = {}
        self.pathList = []  # path to the icon

        for e in range(len(forecast_12)):
            dateConcerned = datetime.fromtimestamp(forecast_12[e].get('EpochDateTime')).strftime('%A %d/%m at %H:%M')
            temp12 = forecast_12[e].get('Temperature').get('Value')
            feelsLike12 = forecast_12[e].get('RealFeelTemperature').get('Value')
            windSpeed12 = forecast_12[e].get('Wind').get('Speed').get('Value')
            humidity12 = forecast_12[e].get('RelativeHumidity')
            rainProbability12 = forecast_12[e].get('PrecipitationProbability')
            cloud12 = forecast_12[e].get('CloudCover')
            icon12 = forecast_12[e].get('WeatherIcon')
            iconPhrase = forecast_12[e].get('IconPhrase')
            # update dictionary
            keyDate = 'date' + str(e + 1)
            keyTemp = 'temp' + str(e + 1)
            keyFeels = 'feels' + str(e + 1)
            keyWind = 'wind' + str(e + 1)
            keyCloud = 'cloud' + str(e + 1)
            keyRain = 'rain' + str(e + 1)
            keyHumid = 'humidity' + str(e + 1)
            keyPhrase = 'iconPhrase' + str(e + 1)
            twelveHoursDic[keyDate] = str(dateConcerned)
            twelveHoursDic[keyTemp] = str(temp12) + '°'
            twelveHoursDic[keyFeels] = str(feelsLike12) + '°'
            twelveHoursDic[keyWind] = str(windSpeed12) + 'km/h'
            twelveHoursDic[keyCloud] = str(cloud12) + '%'
            twelveHoursDic[keyRain] = str(rainProbability12) + '%'
            twelveHoursDic[keyHumid] = str(humidity12) + '%'
            twelveHoursDic[keyPhrase] = str(iconPhrase)

            icon = str(icon12)
            if len(icon) < 2:
                icon = '0' + icon
            path = "weather_icons/" + str(icon) + ".png"
            self.pathList.append(path)

        return twelveHoursDic

    def five_day_forecast(self):
        url_5_days = 'http://dataservice.accuweather.com/forecasts/v1/daily/5day/' + self.cityCode + '?apikey=' + \
                     self.APIkey + '&language=en&details=true&metric=true'
        forecast_5_days = requests.get(url_5_days).json()
        self.CallCounter()
        pathListDay = []  # path to the icon
        pathListNight = []  # path to the icon
        longPhraseDay = []
        longPhraseNight = []
        fiveDayDic = {}

        for e in range(len(forecast_5_days.get('DailyForecasts'))):
            # TEMPERATURES
            dateConcerned = datetime.fromtimestamp(forecast_5_days.get('DailyForecasts')[e].get('EpochDate')).strftime(
                '%A %d/%m at %H:%M')
            tempMini = forecast_5_days.get('DailyForecasts')[e].get('Temperature').get('Minimum').get('Value')
            tempMaxi = forecast_5_days.get('DailyForecasts')[e].get('Temperature').get('Maximum').get('Value')
            feelsLikeMini = forecast_5_days.get('DailyForecasts')[e].get('RealFeelTemperature').get('Minimum').get(
                'Value')
            feelsLikeMaxi = forecast_5_days.get('DailyForecasts')[e].get('RealFeelTemperature').get('Maximum').get(
                'Value')
            # DAY
            iconDayDic = forecast_5_days.get('DailyForecasts')[e].get('Day').get('Icon')
            rainProbabilityDay = forecast_5_days.get('DailyForecasts')[e].get('Day').get('PrecipitationProbability')
            windSpeedDay = forecast_5_days.get('DailyForecasts')[e].get('Day').get('Wind').get('Speed').get('Value')
            cloudDay = forecast_5_days.get('DailyForecasts')[e].get('Day').get('CloudCover')
            commentDay = forecast_5_days.get('DailyForecasts')[e].get('Day').get('LongPhrase')
            # NIGHT
            iconNightDic = forecast_5_days.get('DailyForecasts')[e].get('Night').get('Icon')
            rainProbabilityNight = forecast_5_days.get('DailyForecasts')[e].get('Night').get('PrecipitationProbability')
            windSpeedNight = forecast_5_days.get('DailyForecasts')[e].get('Night').get('Wind').get('Speed').get('Value')
            cloudNight = forecast_5_days.get('DailyForecasts')[e].get('Night').get('CloudCover')
            commentNight = forecast_5_days.get('DailyForecasts')[e].get('Night').get('LongPhrase')
            # update dictionary GENERIC
            keyDate = 'dateConcerned' + str(e + 1)
            keyTempMini = 'Temp mini' + str(e + 1)
            keyTempMaxi = 'Temp maxi' + str(e + 1)
            keyFeelsMini = 'Feels mini' + str(e + 1)
            keyFeelsMaxi = 'Feels maxi' + str(e + 1)
            fiveDayDic[keyDate] = str(dateConcerned)
            fiveDayDic[keyTempMini] = str(tempMini) + '°'
            fiveDayDic[keyTempMaxi] = str(tempMaxi) + '°'
            fiveDayDic[keyFeelsMini] = str(feelsLikeMini) + '°'
            fiveDayDic[keyFeelsMaxi] = str(feelsLikeMaxi) + '°'
            # update dictionary DAY
            keyWindDay = 'Wind SpeedDay' + str(e + 1)
            keyCloudDay = 'Cloud Day' + str(e + 1)
            keyRainDay = 'Rain probabilityDay' + str(e + 1)
            fiveDayDic[keyWindDay] = str(windSpeedDay) + 'km/h'
            fiveDayDic[keyCloudDay] = str(cloudDay) + '%'
            fiveDayDic[keyRainDay] = str(rainProbabilityDay) + '%'
            # update dictionary NIGHT
            keyWindNight = 'Wind speedNight' + str(e + 1)
            keyCloudNight = 'Cloud Night' + str(e + 1)
            keyRainNight = 'Rain probabilityNight' + str(e + 1)
            fiveDayDic[keyWindNight] = str(windSpeedNight) + 'km/h'
            fiveDayDic[keyCloudNight] = str(cloudNight) + '%'
            fiveDayDic[keyRainNight] = str(rainProbabilityNight) + '%'
            # update comments
            longPhraseDay.append(commentDay)
            longPhraseNight.append(commentNight)
            # update dictionary ICONS
            iconDay = str(iconDayDic)
            if len(iconDay) < 2:
                iconDay = '0' + iconDay
            path = "weather_icons/" + str(iconDay) + ".png"
            pathListDay.append(path)

            iconNight = str(iconNightDic)
            if len(iconNight) < 2:
                iconNight = '0' + iconNight
            path = "weather_icons/" + str(iconNight) + ".png"
            pathListNight.append(path)
        # updating dictionary with text values and icon paths
        fiveDayDic['IconDay'] = pathListDay
        fiveDayDic['IconNight'] = pathListNight
        fiveDayDic['Comments Day'] = longPhraseDay
        fiveDayDic['Comments Night'] = longPhraseNight
        # updating dictionary with list of items to create (label & stuff)
        listOfStuff = []
        for e in fiveDayDic.keys():
            if e == 'IconDay' or e == 'IconNight' or e == 'Comments Day' or e == 'Comments Night':
                pass
            else:
                listOfStuff.append(e)
        fiveDayDic['List of stuff to create'] = listOfStuff
        return fiveDayDic

    def currentWeather(self):
        url_current = 'http://dataservice.accuweather.com/currentconditions/v1/' + self.cityCode + '?apikey=' + \
                      self.APIkey + '&language=en&details=true&metric=true'
        current_weather = requests.get(url_current).json()
        current_dic = {}
        self.CallCounter()
        # building dictionary
        current_dic['dateConcerned'] = datetime.fromtimestamp(current_weather[0].get('EpochTime')).strftime(
            '%A %d/%m at %H:%M')
        current_dic['temp'] = current_weather[0].get('Temperature').get('Metric').get('Value')
        current_dic['realFeel'] = current_weather[0].get('RealFeelTemperature').get('Metric').get('Value')
        current_dic['humidity'] = current_weather[0].get('RelativeHumidity')
        current_dic['precipitation'] = current_weather[0].get('PrecipitationType')
        current_dic['description'] = current_weather[0].get('WeatherText')
        current_dic['wind'] = current_weather[0].get('Wind').get('Speed').get('Metric').get('Value')
        current_dic['icon'] = current_weather[0].get('WeatherIcon')

        iconDic = current_dic.get('icon')
        iconDic = str(iconDic)
        if len(iconDic) < 2:
            iconDic = '0' + iconDic
        path = "weather_icons/" + str(iconDic) + ".png"
        current_dic['path'] = path

        return current_dic

    def getIcon(self, path):
        img = Image.open(path)
        returnedIcon = ImageTk.PhotoImage(img)
        returnedIcon.image = returnedIcon
        return returnedIcon.image

    def CallCounter(self):
        self.count += 1
        self.calls.set(self.count)
        update = "UPDATE call_counter SET CALLS=" + '"' + str(
            self.count) + '"' + "WHERE DATE=" + '"' + self.todayDate + '"'
        self.cur.execute(update)
        self.connexion.commit()


if __name__ == "__main__":
    app = WeatherWithAccuweather()
    app.mainloop()
