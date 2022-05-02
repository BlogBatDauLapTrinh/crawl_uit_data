from uit_course_crawler import UITCourseCrawler

database = "database/database_uit.db"
ID_COURSE_START = 2900
ID_COURSE_END = 9330
ID_USER_START = 1
ID_USER_END = 17663
USER_NAME = ""
PASSWORD = ""

def main():
    crawler = UITCourseCrawler()
    crawler.log_in(user_name=USER_NAME, password=PASSWORD)
    crawler.crawl_courses_data(ID_COURSE_START,ID_COURSE_END)
    crawler.crawl_user_data(ID_USER_START,ID_USER_END)
    crawler.quit()

main()