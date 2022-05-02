from selenium import webdriver
from bs4 import BeautifulSoup
import re
from sqlite_helper import SQliteHelper
# export PATH=$PATH:/usr/lib/chromium-browser/
class UITCourseCrawler():
    def __init__(self):
        self.driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
        self.sqliteHelper = SQliteHelper()
        with open('error.log', 'w') as f:
            f.write(f'')

    def log_in(self, user_name, password):
        self.driver.get(f'https://courses.uit.edu.vn')
        self.driver.find_element_by_id('username').send_keys(user_name)
        self.driver.find_element_by_id('password').send_keys(password)
        self.driver.find_element_by_id('loginbtn').click()

    def crawl_courses_data(self, start_course_id=8000, end_course_id=8100):
        for course_id in range(start_course_id, end_course_id):
            soup = self.get_soup_from_cousre_id(course_id)
            if "Khoá học này hiện chưa được mở" in str(soup) or "Không thể tìm thấy bản ghi dữ liệu trong bảng CSDL" in str(soup): continue
            try:
                course_id, course_code, course_name, year_school, semester = self.get_course_data_from_soup(
                    soup)
                print(course_name)
                self.sqliteHelper.insert_into_course_table(
                    course_id, course_code, course_name, year_school, semester)
            except Exception as e:
                with open('error.log', 'a') as f:
                    f.write(f'crawl_courses_data {e}\n')

    def get_soup_from_cousre_id(self, course_id):
        self.driver.get(
            f'https://courses.uit.edu.vn/enrol/index.php?id={course_id}')
        html = self.driver.page_source
        return BeautifulSoup(html, "html.parser")

    def get_course_data_from_soup(self, soup):
        course_id = self.driver.current_url.split("?id=")[1]
        course_name_code = soup.find(
            'div', {'class': 'page-header-headings'}).get_text()
        time_tag = soup.find_all('li', {'class': 'breadcrumb-item'})
        if "CVHT" in course_name_code or "KHBC" in course_name_code:  
            course_name = course_name_code
            course_code = course_name_code.split(" lớp ")[1]
            time = str(time_tag[5].find('a').get_text())
            year_school = course_code[4:8]
            semester = "lớp sinh hoạt"
        elif "VB2" in course_name_code:
            course_name = course_name_code.split(" - ")[0]
            course_code = course_name_code.split(" - ")[1]
            year_school = "VB2  "
            semester = time_tag[2].get_text().split("Văn bằng ")[1]
        elif " - " in course_name_code:    
            course_name = course_name_code.split(" - ")[0]
            course_code = course_name_code.split(" - ")[1]
            time = str(time_tag[2].find('a').string)
            #OEP
            if self.is_not_time(time):
                time = str(time_tag[3].find('a').string)
            if "Term" in time:
                split_time = time.split(" - ")
                year_school = split_time[0] + "-" + split_time[1]
                if 'nd' in time:
                    semester = '2'
                elif 'st' in time:
                    semester = '1'
                elif '3rd' in time:
                    semester = '3'
                else:
                    raise Exception("CAN NOT GET SEMESTER ")
            elif "Học kỳ" in time:
                year_school = re.search(r'\((.*?)\)', time).group(1)
                semester = re.search(r'Học kỳ (.*?) \(', time).group(1)
            else: 
                year_school = "undefined"
                semester = "undefined"
        else:
            raise Exception(f"{course_id} {course_name_code}")

        return course_id, course_code, course_name, year_school, semester

    def crawl_user_data(self, start_user_id=8860, end_user_id=8870):
        for user_id in range(start_user_id, end_user_id):
            try:
                soup = self.get_soup_from_user_id(user_id)
                if "Chi tiết của người dùng này không hiện hữu với bạn" in str(soup) or "Tài khoản thành viên đã được xóa" in str(soup) or "Người dùng không hợp lệ" in str(soup): continue
                if self.is_given_user_id_student(soup) == False:
                    instructor_id, instructor_name, instructor_email, instructor_image_url, first_access, last_access = self.get_instructor_data_from_soup(soup)
                    self.sqliteHelper.insert_into_instructor_table(
                        instructor_id, instructor_name, instructor_email, instructor_image_url, first_access, last_access)
                    print(instructor_name)
                else:
                    student_id, student_code, student_name, class_name, student_email, sudent_image_url, first_access, last_access = self.get_student_data_from_soup(
                        soup)
                    print(student_name)
                    self.sqliteHelper.insert_into_student_table(
                        student_id, student_code, student_name, class_name, student_email, sudent_image_url, first_access, last_access)
                instructor_id,all_courese_id = self.get_enroll_data_from_soup(soup)
                self.sqliteHelper.insert_into_enroll_table(instructor_id,all_courese_id)
            except Exception as e:
                with open('error.log', 'a') as f:
                    f.write(f'crawl_user_data {e} {user_id}\n')

    def get_soup_from_user_id(self, student_id):
        self.driver.get(
            f'https://courses.uit.edu.vn/user/profile.php?id={student_id}')
        html = self.driver.page_source
        return BeautifulSoup(html, "html.parser")

    def is_given_user_id_student(self, soup):
        email_tag = soup.find("dd")
        try:
            email = email_tag.find('a').string
            identity = email.split('@')[0]
        except Exception as e:
            return None
        return identity.isnumeric()

    def get_instructor_data_from_soup(self, soup):
        instructor_id = self.driver.current_url.split("?id=")[1]
        instructor_email_tag = soup.find("dd")
        instructor_email = instructor_email_tag.find('a').string
        instructor_name = soup.find(
            'div', {'class': 'page-header-headings'}).string
        instructor_image_tag = soup.find('div', {'class': 'page-header-image'})
        instructor_image_url = instructor_image_tag.find('img')['src']
        first_access_tag = soup.find_all(
            'div', {'class': 'card-body'})[4].find('ul').find('li').find('dl').find('dd').string
        last_access_tag = soup.find_all(
            'div', {'class': 'card-body'})[4].find('ul').find_all('li')[1].find('dl').find('dd').string
        first_access = re.search('(\(.*?)\)', first_access_tag).group(1)[1:]
        last_access = re.search('(\(.*?)\)', last_access_tag).group(1)[1:]
        return instructor_id, instructor_name, instructor_email, instructor_image_url, first_access, last_access

    def get_enroll_data_from_soup(self, soup):
        instructor_id = self.driver.current_url.split("?id=")[1]
        all_courese_id = self.get_list_course_id_user_enrolled(soup)
        return instructor_id,all_courese_id

    def get_student_data_from_soup(self, soup):
        student_id = self.driver.current_url.split("?id=")[1]
        try:
            student_email_tag = soup.find("dd")
            student_email = student_email_tag.find('a').string
            student_code = student_email.split('@')[0]
        except:
            student_email  = "undefined"
            student_code = "undefined"
        student_name = soup.find(
            'div', {'class': 'page-header-headings'}).string
        student_image_tag = soup.find('div', {'class': 'page-header-image'})
        sudent_image_url = student_image_tag.find('img')['src']
        first_access_tag = soup.find_all(
            'div', {'class': 'card-body'})[4].find('ul').find('li').find('dl').find('dd').string
        last_access_tag = soup.find_all(
            'div', {'class': 'card-body'})[4].find('ul').find_all('li')[1].find('dl').find('dd').string
        first_access = re.search('(\(.*?)\)', first_access_tag).group(1)[1:]
        last_access = re.search('(\(.*?)\)', last_access_tag).group(1)[1:]
        class_name = self.get_class_name(soup)
        return student_id, student_code, student_name, class_name, student_email, sudent_image_url, first_access, last_access

    def quit(self):
        self.driver.quit()
        self.sqliteHelper.connection.close()

    def get_class_name(self, soup):
        class_tag = soup.find_all('div', {'class': 'card-body'})[2].find('ul').find(
            'li').find('dl').find('dd').find('ul').find('li').find('a').string
        class_name = class_tag.split(' ')[-1]
        if self.is_valid_class_name(class_name): return class_name
        return "undefined"

    def is_valid_class_name(self,class_name):
        if len(class_name) < 8: return False
        if not str(class_name[:4]).isnumeric() and str(class_name[4:]).isnumeric(): return True
        return False 


    def get_list_course_id_user_enrolled(self, soup):
        all_course_tag = soup.find_all('div', {'class': 'card-body'})[2].find(
            'ul').find('li').find('dl').find('dd').find('ul').find_all('li')
        all_courses_url = [course_tag.find(
            'a')['href'] for course_tag in all_course_tag]        
        return [course_url.split('course=')[1] for course_url in all_courses_url if "showallcourses" not in course_url]

    def is_not_time(self, time):
        return not '20' in time