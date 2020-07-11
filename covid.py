#COVID - Awareness Bot
import requests
import json
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
import logging
from telegram.ext import Updater
import telegram
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import time
from datetime import datetime
from datetime import timedelta
chroptions = webdriver.ChromeOptions()
chroptions.add_argument("--headless")
chroptions.add_argument('--no-sandbox')
chroptions.add_argument('--disable-dev-shm-usage')
wd = webdriver.Chrome('chromedriver',chrome_options=chroptions)
# Define a function for the thread
covid_json =requests.get('https://covid19-mohfw.herokuapp.com/').text.replace('\n','')
data = json.loads(covid_json)
valid_state= [_['state'] for _ in data['states']]
print(valid_state)
r1 = valid_state[:3]
r2 = valid_state[3:6]
r3 = valid_state[6:9]
r4 = valid_state[9:12]
r5 = valid_state[12:15]
r6 = valid_state[15:18]
r7 = valid_state[18:21]
r8 = valid_state[21:24]
r9 = valid_state[24:27]
r10 = valid_state[27:30]
r11 = valid_state[30:33]
r12 = valid_state[33:]
buttons_state = [r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11,r12]
tkn = '1307582765:AAGMMzPcNzTLY5Bi0WHEpjBKdQiDrUkeBe8'
bot = telegram.Bot(token = tkn)
#updater dispatcher initialised
updater = Updater(token = tkn,use_context = True)
dispatcher = updater.dispatcher
#dont know why
logging.basicConfig(format = '%(asctime)s - %(name)s -%(levelname)s -%(message)s', level = logging.INFO)

#update_covid_status
state_js = []
stat_dis=[]
d = {}
tme={}
def scrape():
	global d,wd,li_ds,tme,stat_dis
	li_ds = []
	wd.get('https://www.covid19india.org/')
	print('searched the url')
	
	tt = 0
	while True:
		if tt >50:break
		print('in while')
		tt+=1
		time.sleep(3)

		if wd.find_element_by_xpath('//div[@class="table-wrapper"]/div/div[@class="cell"]').is_displayed():

			li = wd.find_elements_by_xpath('//div[@class="table-wrapper"]/div/div[@class="cell"]')
			for li_st in li :
				li_st.click()
			print('clicked')
			stat_dis_wd = wd.find_elements_by_xpath('//div[@class="table-wrapper"]/div/div[@class="cell"]')
			stat_dis = [val.text for val in stat_dis_wd]
			try:
			 	for d in stat_dis:
			 		if d['State/UT'] in ['Unknown' , 'Other State',"District",'State/UT']:
			 			stat_dis.remove(d)
			except:pass

			li = wd.find_elements_by_xpath('//div[@class="table-wrapper"]/div')
			for val in li:
				
				fh = val.text.split('\n')
				ristrict = ["District",'State/UT','Unknown','Other State']
				for non_allow in ristrict:
					if non_allow in fh:cont_stat = True
				if  cont_stat == True:
					cont_stat = False
					continue
				if len(fh)==1:continue
				if len(fh)==2:
				  tme[li_ds[-6]] = fh
				  continue
				for h in fh:
				  li_ds.append(h)
			print('Exiting Scrape!')
			print(stat_dis)
			break
		else:
			print('not visible1')
	wd.close()
