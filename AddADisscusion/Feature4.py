# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class Feature4(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome(executable_path=r'')
        self.driver.implicitly_wait(30)
        self.base_url = "https://www.google.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_feature4(self):
        driver = self.driver
        with open('feature4.csv', mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            
            # 2. Vòng lặp duyệt qua từng dòng dữ liệu trong CSV
            for row in csv_reader:
                title = row.get('Tittle', '') or ''
                content = row.get('Content', '') or ''
                
                driver.get("https://hcmutabc.moodlecloud.com/my/")
                driver.find_element_by_id("yui_3_18_1_1_1779003587611_425").click()
                driver.get("https://hcmutabc.moodlecloud.com/course/view.php?id=10")
                driver.find_element_by_xpath("//li[@id='module-281']/div[2]/div[2]/div[2]/div/div/span/a").click()
                driver.get("https://hcmutabc.moodlecloud.com/mod/forum/view.php?id=281")
                driver.find_element_by_link_text("Add discussion topic").click()
                driver.find_element_by_id("id_subject").click()
                driver.find_element_by_id("id_subject").clear()
                driver.find_element_by_id("id_subject").send_keys("${Tittle}")
                #ERROR: Caught exception [ERROR: Unsupported command [selectFrame | index=2 | ]]
                driver.find_element_by_xpath("//html").click()
                driver.find_element_by_xpath("//html").click()
                #ERROR: Caught exception [unknown command [editContent]]
                #ERROR: Caught exception [ERROR: Unsupported command [selectFrame | relative=parent | ]]
                driver.find_element_by_id("id_submitbutton").click()
                driver.get("https://hcmutabc.moodlecloud.com/mod/forum/view.php?f=7")
                driver.find_element_by_xpath("//span[@id='user-notifications']/div").click()
                try: self.assertEqual("Your post was successfully added.", driver.find_element_by_xpath("//div[@id='yui_3_18_1_1_1779003601740_189']/p").text)
                except AssertionError as e: self.verificationErrors.append(str(e))
        #ERROR: Caught exception [ERROR: Unsupported command [endLoadVars |  | ]]
        #ERROR: Caught exception [ERROR: Unsupported command [endLoadVars |  | ]]
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
