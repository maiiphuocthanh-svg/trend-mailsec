# Hướng dẫn test thủ công 10 test case: Trend Micro CEGP

Sản phẩm: **Cloud Email Gateway Protection (CEGP)**, TrendAI Vision One.
Mailbox nhận: `opmanager@pocmail.fecredit.com.vn`
Không cần cài Python. Chỉ cần Outlook/webmail, Notepad và PowerShell có sẵn của Windows.

> Tên menu con trên Console có thể khác đôi chút tùy phiên bản và license. Chỗ nào chưa xác minh được từ tài liệu chính thức, tài liệu này có ghi chú **(cần đối chiếu)**.

---

## 0. Chuẩn bị chung (làm 1 lần)

### 0.1 Mẫu test

**GTUBE (spam).** Dán nguyên một dòng này vào nội dung mail:
```
XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X
```

**EICAR (virus).** Mở Notepad, dán nguyên một dòng này, lưu thành `eicar.txt`:
```
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
```
- Đây là file test chuẩn, vô hại.
- Antivirus trên máy có thể xóa file ngay khi lưu. Nếu vậy, nhờ IT thêm thư mục test vào exclusion.
- Nên dùng đuôi `.txt` hoặc `.com`. Trend nhận diện theo nội dung nên đuôi nào cũng được.

### 0.2 Tạo file dung lượng lớn (cho TC3)
Mở **PowerShell** (không cần quyền admin):
```powershell
$f = "$env:USERPROFILE\Desktop\big_15MB.bin"
$b = New-Object byte[] (15MB)
(New-Object Random).NextBytes($b)
[IO.File]::WriteAllBytes($f, $b)
```
Sẽ có file 15 MB trên Desktop. Mail server gửi (Gmail, Exchange) có thể có giới hạn dung lượng riêng. Nếu mail không gửi đi được, giảm ngưỡng trong policy CEGP xuống thấp hơn (ví dụ 1 MB) rồi gửi file nhỏ hơn.

### 0.3 Tạo file ZIP có mật khẩu (cho TC7)
Windows Explorer không tạo được ZIP có mật khẩu. Các cách:
- **7-Zip** (nếu IT cho phép): chuột phải file → 7-Zip → Add to archive → Archive format `zip` → nhập Password → Encryption method `ZipCrypto`.
- **7-Zip bản portable** (giải nén, không cần cài): chạy được ngay nếu GPO không chặn chạy file từ thư mục người dùng.
- **WinRAR** nếu máy đã có sẵn: Add to archive → Set password.
- Nếu GPO chặn tất cả: nhờ IT tạo hộ, hoặc dùng máy cá nhân.

Nên chọn mã hóa **ZipCrypto** (mặc định), vì AES đôi khi không được mọi engine quét hỗ trợ.

### 0.4 Quy ước ghi nhận kết quả
Mỗi test ghi lại: thời gian gửi, subject, kết quả quan sát, ảnh chụp màn hình Console (Quarantine hoặc log) để làm bằng chứng nghiệm thu.

Đặt subject theo quy ước `[TC-xx] Mô tả` để dễ tìm trong log.

---

## TC1: Spam Filtering

**Mục tiêu:** mail spam bị nhận diện và bị cách ly hoặc chặn.

### Cấu hình
1. Vào `Inbound Protection` → `Spam Filtering` → **Spam Policy**.
2. Mở rule (hoặc **Add** rule mới) → tab **Basic Information**: đặt tên, ví dụ `TEST-Spam`, bật rule.
3. Tab **Recipients and Senders**: áp dụng cho `opmanager@pocmail.fecredit.com.vn` (hoặc cả domain).
4. Tab **Scanning Criteria**: tick **Spam**, chọn **Level** (ví dụ `Moderately low`).
5. Tab **Actions**: chọn **Quarantine** (hoặc Block/Delete theo yêu cầu).
6. Lưu rule, đảm bảo rule ở trạng thái **Enabled**.

### Gửi mail
- To: `opmanager@pocmail.fecredit.com.vn`
- Subject: `[TC-01] Spam test GTUBE`
- Body: dán chuỗi GTUBE (mục 0.1), không thêm ký tự nào vào giữa chuỗi.

### Kết quả mong đợi
- Mail **không** xuất hiện trong Inbox.
- Vào menu `Quarantine`: thấy mail với Reason liên quan đến Spam.

