# -*- coding: utf-8 -*-

import unittest
import pandas as pd
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# =====================================================
# CONFIG
# =====================================================

LOGIN_URL = "https://hcmutabc.moodlecloud.com/login/index.php"

LOGIN_USER = "vy.nguyenngoclan@hcmut.edu.vn"
LOGIN_PASS = "LVHCMUTktpm12@"


# =====================================================
# TEST CLASS
# =====================================================

class MoodleAssignmentSubmission(unittest.TestCase):

    def setUp(self):

        options = Options()

        options.add_argument("--incognito")

        options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )

        self.driver = webdriver.Chrome(options=options)

        self.driver.maximize_window()

        self.wait = WebDriverWait(self.driver, 30)

    # =================================================
    # LOGIN
    # =================================================

    def login(self):

        driver = self.driver

        driver.get(LOGIN_URL)

        time.sleep(2)

        username = self.wait.until(
            EC.presence_of_element_located(
                (By.ID, "username")
            )
        )

        username.clear()

        username.send_keys(LOGIN_USER)

        password = driver.find_element(
            By.ID,
            "password"
        )

        password.clear()

        password.send_keys(LOGIN_PASS)

        password.send_keys(Keys.RETURN)

        time.sleep(5)

        print("LOGIN SUCCESSFUL")

    # =================================================
    # MAIN TEST
    # =================================================

    def test_assignment_submit(self):

        driver = self.driver

        wait = self.wait

        self.login()

        data = pd.read_csv(
            "Level1/assignment_data.csv"
        )

        for index, row in data.iterrows():

            print("\n" + "=" * 50)

            print("RUNNING:", row["testcase_id"])

            try:

                # =====================================
                # OPEN COURSE
                # =====================================

                course_btn = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.PARTIAL_LINK_TEXT,
                            "Data Driven Testing - feature 2"
                        )
                    )
                )

                driver.execute_script(
                    "arguments[0].click();",
                    course_btn
                )

                print("OPENED COURSE")

                time.sleep(3)

                # =====================================
                # OPEN ASSIGNMENT
                # =====================================

                assignment_btn = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.PARTIAL_LINK_TEXT,
                            "Feature 3 - Assignment Submission"
                        )
                    )
                )

                driver.execute_script(
                    "arguments[0].click();",
                    assignment_btn
                )

                print("OPENED ASSIGNMENT")

                time.sleep(5)

                # =====================================
                # CLICK ADD SUBMISSION
                # =====================================

                add_btn = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//*[contains(text(),'Add submission')]"
                        )
                    )
                )

                driver.execute_script(
                    "arguments[0].scrollIntoView(true);",
                    add_btn
                )

                time.sleep(2)

                driver.execute_script(
                    "arguments[0].click();",
                    add_btn
                )

                print("CLICKED ADD SUBMISSION")

                time.sleep(5)

                # =====================================
                # OPEN FILE PICKER
                # =====================================

                upload_area = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//*[contains(@class,'filemanager')]"
                        )
                    )
                )

                driver.execute_script(
                    "arguments[0].scrollIntoView(true);",
                    upload_area
                )

                time.sleep(2)

                driver.execute_script(
                    "arguments[0].click();",
                    upload_area
                )

                print("OPENED FILE PICKER")

                time.sleep(5)

                # =====================================
                # FIND FILE INPUT
                # =====================================

                file_input = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//input[@type='file']"
                        )
                    )
                )

                print("FOUND FILE INPUT")

                # =====================================
                # FILE PATH
                # =====================================

                file_path = os.path.abspath(
                    row["file_path"]
                )

                print("UPLOADING:", file_path)

                # =====================================
                # UPLOAD FILE
                # =====================================

                file_input.send_keys(file_path)

                print("UPLOAD SUCCESS")

                time.sleep(8)

                # =====================================
                # CLICK UPLOAD THIS FILE
                # =====================================

                upload_btn = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//*[contains(text(),'Upload this file')]"
                        )
                    )
                )

                driver.execute_script(
                    "arguments[0].click();",
                    upload_btn
                )

                print("CONFIRMED FILE UPLOAD")

                time.sleep(8)

                # =====================================
                # SAVE CHANGES
                # =====================================

                save_btn = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.ID,
                            "id_submitbutton"
                        )
                    )
                )

                driver.execute_script(
                    "arguments[0].scrollIntoView(true);",
                    save_btn
                )

                time.sleep(2)

                driver.execute_script(
                    "arguments[0].click();",
                    save_btn
                )

                print("SAVED SUBMISSION")

                time.sleep(8)

                # =====================================
                # VERIFY
                # =====================================

                page_text = driver.page_source

                if row["expected_result"] in page_text:

                    print("PASS")

                    driver.save_screenshot(
                        f"{row['testcase_id']}_PASS.png"
                    )

                else:

                    print("FAIL")

                    driver.save_screenshot(
                        f"{row['testcase_id']}_FAIL.png"
                    )

                # =====================================
                # RETURN TO COURSE
                # =====================================

                driver.get(
                    "https://hcmutabc.moodlecloud.com/course/view.php?id=10"
                )

                time.sleep(3)

            except Exception as e:

                print("ERROR:", e)

                driver.save_screenshot(
                    f"{row['testcase_id']}_ERROR.png"
                )

                continue

    # =================================================
    # TEARDOWN
    # =================================================

    def tearDown(self):

        self.driver.quit()


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    unittest.main()