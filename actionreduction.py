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
        prefs = {"profile.default_content_setting_values.notifications": 2}  # 1: Allow, 2: Block
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self, username, password):
        self.__open_site('https://www.reddit.com/login/')
        Timeouts.lng
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
        Timeouts.lng
        

    def __open_site(self, site):
        self.driver.get(site)
    
    def __get_element(self, type, input):
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

    def __send_keys(self, element, keys_to_send):
        for ch in keys_to_send:
            element.send_keys(ch)
            Timeouts.srt                

    def quit(self):
        self.driver.quit()
    
    def navigate_to_create_post_page(self, subreddit):
        link = f'https://www.reddit.com/web/{subreddit}/submit'
        self.__open_site(link)
        Timeouts.lng
    
    def select_post_type(self, content_type):
        button_text = content_type.capitalize()
        xPath = f"//button[text()='{button_text}']"
        buttonObj = self.__get_element(0, xPath)
        buttonObj.click()
        Timeouts.lng
    
    def fill_post_details(self, content_type, title, content, option=None):
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
        titleObj = self.__get_element(0, titlexPath)
        titleObj.click()
        Timeouts.med
        self.__send_keys(titleObj, title)
        Timeouts.med
        #set body
        bodyObj = self.__get_element(0, bodyxPath)
        bodyObj.click()
        Timeouts.med
        self.__send_keys(bodyObj, content)
        Timeouts.med
        #set options
        if content_type == 'poll':
            if len(option) > 2:
                for i in range(0, len(option)-2):
                    addOptionButtonObj = self.__get_element(0, '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[2]/div[2]/div[2]/div/div/div[1]/div[2]/button')
                    addOptionButtonObj.click()
                    Timeouts.med
            
            for i in range(0, len(option)):
                pollTextObj = self.__get_element(0, pollxPath[i])
                pollTextObj.click()
                Timeouts.med
                self.__send_keys(pollTextObj, option[i])
                Timeouts.med
        Timeouts.lng     
        
    def click_submit_button(self):
        PostObj = self.__get_element(0, '//*[@id="AppRouter-main-content"]/div/div/div[2]/div[3]/div[1]/div[2]/div[3]/div[3]/div[2]/div/div/div[1]/button[1]')
        PostObj.click()
        Timeouts.lng
        
'''
rd = RedditPoster()
input()
rd.open_site('https://www.reddit.com/login/')
input()
rd.login('username', 'password')
input()
rd.create_post('r/testautomationcom')
input()
rd.click_content_type('link')
input()
rd.type_text('link', 'test2', 'www.google.com')
input()
rd.submit_post()
input()
rd.create_post('r/testautomationcom')
input()
rd.click_content_type('poll')
input()
rd.type_text('poll', 'test3', 'test poll', ['candies', 'apples', 'glizzies'])
input()
rd.submit_post()
input()
'''