### Pass nếu
Mail bị cách ly hoặc chặn đúng theo action đã cấu hình.

---

## TC2: Virus Scan

**Mục tiêu:** phát hiện file chứa mã độc và xử lý, có cảnh báo.

### Cấu hình
1. Vào `Inbound Protection` → `Virus Scan`.
2. Tạo hoặc mở rule virus, kiểm tra tab **Recipients** có bao gồm mailbox đích.
3. Tab **Scanning Criteria**: bật quét malware. Nếu có tùy chọn quét file nén (compressed files) thì bật.
4. Tab **Actions**: chọn một trong hai:
   - **Delete attachment** (loại bỏ file, giữ mail), hoặc
   - **Quarantine message** (cách ly cả mail).
5. Bật **Notification** gửi cảnh báo tới admin hoặc người nhận **(cần đối chiếu tên mục)**.
6. Lưu và Enable rule.

### Gửi mail
- Subject: `[TC-02] Virus test EICAR`
- Đính kèm file `eicar.txt` (mục 0.1).

### Kết quả mong đợi
- Mail bị cách ly, hoặc tới nơi nhưng file đính kèm đã bị gỡ (tùy action).
- Có email cảnh báo (nếu đã bật Notification).
- Log hoặc Quarantine ghi nhận phát hiện virus.

### Pass nếu
EICAR bị phát hiện và xử lý đúng action, có thông báo.

---

## TC3: Content Filtering

**Mục tiêu:** chặn mail vi phạm chính sách nội dung: dung lượng, đính kèm, file nén, file mã hóa.

### Cấu hình
1. Vào `Inbound Protection` → `Content Filtering`.
2. Tạo các rule sau (mỗi rule một điều kiện, để dễ biết rule nào bắt):

| Rule | Điều kiện (Scanning Criteria) | Action |
|------|-------------------------------|--------|
| `TEST-CF-Size` | Kích thước mail hoặc file đính kèm lớn hơn ngưỡng, ví dụ 10 MB | Quarantine |
| `TEST-CF-FileType` | Loại file đính kèm (true file type), ví dụ `.exe`, `.js` | Quarantine |
| `TEST-CF-Archive` | File nén hoặc số lớp nén vượt giới hạn | Quarantine |
| `TEST-CF-Encrypted` | File mã hóa / có mật khẩu | Quarantine |

3. Lưu và Enable từng rule. Tên chính xác các điều kiện **cần đối chiếu** trên màn hình Scanning Criteria của bạn.

### Gửi mail (4 mail)
| Mail | Subject | Đính kèm |
|------|---------|----------|
| 3a | `[TC-03a] Oversize` | `big_15MB.bin` (mục 0.2) |
| 3b | `[TC-03b] FileType` | file đúng loại bị cấm (ví dụ copy một file `.js` đơn giản đổi từ `.txt`) |
| 3c | `[TC-03c] Archive` | file ZIP bất kỳ (không mật khẩu) |
| 3d | `[TC-03d] Encrypted` | ZIP có mật khẩu (mục 0.3) |

> Khi test 3d, nếu **File Password Analysis** (TC7) đang bật và mở được file, rule Encrypted có thể không khớp. Để test 3d riêng, tạm tắt File Password Analysis.

### Kết quả mong đợi
Mỗi mail bị Block hoặc Quarantine, và trên Console có lý do (tên rule vi phạm).

### Pass nếu
Cả 4 loại vi phạm đều bị bắt và có lý do hiển thị.

---

## TC4: Phishing Filtering

**Mục tiêu:** email lừa đảo hoặc giả mạo bị phát hiện và chặn/cách ly.

### Cấu hình
1. Vào `Inbound Protection` → `Spam Filtering` → **Spam Policy** → rule của bạn (hoặc rule mới).
2. Tab **Scanning Criteria**, tick:
   - **Phishing and other suspicious content**
   - **Business Email Compromise (BEC)**, chọn cách áp dụng (muốn nhạy hơn thì chọn *BEC attacks suspected by Antispam Engine*)
   - **Social engineering attack**
   - (tùy chọn) **Web reputation**
3. Với BEC: bấm link **High Profile Users**, thêm tên và email của một người quan trọng giả định (ví dụ CEO).
4. Tab **Actions**: Quarantine.
5. Lưu, Enable.

