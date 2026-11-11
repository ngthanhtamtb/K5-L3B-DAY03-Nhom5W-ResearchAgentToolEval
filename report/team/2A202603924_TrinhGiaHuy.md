# Báo cáo cá nhân — TrinhGiaHuy-2A202603924

## 1. Thông tin thành viên

- Họ tên: Trịnh Gia Huy
- MSSV: 2A202603924
- Email: 26ai.huytg3@vinuni.edu.vn
- GitHub: TrGiaHuy1710-valid
- Vai trò trong nhóm: AI Engineer
- Nhánh làm việc: `huy_agent`

## 2. Phần việc phụ trách

| Checkpoint | Phần việc |
|---|---|
| CP1 | Chạy baseline `v0` bằng Gemini, phân loại lỗi của từng case FAIL, kiểm tra API key của từng tool |
| CP2 | Viết lại `artifacts/system_prompt.md` và `artifacts/tools.yaml`, tối ưu qua nhiều version có run làm bằng chứng |
| CP3 | Viết 2 tool mới `hackernews_search` và `github_search` (code, `TOOL.md`, đăng ký, khai báo) và 10 unit test |
| CP4 | Viết 10 eval case cho `data/eval_group.json` (5 single turn, 5 multi turn) để kiểm tra 2 tool mới |
| CP5 | Viết backend mô phỏng (`server.py`), CLI client (`cli_client.py`) và giao diện Streamlit (`app.py`) |

## 3. Đóng góp cụ thể

### 3.1. Baseline và phân tích lỗi (CP1)

Run baseline `v0` dùng `gemini-3.8-flash` (`runs/v0_B_base_gemini_20261110T193936222029.json`): `case_accuracy = 0.70` (14/20). Có 6 case fail, mỗi case đều tìm được nguyên nhân trong prompt gốc:

| Case | Loại lỗi | Model đã làm gì | Nguyên nhân trong prompt v0 |
|---|---|---|---|
| R03 | wrong_arg_value | `query="AI artificial intelligence news"`, đáng ra là `"AI"` | Không có quy ước cho `query`; eval so khớp chính xác |
| R08 | out_of_scope | Gọi `lookup` cho bài tích phân | Không định nghĩa phạm vi của agent |
| R10 | missing_info | Tự đoán handle `sama` | "pick a well-known account like Sam Altman" |
| R11 | missing_info | Bịa ra một URL | "assume a likely URL" |
| R12 | wrong_boundary | Gọi `send` với `confirmed=true` mà không hỏi | "just go ahead and do it" |
| R13 | wrong_tool | Chỉ gọi `lookup`, bỏ sót `social_search` | "Pick one tool… single step" |

Kiểm tra từng API bằng cách gọi tool thật:
- Tavily, Firecrawl, arXiv và policy đều OK.
- Twitter (RapidAPI `twitter-api45`) trả về `403 "You are not subscribed to this API."`: key hợp lệ nhưng tài khoản chưa đăng ký API đó.
- `paper_text` lỗi vì môi trường chưa cài `pypdf`.

Một điểm cần nắm: eval chỉ chấm tên tool và args mà model chọn, nên lỗi API không làm thay đổi metric.

### 3.2. Tối ưu prompt và tool declaration (CP2)

| Run | Prompt hash | Tools hash | Thay đổi | Base | Extension |
|---|---|---|---|---:|---:|
| `v0_B_base_gemini_20261110T193936222029` | `f0c107a9d7a1` | `41a2894f8ad1` | Baseline của starter | 0.70 | – |
| `v1_B_base_gemini_20261110T204008385792` | `0843b00364d0` | `41a2894f8ad1` | Viết lại system prompt | 0.95 | – |
| `v3_B_base_gemini_20261110T205742344794` / `v3_B_extension_gemini_20261110T210434460615` | `3f676458ce51` | `41a2894f8ad1` | Thử một prompt ngắn hơn | 0.85 | 0.60 |
| `v4_B_base_gemini_20261110T215136708471` / `v4_B_extension_gemini_20261110T215225881101` | `0843b00364d0` | `f82218f1965c` | Viết lại `tools.yaml` và thêm 2 tool mới | 1.00 | 1.00 |
| `v5_B_base_gemini_20261110T215526532579` / `v5_B_extension_gemini_20261110T215615247457` | `2b64729cdc8e` | `f82218f1965c` | Thêm routing cho tool mới và cách trả lời sau khi có kết quả tool | 1.00 | 1.00 |

