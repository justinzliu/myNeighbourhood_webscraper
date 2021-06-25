import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

#generalization definitions
class School:
	#pass -1 for score and "n/a" for rank when not applicable 
	def __init__(self, city, name, score, rank, retrieved):
		self.city = city
		self.name = name
		self.score = score
		self.rank = rank
		self.retrieved = retrieved
	def __str__(self):
		return (" ".join([self.city,self.name,self.score,self.rank,self.retrieved]))

def scroll_down_element(driver, element, getElement):
	#getElement is the javascript HTML get command to return an element. if the script returns a list, be sure to include the index
    try:
        action = ActionChains(driver)
        action.move_to_element(element).click().send_keys(Keys.SPACE)
        offset = 0; #scroll offset
        new_offset = driver.execute_script("return " + getElement + ".scrollHeight")
        while(offset < new_offset):
            action.perform()
            offset = new_offset
            time.sleep(0.5) #TODO: convert to webdriverwait.until
            new_offset = driver.execute_script("return " + getElement + ".scrollHeight")
            #print(offset, new_offset)
    except Exception as e:
        print('ERROR scroll_down_element(): ', e)