### Gửi mail
**Cách A (đơn giản nhất): giả mạo tên hiển thị.**
- Từ Gmail, đổi tên hiển thị tài khoản gửi thành đúng tên High Profile User (ví dụ `Nguyen Van A - CEO`).
- Subject: `[TC-04] KHAN CAP: yeu cau chuyen khoan`
- Body (mẫu):
  ```
  Chao ban,
  Toi dang hop khan. Hay chuyen ngay 200.000.000 VND vao tai khoan duoi day va khong goi lai cho toi.
  Tai khoan: 0123456789 - Ngan hang ABC
  ```

**Cách B (giả mạo phishing):**
- Subject: `[TC-04] Tai khoan cua ban bi khoa`
- Body: nội dung dọa khóa tài khoản, yêu cầu xác minh trong 24 giờ, kèm link giả, ví dụ `http://secure-verify-login.example.com/verify`.

**Giả mạo địa chỉ From thật sự** (spoofing) không làm được từ Gmail hoặc Outlook thường. Cần gửi trực tiếp tới máy chủ MX của CEGP bằng công cụ SMTP. Nếu cần, nhờ IT hoặc dùng máy được phép; tài liệu này chỉ kiểm thử bằng cách A và B.

### Kết quả mong đợi
Mail bị cách ly với lý do phishing hoặc BEC.

### Pass nếu
Ít nhất một trong hai mail A/B bị bắt đúng lý do.

> Lưu ý: mail từ sender nằm trong **Approved Senders** sẽ không bị áp dụng các rule heuristic spam/phishing/BEC. Hãy chắc là địa chỉ gửi không nằm trong danh sách approved.

---

## TC5: Sandboxing (Virtual Analyzer)

**Mục tiêu:** file high-risk được gửi vào môi trường ảo phân tích hành vi, có báo cáo.

### Điều kiện
- Cần license có **sandbox / Virtual Analyzer / Advanced Threat Protection**. Nếu menu không có mục này thì test này **không thực hiện được** (ghi nhận N/A kèm lý do thiếu license).

### Cấu hình
1. Tìm mục sandbox / Virtual Analyzer trong `Inbound Protection` (thường nằm gần `Virus Scan`; **cần đối chiếu** vị trí chính xác).
2. Bật phân tích, chọn loại file gửi vào sandbox (executable, document, script, file nén).
3. Action khi kết quả độc hại: Quarantine. Lưu và Enable.

### Gửi mail
- Subject: `[TC-05] Sandbox test`
- Đính kèm một file thuộc loại được gửi vào sandbox.
- **Lưu ý trung thực:** EICAR là file test của antivirus, bị bắt ngay bởi pattern nên **không chứng minh được hành vi sandbox**. Để thấy sandbox thật sự chạy, cần mẫu mà engine thường không nhận diện nhưng có hành vi đáng ngờ. Mẫu như vậy phải lấy từ nguồn Trend cung cấp hoặc hỏi Trend support/SE; tài liệu này không tự tạo mã độc.

### Kết quả mong đợi
Log và báo cáo phân tích sandbox hiển thị trên Console, mail bị xử lý theo action nếu kết quả độc hại.

### Pass nếu
Thấy bản ghi phân tích sandbox cho file đã gửi.

---

## TC6: Whitelist / Blacklist (IP, Geo-IP, Sender)

**Mục tiêu:** chặn nguồn trong blacklist, cho phép nguồn trong whitelist.

