# n9b Production
# Produktionsbeginn: 06.03.2022
# Project: VaR (Value at Risk) Calculator App

import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QComboBox, QFileDialog, \
    QTableWidget, QTableWidgetItem
from PyQt6.QtGui import *  # für QFont erforderlich
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import pandas_datareader as web


class EingabeFenster(QWidget):
    def __init__(self):
        super().__init__()
        self.initMe()

    def initMe(self):
        self.TextDeclaration = QLabel("Value at Risk (VaR) estimates how much a Investment might lose with a given "
                                      "probability and given timeset.", self)
        self.TextDeclaration.move(20, 25)  # x, y
        self.TextDeclaration.setFont(QFont("Arial", 18))

        self.TextProbability = QLabel("Probability: (in %)", self)
        self.TextProbability.move(25, 60)  # x, y
        self.TextProbability.setFont(QFont("Arial", 18))

        self.Input_Probability = QLineEdit(self)
        self.Input_Probability.move(175, 60)  # x, y
        self.Input_Probability.resize(50, 20)  # x, y
        self.Input_Probability.setInputMask("99.99")  # man kann nur zwei Stellen vor & nach dem Komma eingeben

        self.TextDuration = QLabel("Time Frame:", self)
        self.TextDuration.move(25, 95)  # x, y
        self.TextDuration.setFont(QFont("Arial", 18))

        self.Input_Time_Start = QLineEdit(self)
        self.Input_Time_Start.move(135, 90)  # x, y
        self.Input_Time_Start.resize(80, 30)  # x, y
        self.Input_Time_Start.setInputMask("0000-00-00")  # yyyy-mm-dd

        self.Input_Time_Ende = QLineEdit(self)
        self.Input_Time_Ende.move(225, 90)  # x, y
        self.Input_Time_Ende.resize(80, 30)  # x, y
        self.Input_Time_Ende.setInputMask("0000-00-00")  # yyyy-mm-dd

        self.TextStockTicker = QLabel("Stock Ticker:", self)
        self.TextStockTicker.move(25, 135)  # x, y
        self.TextStockTicker.setFont(QFont("Arial", 18))

        self.Input_Stock_Ticker = QLineEdit(self)
        self.Input_Stock_Ticker.move(135, 135)  # x, y
        self.Input_Stock_Ticker.resize(50, 20)  # x, y
        self.Input_Stock_Ticker.setInputMask("XXXX")  # es können nur vier Symbole eingegeben werden

        self.Button_Kalk_Start = QPushButton("Start Calculations", self)
        self.Button_Kalk_Start.move(25, 180)  # x, y
        self.Button_Kalk_Start.clicked.connect(self.Button_Kalk_Start_Trigger)

        self.setWindowTitle("VaR Calculator - made by n9b")
        self.setGeometry(0, 0, 900, 225)
        self.show()

    def Button_Kalk_Start_Trigger(self):
        # Daten aus Abfrage beim User
        global p
        p = float(self.Input_Probability.text())
        time_start = str(self.Input_Time_Start.text())
        time_end = str(self.Input_Time_Ende.text())
        stock_ticker = str(self.Input_Stock_Ticker.text()).upper()

        global kurs_max_time
        kurs_max_time = []
        kurs_max_time = web.DataReader(stock_ticker, data_source="yahoo", start=time_start, end=time_end)["Close"]

        rendite_max_time = []
        for i in range(len(kurs_max_time) - 1):
            rendite_max_time.append(((kurs_max_time[i] / kurs_max_time[i + 1]) - 1) * 100)

        global rendite_max_time_sortiert
        rendite_max_time_sortiert = sorted(rendite_max_time)

        probability_per_value = round((1 / len(rendite_max_time) * 100), 3)  # Wert ist dann in Prozent
        global kummulierte_Wahrscheinlichkeit
        kummulierte_Wahrscheinlichkeit = []
        for i in range(len(rendite_max_time)):
            if i == 0:  # ist für den ersten Fall wo es noch kein Vorgänger gibt
                kummulierte_Wahrscheinlichkeit.append(probability_per_value)
            else:  # ist für jeden Fall nach dem Ersten, weil es dann einen Vorgänger gibt
                kummulierte_Wahrscheinlichkeit.append(probability_per_value + kummulierte_Wahrscheinlichkeit[i - 1])

        self.quantile = round(np.quantile(rendite_max_time_sortiert, round((1 - (p / 100)), 4)), 2)

        # Berechnung welche & wie viele Werte über dem erwartbaren Verlust liegen
        values_over_probability = []
        for i in range(len(rendite_max_time_sortiert)):
            if rendite_max_time_sortiert[i] <= self.quantile:
                values_over_probability.append(rendite_max_time_sortiert[i])

        # Alte Fensterinhalte löschen (bzw. hidden) oder umbauen
        self.TextDeclaration.setHidden(True)
        self.TextProbability.setHidden(True)
        self.TextProbability.setHidden(True)
        self.TextDuration.setHidden(True)
        self.Input_Probability.setHidden(True)
        self.Input_Time_Start.setHidden(True)
        self.Input_Time_Ende.setHidden(True)
        self.Input_Stock_Ticker.setHidden(True)
        self.Button_Kalk_Start.setHidden(True)

        # Neue Fensterinhalte aufbauen
        self.Button_New = QPushButton("New +", self)
        self.Button_New.move(25, 30)  # x, y
        self.Button_New.clicked.connect(self.Button_New_Trigger)
        self.Button_New.setHidden(False)

        self.Stock_Name = QLabel(stock_ticker, self)
        self.Stock_Name.move(100, 35)  # x, y
        self.Stock_Name.setFont(QFont("Arial", 18))
        self.Stock_Name.setHidden(False)

        self.tabelle = QTableWidget(self)
        self.tabelle.setGeometry(25, 60, 260, 325)
        self.tabelle.setRowCount(10)
        self.tabelle.setColumnCount(1)
        self.tabelle.setVerticalHeaderLabels(["Probability", "Time Frame Start", "Time Frame End", "Total values", "Loss in Probability",
                                              "Values over Probability", "Mean Loss over Probability", "Best", "Mean",
                                              "Worst"])
        self.tabelle.setHorizontalHeaderLabels(["Values"])
        self.tabelle.setItem(0, 0, QTableWidgetItem(str(p) + " %"))  # Probability from User Input
        self.tabelle.setItem(0, 1, QTableWidgetItem(self.Input_Time_Start.text()))  # Time Horizion from User Input
        self.tabelle.setItem(0, 2, QTableWidgetItem(self.Input_Time_Ende.text()))  # Time Horizion from User Input
        self.tabelle.setItem(0, 3, QTableWidgetItem(str(len(kurs_max_time))))  # Total Values of Stock Data 
        self.tabelle.setItem(0, 4, QTableWidgetItem(str(self.quantile) + " %"))  # Quantil Berechnung
        self.tabelle.setItem(0, 5,
                             QTableWidgetItem(str(len(values_over_probability))))  # Number of Values over Probability
        self.tabelle.setItem(0, 6, QTableWidgetItem(
            str(round(np.mean(values_over_probability), 2)) + "%"))  # Mean Loss over Probability
        self.tabelle.setItem(0, 7, QTableWidgetItem(str(round(max(rendite_max_time), 2)) + " %"))  # Best Rendite
        self.tabelle.setItem(0, 8, QTableWidgetItem(str(round(np.mean(rendite_max_time), 2)) + " %"))  # Mean Reandite
        self.tabelle.setItem(0, 9, QTableWidgetItem(str(round(min(rendite_max_time), 2)) + " %"))  # Worst Rendite
        self.tabelle.setHidden(False)

        graphics1 = Canvas1(self)  # Hauptgraphik
        graphics1.setGeometry(300, 20, 1125, 750)
        graphics1.show()

        graphics2 = Canvas2(self)  # Kursverlauf auf der linken Seite
        graphics2.setGeometry(25, 390, 260, 260)
        graphics2.show()

        self.setGeometry(0, 0, 1445, 800)
        self.show()

    def Button_New_Trigger(self):
        self._new_window = EingabeFenster()
        self._new_window.show()


