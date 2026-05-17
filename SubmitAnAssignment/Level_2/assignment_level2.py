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
        # Tự động load cấu hình UI từ file CSV bên ngoài khi khởi tạo (Chuẩn Level 2)
        self.load_locators("locator_config.csv")
        
        # Khởi tạo Trình duyệt Chrome
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()

    def load_locators(self, file_path):
        """
        Level 2 Specification: Đọc động toàn bộ URL, Text fields, và Buttons 
        từ file cấu hình cấu trúc bên ngoài để tránh hard-code.
        """
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.locators[row['element_name']] = {
                    'by': getattr(By, row['locate_by'].upper()) if row['locate_by'] != 'url' else 'url',
                    'value': row['locate_value']
                }

    def get_element(self, name):
        """Hàm Helper để bốc động các phần tử UI từ dữ liệu đã load"""
        locator = self.locators[name]
        return self.driver.find_element(locator['by'], locator['value'])

    def run_tests(self, data_file):
        try:
            # 1. Điều hướng tới Moodle Sandbox bằng URL động từ cấu hình
            print("[INFO] Navigating to Moodle login page...")
            self.driver.get(self.locators['login_url']['value'])
            
            # 2. Thực hiện Authentication sử dụng thông tin tài khoản của má
            print("[INFO] Authenticating user: vy.nguyenngoclan@hcmut.edu.vn")
            self.get_element('username_field').send_keys('vy.nguyenngoclan@hcmut.edu.vn')
            self.get_element('password_field').send_keys('LVHCMUTktpm12@')
            self.get_element('login_button').click()

            # 3. Điều hướng động qua Course và Assignment link
            print("[INFO] Navigating to course and assignment pages...")
            self.get_element('course_link').click()
            self.get_element('assignment_link').click()

            # 4. Vòng lặp Data-Driven Testing (Đọc data kịch bản kiểm thử từ CSV)
            with open(data_file, mode='r', encoding='utf-8') as f:
                test_cases = csv.DictReader(f)
                
                for row in test_cases:
                    print(f"--- Executing Scenario {row['test_id']}: {row['description']} ---")
                    
                    # Xử lý nút bấm Add Submission hoặc Edit Submission tương ứng
                    try:
                        self.get_element('add_submission_btn').click()
                    except Exception:
                        # Fallback phòng trường hợp trạng thái trước đó bắt buộc phải bấm Edit submission
                        self.driver.find_element(By.XPATH, "//button[contains(text(),'Edit submission')]").click()

                    # Kiểm tra xem kịch bản này có yêu cầu upload file hay không
                    if row['file_path'] and row['file_path'].strip():
                        full_path = os.path.abspath(row['file_path'])
                        print(f"[ACTION] Uploading target test file: {row['file_path']}")
                        # Đưa đường dẫn file vào input element động lấy từ file config
                        self.get_element('file_picker_input').send_keys(full_path)
                        time.sleep(2)  # Nghỉ 2 giây để file load lên dropzone ổn định

                    # Thực thi submit form
                    print("[ACTION] Submitting the form changes...")
                    self.get_element('save_changes_btn').click()

                    # 5. Kiểm thử đầu ra dựa trên Expected Result động của từng Test Case
                    expected = row['expected_result']
                    time.sleep(1) # Chờ trang reload kết quả
                    page_source = self.driver.page_source
                    
                    # Tiến hành Assertion (Xác thực kết quả thực tế vs Mong đợi)
                    if expected in page_source:
                        print(f"==> RESULT {row['test_id']}: PASSED\n")
                    else:
                        print(f"==> RESULT {row['test_id']}: FAILED (Expected pattern '{expected}' not found in UI context)\n")
                        
        except Exception as global_error:
            print(f"[CRITICAL ERROR] Automation flow interrupted: {str(global_error)}")
                        
        finally:
            # Đóng trình duyệt sạch sẽ sau khi hoàn thành chuỗi test cases
            print("[INFO] Tearing down WebDriver environment.")
            self.driver.quit()

if __name__ == "__main__":
    # Khởi chạy Framework Level 2
    automation = MoodleAutomationLevel2()
    automation.run_tests("assignment_testdata.csv")