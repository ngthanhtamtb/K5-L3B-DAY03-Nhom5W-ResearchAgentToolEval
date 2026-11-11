# Báo cáo cá nhân — Nguyễn Huy Tấn — 2A202603925

## 1. Thông tin thành viên

- Họ tên: Nguyễn Huy Tấn
- MSSV: 2A202603925
- Email: 26ai.tannh@vinuni.edu.vn
- GitHub: [Besoi2004](https://github.com/Besoi2004)
- Vai trò trong [TEAM.md](../../TEAM.md): Tester

## 2. Phần việc phụ trách

Phụ trách bộ eval nhóm (CP4 / RUBRIC C5):
- [`starter_v0/data/eval_group.json`](../../starter_v0/data/eval_group.json): đúng **10 case, gồm 5 single-turn (G01–G05) và 5 multi-turn (G06–G10)**.
- Chạy `--suite group` để có log đo thật.
- Phân tích từng case trong [`starter_v0/data/eval_group.md`](../../starter_v0/data/eval_group.md).

## 3. Đóng góp cụ thể

### 3.1. Thiết kế 10 case

Mỗi case có `id`, `phase="B"`, `failure_type` hợp lệ, `expect` và `metadata.what_it_tests`. Không case nào chép từ `eval_base.json` hay `eval_research_extension.json`.

| Nhóm kỹ năng | Case |
|---|---|
| Args đúng convention (`search_type`, `screenname` bỏ `@`, `timeframe`) | G01, G02, G03 |
| Boundary của `send` (hỏi xác nhận, gửi khi đã xác nhận, huỷ) | G04, G06, G07 |
| Ngoài phạm vi research | G05 |
| Thiếu thông tin → tiếp tục `clarify` | G08 |
| Đổi nguồn giữa các lượt | G09 (web → arXiv), G10 (Twitter → **tool mới `hackernews_search`**) |

Phân bố `failure_type`:
- `wrong_arg_value`: 3 case
- `wrong_boundary`: 3 case
- `wrong_tool`: 2 case
- `out_of_scope`: 1 case
- `missing_info`: 1 case

G10 là case route tới tool mới của nhóm, đáp ứng yêu cầu "≥ 1 case route tới tool mới".

### 3.2. Kết quả chạy (bảng B3)

Run: [`starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json`](../../starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json)

Cấu hình: provider `openrouter`, model `openai/gpt-4o-mini`, artifacts `v3`, suite `group`.

Run hợp lệ theo RUBRIC: `measured_cases = 10`, `provider_error_cases = 0`.

| Chỉ số | Kết quả |
|---|---:|
| passed_cases | 9/10 |
| case_accuracy | 90% |
| tool_routing_accuracy | 100% |
| argument_accuracy | 90% |
| multiturn_accuracy | 80% (4/5) |

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_topic_latest_search_type | "mới nhất" theo chủ đề → `search_type=Latest`, không nhầm sang `timeline` | `social_search(search_type="Latest")` | PASS |
| G02_handle_strip_at | Handle có `@` → `screenname` bỏ `@`, `limit=7` là số nguyên | `timeline(screenname="karpathy", limit=7)` | PASS |
| G03_timeframe_month | "tháng này" → `timeframe=month`, `topic=news` | `lookup(topic="news", timeframe="month")` | PASS |
| G04_send_with_text_still_needs_confirm | Có sẵn nội dung nhưng "gửi" chưa phải xác nhận | `clarify(response_type="yes_no")` | PASS |
| G05_out_of_scope_booking | Đặt vé máy bay → ngoài phạm vi, không gọi tool | Không gọi tool | PASS |
| G06_confirmed_then_send | User đã xác nhận rõ ở lượt cuối → gửi | `send(confirmed=true)` | PASS |
| G07_user_cancels_send | User huỷ ở lượt cuối → không gửi | Không gọi tool | PASS |
| G08_still_missing_url | Lượt bổ sung vẫn thiếu URL → hỏi tiếp, không đoán | `clarify(response_type="text")` | PASS |
| G09_switch_to_papers_sorted | Web → arXiv, "mới nộp gần đây" → `sort_by=submittedDate` | `papers(sort_by="submittedDate")` | PASS |
| G10_switch_to_hackernews | Twitter → Hacker News, giữ chủ đề Gemini, 3 bài mới nhất | `hackernews_search(query="Gemini", sort="date", limit=3)` | **FAIL** |

### 3.3. Phân tích case FAIL

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix đề xuất |
|---|---|---|---|---|
| G10_switch_to_hackernews | `wrong_arg_value` (observed) | `hackernews_search(query="Gemini", limit=3)` | Thiếu `sort="date"`, nên tool dùng mặc định `relevance` và không trả bài mới nhất | Trong `tools.yaml`/`system_prompt.md`, ghi rõ "mới nhất / gần đây" → `sort="date"` cho `hackernews_search`, rồi chạy lại một version mới |

Model đã chọn đúng tool, giữ đúng chủ đề và `limit`. Lỗi chỉ nằm ở việc ánh xạ từ "mới nhất" sang args. Đáp án `expect` không bị sửa sau khi có kết quả.

### 3.4. Giới hạn của kết quả

- G01 và G02: API Twitter trả HTTP 403/429 nên không lấy được tweet. PASS ở đây chỉ chứng minh routing và args đúng.
- G09: arXiv bị timeout. Routing đúng nhưng chưa lấy được paper.
- G06: Telegram bị tắt trong lúc chạy, nên chỉ kiểm tra quyết định `send(confirmed=true)`, không gửi thật.
- G05 và G07 (`no_tool`): bộ chấm chỉ kiểm tra việc không gọi tool. Nội dung lời từ chối hoặc lời xác nhận huỷ được đọc thủ công trong `actual_text`.

## 4. Bằng chứng

- File: [`starter_v0/data/eval_group.json`](../../starter_v0/data/eval_group.json), [`starter_v0/data/eval_group.md`](../../starter_v0/data/eval_group.md)
- Run: [`starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json`](../../starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json)
- PR: [#8](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/pull/8) (bản eval đầu tiên, đã merge), [#11](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/pull/11) (bộ 10 case cuối và run đo thật)
- AI/công cụ đã dùng và cách tự kiểm tra:
  - Claude Code hỗ trợ thao tác Git (tạo nhánh, commit, push, mở PR) và soạn báo cáo.
  - Đã tự kiểm tra:
    - JSON parse được;
    - đủ 5 `query` + 5 `turns`;
    - không trùng case của `eval_base` hay `eval_research_extension`;
    - các ID case trong run khớp với file;
    - số liệu trong báo cáo lấy trực tiếp từ `summary` và `results` của run JSON;
    - không có API key hay token trong các file commit.

## 5. Tự đánh giá

- **Đã hoàn thành:**
  - 10 case đúng cấu trúc 5 + 5, phủ đủ routing, args, boundary `send`, out-of-scope, missing-info và chuyển nguồn sang tool mới.
  - Có run hợp lệ (9/10 PASS) và phân tích case FAIL.
- **Hạn chế:**
  - Chỉ G10 route tới tool mới, nên phần tool mới chưa được phủ nhiều.
  - Một số PASS chỉ chứng minh routing, vì API Twitter và arXiv lỗi lúc chạy.
- **Nếu có thêm một vòng:**
  - Thêm hướng dẫn `sort="date"` cho `hackernews_search`, rồi chạy lại để kiểm tra G10.
  - Thêm case cho `github_search`.
