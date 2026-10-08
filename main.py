import cloudscraper
import time
import re

url_main = 'https://www.tqsqk7.edu.vn/tu-truong-qsqk7-den-dat-thep-cu-chi-hanh-trinh-tim-hieu-mat-ma-long-dan-cua-tuoi-tre-fpt-cicei-p.html'

num_requests = 50  

# Khởi tạo công cụ giả lập trình duyệt vượt Cloudflare
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

# Headers tiêu chuẩn khi tải trang chủ
headers_main = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="154", "Microsoft Edge";v="154", "Not A(Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1'
}

# Headers đặc trưng của yêu cầu AJAX gửi lên post-view (Dựa theo lệnh curl của bạn)
headers_post_view = {
    'accept': 'text/html, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'priority': 'u=1, i',
    'referer': url_main,
    'sec-ch-ua': '"Chromium";v="154", "Microsoft Edge";v="154", "Not A(Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'x-requested-with': 'XMLHttpRequest'  # Bắt buộc phải có để server hiểu là AJAX request
}

print(f"--- Bắt đầu quy trình tự động lấy Session và gửi Post-View ---")

for i in range(num_requests):
    try:
        # BƯỚC 1: Xóa cookie cũ để đóng vai trò người dùng mới hoàn toàn
        scraper.cookies.clear()
        
        # Gửi request lên trang chủ để lấy PHPSESSID và mã nguồn HTML
        response_main = scraper.get(url_main, headers=headers_main, timeout=15)
        new_sessid = response_main.cookies.get('PHPSESSID')
        
        print(f"\n[Lần {i+1}] ----------------------------------------")
        if new_sessid:
            print(f"   => Khởi tạo thành công PHPSESSID mới: {new_sessid}")
        else:
            print("   ⚠️ Không nhận được PHPSESSID mới từ server.")
            
        # BƯỚC 2: Trích xuất mã v từ nội dung HTML trả về
        html_content = response_main.text
        match = re.search(r'post-view\.html\?v=([a-zA-Z0-9_./=\-+]+)', html_content)
        
        if match:
            full_v_code = match.group(1)
            print(f"   => Bắt được mã v tương ứng: {full_v_code}")
            
            # Đường dẫn API post-view mới kết hợp với mã v vừa bắt được
            url_post_view = f"https://www.tqsqk7.edu.vn/post-view.html?v={full_v_code}"
            
            # Giả lập thời gian chờ ngầm (ví dụ: nghỉ 1-2 giây để giống hành vi đọc bài của con người)
            #time.sleep(1)
            
            # BƯỚC 3: Tự động gửi request post-view lên server 
            # (Lúc này cookie PHPSESSID mới tự động được đính kèm bên trong đối tượng scraper)
            response_ajax = scraper.get(url_post_view, headers=headers_post_view, timeout=15)
            
            print(f"   => Gửi AJAX lên post-view.html - Status: {response_ajax.status_code}")
            # Bạn có thể in response_ajax.text nếu muốn xem kết quả xử lý của server (ví dụ: thành công/thất bại)
            
        else:
            print("   ⚠️ Không tìm thấy liên kết 'post-view.html?v=' để gửi tiếp.")
        
        # Khoảng nghỉ an toàn giữa các vòng lặp lớn
        #time.sleep(2)
            
    except Exception as e:
        print(f"Lần {i+1} - Quy trình gặp lỗi: {e}")
