# Team

## Thông tin nhóm

- Tên nhóm: Nhom5W
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |Nguyễn Thành Tâm|2A202603933|26ai.tamnt@vinuni.edu.vn|ngthanhtamtb|Prompt Engineer|
|   2 |Trịnh Gia Huy|2A202603924|26ai.huytg3@vinuni.edu.vn|TrGiaHuy1710-valid|AI Engineer|
|   3 |Lê Tuấn Đạt|2A202603949|26ai.datlt8@vinuni.edu.vn|etuandat.131|BE|
|   4 |Nguyễn Huy Tấn|2A202603925|26ai.tannh@vinuni.edu.vn|Besoi2004|tester|

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## Nguyễn Thành Tâm - 2A202603933

### Phần việc phụ trách

- Thiết lập và chạy bộ đánh giá chuẩn (`run_eval.py`) với provider `gemini` (`gemini-3.8-flash`) trên bộ đề `starter_v0/data/eval_base.json`.
- Phụ trách vai trò **Prompt Engineer**: Thực hiện vòng lặp tối ưu Evidence-driven qua các phiên bản `v0` → `v1` → `v2` → `v3` dựa trên phân tích log `starter_v0/runs/*.json`, đặt giả thuyết và tinh chỉnh `starter_v0/artifacts/system_prompt.md` cùng `starter_v0/artifacts/tools.yaml` đến khi đạt độ chính xác tuyệt đối `1.00` (20/20 cases).
- Phân tích lỗi (Failure Analysis) giữa các nhóm lỗi hành vi trong `system_prompt.md` (`missing_info`, `out_of_scope`, `wrong_boundary`, `parallel_tool_calls`) và nhóm lỗi quy ước tham số trong `tools.yaml` (`wrong_arg_value` ở `lookup.query`).

### Đóng góp cụ thể

- **Baseline (`v0`):** Chạy đánh giá ban đầu đạt `case_accuracy = 0.75` (15/20 PASS) và xác định 5 cases FAIL gốc (`R03`, `R10`, `R11`, `R12`, `R13`).
- **Vòng `v1` (`0.70` → `0.80`):** Phát hiện và khắc phục lỗi mâu thuẫn câu lệnh trong `system_prompt.md`, xóa triệt để chỉ dẫn ép đoán mò, quy định gọi `clarify(response_type="text")` khi thiếu thông tin tài khoản/URL → PASS `R10_missing_handle` và `R11_missing_url`.
- **Vòng `v2` (`0.80` → `0.85`):** Bổ sung quy tắc từ chối ngoài phạm vi (`Out of Scope`), gọi nhiều tool song song (`Multi-tool`) và xác nhận trước khi gửi (`Confirmation Before Sending` với `clarify(response_type="yes_no")`) → PASS `R08_out_of_scope`, `R12_confirm_before_send` và gọi đủ 2 tool ở `R13`.
- **Vòng `v3` (`0.85` → `1.00`):** Chuẩn hóa mô tả và quy ước tham số của tool `lookup` (`query` chỉ lấy từ khóa chủ đề cốt lõi, không thêm `"news"` / `"tin tức"`, gọi đúng 1 lần) trong `starter_v0/artifacts/tools.yaml` → PASS toàn bộ `R03`, `R13`, `M02`, nâng `case_accuracy`, `tool_routing_accuracy`, `argument_accuracy`, `multiturn_accuracy` lên **`1.00` (20/20 PASS)**.

### Bằng chứng

- Báo cáo cá nhân chi tiết: [`report/team/2A202603933_NguyenThanhTam.md`](report/team/2A202603933_NguyenThanhTam.md)
- File đã chỉnh sửa: `starter_v0/artifacts/system_prompt.md` (`prompt_hash: 9c43efb47199`), `starter_v0/artifacts/tools.yaml` (`tools_hash: 65e0ae20ecad`).
- Run logs:
  - `v0` (`acc = 0.75`): `starter_v0/runs/v0_B_base_gemini_20261110T180840811830.json`
  - `v1` (`acc = 0.70` → `0.80`): `starter_v0/runs/v1_B_base_gemini_20261110T183140172591.json`, `starter_v0/runs/v1_B_base_gemini_20261110T185237539301.json`
  - `v2` (`acc = 0.85`): `starter_v0/runs/v2_B_base_gemini_20261110T185924162965.json`, `starter_v0/runs/v2_B_base_gemini_20261110T191813503578.json`
  - `v3` (`acc = 1.00`, 20/20 PASS): `starter_v0/runs/v3_B_base_gemini_20261110T192529403171.json`

