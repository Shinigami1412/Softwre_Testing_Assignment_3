# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest, time, csv, os

class CreateAQuiz(unittest.TestCase):
    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10) 
        self.driver.maximize_window()
        self.verificationErrors = []
    
    def test_create_a_quiz(self):
        driver = self.driver
        
        # ==============================================================
        # 1. ĐĂNG NHẬP 
        # ==============================================================
        driver.get("https://hcmutabc.moodlecloud.com/login/index.php")
        try:
            cookie_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_btn.click()
            time.sleep(1)
        except: pass

        driver.find_element(By.ID, "username").clear()
        driver.find_element(By.ID, "username").send_keys("quyen.doazas@hcmut.edu.vn")
        driver.find_element(By.ID, "password").clear()
        driver.find_element(By.ID, "password").send_keys("123456Moodle@")
        
        login_btn = driver.find_element(By.ID, "loginbtn")
        driver.execute_script("arguments[0].click();", login_btn)
        time.sleep(2)

        # ==============================================================
        # 2. VÒNG LẶP DATA-DRIVEN TỐI ƯU HÓA TỐC ĐỘ
        # ==============================================================
        csv_path = os.path.join(os.path.dirname(__file__), 'testdata.csv')
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                with self.subTest(row=row):
                    tc_id = row.get('tc_id', 'Unknown_TC').strip()
                    quiz_name = row.get('quiz_name', '').strip()
                    print(f"\n>> Đang thực thi {tc_id}...")
                    
                    # Các field dữ liệu này có thể rỗng
                    to_day = row.get('timeopen_day', '').strip()
                    to_month = row.get('timeopen_month', '').strip()
                    to_year = row.get('timeopen_year', '').strip()
                    to_hour = row.get('timeopen_hour', '').strip()
                    to_min = row.get('timeopen_minute', '').strip()
                    
                    tc_day = row.get('timeclose_day', '').strip()
                    tc_month = row.get('timeclose_month', '').strip()
                    tc_year = row.get('timeclose_year', '').strip()
                    tc_hour = row.get('timeclose_hour', '').strip()
                    tc_min = row.get('timeclose_minute', '').strip()
                    
                    timelimit = row.get('timelimit', '').strip()
                    gradepass = row.get('gradepass', '').strip()

                    driver.get("https://hcmutabc.moodlecloud.com/course/modedit.php?add=quiz&type&course=10&sectionid=39&return=0&beforemod=0")
                    time.sleep(2)
                    
                    # --- ĐIỀN TÊN (LUÔN XỬ LÝ) ---
                    driver.find_element(By.ID, "id_name").clear()
                    if quiz_name:
                        driver.find_element(By.ID, "id_name").send_keys(quiz_name)
                    
                    # --- TAB TIMING (CHỈ MỞ NẾU CÓ ÍT NHẤT 1 DỮ LIỆU CẦN ĐIỀN) ---
                    if to_day or tc_day or timelimit:
                        timing_tab = driver.find_element(By.ID, "collapseElement-1")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", timing_tab)
                        driver.execute_script("arguments[0].click();", timing_tab)
                        time.sleep(1)
                        
                        # Chỉ điền Ngày mở nếu có data
                        if to_day:
                            enable_open = driver.find_element(By.ID, "id_timeopen_enabled")
                            driver.execute_script("arguments[0].click();", enable_open)
                            Select(driver.find_element(By.ID, "id_timeopen_day")).select_by_visible_text(to_day)
                            Select(driver.find_element(By.ID, "id_timeopen_month")).select_by_visible_text(to_month)
                            Select(driver.find_element(By.ID, "id_timeopen_year")).select_by_visible_text(to_year)
                            Select(driver.find_element(By.ID, "id_timeopen_hour")).select_by_visible_text(to_hour)
                            Select(driver.find_element(By.ID, "id_timeopen_minute")).select_by_visible_text(to_min)
                        
                        # Chỉ điền Ngày đóng nếu có data
                        if tc_day:
                            enable_close = driver.find_element(By.ID, "id_timeclose_enabled")
                            driver.execute_script("arguments[0].click();", enable_close)
                            Select(driver.find_element(By.ID, "id_timeclose_day")).select_by_visible_text(tc_day)
                            Select(driver.find_element(By.ID, "id_timeclose_month")).select_by_visible_text(tc_month)
                            Select(driver.find_element(By.ID, "id_timeclose_year")).select_by_visible_text(tc_year)
                            Select(driver.find_element(By.ID, "id_timeclose_hour")).select_by_visible_text(tc_hour)
                            Select(driver.find_element(By.ID, "id_timeclose_minute")).select_by_visible_text(tc_min)
                        
                        # Chỉ điền Time limit nếu có data
                        if timelimit:
                            enable_limit = driver.find_element(By.ID, "id_timelimit_enabled")
                            driver.execute_script("arguments[0].click();", enable_limit)
                            driver.find_element(By.ID, "id_timelimit_number").clear()
                            driver.find_element(By.ID, "id_timelimit_number").send_keys(timelimit)
                    
                    # --- TAB GRADE (CHỈ MỞ NẾU CÓ NHẬP ĐIỂM) ---
                    if gradepass:
                        grade_tab = driver.find_element(By.ID, "collapseElement-2")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", grade_tab)
                        driver.execute_script("arguments[0].click();", grade_tab)
                        time.sleep(1)
                        
                        driver.find_element(By.ID, "id_gradepass").clear()
                        driver.find_element(By.ID, "id_gradepass").send_keys(gradepass)
                    
                    # BẤM SAVE
                    btn_save = driver.find_element(By.ID, "id_submitbutton")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_save)
                    driver.execute_script("arguments[0].click();", btn_save)
                    time.sleep(2)
                    
                    # ==============================================================
                    # 3. VERIFICATION (KIỂM TRA KẾT QUẢ)
                    # ==============================================================
                    expected_output = row.get('expected_output', 'passed').strip().lower()
                    expected_result = (row.get('expected_result') or '').strip()
                    actual_page_source = driver.page_source
                    
                    if expected_output == 'passed':
                        try:
                            actual_h1 = driver.find_element(By.XPATH, "//h1").text
                            expected_ui_name = quiz_name[:255] 
                            
                            if expected_ui_name in actual_h1:
                                display_name = expected_ui_name if len(expected_ui_name) < 50 else expected_ui_name[:47] + "..."
                                print(f"   => PASSED: Đã tạo '{display_name}' thành công.")
                            else:
                                msg = f"[{tc_id}] FAILED: Tạo thành công nhưng sai tên. Không tìm thấy '{expected_ui_name}'"
                                self.verificationErrors.append(msg)
                                print(f"   => {msg}")
                        except Exception:
                            msg = f"[{tc_id}] FAILED: Lỗi không xác định hoặc hệ thống chặn lỗi không mong muốn."
                            self.verificationErrors.append(msg)
                            print(f"   => {msg}")
                    else:
                        if expected_result in actual_page_source:
                            print(f"   => PASSED: Hệ thống chặn đúng lỗi '{expected_result}'")
                        else:
                            msg = f"[{tc_id}] FAILED: Không hiển thị thông báo lỗi '{expected_result}'"
                            self.verificationErrors.append(msg)
                            print(f"   => {msg}")

    def tearDown(self):
        self.driver.quit()
        if self.verificationErrors:
            print("\n" + "="*40 + "\nCÁC TEST CASE BỊ FAIL:\n" + "\n".join(self.verificationErrors) + "\n" + "="*40)
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()