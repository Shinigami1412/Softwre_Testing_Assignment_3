# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest, time, csv, os

class CreateAQuizLevel2(unittest.TestCase):
    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()
        self.locators = self.load_locators()
        self.verificationErrors = []

    def load_locators(self):
        """Đọc và ánh xạ toàn bộ element từ file locators.csv"""
        loc_map = {}
        path = os.path.join(os.path.dirname(__file__), 'locators.csv')
        with open(path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                by_type = getattr(By, row['locate_by'].upper())
                loc_map[row['element_name']] = (by_type, row['locate_value'])
        return loc_map

    def find(self, name):
        """Hàm helper để tìm element nhanh dựa trên tên trong locator file"""
        return self.driver.find_element(*self.locators[name])

    def fill_date_time(self, prefix, row):
        """Hàm xử lý điền trọn bộ Ngày/Tháng/Năm/Giờ/Phút"""
        # prefix sẽ là 'timeopen' hoặc 'timeclose'
        Select(self.find(f'{prefix}_day')).select_by_visible_text(row[f'{prefix}_day'])
        Select(self.find(f'{prefix}_month')).select_by_visible_text(row[f'{prefix}_month'])
        Select(self.find(f'{prefix}_year')).select_by_visible_text(row[f'{prefix}_year'])
        Select(self.find(f'{prefix}_hour')).select_by_visible_text(row[f'{prefix}_hour'])
        Select(self.find(f'{prefix}_minute')).select_by_visible_text(row[f'{prefix}_minute'])

    def test_create_a_quiz_level_2(self):
        driver = self.driver
        
        # 1. ĐĂNG NHẬP
        driver.get("https://hcmutabc.moodlecloud.com/login/index.php")
        try:
            cookie = WebDriverWait(driver, 3).until(EC.element_to_be_clickable(self.locators['cookie_button']))
            cookie.click()
        except: pass

        self.find('username_field').send_keys("quyen.doazas@hcmut.edu.vn")
        self.find('password_field').send_keys("123456Moodle@")
        driver.execute_script("arguments[0].click();", self.find('login_button'))
        time.sleep(2)

        # 2. THỰC THI TEST CASE TỪ CSV
        data_path = os.path.join(os.path.dirname(__file__), 'testdata.csv')
        with open(data_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                with self.subTest(row=row):
                    tc_id = row.get('tc_id', 'Unknown').strip()
                    print(f"\n>> Level 2 - Executing: {tc_id}")
                    
                    driver.get("https://hcmutabc.moodlecloud.com/course/modedit.php?add=quiz&type&course=10&sectionid=39&return=0&beforemod=0")
                    
                    # Tên Quiz
                    q_name = row.get('quiz_name', '').strip()
                    self.find('quiz_name_field').clear()
                    if q_name: self.find('quiz_name_field').send_keys(q_name)

                    # Tab Timing
                    if row.get('timeopen_day') or row.get('timeclose_day') or row.get('timelimit'):
                        driver.execute_script("arguments[0].click();", self.find('timing_tab'))
                        time.sleep(1)
                        
                        # Xử lý Open Date
                        if row.get('timeopen_day'):
                            driver.execute_script("arguments[0].click();", self.find('timeopen_enable'))
                            self.fill_date_time('timeopen', row)
                        
                        # Xử lý Close Date
                        if row.get('timeclose_day'):
                            driver.execute_script("arguments[0].click();", self.find('timeclose_enable'))
                            self.fill_date_time('timeclose', row)
                        
                        # Xử lý Time Limit
                        if row.get('timelimit'):
                            driver.execute_script("arguments[0].click();", self.find('timelimit_enable'))
                            self.find('timelimit_field').clear()
                            self.find('timelimit_field').send_keys(row['timelimit'])

                    # Tab Grade
                    if row.get('gradepass'):
                        driver.execute_script("arguments[0].click();", self.find('grade_tab'))
                        time.sleep(1)
                        self.find('gradepass_field').clear()
                        self.find('gradepass_field').send_keys(row['gradepass'])

                    # Lưu
                    driver.execute_script("arguments[0].click();", self.find('save_button'))
                    time.sleep(2)

                    # 3. VERIFICATION
                    expected_out = row.get('expected_output', 'passed').lower()
                    expected_res = (row.get('expected_result') or '').strip()

                    if expected_out == 'passed':
                        try:
                            actual_h1 = self.find('header_title').text
                            if expected_res[:255] in actual_h1:
                                print(f"   => PASSED: Verify text '{expected_res[:20]}...' thành công.")
                            else:
                                msg = f"[{tc_id}] FAILED: Sai tiêu đề H1"
                                self.verificationErrors.append(msg)
                                print(f"   => {msg}")
                        except:
                            self.verificationErrors.append(f"[{tc_id}] FAILED: Không thấy trang kết quả")
                    else:
                        if expected_res.lower() in driver.page_source.lower():
                            print(f"   => PASSED: Thấy lỗi mong muốn '{expected_res}'")
                        else:
                            msg = f"[{tc_id}] FAILED: Không thấy lỗi '{expected_res}'"
                            self.verificationErrors.append(msg)
                            print(f"   => {msg}")

    def tearDown(self):
        self.driver.quit()
        if self.verificationErrors:
            print("\nDANH SÁCH LỖI:\n" + "\n".join(self.verificationErrors))
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()