class Canvas1(FigureCanvas):  # Hauptgraphiken
    def __init__(self, parent=None):
        fig = Figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.plot()

    def plot(self):
        graph_rendite = self.figure.add_subplot(1, 3, 1)
        graph_rendite.plot(rendite_max_time_sortiert)
        graph_rendite.set_title("sortierte Rendite")
        graph_rendite.axhline(0, color="red")

        graph_kummulierte_Wahrscheinlichkeit = self.figure.add_subplot(1, 3, 2)
        graph_kummulierte_Wahrscheinlichkeit.plot(rendite_max_time_sortiert, kummulierte_Wahrscheinlichkeit)
        graph_kummulierte_Wahrscheinlichkeit.set_title("kummulierte Wahrscheinlichkeit")
        graph_kummulierte_Wahrscheinlichkeit.axvline(min(rendite_max_time_sortiert), color="red")
        graph_kummulierte_Wahrscheinlichkeit.axvline(np.mean(rendite_max_time_sortiert), color="red")
        graph_kummulierte_Wahrscheinlichkeit.axvline(max(rendite_max_time_sortiert), color="red")

        graph_histogram = self.figure.add_subplot(1, 3, 3)
        graph_histogram.hist(rendite_max_time_sortiert, bins=30)
        graph_histogram.set_title("Rendite Histogram")
        graph_histogram.axvline(0, color="red")


class Canvas2(FigureCanvas):  # Kursverlauf auf der linken Seite
    def __init__(self, parent=None):
        fig = Figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.plot()

    def plot(self):
        graph_stock_chart = self.figure.add_subplot(1, 1, 1)
        graph_stock_chart.plot(kurs_max_time)
        graph_stock_chart.set_title("Kursverlauf")
        graph_stock_chart.set_xticks([])  # Dadurch hat die x-Achse keine Beschriftung
        graph_stock_chart.set_yticks([])  # Dadurch hat die y-Achse keine Beschriftung


app = QApplication(sys.argv)
window = EingabeFenster()
sys.exit(app.exec())  # Wenn die App beendet wird, endet auch das Python Programm
