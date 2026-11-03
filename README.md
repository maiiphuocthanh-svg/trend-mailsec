# Bộ Script Test Trend Micro Cloud App Security (CAS)

Công cụ gửi **10 loại email test** qua **Gmail SMTP** tới mailbox đích để kiểm thử các tính năng bảo mật của **Trend Micro Cloud App Security**.

> ⚠️ **An toàn:** Bộ script dùng các mẫu test **chuẩn công nghiệp, hoàn toàn vô hại** — **EICAR** (file test antivirus chuẩn) và **GTUBE** (chuỗi test spam chuẩn). **Không** chứa mã độc thật hay link phishing thật. Đây là các mẫu được chính Trend Micro và mọi hãng AV công nhận để kiểm tra chức năng phát hiện.

---

## 📁 Cấu trúc file

| File | Mô tả |
|------|-------|
| `send_tests.py` | Script chính — gửi email test |
| `payloads.py` | Chứa các mẫu test chuẩn (EICAR, GTUBE...) |
| `config.ini` | **File cấu hình — bạn cần sửa trước khi chạy** |
| `requirements.txt` | Thư viện tùy chọn (chỉ cho ZIP mã hóa) |
| `README.md` | File hướng dẫn này |

---

## 🪟 Hướng dẫn chạy trên Windows

### Bước 1 — Cài Python

1. Tải Python 3.8+ tại https://www.python.org/downloads/
2. Khi cài, **tích vào ô `Add Python to PATH`**.
3. Mở **Command Prompt** (gõ `cmd` ở Start Menu), kiểm tra:
   ```cmd
   python --version
   ```

### Bước 2 — Lấy Gmail App Password (BẮT BUỘC)

Gmail **không** cho dùng mật khẩu thường để gửi qua SMTP. Phải tạo **App Password**:

1. Bật **Xác minh 2 bước (2-Step Verification)** cho tài khoản Gmail:
   https://myaccount.google.com/security
2. Vào trang App Passwords: https://myaccount.google.com/apppasswords
3. Đặt tên bất kỳ (vd: `CAS Test`) → bấm **Create**.
4. Google hiển thị **16 ký tự** (dạng `abcd efgh ijkl mnop`).
5. Copy 16 ký tự này (**bỏ dấu cách** khi dán vào config).

### Bước 3 — Cấu hình `config.ini`

Mở file `config.ini` bằng Notepad, sửa các dòng:

```ini
[smtp]
username = your_gmail@gmail.com        ; Gmail dùng để GỬI
app_password = abcdefghijklmnop        ; App Password 16 ký tự (bỏ dấu cách)

[recipient]
to = opmanager@pocmail.fecredit.com.vn ; Mailbox ĐÍCH (được CAS bảo vệ)
```

### Bước 4 — (Tùy chọn) Cài thư viện cho ZIP mã hóa

