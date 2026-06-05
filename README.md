# FlowAIssistant

FlowAIssistant là một hệ thống hội thoại thông minh dựa trên hướng tiếp cận lai, kết hợp giữa khả năng xử lý ngôn ngữ tự nhiên linh hoạt của các mô hình ngôn ngữ lớn (LLMs) và tính quy trình logic, minh bạch của Flowchart. 

Hệ thống được thiết kế hướng tới giải quyết các bài toán hội thoại đa bước đòi hỏi tính tuân thủ quy trình khắt khe như hỗ trợ kỹ thuật, dịch vụ công, y tế hay tài chính. Trong kiến trúc này, Flowchart đóng vai trò là "bộ định tuyến" (router) quản lý trạng thái để điều hướng luồng nghiệp vụ chặt chẽ, còn LLM đóng vai trò là "bộ não" giao tiếp tự nhiên và phân tích ý định dựa trên trạng thái hiện tại. Cách tiếp cận này giúp loại bỏ triệt để hiện tượng ảo giác (hallucination) trong nghiệp vụ, giữ được sự tương tác mềm dẻo nhưng vẫn đảm bảo tính chính xác tuyệt đối ở mọi bước chuyển trạng thái.

## Cấu trúc thư mục dự án

Dưới đây là cây cấu trúc của dự án. Các thư mục và file quan trọng được chú thích rõ ràng về vai trò:

```text
FlowAIssistant/
├── .env                    # File cấu hình biến môi trường (chứa các API keys, environment variables)
├── .gitignore              # Các file/thư mục cần được bỏ qua khi sử dụng Git
├── pyproject.toml          # File cấu hình dự án Python, quản lý thư viện và dependencies
├── docs/                   # Thư mục chứa tài liệu dự án
│   └── midterm-report.pdf  # Báo cáo giữa kỳ, tài liệu nghiên cứu chi tiết về kiến trúc Flowchart kết hợp LLM
├── dataset/                # Thư mục chứa các bộ dữ liệu, kịch bản hội thoại chuẩn hóa
│   ├── STAR/               # Bộ dữ liệu đánh giá hội thoại dựa trên sơ đồ quy trình
│   └── meta/               # Siêu dữ liệu liên quan đến các tập dữ liệu
├── scripts/                # Các script hỗ trợ tự động hóa và tiện ích
│   └── run_cli.sh          # Script bash để khởi chạy nhanh chương trình CLI trong môi trường
├── backend/                # Backend API Layer (FastAPI + MongoDB)
│   └── app.py              # File chạy ứng dụng backend API lưu lịch sử hội thoại thực tế
├── flowagent/              # FlowAgent Controller Layer
│   ├── configs/            # Chứa file thiết lập thông số hệ thống (vd: default.yaml)
│   ├── controller/         # Điều phối luồng chương trình, quản lý duyệt trạng thái Flowchart
│   │   └── flowagent.py    # Agent điều phối chính kết hợp việc gọi LLM và duyệt trạng thái
│   ├── roles/              # Định nghĩa các vai trò hội thoại (bot.py, user.py, api.py)
│   ├── data/               # Định nghĩa cấu trúc dữ liệu hội thoại (workflow.py, db.py, etc.)
│   ├── eval/               # Bộ công cụ tự động đánh giá và chấm điểm chất lượng (judger.py, analyzer.py)
│   └── ui/                 # Giao diện người dùng Streamlit (app.py, show_conversation.py)
├── utils/                  # Chứa các hàm tiện ích dùng chung (utility, jinja prompt templates)
├── easonsi/                # Module chịu trách nhiệm kết nối, bao bọc và xử lý API với các LLM provider
├── run_flowagent_cli.py    # Điểm khởi chạy chính (entrypoint) để chạy chatbot trên giao diện CLI
└── deleted_resources.md    # Tài liệu thống kê các tài nguyên cũ liên quan đến PDL/Code/Text đã xóa
```

## Cách setup local LLM cho project
**Bước 1**: Cài đặt LM Studio theo link: https://lmstudio.ai/download/ 

**Bước 2**: Mở LM Studio, ở thanh tab bên trái, chọn tab *Model Search*

**Bước 3**: Tìm và tải mô hình *GPT-OSS 20B*

**Bước 4**: Ở thanh tab bên trái, vào tab *Developer*, vào *Local Server*, bật vào công tắc bên cạnh dòng chữ *Status: Stopped*.

**Bước 5**: Bấm vào nút *Load Model*, sau đó chọn model *GPT-OSS 20B* đã tải về.

**Bước 6**: Đợi cho đến khi model load xong là ok. Key và base url đã được config sẵn trong file `.env`.

## Hướng dẫn chạy chương trình

**Bước 1**: Chọn terminal là Git Bash.

