# Deleted Resources & Cleanup Report

Tài liệu này liệt kê toàn bộ các thư mục, tệp tin, lớp, hàm và cấu hình liên quan đến PDL (Program Description Language), Code và Text workflows đã bị loại bỏ khỏi dự án **FlowAIssistant**. Việc dọn dẹp này nhằm tối ưu hóa mã nguồn, tập trung hoàn toàn vào cấu trúc quy trình dạng **Flowchart**.

---

## 1. Danh sách các thư mục và tệp tin đã xóa (Datasets & Templates)

### 📂 Bộ dữ liệu (Datasets)
- `dataset/PDL/` (Toàn bộ thư mục chứa kịch bản PDL gốc)
- `dataset/STAR/pdl/` (Thư mục chứa các tệp `.yaml` mô tả quy trình theo định dạng PDL)
- `dataset/STAR/code/` (Thư mục chứa các tệp `.py` mô tả quy trình theo định dạng Code)
- `dataset/STAR/text/` (Thư mục chứa các tệp `.txt` mô tả quy trình theo định dạng Text tự nhiên)

### 📂 Mẫu prompt và Logic chuyên biệt (Templates & Modules)
- `src/flowagent/data/pdl.py` (Lớp xử lý cấu trúc file YAML của PDL)
- `src/flowagent/controller/pdl_utils.py` (Cấu trúc dạng đồ thị hỗ trợ kiểm tra ràng buộc của PDL)
- `src/flowagent/controller/pdl_checker.py` (Bộ kiểm tra tính hợp lệ của cuộc gọi API và ràng buộc bước của PDL)
- `src/utils/templates/flowagent/bot_pdl.jinja` (Template prompt hệ thống dành riêng cho PDLBot)

---

## 2. Các hàm và lớp đã xóa trong mã nguồn Python (Code Refactoring)

### 🤖 Lớp và Registry của Agent Bot (`src/flowagent/roles/`)
- Loại bỏ lớp `PDLBot(ReactBot)` khỏi `src/flowagent/roles/bot.py`. Lớp này chuyên biệt cho việc đọc dữ liệu PDL và tối ưu hóa hội thoại theo lượt.
- Loại bỏ import và ánh xạ của `PDLBot` trong `src/flowagent/roles/__init__.py`.

### 🗄️ Dữ liệu và Cấu trúc Workflow (`src/flowagent/data/`)
- Loại bỏ thuộc tính `pdl: PDL = None` khỏi lớp `Workflow` ở `src/flowagent/data/workflow.py`.
- Xóa bỏ logic tự động load file PDL khi `type == WorkflowType.PDL` trong hàm khởi tạo của `Workflow`.
- Rút gọn enum `WorkflowType` và `WorkflowTypeStr`, chỉ giữ lại duy nhất định dạng `FLOWCHART`.
- Sửa đổi cấu hình mặc định trong `src/flowagent/data/config.py` đặt `workflow_type` mặc định là `"flowchart"`.
- Xóa bỏ các tham số cấu hình liên quan đến PDL trong lớp `Config`:
  - `pdl_check_dependency`
  - `pdl_check_api_dup_calls`
  - `pdl_check_api_dup_calls_threshold`

### 🎮 Bộ điều phối chính (`src/flowagent/controller/`)
- Xóa bỏ import `PDLDependencyChecker` và `APIDuplicatedChecker` trong `src/flowagent/controller/flowagent.py`.
- Xóa bỏ phần khởi tạo checker kiểm tra ràng buộc trong phương thức `__init__` của `FlowagentController`.
- Rút gọn phương thức `check_bot_action` luôn trả về `True` đối với flowchart.

---

## 3. Thay đổi trong cấu hình và scripts kiểm thử

### ⚙️ Cấu hình mặc định (`src/flowagent/configs/default.yaml`)
- Loại bỏ các tham số cấu hình kiểm tra PDL:
  - `pdl_check_dependency`
  - `pdl_check_api_dup_calls`
  - `pdl_check_api_dup_calls_threshold`
- Cập nhật ghi chú của `bot_mode` chỉ còn các tùy chọn: `dummy_bot`, `react_bot`, `state_react_bot`.

### 🐚 Bash script khởi chạy CLI (`scripts/run_cli.sh`)
- Xóa toàn bộ các ví dụ chạy thử nghiệm (commented lines) sử dụng `--workflow-type=pdl` và `--bot-mode=pdl_bot`.

### 📖 Tài liệu hướng dẫn (`README.md`)
- Cập nhật sơ đồ cấu trúc dự án loại bỏ `PDL/`.
- Sửa đổi phần giải thích các tham số để loại bỏ các đề xuất sử dụng PDL, pdl_bot hay bộ dữ liệu PDL.

---

## 4. Tái cấu trúc cấu trúc thư mục (Directory Reorganization)

Để làm nổi bật kiến trúc hệ thống 3 lớp và giúp cấu trúc dự án trực quan hơn, thư mục trung gian `src/` đã được loại bỏ hoàn toàn. Các module chính đã được chuyển thẳng ra thư mục gốc (root) của dự án:
- `src/backend/` ➡️ `backend/` (FastAPI + MongoDB Backend API Layer)
- `src/flowagent/` ➡️ `flowagent/` (Core FlowAgent Controller Layer)
- `src/utils/` ➡️ `utils/` (Common Utilities)
- `src/easonsi/` ➡️ `easonsi/` (LLM Client Layer)
- `src/run_flowagent_cli.py` ➡️ `run_flowagent_cli.py` (CLI Driver Entrypoint)

Đồng thời, toàn bộ cấu hình đường dẫn tệp trong `flowagent/data/workflow.py`, `backend/app.py`, `scripts/run_cli.sh`, `README.md` và `README_BACKEND.md` đã được hiệu chỉnh tương ứng để hoạt động chính xác theo kiến trúc mới.
