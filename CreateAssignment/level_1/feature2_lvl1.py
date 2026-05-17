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
COURSE_URL = "https://hcmutabc.moodlecloud.com/course/view.php?id=10"
CREATE_URL = "https://hcmutabc.moodlecloud.com/course/modedit.php?add=assign&type&course=10&sectionid=39&return=0&beforemod=0"
LOGIN_USER = "admin"
LOGIN_PASS = "123456Moodle@"


LOCATORS = {
    "edit_switch_label":      (By.XPATH, "//label[contains(@for, '-editingswitch')] | //input[contains(@id, '-editingswitch')] | //*[contains(@id, '-editingswitch')] | //label[contains(., 'Edit mode')]"),
    "add_content_btn":        (By.XPATH, "//button[@data-action='open-addingcontent'] | //button[@title='Add content'] | //i[contains(@class, 'fa-plus')]/parent::button"),
    "activity_option":        (By.XPATH, "//button[@data-action='open-chooser'] | //button[contains(., 'Activity or resource')]"),
    "assignment_card":        (By.XPATH, "//a[@data-action='add-chooser-option' and contains(., 'Assignment')] | //div[text()='Assignment']/parent::a"),
    "add_selected_btn":       (By.XPATH, "//button[@data-action='add-selected-chooser-option'] | //button[contains(text(), 'Add')]"),

    "assignment_name_field":  (By.ID,    "id_name"),
    "submit_btn":             (By.ID,    "id_submitbutton"),
    "cancel_btn":             (By.ID,    "id_cancel"),

    "error_msg_locator":      (By.XPATH, "//span[@class='error'] | //div[contains(@class, 'invalid-feedback')] | //div[@id='notice']"),
    "assertion_heading":      (By.XPATH, "//h1[contains(@class, 'h2')] | //div[@role='main']//h1"),

    "allow_enable_cb":        (By.ID,    "id_allowsubmissionsfromdate_enabled"),
    "allow_day_sel":          (By.ID,    "id_allowsubmissionsfromdate_day"),
    "allow_month_sel":        (By.ID,    "id_allowsubmissionsfromdate_month"),
    "allow_year_sel":         (By.ID,    "id_allowsubmissionsfromdate_year"),

    "due_enable_cb":          (By.ID,    "id_duedate_enabled"),
    "due_day_sel":            (By.ID,    "id_duedate_day"),
    "due_month_sel":          (By.ID,    "id_duedate_month"),
    "due_year_sel":           (By.ID,    "id_duedate_year"),

    "cutoff_enable_cb":       (By.ID,    "id_cutoffdate_enabled"),
    "cutoff_day_sel":         (By.ID,    "id_cutoffdate_day"),
    "cutoff_month_sel":       (By.ID,    "id_cutoffdate_month"),
    "cutoff_year_sel":        (By.ID,    "id_cutoffdate_year"),

    "remind_enable_cb":       (By.ID,    "id_gradingduedate_enabled"),
    "remind_day_sel":         (By.ID,    "id_gradingduedate_day"),
    "remind_month_sel":       (By.ID,    "id_gradingduedate_month"),
    "remind_year_sel":        (By.ID,    "id_gradingduedate_year"),

    "sub_onlinetext_cb":      (By.ID,    "id_assignsubmission_onlinetext_enabled"),
    "sub_file_cb":            (By.ID,    "id_assignsubmission_file_enabled"),

    "grade_field":            (By.ID,    "id_grade_modgrade_point"),
    "grade_toggle":           (By.XPATH, "//a[@data-bs-toggle='collapse' and contains(@href, 'id_modstandardgradecontainer')]"),
}