**Giả thuyết của từng bước:**

- **v1 (system prompt):**
  - Giả thuyết: prompt v0 chủ động dạy model đoán và tự gửi, nên thay bằng một thứ tự quyết định rõ ràng sẽ sửa được các lỗi về phạm vi, hỏi lại và xác nhận.
  - Cách làm: thứ tự 5 bước (ngoài phạm vi → câu hỏi về agent → thiếu thông tin thì `clarify` dạng text → hành động ghi thì `clarify` dạng yes_no → chọn tool), cộng bảng routing, quy ước args, rule cho hội thoại nhiều lượt và rule an toàn.
  - Kết quả: R03, R08, R10, R11, R13 đều được sửa; base tăng từ 0.70 lên 0.95.
- **Thử prompt ngắn:** base giảm còn 0.85 và extension chỉ 0.60. Khi request có nhiều ý (E06–E09), model chỉ gọi `policy` mà bỏ tool chính. Kết luận: bỏ ví dụ cho request nhiều ý và bỏ quy ước `query` thì điểm giảm.
- **v4 (`tools.yaml`):**
  - Giả thuyết: R12 (model hỏi xin nội dung thay vì hỏi xác nhận yes/no) và lỗi bỏ tool chính khi có câu "kiểm tra policy" là do mô tả tool quá sơ sài.
  - Cách làm: viết mô tả mỗi tool theo 3 phần (làm gì, khi nào dùng, khi nào không dùng) và ghi quy ước vào mô tả từng tham số.
  - Kết quả: base 1.00, extension 1.00.
- **v5 (system prompt):** thêm routing cho `hackernews_search` và `github_search`, ghi rõ "tìm repo thì trong phạm vi, viết code thì ngoài phạm vi", và quy định cách trả lời sau khi có kết quả tool (chỉ dùng dữ liệu tool trả về, có link nguồn, báo lỗi rõ ràng). Base và extension giữ ở 1.00, không có case nào bị lùi điểm.

**Ghi chú trung thực về nhãn version:** run `v1_B_base_gemini_20261110T203015273552` và `v2_B_base_gemini_20261110T205216453294` có cùng hash với version trước đó, tức là chỉ đổi nhãn. Theo rubric C3, các run này không được tính, nên mình không đưa vào bảng.

### 3.3. Tool mới (CP3)

| Tool | API | Input | Output |
|---|---|---|---|
| `hackernews_search` | Hacker News Algolia (`/search`, `/search_by_date`), không cần key | `query`, `tags` (`story`/`show_hn`/`ask_hn`/`front_page`/`comment`), `sort` (`relevance`/`date`), `date_from`, `date_to`, `limit` | `title, url, hn_url, points, author, num_comments, created_at` |
| `github_search` | GitHub REST `search/repositories`, `GITHUB_TOKEN` là tùy chọn | `query`, `sort` (`stars`/`forks`/`updated`/`best_match`), `order`, `language`, `created_after`, `limit` | `title (owner/repo), url, description, stars, forks, language, topics, updated_at` |

