from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random

class Timeouts:
    def srt() -> None:
        """short timeout"""
        time.sleep(random.random() + random.randint(0, 2))

    def med() -> None:
        """medium timeout"""
        time.sleep(random.random() + random.randint(2, 5))

    def lng() -> None:
        """long timeout"""
        time.sleep(random.random() + random.randint(5, 10))


class RedditPoster:
    def __init__(self):
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("user-data-dir=./userdata")  # Replace with your profile path
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def login(self, username, password):
        """Login to Reddit."""
        username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
        
        for ch in username:
            username_field.send_keys(ch)
            Timeouts.srt
        Timeouts.lng

        for ch in password:
            password_field.send_keys(ch)
            Timeouts.srt
        Timeouts.lng

        password_field.send_keys(Keys.ENTER)
        

    def open_site(self, site):
        self.driver.get(site)
    
    def get_element(self, type, input):
        match type:
            case 0:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, input))
                )
            case 1:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, input))
                ) 
            case 2:
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, input))
                )                 
        return element

    def send_keys(self, element, keys_to_send):
        for ch in keys_to_send:
            element.send_keys(ch)
            Timeouts.srt                

    def quit(self):
        self.driver.quit()

class Actions:
    def create_post(subreddit):
        link = f'reddit.com/web/f{subreddit}/submit'
        rd.open_site(link)
    
    def click_content_type(content_type):
        button_text = button_text.capitalize()
        xPath = f"//button[text()='{button_text}']"
        rd.get_element(0, xPath)
    
    def type_text(content_type, title, body, option=None):
        titlexPath = '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div[1]/div/textarea'
        if content_type == 'post':
            bodyxPath = '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div/div/div[3]/div/div[1]/div/div/div'
        if content_type == 'link':
            bodyxPath = '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/textarea'
        if content_type == 'poll':
            bodyxPath = '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div[1]/div/div[3]/div/div[1]/div/div/div'
            basePollxPath='//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div[2]/div/div/div[1]/div[1]/div[{}]/div/input'
            pollxPath = [basePollxPath.format(i) for i in range(1,len(option)+1)]
        #set title
        titleObj = rd.get_element(0, titlexPath)
        titleObj.click()
        Timeouts.med
        rd.send_keys(titleObj, title)
        Timeouts.med
        #set body
        bodyObj = rd.get_element(0, bodyxPath)
        bodyObj.click()
        Timeouts.med
        rd.send_keys(bodyObj, body)
        Timeouts.med
        #set options
        if content_type == 'poll':
            if len(option) > 2:
                for i in range(0, len(option)-2):
                    addOptionButtonObj = rd.get_element(0, '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div[2]/div/div/div[1]/div[2]/button')
                    addOptionButtonObj.click()
                    Timeouts.med
            
            for i in range(0, len(option)):
                pollTextObj = rd.get_element(0, pollxPath[i])
                pollTextObj.click()
                Timeouts.med
                rd.send_keys(pollTextObj, option[i])
                Timeouts.med       
        
    def submit_post():
        PostObj = rd.get_element(0, '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[3]/div[2]/div/div/div[1]/button[1]')
        PostObj.click()
        Timeouts.med

rd = RedditPoster()
input()
rd.open_site('https://www.reddit.com/login/')
input()
rd.login('thomas.pazhaidam19@gmail.com', '256sunny')
input()

texts = rd.driver.find_element(By.XPATH, "//button[text()='Image & Video']")
texts.click()


texts = rd.driver.find_element(By.XPATH, "//*[@id=\"AppRouter-main-content\"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div/div/div[3]/div/div[1]/div/div/div")
texts.click()
Timeouts.med
texts.send_keys('h')
input()

#rd.click_element_xPath('//*[contains(text(), "Create")]')
#input()
#input()
#rd.click_element_xPath('Link')
#input()
#rd.click_element_xPath('Poll')
#rd.quit()