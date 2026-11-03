# 📖 Giải Thích Chi Tiết Từng Policy — Cloud Email Gateway Protection (CEGP)

Tài liệu giải thích **từng tùy chọn cấu hình** bên trong mỗi policy, tương ứng 10 test case bảo mật email.

> **Cấu trúc chung của mọi policy:** mỗi rule gồm 3 phần → **Recipients** (áp cho ai) + **Scanning Criteria** (điều kiện phát hiện) + **Actions** (hành động khi khớp).
>
> **Thứ tự CEGP xử lý một email đến:**
> `Connection Filtering (IP/Geo)` → `Sender Filter` → `Virus Scan` → `Spam/Phishing` → `Content Filtering`

---

## 🔹 TC1 — Spam Filtering

**Đường dẫn:** `Inbound Protection > Spam Filtering`

### Giải thích từng tùy chọn

| Tùy chọn | Giải thích chi tiết |
|----------|---------------------|
| **Enable spam detection** | Công tắc bật/tắt lọc spam cho policy này. Phải bật để TC1 chạy. |
| **Spam catch rate** | Độ nhạy bắt spam, 4 mức: **High / Medium / Low / Lowest**. Mức càng cao bắt càng nhiều spam nhưng tăng nguy cơ **false positive** (bắt nhầm mail thật). Khuyến nghị bắt đầu ở **Medium** rồi tinh chỉnh. |
| **Graymail detection** | "Graymail" = mail nằm giữa spam và mail hợp lệ (bản tin quảng cáo, newsletter, mail marketing mà bạn từng đăng ký). Có thể xử lý **riêng** với graymail (vd chỉ gắn nhãn thay vì cách ly). |
| **Approved Senders** (mức policy) | Danh sách địa chỉ/domain được tin tưởng — **bỏ qua** kiểm tra spam heuristic. |
| **Blocked Senders** (mức policy) | Danh sách bị chặn thẳng. |

### Actions (hành động khi phát hiện spam)

| Action | Giải thích |
|--------|-----------|
| **Quarantine** | Đưa vào khu cách ly để admin/người dùng xem lại. **Khuyến nghị.** |
| **Delete** | Xóa hẳn, không giữ lại. |
| **Deliver + Tag subject** | Vẫn giao mail nhưng chèn nhãn (vd `[SPAM]`) vào tiêu đề để người nhận cảnh giác. |
| **Pass** | Cho qua, không hành động (dùng khi chỉ muốn ghi log). |

> ⚠️ **Lưu ý quan trọng:** Mail từ **Approved Senders** sẽ **KHÔNG** bị áp dụng các rule heuristic spam/BEC/phishing/web reputation. Đây là lý do khi test whitelist (TC6), mail spam từ địa chỉ đã approve vẫn lọt qua.

**🧪 Cách test:** Gửi mail chứa chuỗi **GTUBE** → mail bị nhận diện Spam → vào `Quarantine`, cột Reason = Spam.

---

## 🔹 TC2 — Virus Scan

**Đường dẫn:** `Inbound Protection > Virus Scan`

### Scanning Criteria (quét những gì)

| Tùy chọn | Giải thích chi tiết |
|----------|---------------------|
| **Cleanable malware** | Mã độc có thể "làm sạch" — gỡ bỏ phần nhiễm và khôi phục file gốc sạch. Áp dụng rule cho loại này. |
| **Uncleanable malware** | Mã độc không thể làm sạch → buộc phải xóa/cách ly. |
| **Mass-mailing virus** | Virus tự phát tán qua email hàng loạt — thường cấu hình hành động mạnh (xóa). |
| **Scan compressed files** | Giải nén file ZIP/RAR để quét bên trong. **BẮT BUỘC bật** nếu muốn bắt EICAR nằm trong file nén (liên quan TC5, TC7). |
| **Compression layers** | Số lớp nén tối đa sẽ giải (vd nén trong nén). Đặt quá cao tốn tài nguyên. |
| **IntelliTrap** | Chặn file **nén thực thi theo thời gian thực** (real-time compressed executable) — một kỹ thuật virus hay dùng để né AV. Bật để tăng bảo vệ. |

### Actions — 2 kiểu

