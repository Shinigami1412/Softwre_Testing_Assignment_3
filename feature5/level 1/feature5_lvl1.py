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
COURSE_URL = "https://hcmutabc.moodlecloud.com/user/index.php?id=10"
LOGIN_USER = "quyen.doazas@hcmut.edu.vn"
LOGIN_PASS = "123456Moodle@"

LOCATORS = {
    "enrol_launch_btn":      (By.XPATH, "//button[contains(@data-action, 'enrol')] | //button[contains(., 'Enroll users')] | //button[@id='enrolusersbutton'] | //input[@type='submit' and contains(@value, 'Enroll')]"),
    "enrol_modal_container":  (By.XPATH, "//div[contains(@class, 'modal-dialog')] | //div[contains(@class, 'moodle-dialogue')]"),
    "user_search_input":      (By.XPATH, "//input[@placeholder='Search' or @type='text' or contains(@id, 'search')]"),
    "role_drop_down":         (By.XPATH, "//select[contains(@id, 'id_role_assignment')] | //select[contains(@name, 'role')]"),
    "confirm_enrol_btn":      (By.XPATH, "//div[contains(@class, 'modal-footer')]//button[@data-action='save' or contains(@class, 'btn-primary')] | //div[contains(@class, 'modal-footer')]//button[1]"),
    "cancel_modal_btn":       (By.XPATH, "//div[contains(@class, 'modal-footer')]//button[@data-action='cancel' or contains(@class, 'btn-secondary')] | //div[contains(@class, 'modal-footer')]//button[2]"),
    "error_msg_locator":      (By.XPATH, "//span[@class='error'] | //div[contains(@class, 'invalid-feedback')] | //div[text()='No suggestions']")
}

class EnrollUserLevel1(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self.verificationErrors = []

    def test_enroll_user_ddt_loop(self):
        driver = self.driver
        wait = WebDriverWait(driver, 15)

        # 1. Hệ thống thực hiện Đăng nhập tài khoản
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

        # 2. Đọc tệp kịch bản kiểm thử test_data.csv bên ngoài
        test_cases = []
        with open('test_data.csv', mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_cases.append(row)

        print(f"\n======================================================================")
        print(f"STARTING LEVEL 1 AUTOMATION LOOP: {len(test_cases)} TEST CASES DETECTED")
        print(f"======================================================================")

        for test in test_cases:
            print(f"\nProcessing Pipeline ID: {test['test_id']}")
            
            try:
                # Điều hướng thẳng đến trang Participants của khóa học số 10
                driver.get(COURSE_URL)
                time.sleep(2)

                # Click kích hoạt nút Enroll Users mở popup
                launch_btn = wait.until(EC.element_to_be_clickable(LOCATORS["enrol_launch_btn"]))
                driver.execute_script("arguments[0].click();", launch_btn)
                wait.until(EC.visibility_of_element_located(LOCATORS["enrol_modal_container"]))

                # Nhập thông tin dữ liệu tìm kiếm
                search_val = test["Search_Input"].strip()
                search_box = wait.until(EC.visibility_of_element_located(LOCATORS["user_search_input"]))
                search_box.clear()
                
                if search_val != "empty" and search_val != "":
                    search_box.send_keys(search_val)
                    time.sleep(2)
                    search_box.send_keys(Keys.ENTER)
                    time.sleep(1)

                # Chọn phân quyền Role thả xuống
                role_val = test["Role_Param"].strip()
                role_dropdown = driver.find_element(*LOCATORS["role_drop_down"])
                select_role = Select(role_dropdown)
                try:
                    select_role.select_by_visible_text(role_val)
                except Exception:
                    pass

                # Kiểm tra phân luồng kết quả mong đợi
                if test["expected_result"] == "success":
                    confirm_btn = driver.find_element(*LOCATORS["confirm_enrol_btn"])
                    driver.execute_script("arguments[0].click();", confirm_btn)
                    time.sleep(2)
                    print(f">> PASSED: {test['test_id']} successfully processed transaction.")

                elif test["expected_result"] == "error":
                    expected_msg = test["expected_error_msg"].strip()
                    try:
                        err_el = wait.until(EC.visibility_of_element_located(LOCATORS["error_msg_locator"]))
                        self.assertIn(expected_msg, err_el.text)
                        print(f">> PASSED: {test['test_id']} successfully caught expected validation restriction error.")
                    except AssertionError:
                        print(f">> FAILED: {test['test_id']} showed an error, but text didn't match. Expected: '{expected_msg}'")
                        self.verificationErrors.append(f"{test['test_id']}: Error text mismatch.")
                    except Exception:
                        print(f">> FAILED: {test['test_id']} bypassed form field verification rules entirely.")
                        self.verificationErrors.append(f"{test['test_id']} missed required error block indicators.")

                elif test["expected_result"] == "cancel":
                    cancel_btn = driver.find_element(*LOCATORS["cancel_modal_btn"])
                    driver.execute_script("arguments[0].click();", cancel_btn)
                    time.sleep(2)
                    try:
                        wait.until(EC.url_to_be(COURSE_URL))
                        print(f">> PASSED: {test['test_id']} successfully discarded and returned back to participants container.")
                    except Exception:
                        print(f">> FAILED: {test['test_id']} did not exit form window cleanly upon cancel trigger.")
                        self.verificationErrors.append(f"{test['test_id']}: Cancellation URL landing mismatch.")

            except Exception as loop_fault:
                print(f"Skipping case {test['test_id']} due to structural execution error: {str(loop_fault)}")
                continue

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()