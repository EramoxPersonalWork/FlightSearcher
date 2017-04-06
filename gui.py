#!/usr/bin/env
# coding: utf-8

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget

from find_flight import Skyscanner

import xml.sax
class LocaleHandler(xml.sax.ContentHandler):
   def __init__(self):
      self.Code = ""
      self.Name = ""


class LoginScreen(GridLayout):

    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text='Origin'))
        self.orig = TextInput(multiline=False)
        self.add_widget(self.orig)
        self.add_widget(Label(text='Destination'))
        self.dest = TextInput(multiline=False)
        self.add_widget(self.dest)

class FlightSearcherApp(App):

	def build(self):
		parent = Widget()

		initBtn = Button(text='init databases')
		parent.add_widget(initBtn)
		initBtn.bind(on_release=self.initdb)

		parent.add_widget(LoginScreen())
		Skyscanner.create_session()

		return parent

	def initdb(self, obj):
		locale_data = poling_ref_data("locales")
#		insert_into_db("Locales", "()", transform_locales(locale_data)
#		currency_data = poling_ref_data("currencies")
#		insert_into_db("Currencies", "()", transform_currencies(currency_data)

# Start the GUI
if __name__ == '__main__':
    FlightSearcherApp().run()