**① ActiveAction (khuyến nghị cho người mới):**
> Trend Micro **tự chọn** hành động tối ưu nhất theo từng loại virus/malware cụ thể. Bạn không phải cấu hình thủ công từng loại.

**② Customized action (tự chọn thủ công):**

| Action | Giải thích |
|--------|-----------|
| **Clean** | Thử làm sạch trước; nếu thất bại → chuyển sang action dự phòng bạn chọn. |
| **Delete matching attachment** | Chỉ xóa **file đính kèm** bị nhiễm, vẫn giao phần còn lại của email. |
| **Quarantine entire message** | Cách ly **toàn bộ** email. |
| **Delete entire message** | Xóa **toàn bộ** email. |
| **Replace with text/file** | Thay file nhiễm bằng một thông báo giải thích. |
| **Pass** | Cho qua (chỉ để ghi log). |

| Tùy chọn bổ sung | Giải thích |
|------------------|-----------|
| **Notification** | Gửi cảnh báo cho admin và/hoặc người nhận khi bắt được virus. Nên bật. |

**🧪 Cách test:** Gửi file **EICAR** (file test AV chuẩn, vô hại) → hệ thống phát hiện mã độc → loại bỏ file / cách ly email + gửi cảnh báo.

---

## 🔹 TC3 — Content Filtering

**Đường dẫn:** `Inbound Protection > Content Filtering`

### Scanning Criteria (lọc theo tiêu chí nào)

| Tùy chọn | Giải thích chi tiết | Khớp yêu cầu |
|----------|---------------------|--------------|
| **Message size** | Giới hạn **dung lượng toàn bộ email**. Vượt ngưỡng → vi phạm. | ✅ dung lượng |
| **Attachment size** | Giới hạn **dung lượng file đính kèm** riêng. | ✅ dung lượng |
| **Attachment true file type** | Lọc theo **loại file THẬT** (đọc chữ ký file), không chỉ theo phần mở rộng. Dù kẻ gửi đổi `virus.exe` → `anh.jpg` vẫn bị nhận ra. | ✅ đính kèm |
| **Number of attachments** | Giới hạn số lượng file đính kèm trong một mail. | ✅ đính kèm |
| **Compressed file** | Lọc **file nén** và số lớp nén. Có thể chặn file nén quá nhiều lớp (dấu hiệu né quét). | ✅ file nén |
| **Password-protected / Encrypted file** | Lọc **file mã hóa/có mật khẩu** — có thể chặn nếu chính sách không cho phép file mã hóa đi vào. | ✅ mã hóa |
| **Keyword / Regular expression** | Lọc theo **từ khóa** hoặc **biểu thức chính quy** trong subject/body (vd chặn mail chứa từ nhạy cảm). | |

### Actions

| Action | Giải thích |
|--------|-----------|
| **Block / Delete** | Chặn hoặc xóa email vi phạm. |
| **Quarantine** | Cách ly kèm **lý do** hiển thị trên Console (vd "exceeds size limit"). |
| **Deliver + Notify** | Vẫn giao nhưng gửi thông báo cảnh báo. |
| **Strip attachment** | Gỡ bỏ file đính kèm vi phạm, giao phần còn lại. |

**🧪 Cách test:** Gửi file đính kèm >10MB (hoặc file mã hóa) → email bị chặn/cách ly kèm lý do vi phạm chính sách hiển thị trên Console.

---

## 🔹 TC4 — Phishing Filtering

**Đường dẫn:**
- `Inbound Protection > Spam Filtering` (tiêu chí Phishing + BEC)
- `Inbound Protection > Domain-based Authentication` (SPF/DKIM/DMARC)

### Các lớp phát hiện — giải thích từng lớp

| Lớp | Giải thích chi tiết |
|-----|---------------------|
| **Phishing criteria** | Phát hiện email lừa đảo điển hình: giả mạo ngân hàng/dịch vụ, dụ nhập thông tin đăng nhập, link giả. |
| **BEC** (Business Email Compromise) | Chống **giả mạo lãnh đạo**. Bạn khai báo **High Profile Users** (CEO, CFO, kế toán trưởng...). CEGP kiểm tra mọi mail "tự xưng" gửi từ những người này để phát hiện mail giả mạo (vd kẻ gian giả sếp yêu cầu chuyển tiền). |
| **High Profile Users** | Danh sách tên + email của nhân sự quan trọng cần được bảo vệ khỏi mạo danh. Khai báo trong global BEC settings. |
| **Social engineering attack** | Phát hiện thủ đoạn thao túng tâm lý (giục gấp, đe dọa, dụ dỗ). |
| **Web Reputation** | Kiểm tra độ tin cậy của các URL/domain trong mail. |

