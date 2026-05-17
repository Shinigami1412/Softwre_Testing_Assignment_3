# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
import unittest
import time
import csv

class Feature4(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        # Phóng to cửa sổ trình duyệt để tránh phần tử bị che khuất khuất tầm nhìn
        self.driver.maximize_window()
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_feature4(self):
        driver = self.driver
        
        with open('feature4.csv', mode='r', encoding='utf-8-sig') as file:
            csv_reader = csv.DictReader(file)
            
            for row in csv_reader:
                title = row.get('Title', '') or row.get('Tittle', '') or ''
                content = row.get('Content', '') or ''
                
                driver.get("https://hcmutabc.moodlecloud.com/mod/forum/view.php?id=281")
                
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.LINK_TEXT, "Add discussion topic"))
                ).click()
                
                subject_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "id_subject"))
                )
                subject_input.clear()
                subject_input.send_keys(title)
                
                # --- XỬ LÝ KHUNG SOẠN THẢO VĂN BẢN (TINYMCE HOẶC ATTO) ---
                try:
                    iframes = driver.find_elements(By.TAG_NAME, "iframe")
                    if iframes:
                        driver.switch_to.frame(iframes[0])
                        editor_body = driver.find_element(By.TAG_NAME, "body")
                        # Không dùng .clear() ở đây để tránh lỗi 'invalid element state'
                        editor_body.send_keys(content)
                        driver.switch_to.default_content()
                    else:
                        editor_div = driver.find_element(By.ID, "id_messageeditable")
                        # Không dùng .clear() cho div contenteditable nếu bị lỗi
                        editor_div.send_keys(content)
                except Exception as e:
                    print(f"Lỗi khi nhập nội dung: {e}")
                    driver.switch_to.default_content()
                
                # --- XỬ LÝ LỖI CLICK INTERCEPTED (NÚT SUBMIT BỊ CHE) ---
                submit_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "id_submitbutton"))
                )
                # Cuộn màn hình tới vị trí nút bấm
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(0.5) # Chờ hiệu ứng cuộn mượt hoàn tất
                
                try:
                    submit_button.click()
                except Exception:
                    # Nếu click thông thường vẫn bị che, dùng JavaScript click ép buộc (Bỏ qua mọi vật cản)
                    driver.execute_script("arguments[0].click();", submit_button)
                
                # Kiểm tra thông báo thành công
                try:
                    success_msg = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Your post was successfully added.')]"))
                    )
                    self.assertTrue(success_msg.is_displayed())
                except AssertionError as e:
                    self.verificationErrors.append(f"Không tìm thấy thông báo cho bài: {title}. Lỗi: {str(e)}")
                except Exception:
                    self.verificationErrors.append(f"Lỗi kiểm tra thông báo cho bài: {title}")
                
                time.sleep(2)
    
    def is_element_present(self, how, what):
        try: 
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException: 
            return False
        return True
    
    def is_alert_present(self):
        try: 
            self.driver.switch_to.alert
        except NoAlertPresentException: 
            return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: 
            self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()