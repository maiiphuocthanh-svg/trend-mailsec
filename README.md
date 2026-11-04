# Bộ Test Trend Micro Cloud Email Gateway Protection (CEGP)

Tài liệu kiểm thử 10 tính năng bảo mật email trên **Cloud Email Gateway Protection (CEGP)**, thuộc TrendAI Vision One.

> ⚠️ **An toàn:** chỉ dùng mẫu test chuẩn, vô hại: **EICAR** (file test antivirus) và **GTUBE** (chuỗi test spam). Không dùng mã độc thật.

CEGP là **gateway inline**: mail đi qua CEGP (qua MX) rồi mới tới hộp thư. Menu chính: `Dashboard`, `Domains`, `Inbound Protection`, `Outbound Protection`, `Quarantine`.

---

## 📁 Các file trong repo

| File | Mô tả |
|------|-------|
| `HUONG_DAN_THU_CONG.md` | **Hướng dẫn từng bước cho 10 test case** (cấu hình, gửi mail, kiểm tra, bảng ghi kết quả) |
| `GIAI_THICH_POLICY.md` | Giải thích từng policy trên CEGP theo test case |
| `payloads.py` | Chuỗi EICAR, GTUBE để copy |
| `send_tests.py`, `config.ini`, `requirements.txt` | Script Python gửi mail tự động (**tùy chọn**, chỉ dùng được nếu máy cài được Python) |

> Máy bị GPO chặn cài Python thì dùng cách **thủ công** bên dưới, không cần script.

---

## ✋ Cách làm thủ công (không cần cài gì)

### Mẫu dùng để gửi

**GTUBE (TC1 - Spam):** dán nguyên chuỗi sau vào nội dung mail (một dòng, không xuống dòng):
```
XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X
```

**EICAR (TC2, TC5, TC7 - Virus):** tạo file bằng Notepad, dán nguyên một dòng sau, lưu thành `eicar.com` (hoặc `eicar.txt`):
```
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
```
Antivirus trên máy có thể xóa file này ngay khi tạo. Nếu vậy, hãy tạm thêm thư mục đó vào exclusion hoặc nhờ bộ phận IT hỗ trợ.

### Gửi mail
Soạn mail bằng Outlook hoặc webmail, gửi tới mailbox đích `opmanager@pocmail.fecredit.com.vn`.

---

## 🧪 10 test case: cấu hình, cách gửi, nơi kiểm tra

Chi tiết từng option của policy xem trong `GIAI_THICH_POLICY.md`.

| # | Test case | Cấu hình trên CEGP | Cách gửi mail test | Kiểm tra |
|---|-----------|--------------------|--------------------|----------|
| 1 | Spam | `Inbound Protection > Spam Filtering > Spam Policy`: bật **Spam**, Actions = Quarantine | Dán chuỗi GTUBE vào body | `Quarantine`: Reason = Spam |
| 2 | Virus | `Inbound Protection > Virus Scan`: bật rule, action Delete attachment hoặc Quarantine, bật notification | Đính kèm file EICAR | `Quarantine` / log: phát hiện virus |
| 3 | Content Filtering | `Inbound Protection > Content Filtering`: rule theo size, true file type, file nén, file mã hóa | Gửi file lớn hơn ngưỡng, file nén, file mã hóa | Mail bị chặn/cách ly kèm lý do |
| 4 | Phishing | Spam Policy: bật **Phishing and other suspicious content**, BEC, Social engineering attack | Mail giả From + nội dung lừa đảo + link giả | `Quarantine`: lý do phishing/BEC |
| 5 | Sandboxing | Bật Virtual Analyzer nếu có trong menu `Inbound Protection` (cần license) | Gửi file high-risk | Báo cáo phân tích sandbox |
| 6 | Whitelist/Blacklist | `Inbound Protection > Connection Filtering` (Sender Filter, IP Reputation) | Gửi mail từ sender/IP đã thêm vào danh sách | Blocked: bị chặn. Approved: mail đi qua |
| 7 | File password | `Inbound Protection > Virus Scan > File Password Analysis`: bật, timeout 5 phút | ZIP có mật khẩu chứa EICAR, ghi mật khẩu trong body | Mail bị bắt do EICAR bên trong |
| 8 | Time-of-Click | Bật Time-of-Click Protection trong Spam Policy | Mail chứa URL | URL bị rewrite, click link độc sẽ ra trang cảnh báo |
| 9 | Dashboard | `Dashboard` | Không cần gửi thêm | Biểu đồ traffic, top threats, log |
| 10 | Report | Mục báo cáo trên Console | Không cần gửi thêm | Xuất report, lên lịch gửi cho Admin |

> Tên menu con có thể khác đôi chút tùy phiên bản/license (đặc biệt TC5 và Geo-IP của TC6). Nếu không thấy menu, hãy kiểm tra license hoặc mở menu `Inbound Protection` để đối chiếu.

---

## ⚙️ (Tùy chọn) Dùng script Python

Chỉ khi máy cài được Python 3.8+:
1. Tạo Gmail **App Password** (bật 2FA, vào https://myaccount.google.com/apppasswords).
2. Sửa `config.ini`: `username`, `app_password`, `to`.
3. Chạy `python send_tests.py` (tất cả) hoặc `python send_tests.py 1 2 4` (chọn case).

Gmail có thể tự chặn việc gửi EICAR hoặc file lớn trước khi tới CEGP. Khi đó hãy gửi từ máy chủ mail khác (M365 hoặc relay nội bộ).