---

## Trịnh Gia Huy - 2A202603924

### Phần việc phụ trách

- Phụ trách vai trò **AI Engineer**: Kiểm tra kết nối API thật của các tool (Tavily, Firecrawl, arXiv, policy, RapidAPI), chạy baseline và tối ưu mở rộng cho cả bộ `base` lẫn `extension`.
- Thiết kế và hiện thực hóa 2 tool mới ở CP3 (`hackernews_search` và `github_search`) kèm `TOOL.md` và bộ 10 unit test offline.
- Xây dựng hệ thống Demo ở CP5 gồm HTTP backend (`starter_v0/server.py`), CLI client (`starter_v0/cli_client.py`) và giao diện web Streamlit (`starter_v0/app.py`).

### Đóng góp cụ thể

- **CP1 & CP2 (Phân tích API & tối ưu mở rộng):** Kiểm tra thực tế từng API (phát hiện lỗi 403 chưa subscribe của RapidAPI Twitter), viết lại `system_prompt.md` và `tools.yaml` giúp cả bộ `base` và `extension` đạt `1.00`, đồng thời bổ sung quy tắc routing cho 2 tool mới mà không làm giảm điểm regression.
- **CP3 (2 Tool mới & Unit test):**
  - Viết `hackernews_search` (gọi Algolia HN API `/search` và `/search_by_date`, hỗ trợ lọc `tags`, `sort`, khoảng ngày) và `github_search` (gọi GitHub REST `search/repositories`, tự ghép qualifier `language:` và `created:>=`, xử lý lỗi rate limit/timeout theo chuẩn dict `{"tool", "error", "message"}`).
  - Viết 10 unit test trong `starter_v0/tests/test_tools_todo.py` (5 test/tool) dùng `fake_http`, nâng kết quả `pytest` lên **82 passed, 0 failed**.
- **CP5 (Backend, CLI & Streamlit UI):** Xây dựng `server.py` (REST API `/health`, `/tools`, `/chat`, `/reset`, `/sessions/<id>`, tự lưu transcript), `cli_client.py` và `app.py` (hiển thị trực quan từng tool call, nút xác nhận Có/Không cho `clarify`, câu hỏi mẫu dùng thử).

### Bằng chứng