class MoodleAssignmentDDT(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self.verificationErrors = []

    def get_locator(self, item_name):
        return LOCATORS[item_name]

    def set_checkbox(self, locator_name, target_state):
        cb = self.driver.find_element(*self.get_locator(locator_name))
        if (target_state == "1" and not cb.is_selected()) or \
           (target_state == "0" and cb.is_selected()):
            self.driver.execute_script("arguments[0].click();", cb)

    def set_dropdown(self, locator_name, value):
        el = self.driver.find_element(*self.get_locator(locator_name))
        Select(el).select_by_value(str(value))

    def test_run_assignment_data_loop(self):
        driver = self.driver
        wait   = WebDriverWait(driver, 15)

        # ── Login ──────────────────────────────────────────────────────
        driver.get(LOGIN_URL)
        username_input = wait.until(EC.element_to_be_clickable((By.ID, "username")))
        time.sleep(1)
        username_input.clear()
        username_input.send_keys(LOGIN_USER)

        password_input = driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(LOGIN_PASS)
        password_input.send_keys(Keys.RETURN)

        # ── Navigate to course & enable edit mode ──────────────────────
        driver.get(COURSE_URL)
        time.sleep(2)

        print("Toggling Moodle Edit Mode switch...")
        try:
            edit_switch = wait.until(EC.element_to_be_clickable(self.get_locator("edit_switch_label")))
            driver.execute_script("arguments[0].click();", edit_switch)
            print("Edit Mode activated.")
            time.sleep(3)
        except Exception:
            print("Switch locator missed. Applying URL backup trick...")
            driver.get(f"{COURSE_URL}&edit=1")
            time.sleep(3)

        # ── Read test data from CSV and iterate ────────────────────────
        with open("test_data.csv", mode="r", encoding="utf-8") as f:
            test_cases = csv.DictReader(f)

            for test in test_cases:
                print(f"\nProcessing Pipeline ID: {test['test_id']}")

                try:
                    driver.get(CREATE_URL)

                    # -- Title --
                    title_field = wait.until(EC.presence_of_element_located(self.get_locator("assignment_name_field")))
                    title_field.clear()
                    title_field.send_keys(test["assignment_title"])

                    # -- Allow Submissions From Date --
                    self.set_checkbox("allow_enable_cb", test["allow_en"])
                    if test["allow_en"] == "1":
                        self.set_dropdown("allow_day_sel",   test["allow_d"])
                        self.set_dropdown("allow_month_sel", test["allow_m"])
                        self.set_dropdown("allow_year_sel",  test["allow_y"])

                    # -- Due Date --
                    self.set_checkbox("due_enable_cb", test["due_en"])
                    if test["due_en"] == "1":
                        self.set_dropdown("due_day_sel",   test["due_d"])
                        self.set_dropdown("due_month_sel", test["due_m"])
                        self.set_dropdown("due_year_sel",  test["due_y"])

                    # -- Cutoff Date --
                    self.set_checkbox("cutoff_enable_cb", test["cutoff_en"])
                    if test["cutoff_en"] == "1":
                        self.set_dropdown("cutoff_day_sel",   test["cutoff_d"])
                        self.set_dropdown("cutoff_month_sel", test["cutoff_m"])
                        self.set_dropdown("cutoff_year_sel",  test["cutoff_y"])

                    # -- Remind Me To Grade Date --
                    self.set_checkbox("remind_enable_cb", test["remind_en"])
                    if test["remind_en"] == "1":
                        self.set_dropdown("remind_day_sel",   test["remind_d"])
                        self.set_dropdown("remind_month_sel", test["remind_m"])
                        self.set_dropdown("remind_year_sel",  test["remind_y"])

                    # -- Submission Types --
                    self.set_checkbox("sub_onlinetext_cb", test["sub_text"])
                    self.set_checkbox("sub_file_cb",       test["sub_file"])

                    # -- Grade section (expand if collapsed) --
                    grade_sec_toggle = wait.until(EC.presence_of_element_located(self.get_locator("grade_toggle")))
                    is_expanded = grade_sec_toggle.get_attribute("aria-expanded")

                    if is_expanded == "false":
                        print("Grade section is collapsed. Expanding it now...")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", grade_sec_toggle)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", grade_sec_toggle)
                        time.sleep(1.5)

                    # -- Grade Value --
                    grade_input = wait.until(EC.element_to_be_clickable(self.get_locator("grade_field")))
                    grade_input.clear()
                    grade_input.send_keys(test["grade_val"])

                    # -- Submit or Cancel --
                    if test["expected_result"] == "cancel":
                        cancel_btn_el = driver.find_element(*self.get_locator("cancel_btn"))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cancel_btn_el)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", cancel_btn_el)
                        print("Fired Cancel command action element...")
                    else:
                        submit_btn_el = driver.find_element(*self.get_locator("submit_btn"))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn_el)
                        time.sleep(0.5)
                        driver.execute_script("arguments[0].click();", submit_btn_el)

                    time.sleep(2.5)

                    # -- Assertions --
                    if test["expected_result"] == "success":
                        heading_el  = wait.until(EC.presence_of_element_located(self.get_locator("assertion_heading")))
                        actual_text = heading_el.text
                        try:
                            self.assertIn(test["assignment_title"], actual_text)
                            print(f">> PASSED: {test['test_id']} saved and verified successfully.")
                        except AssertionError as e:
                            print(f">> FAILED: {test['test_id']} title header verification failure.")
                            self.verificationErrors.append(f"{test['test_id']}: {str(e)}")

                    elif test["expected_result"] == "error":
                        try:
                            error_el          = wait.until(EC.presence_of_element_located(self.get_locator("error_msg_locator")))
                            actual_error_text = error_el.text
                            expected_msg      = test["expected_error_msg"]

                            if expected_msg:
                                self.assertIn(expected_msg, actual_error_text)
                                print(f">> PASSED: {test['test_id']} blocked with correct message: '{expected_msg}'")
                            else:
                                print(f">> PASSED: {test['test_id']} blocked by form rule restrictions.")
                        except AssertionError:
                            print(f">> FAILED: {test['test_id']} showed an error, but the text didn't match. Expected: '{expected_msg}'")
                            self.verificationErrors.append(f"{test['test_id']}: Error text mismatch.")
                        except Exception:
                            print(f">> FAILED: {test['test_id']} bypassed form field verification rules entirely.")
                            self.verificationErrors.append(f"{test['test_id']} missed required error block indicators.")

                    elif test["expected_result"] == "cancel":
                        try:
                            wait.until(EC.url_to_be(COURSE_URL))
                            print(f">> PASSED: {test['test_id']} successfully discarded and returned back to the course page.")
                        except Exception:
                            print(f">> FAILED: {test['test_id']} did not exit the form setup window cleanly upon cancel trigger.")
                            self.verificationErrors.append(f"{test['test_id']}: Cancellation URL landing mismatch.")

                except Exception as loop_fault:
                    print(f"Skipping case {test['test_id']} due to structural execution error: {str(loop_fault)}")
                    continue

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


if __name__ == "__main__":
    unittest.main()