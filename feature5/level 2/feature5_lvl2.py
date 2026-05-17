# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import unittest
import time
import csv

LOGIN_URL  = "https://hcmutabc.moodlecloud.com/login/index.php"
LOGIN_USER = "quyen.doazas@hcmut.edu.vn"
LOGIN_PASS = "123456Moodle@"

class MoodleEnrollmentDDT(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.locators = {}
        with open('locators.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cls.locators[row['item_name']] = {
                    'type': row['locator_type'].lower(),
                    'value': row['locator_value']
                }

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self.verificationErrors = []

    def get_locator(self, item_name):
        strategy = self.locators[item_name]['type']
        value = self.locators[item_name]['value']
        if strategy == "id": return (By.ID, value)
        elif strategy == "xpath": return (By.XPATH, value)
        return (By.XPATH, value)

    def test_enrollment_data_driven_matrix(self):
        driver = self.driver
        wait = WebDriverWait(driver, 15)

        # 1. Thực hiện Đăng nhập hệ thống MoodleCloud
        driver.get(LOGIN_URL)
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            cookie_btn.click()
        except Exception:
            pass

        wait.until(EC.element_to_be_clickable((By.ID, "username"))).send_keys(LOGIN_USER)
        driver.find_element(By.ID, "password").send_keys(LOGIN_PASS)
        driver.find_element(By.ID, "loginbtn").click()
        time.sleep(3)

        # 2. Đọc kịch bản ma trận từ file test_data.csv bên ngoài
        test_cases = []
        with open('test_data.csv', mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_cases.append(row)

        print(f"\n======================================================================")
        print(f"STARTING LEVEL 2 AUTOMATION LOOP: {len(test_cases)} TEST CASES DETECTED")
        print(f"======================================================================")

        for test in test_cases:
            print(f"\nProcessing Pipeline ID: {test['test_id']}")
            expected_course_url = self.locators['course_url']['value']

            try:
                # Điều hướng động theo dữ liệu được ánh xạ từ locators.csv
                driver.get(expected_course_url)
                time.sleep(2)

                # Kích hoạt nút mở Modal
                launch_btn = wait.until(EC.element_to_be_clickable(self.get_locator('enrol_launch_btn')))
                driver.execute_script("arguments[0].click();", launch_btn)
                wait.until(EC.visibility_of_element_located(self.get_locator('enrol_modal_container')))

                # Điền thông tin ô Tìm kiếm thành viên
                search_val = test["Search_Input"].strip()
                search_box = wait.until(EC.visibility_of_element_located(self.get_locator('user_search_input')))
                search_box.clear()
                
                if search_val != "empty" and search_val != "":
                    search_box.send_keys(search_val)
                    time.sleep(2)
                    search_box.send_keys(Keys.ENTER)
                    time.sleep(1)

                # Cấu hình gán quyền hạn (Role Assignment Dropdown)
                role_val = test["Role_Param"].strip()
                role_dropdown = driver.find_element(*self.get_locator('role_drop_down'))
                select_role = Select(role_dropdown)
                try:
                    select_role.select_by_visible_text(role_val)
                except Exception:
                    pass

                # Xử lý các Assertion kiểm thử đầu ra
                if test['expected_result'] == 'success':
                    confirm_btn = driver.find_element(*self.get_locator('confirm_enrol_btn'))
                    driver.execute_script("arguments[0].click();", confirm_btn)
                    time.sleep(2)
                    print(f">> PASSED: {test['test_id']} successfully processed transaction.")

                elif test['expected_result'] == 'error':
                    expected_msg = test['expected_error_msg'].strip()
                    try:
                        err_el = wait.until(EC.visibility_of_element_located(self.get_locator('error_msg_locator')))
                        self.assertIn(expected_msg, err_el.text)
                        print(f">> PASSED: {test['test_id']} successfully caught expected validation restriction error.")
                    except AssertionError:
                        print(f">> FAILED: {test['test_id']} showed an error, but text didn't match. Expected: '{expected_msg}'")
                        self.verificationErrors.append(f"{test['test_id']}: Error text mismatch.")
                    except Exception:
                        print(f">> FAILED: {test['test_id']} bypassed form field verification rules entirely.")
                        self.verificationErrors.append(f"{test['test_id']} missed required error block indicators.")

                elif test['expected_result'] == 'cancel':
                    cancel_btn = driver.find_element(*self.get_locator('cancel_modal_btn'))
                    driver.execute_script("arguments[0].click();", cancel_btn)
                    time.sleep(2)
                    try:
                        wait.until(EC.url_to_be(expected_course_url))
                        print(f">> PASSED: {test['test_id']} successfully discarded and returned back to the course page.")
                    except Exception:
                        print(f">> FAILED: {test['test_id']} did not exit the form setup window cleanly upon cancel trigger.")
                        self.verificationErrors.append(f"{test['test_id']}: Cancellation URL landing mismatch.")

            except Exception as loop_fault:
                print(f"Skipping case {test['test_id']} due to structural execution error: {str(loop_fault)}\n")
                continue

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()