### Domain-based Authentication (chống spoofing)

| Cơ chế | Giải thích |
|--------|-----------|
| **SPF** | Kiểm tra IP gửi có được domain cho phép không. |
| **DKIM** | Kiểm tra chữ ký số xác thực mail không bị sửa và đúng người gửi. |
| **DMARC** | Chính sách tổng hợp dựa trên SPF+DKIM; quyết định xử lý mail giả mạo (none/quarantine/reject). |

### Actions
Giống spam: **Quarantine / Block / Delete / Tag subject**.

**🧪 Cách test:** Gửi mail **giả mạo địa chỉ From** + nội dung lừa đảo → bị bắt với Reason = Phish / BEC / Spoofing.

---

## 🔹 TC5 — Sandboxing (Virtual Analyzer)

**Đường dẫn:** `Inbound Protection > Virus Scan > Virtual Analyzer` (Advanced Threat Protection)

### Cách hoạt động
File **nghi ngờ / high-risk** (chưa có chữ ký virus rõ ràng — vd mã độc zero-day) được gửi tới **Virtual Analyzer** — một **môi trường ảo (sandbox)**. Tại đó file được **chạy thử**, hệ thống **quan sát hành vi** (có cố sửa registry, kết nối máy chủ lạ, mã hóa file...). Nếu hành vi độc hại → chặn.

### Giải thích từng tùy chọn

| Tùy chọn | Giải thích chi tiết |
|----------|---------------------|
| **Enable Virtual Analyzer** | Bật tính năng gửi file đi phân tích sandbox. |
| **File types to submit** | Chọn loại file được đưa vào sandbox: executable, document (Office/PDF), script, file nén... File high-risk nên bật. |
| **Risk level threshold** | Ngưỡng mức rủi ro để quyết định có đưa file đi phân tích hay không. |
| **Action khi phát hiện độc hại** | Thường chọn **Quarantine** và **xuất báo cáo** kết quả phân tích. |
| **Analysis timeout** | Thời gian chờ tối đa cho một lần phân tích. |

> ⚠️ **Yêu cầu license Advanced Threat Protection.** Nếu không thấy menu Virtual Analyzer → license chưa kích hoạt tính năng này.

**🧪 Cách test:** Gửi file high-risk (hoặc EICAR đóng gói) → kiểm tra kết quả tại `Logs > Virtual Analyzer`. Nếu phát hiện hành vi độc → email bị cách ly/chặn + có báo cáo.

---

## 🔹 TC6 — Whitelist / Blacklist

**Đường dẫn:** `Inbound Protection > Connection Filtering`

### 3 cơ chế lọc — giải thích từng cái

| Cơ chế | Vị trí | Giải thích |
|--------|--------|-----------|
| **IP Reputation** | `Connection Filtering > IP Reputation` | Dựa trên **danh tiếng IP nguồn**. CEGP tham chiếu cơ sở dữ liệu IP xấu đã biết của Trend để chặn ngay ở mức kết nối (MTA), trước cả khi nhận nội dung mail. |
| **Geolocation (Geo-IP)** | `Connection Filtering` (nếu license hỗ trợ) | Chặn/cho phép theo **quốc gia** của IP nguồn. Vd chặn toàn bộ mail đến từ các quốc gia không giao dịch. |
| **Sender Filter** | `Connection Filtering > Sender Filter` | Lọc theo **địa chỉ email / domain người gửi** qua 2 tab: **Approved Senders** và **Blocked Senders**. |

### Điểm mấu chốt về thứ tự ưu tiên (rất quan trọng khi test)

| Loại | Hành vi |
|------|---------|
| **Approved Senders (whitelist)** | **Bỏ qua** lọc IP reputation (mức MTA) **và** lọc spam (mức nội dung) → mail đi thẳng tới bước **quét malware**. |
| **Blocked Senders (blacklist)** | **Chặn ngay lập tức**. |

