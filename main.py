"""
opaque is an encrypted communications package using kivy.

"""


# File: main.py
# 
# Copyright (c) 2013 Charles Perkins
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import kivy
kivy.require('1.7.2') # replace with your current kivy version !

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.modalview import ModalView
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.lang import Builder
from kivy.properties import ObjectProperty 
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.adapters.listadapter import ListAdapter

from kivy.network.urlrequest import UrlRequest



class RootWidget(AnchorLayout):
    anchor = 'right', 'top'
    rootbox_id = ObjectProperty()
    leftgrid_id = ObjectProperty()
    rightpane_id = ObjectProperty()

    def do_action(self):
        self.something='Y'
        self.app.open_settings()

    def la_callback(self, value):
	sel = value.selection
	self.obutton.text=sel[0].text+"\n"+self.sect+"\n\n"
	self.drawMain( sel[0].text )


    def makeMenu(self, selected):
	self.leftgrid_id.clear_widgets()

	buttons=["Home","Conversations","People","Notebooks"]
	detail=["nothing"]
	sel=""
	for b in buttons:
        	b1 = Button(size_hint_y=None, height= 50, text= b, id= b+"Button")
        	b1.bind(on_press=self.buttonAction)
        	self.leftgrid_id.add_widget(b1)
		if selected == b:
		  self.sect=b
        	  gl = GridLayout(size_hint_y=1, cols=2)
		  if b == "Home":
		    la = ListAdapter(data=self.home, cls=ListItemButton, allow_empty_selection=False)
		    la.bind(on_selection_change=self.la_callback)
		  if b == "People":
		    la = ListAdapter(data=self.contacts, cls=ListItemButton, allow_empty_selection=False)
		    la.bind(on_selection_change=self.la_callback)
		  if b == "Notebooks":
		    la = ListAdapter(data=self.notebooks, cls=ListItemButton, allow_empty_selection=False)
		    la.bind(on_selection_change=self.la_callback)
		  if b == "Conversations":
		    la = ListAdapter(data=self.conversations, cls=ListItemButton, allow_empty_selection=False)
		    la.bind(on_selection_change=self.la_callback)

		  lv = ListView(adapter=la,padding= 10,spacing= 10, size_hint_x =.8,size_hint_y = .8)
		  sel = la.selection

        	  b2 = Label(size_hint_x=None, width= 10, text= " ")
        	  gl.add_widget(b2)
        	  gl.add_widget(lv)
        	  self.leftgrid_id.add_widget(gl)

	self.drawMain( sel[0].text )



    def drawMain(self, seltext ):


	self.rightpane_id.clear_widgets()

	thislist=()

	if self.sect=="Home":
	    if seltext=="Timeline":
	        thislist=self.timelist
	    if seltext=="Messages":
	        thislist=self.mesglist
	if self.sect=="Conversations":
	        thislist=self.convlist
	if self.sect=="People":
	        thislist=self.peoplist
	if self.sect=="Notebooks":
	        thislist=self.notelist

	pla = ListAdapter(data=thislist, cls=ListItemButton)
	plv = ListView(adapter=pla,padding= 10,spacing= 10, size_hint_x =1,size_hint_y = 1)
	self.rightpane_id.add_widget(plv)


	al = FloatLayout()
	if self.app.connstat=="offline":
	    downimg="peel-100-orange-selected.png"
	    normimg="peel-100-orange.png"
	else:
	    downimg="peel-100-green-selected.png"
	    normimg="peel-100-green.png"

        self.obutton = Button(size_hint_y=None, 
                    size_hint_x=None, 
                    height= 100, 
                    width= 100, 
                    color= [0,0,0,1], 
                    text= seltext+"\n"+self.sect+"\n\n", 
                    id= "moreButton", 
                    background_down= downimg,
                    background_normal= normimg,
                    pos=(self.app.win.width-100,0))
        self.obutton.bind(on_press=self.buttonAction)
        al.add_widget(self.obutton)
	self.rightpane_id.add_widget(al)



    def buttonAction(self,button):
	if button.text=="Home":
		self.makeMenu("Home")
	if button.text=="People":
		self.makeMenu("People")
	if button.text=="Conversations":
		self.makeMenu("Conversations")
	if button.text=="Notebooks":
		self.makeMenu("Notebooks")
	if button.text=="Settings":
		self.app.open_settings()

class DetailButton(ListItemButton):
    def __init__(self, **kwargs):
        self.value = kwargs.get('value', '')
        super(DetailButton, self).__init__(**kwargs)


class OpaqueApp(App):

    classvar = ""
    root = ""
    connstat = "offline"
    temp = ""
    win = Window

    def build(self):
        root = RootWidget()
        root.app = self
	root.connstat = "offline"
	root.accounts = dict(self.config.items('Accounts'))
	root.keys = dict(self.config.items('Keys'))

	root.conversations = {}
	dt = dict(self.config.items('Conversations'))
	for t  in dt:
	    if t != "modconv" and t != "addconv":
	        root.conversations[t]=dt[t]

	root.contacts = {}
	dc = dict(self.config.items('Contacts'))
	for c  in dc:
	    if c != "modcontact" and c != "addcontact":
                i = c.split('#')
	        root.contacts[i[0]]=dc[c]

	root.notebooks = {}
	nc = dict(self.config.items('Notebooks'))
	for n  in nc:
	    if n != "modnote" and n != "addnote":
                i = n.split('#')
	        root.notebooks[i[0]]=nc[n]

#	root.mainlist = dict(self.config.items('Accounts'))
	root.makeMenu("Home")

        def win_cb(window, width, height):
            root.makeMenu("Home")

        Window.bind(on_resize=win_cb)