Các quyết định thiết kế:
- Input sai từ model không làm tool crash: enum sai thì quay về giá trị mặc định, `limit` bị giới hạn trong khoảng 1–20, còn `query` rỗng hoặc ngày sai định dạng thì trả về dict lỗi và không gửi request.
- Lỗi API (HTTP error, rate limit 403/429, timeout) được trả về dạng `{"tool", "error", "message"}`, theo đúng contract trong `tools/README.md`.
- `github_search` ghép `language:` và `created:>=` thành qualifier của GitHub, để model không phải tự nhét các qualifier này vào `query`.

**Unit test** nằm trong `starter_v0/tests/test_tools_todo.py`, gồm 10 test chạy offline, mock HTTP bằng `fake_http`:

- `hackernews_search` (5 test):
  - Trường hợp chuẩn: kiểm tra request gửi đi và cách map kết quả, kể cả bài Ask HN không có link ngoài.
  - `sort=date` thì dùng `search_by_date`, kèm `numericFilters` đúng timestamp.
  - Input sai từ model: enum sai, `limit=999`, `query` rỗng, ngày sai định dạng.
  - `front_page` cho phép `query` rỗng.
  - HTTP 503 trả về dict lỗi.
- `github_search` (5 test):
  - Trường hợp chuẩn: ghép qualifier, gửi header `Authorization`, map đúng các trường kết quả.
  - Không có token vẫn chạy và không gửi header auth.
  - Input sai từ model: enum sai, `limit="abc"`, `best_match` không gửi tham số `sort`, `query` rỗng, ngày sai định dạng.
  - Rate limit 403 trả về dict lỗi có gợi ý `GITHUB_TOKEN`.
  - Timeout trả về dict lỗi.

Kết quả `pytest`: **82 passed, 0 failed, 14 skipped**. 14 test skipped là stub của các tool có sẵn; README cho phép để vậy.

### 3.4. Eval case của nhóm (CP4)

`starter_v0/data/eval_group.json` có 10 case, tất cả xoay quanh 2 tool mới:
- Single turn:
  - Route sang HN.
  - Args của HN: `show_hn`, `date`, `limit`.
  - Args của GitHub: `language`, `stars`, `limit`.
  - Gọi song song GitHub và HN.
  - "Viết code … đẩy lên GitHub" thì ngoài phạm vi, không gọi tool.
- Multi turn:
  - Chuyển từ web sang HN.
  - Sửa `language` và `limit` của GitHub qua các lượt.
  - `sort=updated`.
  - Chuyển từ GitHub sang HN mà vẫn giữ chủ đề.
  - Lấy tin HN xong rồi yêu cầu đăng Telegram thì phải `clarify` dạng `yes_no`.

Kết quả với v5: **10/10** (`runs/v5_B_group_gemini_20261111T113347358950.json`).

**Phát hiện:** chạy cùng bộ case với prompt v1 (chưa có routing cho tool mới) cộng `tools.yaml` v4 cũng cho 10/10. Vậy model chọn đúng tool mới là nhờ phần mô tả khi dùng / khi không dùng trong `tools.yaml`, chứ không phải nhờ prompt. Hiện bộ case này đóng vai trò chống lùi điểm (regression guard). Muốn phân biệt được v4 với v5 thì cần thêm case khó hơn, mập mờ giữa `lookup` và HN.

### 3.5. Demo: backend, CLI và Streamlit (CP5)

- **`starter_v0/server.py`:** JSON HTTP API chỉ dùng thư viện chuẩn.
  - Endpoint: `GET /health`, `GET /tools`, `POST /chat`, `POST /reset`, `GET /sessions/<id>`.
  - Tái sử dụng vòng lặp model → tool của `chat.py`.
  - Mỗi phiên lưu transcript vào `transcripts/`.
  - Có CORS để UI web gọi vào được.
- **`starter_v0/cli_client.py`:** chat qua backend, có các lệnh `/tools`, `/debug`, `/reset`, `/session`.
- **`starter_v0/app.py`:** giao diện Streamlit.
  - Hiện từng tool call kèm args và kết quả, có câu hỏi mẫu để bấm thử.
  - Có nút Có/Không cho `clarify` dạng `yes_no` và nút lựa chọn cho dạng `choice`.
  - Sidebar để chọn provider, model và nhãn version.
  - Lưu transcript với channel là `streamlit`.