> 💡 Whitelist **không** bỏ qua quét virus — mail từ đối tác tin cậy **vẫn được quét malware** để đảm bảo an toàn. Đây là thiết kế hợp lý: tin tưởng người gửi ≠ bỏ qua an ninh.

**🧪 Cách test:**
- **Blacklist:** thêm sender/domain/IP vào **Blocked Senders** → gửi mail từ nguồn đó → bị chặn.
- **Whitelist:** thêm vào **Approved Senders** → gửi mail chứa GTUBE → **vẫn lọt** (chứng minh đã bypass spam filter theo đúng thiết kế).

---

## 🔹 TC7 — File Password Analysis

**Đường dẫn:** `Inbound Protection > Virus Scan > File Password Analysis`

### Giải thích từng tùy chọn

| Tùy chọn | Giải thích chi tiết |
|----------|---------------------|
| **Enable file password analysis** | Bật khả năng giải mã file có mật khẩu để quét. Sau khi giải mã, file được quét bởi **tất cả** chức năng inbound đang bật (Virus Scan, Content Filter...). |
| **Hold on a message to associate later messages** | Giữ tạm mail có file khóa lại, chờ email đến sau (có thể chứa mật khẩu gửi riêng) để ghép giải mã. Hữu ích khi người gửi tách file và mật khẩu thành 2 mail. |
| **Analysis timeout** | Thời gian tối đa thử giải mã một file (mặc định 5 phút). |
| **User-Defined Passwords** | Danh sách mật khẩu tổ chức tự khai báo. CEGP **thử các pass này TRƯỚC**. Nếu để trống → tự trích xuất pass từ nội dung email (heuristic). Có thể **Add** từng pass hoặc **Import** cả danh sách. |

### Hai cơ chế tìm mật khẩu (theo thứ tự)

1. **User-Defined Passwords** (bạn khai báo) — thử trước.
2. **Heuristic extraction** — tự dò pass từ **subject + body + tên file đính kèm**.

> ⚠️ CEGP **KHÔNG có từ điển mật khẩu brute-force dựng sẵn**. Nếu pass không có trong email và bạn không khai báo → hệ thống không đoán mò được.

> 💡 **Phụ thuộc Virus Scan:** File Password Analysis chỉ **mở file**. Việc **bắt mã độc** do Virus Scan (TC2) đảm nhiệm. Phải bật cả hai.

**🧪 Cách test:**
- **Kịch bản A (tự dò pass):** để trống User-Defined Passwords → gửi ZIP có pass `infected`, ghi pass trong body → hệ thống tự đọc pass, giải nén, bắt EICAR.
- **Kịch bản B (database pass riêng):** Import/Add `infected` vào danh sách → hệ thống dùng pass khai báo để giải nén.

---

## 🔹 TC8 — Time-of-Click Protection

**Đường dẫn:** `Inbound Protection > Spam Filtering` (bật bên trong **spam policy**)

### Cách hoạt động — 3 bước

| Bước | Giải thích |
|------|-----------|
| **1. Rewrite URL** | Khi bật, CEGP **viết lại** mọi link trong email thành link trung gian của Trend. |
| **2. Phân tích lúc click** | Khi người dùng **thực sự bấm vào link**, TrendAI phân tích URL **theo thời gian thực** — chứ không phải chỉ lúc nhận mail. |
| **3. Hành động** | Nếu link độc hại → **Block** (hiện trang cảnh báo) hoặc **Warn** (cảnh báo nhưng vẫn cho đi tiếp). |

### Giải thích tùy chọn

| Tùy chọn | Giải thích |
|----------|-----------|
| **Enable Time-of-Click Protection** | Bật rewrite + phân tích URL lúc click. |
| **Action: Block / Warn** | Chọn chặn hẳn (trang cảnh báo) hay chỉ cảnh báo. |
| **Bypass digitally signed email** | Mặc định **bật** — không rewrite mail có **chữ ký số** (tránh làm hỏng chữ ký). Muốn test link trong mail ký số thì phải **tắt** tùy chọn này. |

> 💡 **Vì sao cần "time-of-click"?** Link có thể **sạch lúc gửi** nhưng bị kẻ tấn công gài mã độc **sau đó**. Chỉ phân tích đúng thời điểm click mới bắt được loại tấn công này.