#        req = UrlRequest(url, on_success, on_error, req_body, req_headers)

	self.sendheartbeat('')
	Clock.schedule_interval(self.sendheartbeat, 5)

	return root

    def sendheartbeat(self,b):
        req = UrlRequest("http://localhost:8082/b?EeSkBFSoysfdKSB46GyHG/32D4/dxS5tdt3ZRQ==", self.heartbeatgood,self.heartbeatbad)

    def heartbeatgood(self,b,c):
	self.root.app.connstat = "online"
        self.root.obutton.background_down = "peel-100-green-selected.png"
        self.root.obutton.background_normal = "peel-100-green.png"

    def heartbeatbad(self,b,c):
	self.root.app.connstat = "offline"
        self.root.obutton.background_down = "peel-100-orange-selected.png"
        self.root.obutton.background_normal = "peel-100-orange.png"


    def build_config(self, config):
	config.read("opaque.ini")
        
        config.setdefaults('Accounts', {
            'addAccount': 'Add',
            'modAccount': 'Modify'
        })

        config.setdefaults('Notebooks', {
            'addNote': 'Add',
            'modNote': 'Modify'
        })

        config.setdefaults('Keys', {
            'addKey': 'Add',
            'modKey': 'Modify'
        })
        config.setdefaults('Conversations', {
            'addConv': 'Add',
            'modConv': 'Modify'
        })
        config.setdefaults('Contacts', {
            'addContact': 'Add',
            'modContact': 'Modify'
        })

    def build_settings(self, settings):

	jAcc = "["
	for key, item in self.config.items('Accounts'):
	  if key != "addaccount" and key != "modaccount":
            its = item.split(',')
            jAcc = jAcc + """
	    { "type": "options",
	      "title": \""""+key+""" \",
	      "desc": \""""+its[1]+" "+its[2]+" "+its[3]+" "+its[4]+" "+its[5]+""" \",
	      "section": "Accounts",
	      "key": "modAccount",
	      "options": ["Modify"] },
	    """
        jAcc = jAcc + """
	    { "type": "options",
	      "title": " ",
	      "desc": "Add an account to an Opaque service",
	      "section": "Accounts",
	      "key": "addAccount",
	      "options": ["Add"] }
	    ]"""
        settings.add_json_panel('Accounts',
            self.config, data=jAcc)
	jN = "["
	for key, item in self.config.items('Notebooks'):
	  if key != "addnote" and key != "modnote":
            its = item.split(',')
            jN = jN + """
	    { "type": "options",
	      "title": \""""+key+""" \",
	      "desc": \""""+its[1]+" "+its[2]+" "+its[3]+" "+its[4]+" "+its[5]+""" \",
	      "section": "Notebooks",
	      "key": "modNote",
	      "options": ["Modify"] },
	    """
        jN = jN + """
	    { "type": "options",
	      "title": " ",
	      "desc": "Add an Opaque note",
	      "section": "Notebooks",
	      "key": "addNote",
	      "options": ["Add"] }
	    ]"""
        settings.add_json_panel('Notebooks',
            self.config, data=jN)
	jKeys = "["
	for key, item in self.config.items('Keys'):
	  if key != "addkey" and key != "modkey":
            its = item.split(',')
            jKeys = jKeys + """
	    { "type": "options",
	      "title": \""""+key+""" \",
	      "desc": \""""+its[1]+" "+its[2]+""" \",
	      "section": "Keys",
	      "key": "modKey",
	      "options": ["Modify"] },
	    """
        jKeys = jKeys + """
	    { "type": "options",
	      "title": " ",
	      "desc": "Add a key to an Opaque topic",
	      "section": "Keys",
	      "key": "addKey",
	      "options": ["Add"] }
	    ]"""
        settings.add_json_panel('Keys',
            self.config, data=jKeys)
	jT = "["
	for key, item in self.config.items('Conversations'):
	  if key != "addconv" and key != "modconv":
            its = item.split(',')
            jT = jT + """
	    { "type": "options",
	      "title": \""""+key+""" \",
	      "desc": \""""+its[1]+" "+its[2]+" "+its[3]+" "+its[4]+""" \",
	      "section": "Conversations",
	      "key": "modConv",
	      "options": ["Modify"] },
	    """
        jT = jT + """
	    { "type": "options",
	      "title": " ",
	      "desc": "Add a topic for Opaque discussion",
	      "section": "Conversations",
	      "key": "addConv",
	      "options": ["Add"] }
	    ]"""
        settings.add_json_panel('Conversations',
            self.config, data=jT)
	jC = "["
	for key, item in self.config.items('Contacts'):
	  if key != "addcontact" and key != "modcontact":
            jC = jC + """
	    { "type": "options",
	      "title": \""""+key+""" \",
	      "desc": \""""+item+""" \",
	      "section": "Contacts",
	      "key": "modContact",
	      "options": ["Modify"] },
	    """
        jC = jC + """
	    { "type": "options",
	      "title": " ",
	      "desc": "Add a contact for Opaque correspondence",
	      "section": "Contacts",
	      "key": "addContact",
	      "options": ["Add"] }
	    ]"""
        settings.add_json_panel('Contacts',
            self.config, data=jC)

    def on_config_change(self, config, section, key, value):
        if config is self.config:
            token = (section, key)
            if token == ('section1', 'key1'):
                pass
            elif token == ('section1', 'key2'):
                pass

    use_kivy_settings = False
    icon = 'hashicon-24.png'

if __name__ == '__main__':
    OpaqueApp().run()
