# Hướng dẫn Vận hành Hệ thống FlowAIssistant cùng Backend API (MongoDB)

Tài liệu này hướng dẫn chi tiết cách cấu hình, khởi chạy và vận hành hệ thống **FlowAIssistant** kết hợp với **Backend API thực tế (FastAPI)** lưu trữ dữ liệu trực tiếp trong cơ sở dữ liệu **MongoDB**, thay thế cho cơ chế gọi API giả lập (simulated API) trước đây.

---

## 1. Kiến trúc luồng hoạt động thực tế

Khi người dùng tương tác với Chatbot:
1. **LLM (Bot)** nhận diện ý định và quyết định trạng thái tiếp theo cần gọi API chức năng (Ví dụ: kiểm tra lịch trống hoặc đặt lịch).
2. Bot gửi lệnh hành động (`Action` và `Action Input`) về hệ thống.
3. Hệ thống kích hoạt **`RealAPIHandler`** (`--api-mode=real_api`), tạo yêu cầu HTTP POST thực tế gửi tới **FastAPI Backend Server** (`http://127.0.0.1:8000`).
4. **Backend Server** tiếp nhận thông tin, thực hiện kiểm tra hoặc chèn dữ liệu trực tiếp vào **MongoDB**.
5. Backend phản hồi trạng thái và kết quả (JSON) về hệ thống chatbot để cập nhật vào lịch sử hội thoại hiện tại.

---

## 2. Chuẩn bị môi trường

Đảm bảo bạn đã hoàn thành các bước chuẩn bị sau:

### Khởi động MongoDB (Docker)
Đảm bảo container chứa MongoDB đang chạy trên cổng `27017`:
```bash
docker start mongodb
```

### Cấu hình tệp `.env`
Kiểm tra cấu hình `DB_URI` trong tệp `.env` ở thư mục gốc của dự án:
```env
DB_URI=mongodb://admin:123456@localhost:27017/?authSource=admin
```

### Kích hoạt môi trường ảo `.venv`
Mở Terminal của bạn (Git Bash hoặc PowerShell) tại thư mục dự án và kích hoạt:
* **Trên Git Bash:**
  ```bash
  source .venv/Scripts/activate
  ```
* **Trên PowerShell / Command Prompt:**
  ```powershell
  .venv\Scripts\activate
  ```

---

## 3. Khởi chạy Backend Server

Backend được xây dựng dựa trên FastAPI tại tệp `src/backend/app.py`. Chạy lệnh sau trong terminal đã kích hoạt môi trường ảo:

```bash
python src/backend/app.py
```

* Máy chủ uvicorn sẽ khởi chạy thành công tại địa chỉ: `http://127.0.0.1:8000`
* Khi kết nối thành công tới cơ sở dữ liệu, màn hình sẽ in dòng chữ: `Successfully connected to MongoDB!`

---

## 4. Khởi chạy Chatbot CLI với API thực tế

Để chạy chatbot tích hợp gọi API thực tế tới Backend, bạn chỉ cần thay đổi tham số `--api-mode` thành **`real_api`**.

### Cách 1: Sử dụng script `run_cli.sh` (Khuyên dùng)
1. Mở tệp `scripts/run_cli.sh`.
2. Sửa tham số `--api-mode=llm` thành `--api-mode=real_api`.
3. Mở **Git Bash** và chạy lệnh:
   ```bash
   bash scripts/run_cli.sh
   ```

### Cách 2: Chạy trực tiếp qua lệnh Python
Mở Terminal và thực thi lệnh đầy đủ sau (ví dụ kiểm tra workflow khám bệnh bác sĩ `005`):
```bash
python src/run_flowagent_cli.py --config=default.yaml --exp-version=defaultss --exp-mode=session \
    --workflow-dataset=STAR \
    --workflow-type=flowchart --workflow-id=005 \
    --user-mode=manual --user-llm-name=openai/gpt-oss-20b --user-profile-id=0 \
    --bot-mode=state_react_bot --bot-llm-name=openai/gpt-oss-20b \
    --api-mode=real_api --api-llm-name=openai/gpt-oss-20b \
    --bot-template-fn=baselines/state_flowbench.jinja \
    --conversation-turn-limit=20 --log-utterence-time --log-to-db
```

---

## 5. Danh sách các API được hỗ trợ

### A. Workflow `000`: Đặt lịch xem căn hộ (`book_apartment_viewing`)
* **Endpoint:** `POST http://127.0.0.1:8000/api/book_apartment_viewing`
* **Collection lưu trữ:** `apartment_viewings` trong database `pdl`.
* **Cơ chế hoạt động:**
  * Nếu `RequestType` là `"Check"`: Kiểm tra xem căn hộ đó tại ngày và giờ yêu cầu đã được đặt trước đó hay chưa. Trả về trạng thái trống/bận.
  * Nếu `RequestType` là `"Book"`: Lưu bản ghi đặt căn hộ trực tiếp vào MongoDB kèm thời gian khởi tạo.

### B. Workflow `005`: Đặt lịch khám bệnh (`doctor_schedule`)
* **Endpoint:** `POST http://127.0.0.1:8000/api/doctor_schedule`
* **Collection lưu trữ:** `doctor_appointments` trong database `pdl`.
* **Cơ chế hoạt động:**
  * Nếu `RequestType` là `"Check"`: Kiểm tra lịch trống của bác sĩ.
  * Nếu `RequestType` là `"Book"`: Lưu thông tin lịch hẹn (bao gồm triệu chứng bệnh, tên bệnh nhân, tên bác sĩ) vào MongoDB.

---

## 6. Kiểm tra dữ liệu trong MongoDB

Sau khi thực hiện đặt lịch thành công qua Chatbot, bạn có thể kiểm tra dữ liệu thực tế lưu trữ trong MongoDB bằng bất kỳ MongoDB Client nào (Compass, Studio 3T) hoặc thông qua dòng lệnh python nhanh:

```python
import pymongo
client = pymongo.MongoClient("mongodb://admin:123456@localhost:27017/?authSource=admin")
db = client["pdl"]

# Xem danh sách đặt căn hộ
print(list(db.apartment_viewings.find()))

# Xem danh sách lịch hẹn bác sĩ
print(list(db.doctor_appointments.find()))
```