**🧪 Cách test:** Nhận mail → thấy URL đã bị rewrite (đổi thành link Trend) → click vào link độc → hiển thị trang cảnh báo chặn.

---

## 🔹 TC9 — Dashboard & Threat Visibility

**Đường dẫn:** `Dashboard` + `Logs`

| Khu vực | Giải thích |
|---------|-----------|
| **Dashboard** | Hiển thị trực quan: biểu đồ **lưu lượng mail**, widget **Top Threats** (Spam/Virus/Phishing), xu hướng mối đe dọa theo thời gian. |
| **Logs > Mail Tracking** | Tra vết hành trình từng email đi qua hệ thống (nhận, quét, hành động). |
| **Logs > Policy Events** | Log các sự kiện policy khớp — mail nào bị rule nào bắt, lý do gì. |
| **Quarantine Query** | Danh sách mail bị cách ly, kèm Sender/Recipient/Subject/Reason/Rule (màn hình chi tiết này giống Quarantine Query Details). |

→ **Không cần cấu hình policy** — chỉ cần **xem** sau khi đã chạy các test TC1–TC8 vài phút.

**🧪 Cách test:** Sau khi gửi các mail test, vào Dashboard → xác nhận biểu đồ threats tăng, Top Threats hiển thị đúng loại (Spam/Virus/Phishing), và log sự kiện chi tiết đầy đủ.

---

## 🔹 TC10 — Report Generation & Scheduling

**Đường dẫn:** `Reports`

| Loại | Giải thích |
|------|-----------|
| **On-demand report** | Xuất báo cáo ngay: chọn loại (tổng quan / chi tiết) + khoảng thời gian → export **PDF / CSV**. |
| **Scheduled report** | Lên lịch tạo & gửi báo cáo **tự động** theo tần suất **Daily / Weekly / Monthly**. |
| **Recipients** | Danh sách email **Administrator** nhận báo cáo định kỳ. |
| **Report content** | Chọn nội dung đưa vào báo cáo: thống kê spam, virus, phishing, top sender/recipient, lưu lượng... |

**🧪 Cách test:** Tạo một **Scheduled Report** (vd Daily) → nhập email admin → xác nhận admin nhận được báo cáo qua email đúng lịch và đúng nội dung.

---

## 📊 Bảng tổng hợp đường dẫn policy

| # | Test case | Đường dẫn cấu hình | Action chính |
|---|-----------|---------------------|--------------|
| 1 | Spam Filtering | `Inbound Protection > Spam Filtering` | Quarantine |
| 2 | Virus Scan | `Inbound Protection > Virus Scan` | ActiveAction / Delete / Quarantine |
| 3 | Content Filtering | `Inbound Protection > Content Filtering` | Block / Quarantine + lý do |
| 4 | Phishing Filtering | `Spam Filtering` + `Domain-based Authentication` | Quarantine |
| 5 | Sandboxing | `Virus Scan > Virtual Analyzer` | Quarantine + report |
| 6 | Whitelist/Blacklist | `Connection Filtering` (IP / Geo / Sender) | Block / Allow |
| 7 | File Password Analysis | `Virus Scan > File Password Analysis` | Decrypt → Virus Scan |
| 8 | Time-of-Click | `Spam Filtering` (spam policy) | Block + warning page |
| 9 | Dashboard | `Dashboard` + `Logs` | Xem (không cấu hình) |
| 10 | Report | `Reports` | Export + email admin |

---

## ⚠️ Lưu ý chung

1. **Tên menu con có thể khác đôi chút** tùy phiên bản/tenant CEGP của bạn.
2. **License:** TC5 (Virtual Analyzer) và Geo-IP (TC6) yêu cầu license tương ứng — nếu không thấy menu, kiểm tra license.
3. **Quan hệ phụ thuộc:** TC7 (File Password Analysis) cần TC2 (Virus Scan) bật để bắt được mã độc sau khi giải nén.
4. **Approved Senders** bỏ qua lọc spam/phishing/IP nhưng **vẫn quét virus**.

---

*Nội dung được tổng hợp và diễn giải lại từ tài liệu chính thức Trend Micro để phù hợp với giấy phép sử dụng. Tham khảo: [docs.trendmicro.com](https://docs.trendmicro.com).*
