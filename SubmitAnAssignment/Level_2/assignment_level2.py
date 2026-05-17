import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class MoodleAutomationLevel2:
    def __init__(self):
        self.locators = {}
        self.load_locators("locator_config.csv")
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()

    def load_locators(self, file_path):
        """Level 2: Đọc động các phần tử UI từ file cấu hình bên ngoài"""
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.locators[row['element_name']] = {
                    'by': getattr(By, row['locate_by'].upper()) if row['locate_by'] != 'url' else 'url',
                    'value': row['locate_value']
                }

    def get_element(self, name):
        """Hàm helper để tìm element dựa trên cấu hình động"""
        locator = self.locators[name]
        return self.driver.find_element(locator['by'], locator['value'])

    def run_tests(self, data_file):
        try:
            # 1. Đi tới trang Login bằng URL động
            self.driver.get(self.locators['login_url']['value'])
            
            # 2. Đăng nhập (Thay thông tin thật của má vào đây hoặc đưa vào file config luôn nha)
            self.get_element('username_field').send_keys('student_account')
            self.get_element('password_field').send_keys('student_password')
            self.get_element('login_button').click()

            # 3. Điều hướng tới Assignment
            self.get_element('course_link').click()
            self.get_element('assignment_link').click()

            # 4. Đọc file Data-Driven Test Cases
            with open(data_file, mode='r', encoding='utf-8') as f:
                test_cases = csv.DictReader(f)
                
                for row in test_cases:
                    print(f"Executing {row['test_id']}: {row['description']}")
                    
                    # Click Add Submission
                    try:
                        self.get_element('add_submission_btn').click()
                    except:
                        # Nếu đã có submission trước đó, click Edit thay thế
                        self.driver.find_element(By.XPATH, "//button[contains(text(),'Edit submission')]").click()

                    # Upload file động từ testdata nếu có
                    if row['file_path']:
                        full_path = os.path.abspath(row['file_path'])
                        # Level 2: Truy xuất input file động từ config
                        self.get_element('file_picker_input').send_keys(full_path)
                        time.sleep(2)  # Chờ file load một xíu

                    # Lưu thay đổi
                    self.get_element('save_changes_btn').click()

                    # 5. Xác thực kết quả động (Assertion)
                    expected = row['expected_result']
                    actual = ""
                    
                    try:
                        # Thử tìm text trong bảng status hoặc trong banner báo lỗi
                        page_source = self.driver.page_source
                        if expected in page_source:
                            print(f"-> {row['test_id']}: PASSED\n")
                        else:
                            print(f"-> {row['test_id']}: FAILED (Expected content '{expected}' not found)\n")
                    except Exception as e:
                        print(f"-> {row['test_id']}: ERROR ({str(e)})\n")
                        
        finally:
            self.driver.quit()

if __name__ == "__main__":
    automation = MoodleAutomationLevel2()
    automation.run_tests("assignment_testdata.csv")