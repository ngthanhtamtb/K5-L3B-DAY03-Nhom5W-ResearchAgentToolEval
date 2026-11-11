# Báo cáo cá nhân — Nguyễn Huy Tấn — 2A202603925

## 1. Thông tin thành viên

- Họ tên: Nguyễn Huy Tấn
- MSSV: 2A202603925
- Email: 26ai.tannh@vinuni.edu.vn
- GitHub: [Besoi2004](https://github.com/Besoi2004)
- Vai trò trong [TEAM.md](../../TEAM.md): Tester

## 2. Phần việc phụ trách

Phụ trách **bộ eval nhóm (CP4 / RUBRIC C5)**: file [`starter_v0/data/eval_group.json`](../../starter_v0/data/eval_group.json), gồm đúng **10 case: 5 single-turn + 5 multi-turn**. Các case kiểm tra agent có gọi đúng 2 tool mới của nhóm là `hackernews_search` và `github_search` hay không. Mỗi case có `expect` và `metadata.what_it_tests`.

Làm theo quy trình nhóm trưởng đặt ra: tạo nhánh mới từ `main` → commit file của mình → đẩy nhánh → tạo PR để nhóm trưởng review.

Nguồn gốc nội dung:
- Bộ case ban đầu (G01–G05, GM01–GM04 và bản GM05 cũ) nằm trong commit [7d03d62](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/commit/7d03d62) trên nhánh `huy_agent` của Trịnh Gia Huy.
- Tấn viết lại case GM05 và đóng gói toàn bộ file để đưa vào `main`.

## 3. Đóng góp cụ thể

### 3.1. Viết lại case GM05 thành `GM05_hn_rust_refine`

Commit [80f23a6](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/commit/80f23a6), thay `GM05_hn_digest_then_send_needs_confirm` bằng case mới:

| Trường | Giá trị |
|---|---|
| Turn 1 | "Tìm tin mới về Rust" |
| Turn 2 | "Mình muốn 3 bài mới nhất trên Hacker News" |
| `failure_type` | `wrong_arg_value` |
| `expect` | `hackernews_search(query="Rust", sort="date", limit=3)` |
| `difficulty` | medium |

Mục đích của case:
- Lượt 1 chỉ có chủ đề, chưa có nguồn.
- Lượt 2 mới chỉ rõ nguồn (Hacker News), thứ tự ("mới nhất" → `sort="date"`) và số lượng ("3 bài" → `limit=3`).
- Agent phải **giữ topic `Rust` từ lượt 1** và **ánh xạ đúng args** theo [`tools/hackernews_search/TOOL.md`](../../starter_v0/tools/hackernews_search/TOOL.md): `sort` nhận `relevance | date`, `limit` bị giới hạn 1–20.

### 3.2. Đưa bộ eval vào `main` qua PR riêng

- Nhánh `eval-group` đầu tiên tách ra từ commit merge PR #3. Sau đó `main` bị đưa về `d540590`, nên nhánh này kéo theo 38 file của nhánh `huy_agent`.
- Đã tạo lại nhánh `eval-group-v2` từ `main` hiện tại (`d540590`) và commit [79d5c7d](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/commit/79d5c7d), chỉ chứa `starter_v0/data/eval_group.json` (+155 / −2).
- Mở PR [#8](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/pull/8) `eval-group-v2 → main`. PR này cần merge **sau** PR [#6](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/pull/6), vì hai tool `hackernews_search` / `github_search` nằm ở PR #6.

### 3.3. Bảng 10 case (dùng cho mục B3 của group report)

| # | Case ID | Loại | What It Tests | Expected Tool/Behavior | Result (run v5 group) |
|---|---|---|---|---|---|
| 1 | `G01_hn_topic_routing` | single | Nhắc Hacker News → không dùng `lookup`/`social_search` | `hackernews_search(query="LLM")` | PASS |
| 2 | `G02_hn_show_hn_latest_args` | single | "Show HN", "mới nhất", "3 bài" → đúng args | `hackernews_search(query="Rust", tags="show_hn", sort="date", limit=3)` | PASS |
| 3 | `G03_github_language_stars_args` | single | Ngôn ngữ vào `language`, không nhét vào query | `github_search(query="RAG", language="python", sort="stars", limit=3)` | PASS |
| 4 | `G04_parallel_github_and_hn` | single | Một yêu cầu cần 2 nguồn → gọi song song | `github_search` + `hackernews_search`, `query="agentic AI"` | PASS |
| 5 | `G05_write_code_out_of_scope` | single | Có chữ "GitHub" nhưng là yêu cầu viết code | `no_tool`, từ chối | PASS |
| 6 | `GM01_switch_web_to_hn` | 3 turns | Bỏ web, chuyển sang HN, giữ chủ đề | `hackernews_search(query="AI")` | PASS |
| 7 | `GM02_github_correction_language_limit` | 3 turns | Giữ query lượt 1, thêm language, limit | `github_search(query="vector database", language="rust", limit=3)` | PASS |
| 8 | `GM03_github_sort_updated` | 3 turns | "mới cập nhật" → `sort=updated` | `github_search(query="MCP server", sort="updated", limit=5)` | PASS |
| 9 | `GM04_switch_github_to_hn_keep_topic` | 3 turns | Đổi tool, giải nghĩa đại từ "nó" | `hackernews_search(query="agentic AI")` | PASS |
| 10 | `GM05_hn_rust_refine` | 2 turns | Giữ topic, áp args khi user tinh chỉnh nguồn | `hackernews_search(query="Rust", sort="date", limit=3)` | **Chưa có run** (xem mục 4) |

Phân bố `failure_type`:
- `wrong_tool`: 4 case (G01, G04, GM01, GM04)
- `wrong_arg_value`: 5 case (G02, G03, GM02, GM03, GM05)
- `out_of_scope`: 1 case (G05)

Cả 10 case đều route tới ít nhất một tool mới (riêng G05 kiểm tra việc **không** gọi tool), nên đạt yêu cầu "≥ 1 case route tới tool mới" của RUBRIC C5.

## 4. Bằng chứng

- File: [`starter_v0/data/eval_group.json`](../../starter_v0/data/eval_group.json). JSON hợp lệ; đủ 5 case có `query` và 5 case có `turns`.
- Commit: [80f23a6](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/commit/80f23a6) (viết lại GM05), [79d5c7d](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/commit/79d5c7d) (đưa file lên nhánh từ `main`).
- PR: [#8](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/pull/8).
- Run eval nhóm: `starter_v0/runs/v5_B_group_gemini_20261111T113347358950.json` (provider `gemini`, model `gemini-3.8-flash`, sinh lúc 2026-11-11T11:33:47). Kết quả:
  - `total_cases = measured_cases = 10`, `provider_error_cases = 0` → đây là run hợp lệ theo RUBRIC.
  - `case_accuracy = tool_routing_accuracy = argument_accuracy = multiturn_accuracy = 1.0`.
  - **Lưu ý:** run này chạy trên bản **GM05 cũ** (`GM05_hn_digest_then_send_needs_confirm`, kết quả gọi `clarify(response_type="yes_no")` → PASS). Chưa có run nào cho `GM05_hn_rust_refine`. Cần chạy lại `--suite group` sau khi merge PR #6 và PR #8 để có bằng chứng cho đủ 10 case hiện tại.
- AI/công cụ đã dùng và cách tự kiểm tra:
  - Claude Code hỗ trợ kiểm tra nhánh so với `main`, tạo nhánh mới, kiểm tra nội dung PR và soạn báo cáo.
  - Đã tự kiểm tra:
    - args của GM05 khớp `inputs` trong `TOOL.md` của `hackernews_search`;
    - file parse được bằng `json.load`;
    - PR #8 chỉ thay đổi 1 file.
  - Số liệu PASS ở trên đọc trực tiếp từ run JSON, không tự điền.

## 5. Tự đánh giá

- **Đã hoàn thành:**
  - Bộ eval nhóm đúng cấu trúc 5 + 5, có `expect` và `what_it_tests`, tập trung vào 2 tool mới.
  - Đã đưa lên PR riêng, tách từ `main` và chỉ chứa đúng file của mình, theo đúng quy trình nhóm trưởng yêu cầu.
- **Hạn chế và việc cần làm tiếp:**
  1. **Thiếu run cho GM05 mới.** Sau khi merge PR #6 và #8, cần chạy `python run_eval.py --suite group`. Nếu GM05 FAIL thì ghi lỗi vào bảng B2.
  2. **GM05 mới khá giống G02:** cùng `query="Rust"`, `sort="date"`, `limit=3`. Điểm khác là GM05 chia thông tin qua 2 lượt và không có `tags="show_hn"`. Nếu người chấm coi đây là trùng case thì có thể đổi chủ đề hoặc đổi args (ví dụ `tags="ask_hn"` hoặc thêm `date_from`).
  3. **Mất case boundary.** GM05 cũ là case duy nhất kiểm tra boundary của `send` (phải hỏi `clarify(yes_no)` trước khi đăng Telegram). Sau khi thay, bộ eval nhóm không còn case `wrong_boundary`. Nên cân nhắc đưa case này trở lại bằng cách thay một case multi-turn khác.
  4. Toàn bộ 9 case còn lại PASS 100% trên `gemini-3.8-flash`. Bộ case có thể đang hơi dễ với model cloud, nên vòng sau có thể thêm case mơ hồ hơn (thiếu thông tin → `clarify`).