- Báo cáo cá nhân chi tiết: [`report/team/2A202603924_TrinhGiaHuy.md`](report/team/2A202603924_TrinhGiaHuy.md)
- Code tool mới & test: `starter_v0/tools/hackernews_search/`, `starter_v0/tools/github_search/`, `starter_v0/tests/test_tools_todo.py`
- Code UI & Backend: `starter_v0/app.py`, `starter_v0/server.py`, `starter_v0/cli_client.py`
- Transcripts live: `starter_v0/transcripts/v5_gemini_streamlit_20261110T220033075947.transcript.json` và các transcript backend trong `starter_v0/transcripts/`
- PR/Commit: PR [#10](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/pull/10), commit `67f8837`, `e90ff2a`

---

## Lê Tuấn Đạt - 2A202603949

### Phần việc phụ trách

- Phụ trách vai trò **BE (Backend)**: Tích hợp 2 tool mới của CP3 (`hackernews_search` và `github_search`) vào nhánh chính `main`, chuẩn hóa khai báo contract giữa `tools/__init__.py`, `artifacts/tools.yaml` và `TOOL.md`.
- Thiết lập môi trường fixture kiểm thử cô lập (`conftest.py`) và chạy kiểm chứng toàn bộ contract test + unit test của tool mới bằng `pytest`.

### Đóng góp cụ thể

- Đưa `tool.py` và `TOOL.md` của `hackernews_search` và `github_search` vào đúng cấu trúc `starter_v0/tools/`, đăng ký hàm vào `TOOL_FUNCTIONS` trong `starter_v0/tools/__init__.py` và đồng bộ khai báo trong `starter_v0/artifacts/tools.yaml`.
- Chuẩn hóa frontmatter của `starter_v0/tools/github_search/TOOL.md` (`requires_env: []` vì `GITHUB_TOKEN` là tùy chọn) và bổ sung `GITHUB_TOKEN` vào danh sách biến môi trường được xóa trong `starter_v0/tests/conftest.py` để đảm bảo test chạy hoàn toàn độc lập, không phụ thuộc biến môi trường máy local.
- Kiểm chứng quy trình TDD/Regression với `pytest`: xác nhận trước khi đăng ký vào registry thì 10 test của tool mới báo fail, và sau khi hoàn tất tích hợp toàn bộ suite đạt **82 passed, 14 skipped, 0 failed** (giữ xanh hoàn toàn `test_tool_contract.py`).

### Bằng chứng

- Báo cáo cá nhân chi tiết: [`report/team/2A202603949_Lê Tuấn Đạt.md`](report/team/2A202603949_Lê%20Tuấn%20Đạt.md)
- File tích hợp & kiểm thử: `starter_v0/tools/__init__.py`, `starter_v0/tools/hackernews_search/`, `starter_v0/tools/github_search/`, `starter_v0/tests/conftest.py`, `starter_v0/tests/test_tools_todo.py`
- Nhánh & Commit: nhánh `dat/cp3-research-tools`, tích hợp và kiểm chứng trên nền `main`

---

## Nguyễn Huy Tấn - 2A202603925

### Phần việc phụ trách

- Phụ trách vai trò **Tester**: Thiết kế và xây dựng bộ đánh giá của nhóm tại `starter_v0/data/eval_group.json` (CP4 / Rubric C5) gồm đúng **10 cases (5 single-turn `G01`–`G05` và 5 multi-turn `G06`–`G10`)**.
- Thực thi đánh giá thực tế với `--suite group`, thu thập run log hợp lệ và viết tài liệu phân tích chi tiết từng case trong `starter_v0/data/eval_group.md`.

### Đóng góp cụ thể

- **Thiết kế 10 eval cases đa dạng, không trùng lặp với `eval_base.json`:**
  - Kiểm tra convention tham số (`search_type="Latest"`, tách bỏ ký tự `@` trong `screenname="karpathy"`, `timeframe="month"`): `G01`, `G02`, `G03`.
  - Kiểm tra ranh giới xác nhận `send` (xin phép `yes_no` cả khi đã có sẵn nội dung, gửi khi user xác nhận, và hủy không gọi tool khi user từ chối): `G04`, `G06`, `G07`.
  - Kiểm tra câu hỏi ngoài phạm vi đặt vé máy bay (`G05`), hỏi lại liên tiếp khi lượt bổ sung vẫn thiếu URL (`G08`), và đổi nguồn tìm kiếm giữa các lượt sang arXiv (`G09`) cũng như sang tool mới `hackernews_search` (`G10`).
- **Chạy đánh giá `--suite group` và phân tích lỗi:**
  - Chạy bộ 10 cases đạt `measured_cases = 10`, `provider_error_cases = 0`, kết quả **9/10 PASS (`case_accuracy = 0.90`, `tool_routing_accuracy = 1.00`, `argument_accuracy = 0.90`)**.
  - Phân tích chi tiết 1 case FAIL (`G10_switch_to_hackernews`: model đã route đúng sang `hackernews_search` với `query="Gemini"`, `limit=3` nhưng thiếu `sort="date"`) và đề xuất hướng cải thiện trong `tools.yaml` mà không sửa đáp án `expect`.

### Bằng chứng

- Báo cáo cá nhân chi tiết: [`report/team/2A202603925_NguyenHuyTan.md`](report/team/2A202603925_NguyenHuyTan.md)
- Bộ đề & phân tích eval nhóm: `starter_v0/data/eval_group.json`, `starter_v0/data/eval_group.md`
- Run log thực tế: `starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json`
- PR: [#8](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/pull/8), [#11](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/pull/11)
