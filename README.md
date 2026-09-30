# Lịch Phụng Vụ Công Giáo - Web App Tự Động Thêm Vào Lịch (iOS & Android)

Hệ thống Web App giúp người dùng thông thường **chỉ cần vào trang Web trên điện thoại và bấm 1 Chạm** là toàn bộ ngày lễ Công giáo sẽ được tự động thêm vào ứng dụng Lịch của **iPhone (Apple Calendar)** hoặc **Android (Google Calendar)** kèm chuông báo nhắc lễ.

---

## 🌟 Trải Nghiệm Của Người Dùng (1 Chạm - Cực Kỳ Dễ Dàng)

Khi người dùng mở trang Web trên điện thoại:

1. **Người dùng iPhone / iPad (iOS)**:
   - Chỉ cần bấm vào nút đen: **"Thêm vào Lịch iPhone / iPad (Apple)"**.
   - Trình duyệt Safari sẽ tự động kích hoạt hộp thoại hệ thống: **"Đăng ký lịch 'Lịch Phụng Vụ Công Giáo'?"**
   - Người dùng bấm nút **"Đăng ký" (Subscribe)** -> **XONG!**
   - Không cần cài app, không cần cấu hình tài khoản, không cần copy link.

2. **Người dùng Android / Máy tính (Google Calendar)**:
   - Bấm vào nút xanh: **"Thêm vào Google Calendar"**.
   - Màn hình Google Calendar mở ra với thông báo: **"Thêm lịch này vào tài khoản của bạn?"**
   - Người dùng bấm **"Thêm" (Add)** -> **XONG!** Lịch tự động đồng bộ về app Google Calendar trên điện thoại.

---

## 🚀 Cách Chạy Web Server

### Khởi chạy nhanh bằng Python:
```bash
python3 app.py
```
Máy chủ sẽ chạy tại: **`http://localhost:8080`** (hoặc địa chỉ IP mạng nội bộ của bạn, ví dụ `http://192.168.1.x:8080`).

---

## 📱 Các Tính Năng Trên Giao Diện Web

1. **Bộ nút 1 Chạm thông minh**:
   - Tự động nhận diện domain/host để tạo link chuẩn `webcal://` cho Apple và link render cho Google Calendar.
   - Nút tải file `.ics` trực tiếp nếu người dùng muốn lưu file về máy.
2. **Xem trước danh sách ngày lễ (Preview)**:
   - Hiển thị danh sách các ngày lễ theo thẻ trực quan.
   - Phân loại rõ màu sắc: Đỏ (Lễ Trọng / Lễ Buộc), Xanh dương (Lễ Kính), Xanh lá (Lễ Nhớ).
   - Bộ lọc theo từng tháng (Tất cả, T10, T11, T12).
   - Hiển thị đầy đủ bài đọc Lời Chúa (Cựu Ước, Đáp Ca, Thư Tông Đồ, Tin Mừng) và màu áo phụng vụ.
3. **Khu vực Quản trị (Admin) ngay trên Web**:
   - Ở cuối trang có mục: *⚙️ Quản trị viên: Cập nhật / Thêm danh sách ngày lễ mới*.
   - Bạn chỉ cần dán dữ liệu ngày lễ các tháng tiếp theo (hoặc năm 2027) vào ô văn bản và bấm **"Lưu & Cập Nhật Lịch"**.
   - Toàn bộ người dùng đã đăng ký lịch sẽ tự động nhận được dữ liệu mới mà không cần thao tác lại!

---

## 🌐 Cách Đưa Web Lên Mạng Để Người Khác Truy Cập

Để gửi link cho bạn bè, người thân hoặc cộng đoàn giáo xứ sử dụng:

### Cách 1: Dùng Cloudflare Tunnel hoặc Ngrok (Miễn phí, chạy ngay trên máy bạn)
```bash
# Cài đặt và mở cổng 8080 ra Internet:
ngrok http 8080
# Bạn sẽ có link dạng: https://xxxx.ngrok-free.app để gửi cho mọi người
```

### Cách 2: Triển khai lên các dịch vụ đám mây miễn phí (Render / Railway / Fly.io / VPS)
- Dự án đã có sẵn [`Dockerfile`](file:///Users/vsf-user-l/SOURCE_CODE/PYTHON/calendar_ios/Dockerfile) và [`requirements.txt`](file:///Users/vsf-user-l/SOURCE_CODE/PYTHON/calendar_ios/requirements.txt).
- Bạn chỉ cần đẩy mã nguồn lên GitHub rồi kết nối với [Render.com](https://render.com) (chọn Web Service, miễn phí 100%).