Chỉ cần nếu muốn test file nén **mã hóa thật** (test case #7):
```cmd
pip install pyzipper
```
Nếu bỏ qua, script vẫn chạy nhưng tạo ZIP không mã hóa.

### Bước 5 — Chạy script

Mở Command Prompt tại thư mục chứa script:
```cmd
cd đường\dẫn\tới\thư-mục
```

| Lệnh | Tác dụng |
|------|----------|
| `python send_tests.py` | Gửi **tất cả** test case tự động (1,2,3,4,5,7,8) |
| `python send_tests.py 1 2 4` | Chỉ gửi test case **1, 2, 4** |
| `python send_tests.py --list` | Liệt kê danh sách test case |
| `python send_tests.py --help` | Xem hướng dẫn lệnh |

---

## 🧪 Chi tiết 10 Test Case

| # | Tên | Loại | Payload gửi đi | Kiểm tra kết quả trên Console |
|---|-----|------|----------------|-------------------------------|
| 1 | **Spam Filtering** | 🤖 Tự động | Email chứa chuỗi **GTUBE** | `Logs > Quarantine Query` → Reason = Spam |
| 2 | **Virus Scan** | 🤖 Tự động | Đính kèm file **EICAR** (`eicar.com`) | `Logs > Security Risk` → phát hiện virus |
| 3 | **Content Filtering** | 🤖 Tự động | Đính kèm file ~12MB | Policy dung lượng → Block/Quarantine kèm lý do |
| 4 | **Phishing Filtering** | 🤖 Tự động | Giả mạo `From` + nội dung lừa đảo mẫu | `Logs` → Reason = Phish / Spoofing |
| 5 | **Sandboxing** | 🤖 Tự động | File high-risk (EICAR trong ZIP) | `Logs > Virtual Analyzer` → kết quả phân tích |
| 6 | **Whitelist/Blacklist** | ✋ Thủ công | *Xem hướng dẫn bên dưới* | Theo chính sách allow/block |
| 7 | **Password file** | 🤖 Tự động | ZIP có mật khẩu + EICAR, mật khẩu ghi trong body | Hệ thống bóc mật khẩu → quét → phát hiện EICAR |
| 8 | **Time-of-Click** | 🤖 Tự động | Email chứa URL test | URL được rewrite; click → trang cảnh báo |
| 9 | **Dashboard** | ✋ Thủ công | *Xem hướng dẫn bên dưới* | `Dashboard` hiển thị biểu đồ & top threats |
| 10 | **Report** | ✋ Thủ công | *Xem hướng dẫn bên dưới* | Xuất & lên lịch gửi báo cáo |

---

## ✋ Hướng dẫn các Test Case thủ công

Các test này **không gửi mail tự động** vì phụ thuộc vào cấu hình/thao tác trên Console.

### #6 — Whitelist / Blacklist (IP hoặc Geo-IP)

CAS dùng **Approved/Blocked Senders** và **Sender Filtering**.

**Test Blacklist (chặn):**
1. Trên Console: `Advanced Threat Protection` / `Policy` → thêm địa chỉ/domain gửi test vào **Blocked Senders** (hoặc chặn theo quốc gia nếu bản có Geo-IP).
2. Chạy: `python send_tests.py 1` (gửi 1 mail bất kỳ từ địa chỉ đã chặn).
3. **Kỳ vọng:** mail bị chặn/cách ly theo rule blacklist.

**Test Whitelist (cho phép):**
1. Thêm địa chỉ Gmail gửi vào **Approved Senders**.
2. Chạy lại test spam `python send_tests.py 1`.
3. **Kỳ vọng:** mail được cho qua dù trùng mẫu spam (tùy mức ưu tiên policy).

> 💡 Để test theo **IP/Quốc gia**, cấu hình trong phần Sender Filtering / IP Reputation. Gmail dùng dải IP của Google nên muốn test IP cụ thể bạn nên gửi từ relay/IP mà bạn kiểm soát.

### #9 — Dashboard & Threat Visibility

1. Sau khi chạy các test #1–#8 và đợi vài phút để CAS xử lý.
2. Trên Console: `Dashboard`.
3. **Kỳ vọng:** thấy biểu đồ lưu lượng mail, widget **Top Threats** (Spam/Virus/Phishing tăng), và log sự kiện chi tiết.

### #10 — Report Generation & Scheduling

1. Trên Console: `Reports`.
2. **Xuất thủ công:** `Generate Report` → chọn khoảng thời gian → export PDF/CSV.
3. **Lên lịch:** `Scheduled Reports` → tạo lịch Daily/Weekly/Monthly → nhập email Administrator nhận báo cáo.
4. **Kỳ vọng:** báo cáo tổng quan/chi tiết được tạo và gửi định kỳ qua email.

---

## 🔍 Kiểm tra kết quả nhanh

Sau khi chạy, vào **CAS Console**:

- **Quarantine:** `Logs > Quarantine Query` — xem các mail bị cách ly (giống ảnh bạn gửi, cột `Reason` và `Rule`).
- **Security Risk:** `Logs > Security Risk Scan` — virus/malware.
- **Virtual Analyzer:** `Logs > Virtual Analyzer` — kết quả sandbox.
- **Dashboard:** tổng quan threats.

---

## ❓ Khắc phục sự cố

| Lỗi | Nguyên nhân & cách sửa |
|-----|------------------------|
| `SMTPAuthenticationError` | Chưa bật 2FA hoặc dùng sai App Password. Tạo lại App Password. |
| `python không được nhận diện` | Chưa cài Python hoặc chưa Add to PATH. Cài lại và tích ô PATH. |
| Mail virus/content bị **chính Gmail** chặn trước khi gửi | Gmail có thể từ chối gửi EICAR/file lớn. Xem mục dưới. |
| Không thấy mail trong Quarantine | Đợi vài phút (CAS quét post-delivery); kiểm tra đúng mailbox đích. |

> ⚠️ **Lưu ý về Gmail:** Gmail có thể **tự chặn** việc GỬI file EICAR hoặc file quá lớn từ phía nó (trước khi tới CAS). Nếu gặp tình huống này, bạn nên gửi từ một **SMTP relay nội bộ** hoặc tài khoản M365 mà bạn kiểm soát, thay vì Gmail. Script được viết sẵn để dễ đổi `host/port/username` trong `config.ini`.

---

## 📌 Tóm tắt lệnh nhanh

```cmd
:: Xem danh sách
python send_tests.py --list

:: Gửi tất cả test tự động
python send_tests.py

:: Gửi riêng test virus + spam
python send_tests.py 1 2
```