## 4. Bằng chứng

- **Commit:** `e90ff2a` "Lab tool calling" trên nhánh `huy_agent`.
- **Prompt và tool:** `starter_v0/artifacts/system_prompt.md`, `starter_v0/artifacts/tools.yaml`.
- **Tool mới:** `starter_v0/tools/hackernews_search/`, `starter_v0/tools/github_search/` (mỗi thư mục có `tool.py` và `TOOL.md`); đăng ký trong `starter_v0/tools/__init__.py`.
- **Test:** `starter_v0/tests/test_tools_todo.py` (10 test mới), `starter_v0/tests/conftest.py`.
- **Eval group:** `starter_v0/data/eval_group.json`.
- **Run:** `starter_v0/runs/` (các file liệt kê ở mục 3.2 và 3.4); bảng CSV trong `starter_v0/analysis/`.
- **Transcript:**
  - `starter_v0/transcripts/v3_gemini_backend_20261110T213707012646.transcript.json`
  - `starter_v0/transcripts/v3_gemini_backend_20261110T215416929445.transcript.json`
  - `starter_v0/transcripts/v3_gemini_backend_20261110T215505638126.transcript.json`
  - `starter_v0/transcripts/v5_gemini_streamlit_20261110T220033075947.transcript.json`
- **Demo:** `starter_v0/server.py`, `starter_v0/cli_client.py`, `starter_v0/app.py`.

### AI/công cụ đã dùng và cách tự kiểm tra kết quả

- **Công cụ:** Claude Code (Claude Opus 5.5, chạy trong VS Code). Mình dùng nó để phân tích run JSON, đề xuất và viết lại system prompt cùng `tools.yaml`, viết code 2 tool mới và unit test, viết `server.py`, `cli_client.py`, `app.py` và 10 eval case.
- **Cách tự kiểm tra:**
  - Mỗi thay đổi đều chạy `run_eval.py` với provider thật. Mình xác nhận prompt/tools hash trong run đã đổi trước khi coi đó là một version mới; nhờ vậy đã phát hiện 2 run chỉ đổi nhãn.
  - Đọc `failures` và `actual_tool_calls` trong run JSON để biết lỗi nằm ở tool nào, args nào, thay vì chỉ nhìn `case_accuracy`.
  - Chạy `pytest` toàn suite (gồm contract test `tools.yaml` ↔ code ↔ eval) sau mỗi lần sửa tool hoặc `tools.yaml`.
  - Gọi API thật cho từng tool (Tavily, Firecrawl, arXiv, HN, GitHub) để kiểm tra key và cách map output. Nhờ vậy tìm ra lỗi 403 của RapidAPI.
  - Chạy lại bộ eval group với prompt v1 để kiểm tra xem bộ case có phân biệt được hai version hay không (kết quả: không).
  - Chạy thử UI Streamlit headless bằng `streamlit.testing.v1.AppTest`, chat thử qua backend và CLI.

## 5. Tự đánh giá

<!-- Phần này cần tự viết bằng lời của bạn (RULES.md: không dùng AI để viết phần tự đánh giá). Gợi ý câu hỏi:
- Điều gì mình hiểu rõ nhất sau lab (ví dụ: vì sao mô tả tool trong tools.yaml lại quyết định routing)?
- Phần nào mình làm tốt, phần nào chưa (ví dụ: nhãn version bị lẫn, Twitter chưa subscribe, eval group chưa phân biệt được v4/v5)?
- Nếu làm lại, mình sẽ đổi gì trong quy trình (một giả thuyết mỗi version, kiểm tra hash trước khi chạy)?
- Tự chấm mức đóng góp so với vai trò AI Engineer.
-->

...