**Bước 2**: Chạy lệnh `bash scripts/run_cli.sh`.

### Giải thích các tham số trong `run_cli.sh`

Khi mở file `scripts/run_cli.sh`, bạn sẽ thấy một lệnh chạy `python run_flowagent_cli.py` với rất nhiều tham số cấu hình. Dưới đây là ý nghĩa cặn kẽ của từng tham số để bạn dễ dàng nắm bắt:

- `--config`: Tên file chứa các cấu hình mặc định khác của hệ thống (ví dụ: `default.yaml`).
- `--exp-version`: Đặt tên cho phiên bản/môi trường chạy thử nghiệm (ví dụ: `defaultss`), giúp phân biệt log và dữ liệu đầu ra giữa các lần thử nghiệm.
- `--exp-mode`: Chế độ chạy thử nghiệm (ví dụ: `session` là chế độ tạo một phiên hội thoại duy trì trạng thái).
- `--workflow-dataset`: Tên của bộ dữ liệu chứa kịch bản quy trình (ví dụ: `STAR`).
- `--workflow-type`: Loại cấu trúc của quy trình. **LƯU Ý:** Tham số này luôn luôn phải được thiết lập là `flowchart` trong dự án này.
- `--workflow-id`: Mã định danh (ID) của sơ đồ/kịch bản cụ thể mà hệ thống sẽ chạy (ví dụ: `005`, `022`).
- `--user-mode`: Chế độ hoạt động của người dùng (ví dụ: `manual` có nghĩa là con người sẽ tự gõ tin nhắn vào terminal).
- `--user-llm-name`: Tên mô hình LLM dùng để giả lập hành vi người dùng (nếu bạn chạy chế độ người dùng tự động).
- `--user-profile-id`: Mã hồ sơ giả định của người dùng, dùng để cung cấp các thông tin nền tảng, bối cảnh cho user (ví dụ: `0`).
- `--bot-mode`: Chế độ luận dịch của tác nhân Bot (ví dụ: `state_react_bot`, `react_bot`).
- `--bot-llm-name`: Tên mô hình LLM chính sẽ được Chatbot sử dụng để sinh văn bản, phân tích và luận dịch trạng thái.
- `--api-mode`: Cơ chế xử lý các API Tool gọi ra ngoài. `llm` có nghĩa là hệ thống sẽ dùng mô hình AI để tự sinh ra kết quả giả lập cho các hàm chức năng.
- `--api-llm-name`: Tên mô hình LLM sẽ được sử dụng để giả lập kết quả API.
- `--bot-template-fn`: Đường dẫn tới file Jinja Template để làm khuôn mẫu định dạng (System Prompt) cho Bot (ví dụ: `baselines/state_flowbench.jinja`).
- `--conversation-turn-limit`: Giới hạn số lượt chat tối đa (bảo vệ hệ thống khỏi vòng lặp vô hạn).
- `--log-utterence-time`: Cờ (flag) bật việc theo dõi và ghi lại thời gian tạo sinh phản hồi (latency) của Bot.
- `--log-to-db`: Cờ (flag) cho phép lưu thông tin phiên chat (lịch sử hội thoại) vào cơ sở dữ liệu.

### Hướng dẫn tùy chỉnh cấu hình cho Developer

Nếu bạn muốn thay đổi mô hình LLM hoặc chuyển sang một kịch bản Flowchart khác, bạn có thể chỉnh sửa trực tiếp nội dung lệnh trong file `scripts/run_cli.sh`.

**1. Đổi mô hình LLM (LLM Model)**
Theo mặc định, hệ thống đang dùng model `openai/gpt-oss-20b` thông qua một máy chủ local (LM Studio). Nếu bạn muốn dùng mô hình khác (ví dụ: GPT-4, Llama 3) hay đổi máy chủ, hãy sửa đổi tên ở các tham số sau:
- `--user-llm-name=tên-model-mới`
- `--bot-llm-name=tên-model-mới`
- `--api-llm-name=tên-model-mới`
*(Nhớ cập nhật lại `BASE_URL` và `API_KEY` tương ứng trong file `.env` nếu bạn muốn dùng model trả phí trên Cloud).*

**2. Đổi kịch bản hội thoại (Workflow/Flowchart)**
- Để sử dụng một quy trình nghiệp vụ khác, hãy tìm tham số `--workflow-id=005` và đổi số `005` thành mã ID kịch bản khác có trong dataset (ví dụ: `022`, `001`,...).
- **Lưu ý đặc biệt quan trọng:** Bất kể bạn thay đổi kịch bản như thế nào, tham số `--workflow-type` **LUÔN LUÔN phải là `flowchart`**. Không được thay đổi tham số này.

Chọn workflow id: 000 và 005 trong thư mục flowchart của STAR