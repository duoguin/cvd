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
│   ├── PDL/                # Bộ dữ liệu kịch bản hội thoại bao gồm flowchart, code, mô tả tools...
│   ├── STAR/               # Bộ dữ liệu đánh giá hội thoại dựa trên sơ đồ quy trình
│   └── meta/               # Siêu dữ liệu liên quan đến các tập dữ liệu
├── scripts/                # Các script hỗ trợ tự động hóa và tiện ích
│   └── run_cli.sh          # Script bash để khởi chạy nhanh chương trình CLI trong môi trường
└── src/                    # Thư mục chứa mã nguồn chính của ứng dụng
    ├── run_flowagent_cli.py # Điểm khởi chạy chính (entrypoint) để chạy chatbot trên giao diện dòng lệnh (CLI)
    ├── utils/              # Chứa các hàm tiện ích dùng chung (utility)
    │   └── jinja_templates.py # Quản lý các file mẫu (template) Prompt cung cấp ngữ cảnh động cho LLM
    ├── easonsi/            # Module chịu trách nhiệm kết nối, bao bọc và xử lý API với các LLM provider
    └── flowagent/          # Core module, chứa các logic quan trọng nhất của hệ thống FlowAIssistant
        ├── configs/        # Thư mục chứa các file thiết lập/cấu hình thông số hệ thống (vd: default.yaml)
        ├── controller/     # Điều phối luồng chương trình, quản lý logic di chuyển trên Flowchart
        │   ├── flowagent.py   # Agent điều phối chính kết hợp việc gọi LLM và duyệt trạng thái
        │   └── pdl_checker.py # Kiểm tra, đánh giá điều kiện chuyển tiếp các nút trong đồ thị Flowchart
        ├── roles/          # Định nghĩa các vai trò (thực thể) tham gia vào quy trình hội thoại
        │   ├── bot.py      # LLM Chatbot: Tiếp nhận ngữ cảnh từ Flowchart, giao tiếp và suy luận
        │   ├── user.py     # Lớp định nghĩa, giả lập hoặc quản lý hành vi của người dùng
        │   └── api.py      # Quản lý giao tiếp với các dịch vụ bên ngoài, cung cấp tools/API cho LLM
        ├── data/           # Module định nghĩa cấu trúc dữ liệu, lưu trữ ngữ cảnh hội thoại
        │   └── workflow.py # Trừu tượng hóa sơ đồ Flowchart thành cấu trúc đồ thị hỗ trợ code xử lý
        ├── eval/           # Cung cấp bộ công cụ tự động đánh giá và chấm điểm chất lượng hội thoại
        │   ├── judger.py   # Bộ chấm điểm kết quả cuối cùng theo nhiều metric khác nhau
        │   └── analyzer.py # Công cụ phân tích chi tiết các phiên tương tác
        └── ui/             # Giao diện người dùng cho việc demo hoặc debug (Web App, CLI tools)
            ├── app.py      # Ứng dụng Streamlit hiển thị giao diện UI web
            └── show_conversation.py # Tiện ích hiển thị, debug hội thoại trực quan
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