### 6a. Blacklist theo Sender
1. Vào `Inbound Protection` → `Connection Filtering` → `Sender Filter` ([KB Trend](https://success.trendmicro.com/en-US/solution/KA-0012059)).
2. Tab **Blocked Senders** → **Add** → nhập địa chỉ Gmail đang dùng để gửi test (hoặc domain `gmail.com` nếu chấp nhận ảnh hưởng, **không nên** với môi trường thật).
3. Lưu.
4. Gửi mail subject `[TC-06a] Blocked sender` từ địa chỉ đó.
5. **Mong đợi:** mail bị chặn, không vào Inbox, có log.

### 6b. Whitelist theo Sender
1. Cùng màn hình → tab **Approved Senders** → **Add** địa chỉ Gmail gửi test. Xóa địa chỉ này khỏi Blocked Senders trước.
2. Gửi mail chứa GTUBE, subject `[TC-06b] Approved sender + GTUBE`.
3. **Mong đợi:** mail **không bị chặn bởi lọc spam** (đúng thiết kế: approved sender bỏ qua IP reputation và lọc nội dung spam), nhưng vẫn bị quét malware.
4. Bổ sung kiểm tra: gửi thêm mail đính kèm EICAR từ địa chỉ approved. **Mong đợi:** vẫn bị bắt virus.

### 6c. IP / Quốc gia (Geo-IP)
1. Trong `Connection Filtering`, tìm mục **IP Reputation** và mục lọc theo IP/quốc gia **(cần đối chiếu có Geo-IP theo license hay không)**.
2. Thêm IP hoặc quốc gia vào danh sách chặn.
3. Gửi từ nguồn có IP hoặc quốc gia đó. Gmail dùng dải IP của Google nên **khó chủ động chọn IP**; muốn test IP cụ thể cần gửi từ máy chủ mail do bạn kiểm soát.
4. **Mong đợi:** kết nối hoặc mail từ IP/quốc gia trong blacklist bị chặn. Với whitelist đối tác: thêm IP của đối tác vào danh sách cho phép rồi xác nhận mail được nhận.

### Pass nếu
Blacklist chặn được, whitelist cho qua đúng thiết kế. Nhớ **dọn lại** các mục đã thêm sau khi test.

---

## TC7: File Password Analysis

**Mục tiêu:** tự đọc mật khẩu trong nội dung thư, giải nén và quét mã độc bên trong.

### Cấu hình
1. Vào `Inbound Protection` → `Virus Scan` → **File Password Analysis**.
2. Tick **Enable file password analysis**.
3. **Analysis timeout**: để 5 phút (mặc định).
4. (Tùy chọn) **Hold on a message to associate later messages**: chỉ cần khi mật khẩu gửi ở mail riêng.
5. **User-Defined Passwords**: để **trống** cho kịch bản A.
6. Lưu. Đảm bảo rule **Virus Scan** (TC2) đang bật, vì File Password Analysis chỉ mở file, việc bắt EICAR do Virus Scan làm.

### Gửi mail
Làm 2 kịch bản:

**Kịch bản A: CEGP tự dò mật khẩu trong nội dung**
1. Nén `eicar.txt` thành `protected.zip` với mật khẩu `infected` (mục 0.3).
2. Mail: Subject `[TC-07A] Password in body`, body có dòng: `Mat khau giai nen la: infected`. Đính kèm `protected.zip`.

**Kịch bản B: dùng danh sách mật khẩu khai báo sẵn**
1. Vào **User-Defined Passwords** → **Add** mật khẩu `Test@2026` (hoặc Import danh sách).
2. Nén `eicar.txt` với mật khẩu `Test@2026`. Mail **không** ghi mật khẩu trong nội dung.
3. Subject `[TC-07B] Password from user-defined list`.

### Kết quả mong đợi
Cả hai mail bị phát hiện EICAR bên trong file nén và xử lý theo action của Virus Scan.

### Pass nếu
- A: bắt được dù mật khẩu chỉ nằm trong body.
- B: bắt được dù body không ghi mật khẩu.

> CEGP không có từ điển mật khẩu dựng sẵn. Mật khẩu phải nằm trong email hoặc trong danh sách bạn khai báo.

---

## TC8: Time-of-Click Protection

**Mục tiêu:** link trong mail được bảo vệ; click vào link độc sẽ hiện trang cảnh báo.

### Cấu hình
1. Vào `Inbound Protection` → `Spam Filtering` → **Spam Policy** → rule của bạn. Bật **Time-of-Click Protection** ([tài liệu Trend](https://docs.trendmicro.com/en-us/documentation/article/trend-vision-one-toc-protection-email-security)): khi bật trong spam policy, CEGP viết lại URL trong mail để phân tích tại thời điểm click.
2. Chọn hành động khi URL độc hại (chặn hoặc hiện trang cảnh báo, tùy lựa chọn có trên màn hình) **(cần đối chiếu tên mục)**.
3. Lưu, Enable.

### Gửi mail
- Subject: `[TC-08] Time of click`
- Body chứa 2 link:
  1. Link sạch, ví dụ `https://www.trendmicro.com`.
  2. Link độc hại **dùng để test**. Cần một URL mà dịch vụ web reputation của Trend đánh giá là nguy hiểm. Tài liệu chính thức không công bố URL này nên bạn cần **lấy từ Trend (support hoặc kỹ sư pre-sales)**. Không tự dùng link độc thật.

### Kiểm tra
1. Mở mail nhận được (nếu mail không bị cách ly bởi rule khác).
2. Rê chuột lên link: URL thật đã bị đổi thành địa chỉ trung gian của Trend (đã rewrite).
3. Click link sạch: truy cập bình thường.
4. Click link độc: hiện trang cảnh báo chặn.

### Pass nếu
Link bị rewrite, link độc bị chặn bằng trang cảnh báo.

> Nếu mail bị rule Spam/Phishing cách ly trước, bạn không mở được để click. Hãy dùng subject và nội dung "sạch" cho test này để mail được giao.

---

## TC9: Dashboard & Threat Visibility

**Mục tiêu:** xem tổng quan an ninh email theo thời gian thực.

### Thực hiện
1. Hoàn tất TC1–TC8, chờ vài phút để dữ liệu cập nhật.
2. Vào `Dashboard`.
3. Chụp ảnh các phần: biểu đồ lưu lượng mail, top mối đe dọa (Spam / Virus / Phishing), thời gian chọn xem.
4. Đối chiếu số liệu với các mail đã gửi (ví dụ spam tăng 1, virus tăng 1...).
5. Tra log chi tiết từng sự kiện: dùng menu `Quarantine` và các mục log/tracking trong CEGP **(cần đối chiếu tên menu log)**; tìm theo subject `[TC-xx]`.

### Pass nếu
Dashboard hiển thị biểu đồ và top threats khớp với các mail test, tra được log chi tiết.

---

## TC10: Report Generation & Scheduling

**Mục tiêu:** xuất báo cáo và tự động gửi định kỳ cho Administrator.

### Thực hiện
1. Tìm mục báo cáo (Reports) trên Console **(cần đối chiếu vị trí; không nằm trong 5 menu bạn đã gửi ảnh, có thể ở phần cuộn xuống dưới)**.
2. Tạo báo cáo tổng quan: chọn khoảng thời gian bao gồm lúc chạy test, xuất file (PDF/CSV/HTML tùy tùy chọn có).
3. Tạo báo cáo chi tiết (ví dụ theo từng loại đe dọa).
4. Tạo **lịch gửi tự động**: chọn tần suất ngày, tuần hoặc tháng; nhập email Administrator nhận báo cáo.
5. Với mục đích test nhanh: đặt lịch gần nhất có thể (nếu hệ thống cho phép) để thấy mail báo cáo.

### Pass nếu
Xuất được báo cáo tổng quan và chi tiết; admin nhận được mail báo cáo theo lịch.

---

## Bảng ghi nhận kết quả

| TC | Mail đã gửi (subject) | Giờ gửi | Kết quả thực tế | Pass/Fail | Ảnh bằng chứng |
|----|----------------------|---------|-----------------|-----------|----------------|
| 1 | [TC-01] ... | | | | |
| 2 | [TC-02] ... | | | | |
| 3a-3d | [TC-03a..d] ... | | | | |
| 4 | [TC-04] ... | | | | |
| 5 | [TC-05] ... | | | | |
| 6a-6c | [TC-06a..c] ... | | | | |
| 7A, 7B | [TC-07A/B] ... | | | | |
| 8 | [TC-08] ... | | | | |
| 9 | (xem Dashboard) | | | | |
| 10 | (xem Reports) | | | | |

---

## Khắc phục sự cố thường gặp

| Hiện tượng | Nguyên nhân thường gặp |
|------------|------------------------|
| Không thấy mail trong Quarantine | Chưa Enable rule, rule không áp dụng cho mailbox đích, hoặc MX của domain chưa trỏ qua CEGP (kiểm tra mục `Domains`) |
| Mail vào thẳng Inbox dù có GTUBE/EICAR | Sender nằm trong Approved Senders; hoặc mail đã bị mail server gửi chặn/làm sạch trước khi tới CEGP |
| Gmail/Outlook không cho gửi file EICAR | Dịch vụ gửi tự chặn. Gửi từ máy chủ mail khác hoặc nén file lại |
| Không gửi được file lớn | Giới hạn dung lượng của dịch vụ gửi. Giảm ngưỡng trong policy CEGP rồi gửi file nhỏ hơn |
| Rule này che rule kia | Nhiều rule cùng khớp thì chỉ một rule xử lý trước. Tắt các rule không liên quan khi test từng case |