def process():
	global state_js
	for f in li_ds:
	  	if '↑' in f:li_ds.remove(f)
	  	elif '↓' in f:li_ds.remove(f)
	if len(li_ds) == 0:print('Error js lenght = 0')
	 

	def mapper():
		def x(a,b):
			global d,state_js,cnt
			if cnt%6==0:
				state_js.append(d)
				d={}
			cnt+=1
			d[a]=b
		global li_ds,state_js,cnt
		cnt = 0
		list(map(x,['State/UT', 'C', 'A', 'R', 'D', 'T']*(len(li_ds)//6),li_ds))
		print(state_js[0],'its Dic')
	mapper()
	mapper()
	mapper()
def update_covid_status():
	while  True:
		x = datetime.now().strftime('%I:%M:%S %p')
		print('Update Started At',x)
		scrape()
		process()
		y = datetime.now().strftime('%I:%M:%S %p')
		print('Update Started At',x)
		print('Update Ended At',y)
		time.sleep(10800)

threading.Thread( target = update_covid_status ).start()
time.sleep(300)
while True:
	if len(state_js) != 0:break
	else:
		print(state_js,"Global")
		time.sleep(10)
#print ("Error: unable to start thread")
#commands
def err(x):
	pass
def response(update,context):
	global valid_state,data,state_js,stat_dis
	print('Runing response')
	while True:
		custom_keyboard = []
		cnt = 0
		dis_pad =False
		temp_dis_lst = []
		in_state = update.message.text
		if in_state == 'Back':
			custom_keyboard = buttons_state
			reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
			bot.send_message(chat_id=update.effective_chat.id, 
	    		        	text="Select State From Custom Keyboard", 	
							reply_markup=reply_markup)
			break
		#valid state+district
		if in_state in stat_dis:
			print(in_state)
			for state_dic in state_js[1:]:
				
				if len(state_dic) == 0:
					india_state = 'Empty'
					continue
				if dis_pad ==True :
					cnt+=1
					if state_dic['State/UT'] in valid_state:
						
						if len(temp_dis_lst)!=0:
							custom_keyboard.append(temp_dis_lst)
			
							temp_dis_lst = []
						dis_pad = False
						custom_keyboard.append(['Back'])
						print(custom_keyboard)
						reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
						bot.send_message(chat_id=update.effective_chat.id, 
	            			text="Select District From Custom Keyboard For More Insights:", 	
							reply_markup=reply_markup)
						custom_keyboard = []
						break
					temp_dis_lst.append(state_dic['State/UT'])
					if cnt%3==0:
						custom_keyboard.append(temp_dis_lst)
						temp_dis_lst=[]	
				if in_state == state_dic['State/UT'] :
					stat = "---\t{}\t---\nActive Cases - {}\nTotal Recoveries - {}\nDeath Counts - {}\nTotal Case Counts - {}"
					stfm = stat.format(state_dic['State/UT'],state_dic['A'],state_dic['R'],state_dic['D'],state_dic['C'])
					context.bot.send_message(chat_id=update.effective_chat.id, text=stfm)
					if in_state in valid_state:
						dis_pad =True
						cnt = 0
					else:
						break
	
					
			

		else:
			print('Not valid',in_state)
		#err(0)
			
		break
def start(update,context):
	global buttons_state
	context.bot.send_message(chat_id=update.effective_chat.id, text="Enter State to check Covid Status:")
	#test
	custom_keyboard = buttons_state
	reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
	bot.send_message(chat_id=update.effective_chat.id, 
	            text="Select State From Custom Keyboard", 	
					reply_markup=reply_markup)


  #underdev
  #context.bot.send_message(chat_id=update.effective_chat.id, text="Type keyword to search about")


	
def help(update,context):
	while True:
		txt = ''' Welcome To Covid Info : India.\n Here is list of useful commands:\n
		/start required after everytime you use /stop command to resubscribe to our Service\n
		For now Enter the names of State you want Chech updates of Covid 19\n
		/help feel free to use this command\n
		/states Under development\n
		/feedback Under development\n
		Buttons mode Under development so stay informed and get updates directly of Ministry of Health & Family Welfare Covid stats\n
		MADE BY: Devarsh Sanghvi
		'''
		context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
		break

#Handlers
start_handler = CommandHandler('start', start)
response_handler = MessageHandler(Filters.text & (~Filters.command), response)
help_handler = CommandHandler('help', help)


#attaching Handlers
dispatcher.add_handler(start_handler)
dispatcher.add_handler(response_handler)
dispatcher.add_handler(help_handler)

print('start')
updater.start_polling()
updater.idle()