Crawl dữ liệu sinh viên UIT
Bài viết này dành riêng cho các bạn là sinh viên UIT, vì để đăng nhập và truy xuất các dữ liệu từ nhà trường thì cần một **tài khoản chứng thực do nhà trường cấp**. Và trong bài viết mình sẽ hướng dẫn về việc truy xuất các dữ liệu từ trang [courses.uit.edu.vn](https://courses.uit.edu.vn), cụ thể các dữ liệu là mã số sinh viên, tên, email, lớp học, các môn học mà sinh viên đã thamg gia,...

### Ý tưởng
Sau khi sử dụng trang web một thời gian thì mình nhận thấy rằng mình có thể xem thông tin các môn học mà mình chưa tham gia hoặc xem thông tin của các sinh viên khác. Từ đó mình có suy nghĩ crawl toàn bộ dữ liệu của các sinh viên và dữ liệu môn học. Dựa vào cơ sở dữ liệu này mình có thể khá phá nhiều thứ, ví dụ mình có thể xem danh sách các sinh viên cùng lớp, có thể truy vấn các môn mà sinh viên học, môn học nào có nhiều người học lại, học giảng viên nào thì có tỉ lệ học lại cao hơn. Ngoài ra mình có thể xem các môn học đã từng được mở từ đó sắp xếp môn học để đăng ký học phần.

### Tiến hành

##### Công cụ

- Ngôn ngữ lập trình được dùng trong bài viết là **Python**.
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) để trích xuất dữ liệu từ HTML.
- [selenium](https://selenium-python.readthedocs.io/). Vì trong quá trình sử dụng mình cần đăng nhập tài khoản chứng thực nên mình chọn sử dụng selenium thay vì [request](https://docs.python-requests.org/en/latest/) để không phải xử lý dữ liệu gửi lên server.
- [SQLite](https://docs.python.org/3/library/sqlite3.html) - cơ sở dữ nhẹ nhất nhưng vẫn có tốc độ xử lý vượt trội.
- [DB Browser for SQLite](https://sqlitebrowser.org/) (không bắt buôc) - Cung cấp giao diện trực quan khi sử dụng hoặc truy vấn cơ sở dữ liệu. 
  
##### Qúa trình từng bước

1. Xác định url để tải file HTML của dữ liệu

Ta có url của người dùng(sinh viên, giảng viên):

```
https://courses.uit.edu.vn/user/profile.php?id=xxx
```
Trong đó xxx là index của sinh viên, ví dụ index của mình là 1276 thì ta có link là <https://courses.uit.edu.vn/user/profile.php?id=12762>.

![my profile](https://raw.githubusercontent.com/Huythanh0x/crawl_uit_data/master/images/user_profile_example.png)

Và ta có url của course(khóa học) AI của thầy Lương Ngọc Hoàng:

```
https://courses.uit.edu.vn/course/view.php?id=yyy
```
Trong đó yyy là index của khóa học, ví dụ index của khóa học Trí tuệ nhân tạo của thầy Lương Ngọc Hoàng trong học kỳ 2 năm 2020-2021 là 7181 thì ta có link là <https://courses.uit.edu.vn/course/view.php?id=7181>

![Luong Ngoc Hoang's course](https://raw.githubusercontent.com/Huythanh0x/crawl_uit_data/master/images/course_example.png)

Sau khi đã xác định được url để lấy dữ liệu ta cần tìm kiếm giới hạn của index trải dài từ đâu đến đâu. Sau một lúc thử bằng phương pháp Binary Search thì mình thấy được `index của user cuối` là **17663** và `index của khóa học cuối` là **9330**.

1. Xác định các thông tin mình nhận được
Từ url đến khóa học thì ta có thể xác định một số thông tin sau:

- index của khóa học
- Tên môn học
- Mã môn học
- Thời gian của khóa học(học kỳ và năm học)
- Giảng viên của khóa học

Từ url đến user thì ta xác định được một số thông tin sau:
- index của user
- mã số sinh viên
- email
- lớp học(nếu là sinh viên)
- hình ảnh
- lần đầu truy cập trang web, lần cuối truy cập trang web
- danh sách các môn người dùng có tham gia(học nếu là sinh viên, giảng dạy nếu là giảng viên)
  
Một số nhận xét về các dữ liệu phía trên:
- Có một số môn học hỗ trợ không phải môn học chính nên không có mã môn học và do vét cạn nên sẽ có các khóa học của học viên cao học dẫn đến việc nhiễu loạn khi bóc tách html để lấy dữ liệu.
- Trong cùng một kỳ có thể có thể mở nhiều lớp của cùng một môn. Các lớp này thì có mã môn và index khác nhau.
- Một giảng viên có thể dạy nhiều môn học và một môn học có thể có nhiều giảng viên. Trong một kỳ thì giảng viên có thể dạy cùng lúc nhiều môn.
- Một sinh viên có thể học một môn nhiều lần(học lại hoặc học cải thiện), nhưng một kỳ chỉ tham gia một môn học một lần.
- Một số môn học lại không có đề cập đến thời gian diễn ra của khóa học.
- Sinh viên có khả năng ẩn email của bản thân nên có thể sẽ không xác định được địa chỉ của một số người.
- Mã số sinh viên được xác định dựa trên email của sinh viên nên nếu email bị ẩn thì mã số sinh viên cũng không thể xác định được.
- Có nhiều sinh viên, giảng viên bị xóa tài khoản do bị đình chỉ học/chuyển trường,...

3. Thiết kế cơ sở dữ liệu

Dựa vào các dữ liệu trên ta có thể xác định được rằng có 2 loại dữ liệu chính là **course** (khóa học)) và **user** (người dùng) gồm giảng viên và sinh viên.
Ta có mối quan hệ giũa course và user là quan hệ **n:n** vì vậy ta cần tạo ra một bảng trung gian, mình đặt tên là **enroll**(tham gia). Bởi vì ta có **student**(sinh viên) và **instructor** (giảng viên) có một số điểm khác nhất đinh. Ví dụ sinh viên có mã sinh viên còn giảng viên thì không. Và sinh viên chỉ có 1 lớp(quan hệ **1:1**) học còn giảng viên thì có thể là cố vấn học tập của một hoặc nhiều lớp (quan hệ **1:n**).Bên cạnh đó thì ta cũng thường không truy vấn cả giảng viên và sinh viên cùng lúc, chính vì thế để đảm bảo tính nhất quán, ta sẽ tách bảng user thành student và instructor.

![database schema](https://raw.githubusercontent.com/Huythanh0x/crawl_uit_data/master/images/uit_table.png)

4. Tiến hành code 

Để biết một số syntax cơ bản của `beatutifulSoup` bạn truy cập [link này](https://www.crummy.com/software/BeautifulSoup/bs4/doc/). Đây là tài liệu chính thức trong mục này cung cấp đầy đủ các syntax thường dùng nhất. Bạn chỉ cần code theo ví dụ là hiểu.
Khi đã hiểu được cách hoạt động của `beatutifulSoup` ta có thể dễ dàng áp dụng với từng url của user hoặc course phía trên.

Nhưng để có HTML để trích xuất thì ta cần đăng nhập vào trang web trước. Selenium đã đến đây. Dưới đây là cách khai báo `selenium` cũng như cách giả lập tao tác nhập bàn phím và click chuột để đăng nhập.

<https://gist.github.com/Huythanh0x/e0d0069216296bb13a9f67f2d1dd4532>

Trong thời gian tới mình sẽ viết bài viết hướng dẫn sử dụng `selenium` chi tiết hơn.

Sau khi đã lấy được dữ liệu cũng như trích xuất thành công thì việc tiếp theo là lưu trữ các dữ liệu này vào cơ sở dữ liệu. Dưới đây là đoạn code tạo cơ sở dữ liệu và chèn dữ liệu vào cơ sở dữ liệu dựa vào dữ liệu được trích xuất phía trên.

<https://gist.github.com/Huythanh0x/149338996ef9607a73ceec2c7775afaa>

Bạn có thể đọc tài liệu hướng dẫn sử dụng `SQLite` trong Python [tại đây](https://docs.python.org/3/library/sqlite3.html).
### Tự chạy code

Bạn có thể cập nhập dữ liệu mới bằng cách clone Github repository [tại đây]() và tử chạy code.
Trước khi chạy code bạn cần thay đổi **USER_NAME** và **PASSWORD** trong file `main.py`.
Để chạy code bạn gọi lệnh:

```
python3 main.py
```

### Kết quả

![result preview](https://raw.githubusercontent.com/Huythanh0x/crawl_uit_data/master/images/result_preview.png)

Sau khi kết quả thì ta thu được file `datasbase/database_uit.db`, bạn có thể tải file [tại đây](https://raw.githubusercontent.com/Huythanh0x/crawl_uit_data/master/database/database_uit.db). Bạn có thể sử dụng công cụ [DB Browser for SQLite](https://sqlitebrowser.org/) mình để cập phía trên để truy vấn dữ liệu.
Mình cũng có chuẩn bị một số câu lệnh SQL để truy vấn trong file `sql_query/sql.txt`.

### Tổng kết
Và trên đây mình đã hướng dẫn bạn crawl dữ liệu môn học và dữ liệu sinh viên của UIT bằng cách sử dụng Selenium và BeatutifulSoup cũng như sử dụng SQLite để lưu trữ kết quả.

Bạn có thể làm gì với đống dữ liệu này? Như mình đã nói phía trên thì bạn có thể sử dụng để xem thông tin của các sinh viên khác ví dụ như tên, email, ảnh, số lượng môn học, các môn học mà giảng viên đã dạy, các môn học nào có tỉ lệ học lại lớn, môn học nào chỉ xuất hiện 2 kỳ 1 lần để bạn đăng ký môn học cho thuận tiện...