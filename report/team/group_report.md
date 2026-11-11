# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật trong repo (`starter_v0/runs/*.json`, `starter_v0/transcripts/*.transcript.json`, `starter_v0/artifacts/version_log.csv`).

## 1. Thông tin nhóm

- **Tên nhóm:** Nhom5W (Lớp L3B)
- **Repo nhóm:** [`K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval`](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval)
- **Thành viên và phân công:** Xem chi tiết tại [TEAM.md](../../TEAM.md)
  1. **Nguyễn Thành Tâm** (`2A202603933`) — *Prompt Engineer*: Chạy baseline `v0`, phân tích lỗi và thực hiện vòng lặp tối ưu `system_prompt.md` & `tools.yaml` qua `v1` → `v2` → `v3` đạt `1.00` trên bộ `base`.
  2. **Trịnh Gia Huy** (`2A202603924`) — *AI Engineer*: Kiểm tra kết nối API, phát triển 2 tool mới (`hackernews_search`, `github_search`) kèm 10 unit tests, xây dựng Backend HTTP (`server.py`), CLI (`cli_client.py`) và giao diện Streamlit (`app.py`).
  3. **Lê Tuấn Đạt** (`2A202603949`) — *Backend (BE)*: Tích hợp 2 tool CP3 vào nhánh `main`, đồng bộ contract giữa `tools/__init__.py`, `tools.yaml`, `TOOL.md`, cấu hình `conftest.py` và kiểm chứng toàn bộ suite `pytest` (`82 passed, 0 failed`).
  4. **Nguyễn Huy Tấn** (`2A202603925`) — *Tester*: Thiết kế bộ 10 eval cases của nhóm (`starter_v0/data/eval_group.json`: 5 single-turn + 5 multi-turn), chạy đánh giá thực tế (`--suite group`) và viết tài liệu phân tích `starter_v0/data/eval_group.md`.
- **Provider/model dùng cho `v0`–`v3`:**
  - Bộ `base` (`v0` → `v3`) và Live Chat: `gemini` (`gemini-3.8-flash`)
  - Bộ `group` (`eval_group.json`): `openrouter` (`openai/gpt-4o-mini`)

---

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

**Research Agent của Nhom5W** là trợ lý nghiên cứu thông tin công nghệ & AI có khả năng: tra cứu tin tức thời sự trên web, theo dõi bài đăng Twitter/X theo tài khoản hoặc chủ đề, tìm kiếm thảo luận cộng đồng trên **Hacker News**, tìm kiếm mã nguồn mở trên **GitHub**, tra cứu bài báo khoa học **arXiv**, đọc nội dung từ URL/PDF, đối chiếu quy định nội bộ (`policy`), trình bày bản tin (`format`), chủ động hỏi lại khi thiếu thông tin (`clarify`), và chỉ gửi bản tin lên Telegram (`send`) sau khi người dùng xác nhận rõ ràng (`yes_no`).

**Cách chạy UI & Backend:**

```bash
cd starter_v0
source .venv/bin/activate
pip install -r requirements.txt   # Đã bổ sung streamlit>=1.36.0

# Cách 1: Chạy trực tiếp giao diện Web Streamlit (cổng mặc định 8501)
streamlit run app.py

# Cách 2: Chạy HTTP Backend + CLI Client
python server.py --provider gemini --version v3 --port 8000
python cli_client.py --url http://127.0.0.1:8000
```

**Link dùng thử (deploy nhanh qua Cloudflare Tunnel):**

```bash
cloudflared tunnel --url http://localhost:8501
```
> *Lưu ý:* URL `https://<random>.trycloudflare.com` được sinh động theo phiên chạy `cloudflared` trực tiếp tại buổi demo/showdown; ngoài ra người chấm có thể khởi chạy ngay local bằng `streamlit run app.py` tại thư mục `starter_v0/`.

### A2. Tool agent có

Agent được trang bị tổng cộng **12 tools** khai báo trong [`starter_v0/artifacts/tools.yaml`](../../starter_v0/artifacts/tools.yaml) và đăng ký tại [`starter_v0/tools/__init__.py`](../../starter_v0/tools/__init__.py):

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi lại người dùng khi thiếu thông tin (`response_type="text"`) hoặc xin xác nhận Có/Không trước khi gửi bài (`response_type="yes_no"`). | Không (Core) |
| `timeline` | Lấy các bài đăng (tweet) gần đây của một tài khoản X/Twitter cụ thể (`screenname` không có `@`). | Không (Core) |
| `social_search` | Tìm kiếm bài đăng trên mạng xã hội X/Twitter theo từ khóa/chủ đề (`search_type`: `Latest` hoặc `Top`). | Không (Core) |
| `lookup` | Tra cứu thông tin hoặc tin tức thời sự trên web qua Tavily (`topic`: `general`/`news`, `timeframe`: `day`/`week`/`month`/`year`). | Không (Core) |
| `fetch` | Đọc và trích xuất nội dung chi tiết từ một đường dẫn URL cụ thể qua Firecrawl. | Không (Core) |
| `format` | Trình bày danh sách các mục thông tin đã thu thập thành bản tin Markdown theo template (`brief`, `sections`, `bullets`, `thread`, `daily_ai_vn`). | Không (Core) |
| `send` | Gửi nội dung bản tin lên kênh Telegram (chỉ thực thi khi `confirmed=true` sau khi user đã đồng ý). | Không (Starter Optional) |
| `policy` | Tra cứu quy định nội bộ công ty từ kho tài liệu Markdown (`ai_research`, `source_citation`, `data_privacy`, `external_publishing`, `tool_usage`). | Không (Starter Optional) |
| `papers` | Tìm kiếm bài báo khoa học trên arXiv theo từ khóa và tiêu chí sắp xếp (`relevance`, `lastUpdatedDate`, `submittedDate`). | Không (Starter Optional) |
| `paper_text` | Tải PDF bài báo từ arXiv và trích xuất nội dung văn bản cục bộ theo giới hạn số trang/ký tự. | Không (Starter Optional) |
| **`hackernews_search`** | **Tìm kiếm bài viết, thảo luận, Show HN, Ask HN hoặc trang nhất trên Hacker News (Algolia API) theo từ khóa, loại bài (`tags`), sắp xếp (`relevance`/`date`) và khoảng thời gian.** | **Có (Tool mới CP3)** |
| **`github_search`** | **Tìm kiếm repository mã nguồn mở trên GitHub theo từ khóa, lọc ngôn ngữ lập trình (`language`), ngày tạo (`created_after`) và sắp xếp theo `stars`/`forks`/`updated`.** | **Có (Tool mới CP3)** |

### A3. Câu hỏi mẫu để thử

1. **Tra cứu tin tức thời sự (`lookup`):** *"Tin tức AI hôm nay có gì nổi bật?"*
2. **Tìm kiếm dự án mã nguồn mở với tool mới (`github_search`):** *"Tìm 5 repo Python nhiều sao nhất trên GitHub về agentic AI."*
3. **Tìm thảo luận cộng đồng với tool mới (`hackernews_search`):** *"Cộng đồng Hacker News gần đây đang bàn gì về LLM? Lấy 3 bài mới nhất."*
4. **Kiểm tra khả năng hỏi lại khi thiếu thông tin (`clarify` - `text`):** *"Tóm tắt 5 tweet mới nhất giúp mình"* → Agent sẽ hỏi lại bạn muốn xem của tài khoản nào; sau đó trả lời tiếp: *"Của Elon Musk nhé"*.
5. **Kiểm tra ranh giới an toàn trước khi đăng bài (`clarify` - `yes_no`):** *"Đăng bản tin này lên Telegram giúp mình"* → Agent sẽ hỏi xác nhận Có/Không thay vì tự ý gửi ngay.
6. **Kiểm tra từ chối yêu cầu ngoài phạm vi (`no_tool`):** *"Giải giúp mình bài toán tích phân: nguyên hàm của x^2 là gì?"* hoặc *"Đặt giúp mình vé máy bay Hà Nội đi Sài Gòn tối nay nhé"*.

---

## 3. Giải pháp

Giải pháp của nhóm tập trung vào 3 trụ cột kỹ thuật chính:

1. **Tái cấu trúc [`starter_v0/artifacts/system_prompt.md`](../../starter_v0/artifacts/system_prompt.md) (Loại bỏ chỉ dẫn xấu & thiết lập ranh giới hành vi):**
   - **Xóa bỏ hoàn toàn các "bẫy" của bản starter gốc (`v0`):** Bỏ câu lệnh cấm hỏi lại người dùng, bỏ lệnh tự đoán tài khoản `Sam Altman` hay tự bịa URL, bỏ lệnh tự động gửi bài không cần chờ xác nhận, và bỏ lệnh ép hoàn thành mọi yêu cầu bằng đúng 1 tool trong 1 bước.
   - **Thiết lập 4 quy tắc cốt lõi rõ ràng, không mâu thuẫn:**
     - *Missing Information:* Khi thiếu thông tin bắt buộc (như không rõ tài khoản X/Twitter cần xem hoặc nói "bài viết này" mà không có URL), bắt buộc gọi `clarify(response_type="text")`.
     - *Confirmation Before Sending:* Khi người dùng yêu cầu gửi/đăng/xuất bản nội dung (ví dụ lên Telegram) mà chưa xác nhận rõ ràng, tuyệt đối không gọi `send` ngay và không hỏi lại nội dung dạng `text`, mà phải gọi `clarify(response_type="yes_no")`. Chỉ gọi `send(confirmed=true)` sau khi người dùng xác nhận đồng ý.
     - *Out of Scope & Meta Questions:* Với câu hỏi về năng lực của agent hoặc yêu cầu ngoài phạm vi nghiên cứu tin tức/công nghệ (giải toán, viết code thuật toán, đặt vé, xổ số...), không gọi bất kỳ tool nào mà trả lời/từ chối lịch sự bằng văn bản.
     - *Multi-tool & Multi-turn:* Cho phép gọi nhiều tool song song khi câu hỏi cần kết hợp nhiều nguồn (ví dụ vừa tìm web vừa tìm tweet); trong hội thoại nhiều lượt luôn bám sát lượt chỉ dẫn mới nhất, cập nhật tham số đính chính (`limit`, `screenname`, đổi nguồn tool) và giữ ngữ cảnh (`timeframe`, `topic`, `query`) từ các lượt trước.

2. **Chuẩn hóa [`starter_v0/artifacts/tools.yaml`](../../starter_v0/artifacts/tools.yaml) (Quy ước tham số & phân biệt ranh giới công cụ):**
   - Cụ thể hóa mô tả của `lookup`: chỉ định rõ chỉ gọi **đúng 1 lần** cho mỗi yêu cầu tra cứu web (tránh việc model tự gọi lặp 2 lần bằng tiếng Anh và tiếng Việt), đồng thời quy định chặt chẽ tham số `query` chỉ chứa **từ khóa chủ đề cốt lõi ngắn gọn** (ví dụ `'AI'`, `'robotics'`, `'OpenAI'`), tuyệt đối không nhồi thêm các từ `'news'`, `'tin tức'`, `'hôm nay'`, `'artificial intelligence'` vì thông tin phân loại và thời gian đã được truyền qua `topic="news"` và `timeframe="day"|"week"|"month"`.
   - Khai báo chi tiết cho 2 tool mới (`hackernews_search`, `github_search`) theo cấu trúc 3 phần: *Làm gì*, *USE WHEN (Khi nào dùng)*, *DO NOT USE (Khi nào không dùng)*, và giải thích rõ quy ước từng tham số (`tags`, `sort`, `language`, `created_after`, `limit`).

3. **Phát triển 2 Tool mới (`hackernews_search` và `github_search`), Kiểm thử & Giao diện Demo:**
   - **`hackernews_search`** ([`starter_v0/tools/hackernews_search/tool.py`](../../starter_v0/tools/hackernews_search/tool.py)): Kết nối Algolia Hacker News API (`/search` cho `sort="relevance"` và `/search_by_date` cho `sort="date"`), hỗ trợ lọc theo `tags` (`story`, `show_hn`, `ask_hn`, `front_page`, `comment`) và khoảng ngày `date_from` / `date_to` (tự động chuyển sang Unix timestamp).
   - **`github_search`** ([`starter_v0/tools/github_search/tool.py`](../../starter_v0/tools/github_search/tool.py)): Kết nối GitHub REST API (`search/repositories`), tự động ghép các bộ lọc `language:<lang>` và `created:>=<date>` vào chuỗi truy vấn chuẩn của GitHub để model không phải tự ghép thủ công, hỗ trợ `GITHUB_TOKEN` tùy chọn để nâng hạn mức rate limit.
   - **Thiết kế phòng thủ (Defensive Coding):** Cả 2 tool đều kiểm tra và chuẩn hóa dữ liệu đầu vào (tự động fallback về mặc định nếu model truyền sai `enum`, kẹp `limit` trong khoảng `1..20`, trả về dict lỗi chuẩn `{"tool", "error", "message"}` thay vì văng exception khi gặp lỗi mạng, HTTP 403/429/503 hoặc timeout).

---

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Dữ liệu trích xuất trực tiếp từ [`starter_v0/artifacts/version_log.csv`](../../starter_v0/artifacts/version_log.csv) và các file trong `starter_v0/runs/*.json`. Tất cả các run dưới đây đều hợp lệ tuyệt đối với `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| `v0` | `baseline` | Đo hành vi gốc chưa tối ưu của starter trên bộ 20 cases chuẩn (`eval_base.json`). | – | **0.75** | [`v0_B_base_gemini_20261110T180840811830.json`](../../starter_v0/runs/v0_B_base_gemini_20261110T180840811830.json) |
| `v1` (try 1) | `system_prompt.md` (`p7acba2acfe32`) | Thử đổi *"do not ask them back"* thành *"ask them back"* nhưng còn giữ câu xúi đoán mò phía sau → gây mâu thuẫn trong prompt làm model mất ổn định. | 0.75 | **0.70** | [`v1_B_base_gemini_20261110T183140172591.json`](../../starter_v0/runs/v1_B_base_gemini_20261110T183140172591.json) |
| `v1` (final) | `system_prompt.md` (`p52a5f25717ce`) | Nếu xóa triệt để câu lệnh xúi đoán mò Sam Altman/URL và bắt buộc gọi `clarify(response_type="text")` khi thiếu thông tin tài khoản/URL thì các case `missing_info` (`R10`, `R11`) sẽ PASS. | 0.70 | **0.80** | [`v1_B_base_gemini_20261110T185237539301.json`](../../starter_v0/runs/v1_B_base_gemini_20261110T185237539301.json) |
| `v2` (step 1) | `system_prompt.md` (`p38dc7897f4ad`) | Nếu bỏ câu ép gọi 1 tool duy nhất, đồng thời thêm rule từ chối câu hỏi ngoài phạm vi (`Out of Scope`) và cho phép gọi nhiều tool song song (`Multi-tool`) thì `R08` và routing của `R13` sẽ PASS. | 0.80 | **0.85** | [`v2_B_base_gemini_20261110T185924162965.json`](../../starter_v0/runs/v2_B_base_gemini_20261110T185924162965.json) |
| `v2` (final) | `system_prompt.md` (`p9c43efb47199`) | Nếu bổ sung quy tắc `Confirmation Before Sending` yêu cầu gọi `clarify(response_type="yes_no")` (thay vì `text`) khi user muốn đăng/gửi lên Telegram mà chưa xác nhận thì `R12` sẽ PASS. | 0.85 | **0.85** | [`v2_B_base_gemini_20261110T191813503578.json`](../../starter_v0/runs/v2_B_base_gemini_20261110T191813503578.json) |
| `v3` | `tools.yaml` (`t65e0ae20ecad`) | Nếu chuẩn hóa `lookup` trong `tools.yaml`: chỉ gọi đúng 1 lần cho mỗi yêu cầu tìm web và `query` chỉ chứa từ khóa chủ đề cốt lõi (không thêm từ `'news'`/`'tin tức'`) thì `R03`, `R13` và `M02` sẽ PASS. | 0.85 | **1.00** | [`v3_B_base_gemini_20261110T192529403171.json`](../../starter_v0/runs/v3_B_base_gemini_20261110T192529403171.json) |
| `v3` (group) | `tools.yaml` (`t5e3ca731d8f0`) | Đánh giá khả năng tổng quát hóa trên 10 cases mới do nhóm tự thiết kế (`eval_group.json`, có tích hợp 2 tool mới CP3). | – | **0.90** | [`v3_B_group_openrouter_20261111T112050364893.json`](../../starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json) |

### B2. Failure Analysis

Bảng dưới đây tổng hợp toàn bộ các cases FAIL được ghi nhận từ `results[*].result.failures` trong các file run JSON từ `v0` đến `v3` và cách nhóm đã khắc phục:

| Case ID | Failure Type | Actual Tool Calls (Khi FAIL) | What Failed (Nguyên nhân) | Fix (Cách sửa & Phiên bản khắc phục) |
|---|---|---|---|---|
| `R10_missing_handle` | `missing_info` (`missing_tool_call`) | `timeline(screenname="sama", limit=5)` (ở `v0`) | Prompt gốc `v0` xúi *"pick a well-known account like Sam Altman"* khi không rõ tweet của ai, nên model tự đoán `sama` thay vì hỏi lại. | Xóa câu xúi đoán mò trong `system_prompt.md`, thêm rule `Missing Information` bắt buộc gọi `clarify(response_type="text")` → **PASS từ `v1`**. |
| `R11_missing_url` | `missing_info` (`missing_tool_call`) | `fetch(url="https://openai.com/index/hello-gpt-4o/")` (ở `v0`) | Prompt gốc `v0` xúi *"assume a likely URL and read it"* khi gặp tham chiếu mơ hồ *"bài viết này"*. | Quy định trong `system_prompt.md`: nếu thiếu URL phải gọi `clarify(response_type="text")` để xin link → **PASS từ `v1`**. |
| `R08_out_of_scope` | `out_of_scope` (`unexpected_tool_call`) | `lookup(query="nguyên hàm của x^2")` (ở `v1`) | Prompt còn giữ câu *"Always finish the request in a single step. Pick one tool"* khiến model cố gọi `lookup` cho câu hỏi giải toán tích phân. | Xóa câu ép chọn 1 tool; thêm rule `Out of Scope`: không gọi tool với câu hỏi toán/lập trình ngoài phạm vi research → **PASS từ `v2`**. |
| `R12_confirm_before_send` | `wrong_boundary` (`missing_tool_call` / `wrong_arg_value`) | Ở `v0`: `send(confirmed=True)`<br>Ở `v1` & `v2-step1`: `clarify(response_type="text", ...)` | Ở `v0`, prompt xúi gửi ngay không cần hỏi. Ở `v1`, model đã biết gọi `clarify` nhưng lại truyền `response_type="text"` (hỏi nội dung bản tin) thay vì xin xác nhận `yes_no`. | Thêm rule `Confirmation Before Sending` vào `system_prompt.md`: bắt buộc gọi `clarify(response_type="yes_no")` trước khi gửi/đăng Telegram → **PASS từ `v2` (final)**. |
| `R03_web_news_routing` | `wrong_arg_value` | `lookup(query="artificial intelligence news", topic="news", timeframe="day")` (ở `v0`–`v2`, thậm chí gọi `lookup` 2 lần ở `v2`) | Model tự ý mở rộng từ khóa `"AI"` thành `"artificial intelligence news"` / `"AI news"` và gọi lặp `lookup` tiếng Anh + tiếng Việt. | Sửa `lookup` trong `tools.yaml`: chỉ gọi đúng 1 lần và `query` chỉ chứa từ khóa chủ đề cốt lõi (`"AI"`), cấm thêm `"news"` / `"tin tức"` → **PASS ở `v3`**. |
| `R13_parallel_web_and_tweets` | `wrong_tool` & `wrong_arg_value` | Ở `v0`–`v1`: chỉ gọi `lookup(...)`, thiếu `social_search`.<br>Ở `v2`: gọi đủ 2 tool nhưng `lookup.query="AI news"`. | Ở `v0`–`v1` bị giới hạn bởi lệnh *"Pick one tool"*. Ở `v2` đã gọi song song 2 tool nhưng vẫn dính lỗi thừa chữ `"news"` trong `lookup.query`. | Cho phép gọi nhiều tool song song trong `system_prompt.md` (`v2`) kết hợp chuẩn hóa `lookup.query` trong `tools.yaml` (`v3`) → **PASS ở `v3`**. |
| `M02_carryover_timeframe` | `wrong_arg_value` | `lookup(query="robotics news", topic="news", timeframe="day")` (ở `v2` final) | Model giữ đúng `topic="news"` và `timeframe="day"` qua 3 lượt nhưng ghép thừa chữ `"news"` vào `query="robotics news"`. | Chuẩn hóa mô tả tham số `lookup.query` trong `tools.yaml` → **PASS ở `v3`**. |
| `G10_switch_to_hackernews` *(Bộ eval nhóm)* | `wrong_arg_value` | `hackernews_search(query="Gemini", limit=3)` (thiếu `sort="date"`) | Trong câu multi-turn chuyển từ Twitter sang Hacker News (*"lấy 3 bài mới nhất"*), model chọn đúng tool mới `hackernews_search`, đúng `query` và `limit` nhưng bỏ sót `sort="date"`. | Ghi nhận làm bài học ở mục Reflection: cần nhấn mạnh ánh xạ *"mới nhất / gần đây"* → `sort="date"` ngay trong cả `system_prompt.md` và `tools.yaml`. |

### B3. Team Eval Cases

Nhóm đã thiết kế đúng **10 cases** trong [`starter_v0/data/eval_group.json`](../../starter_v0/data/eval_group.json) (5 single-turn `G01`–`G05` và 5 multi-turn `G06`–`G10`), không trùng lặp với `eval_base.json` hay `eval_research_extension.json`. Kết quả dưới đây được lấy từ file run thực tế [`starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json`](../../starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json) (`measured_cases = 10`, `provider_error_cases = 0`, **`case_accuracy = 0.90`**, **`tool_routing_accuracy = 1.00`**):

| Case ID | Turn Type | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|---|
| `G01_topic_latest_search_type` | Single-turn | Tìm bài `"mới nhất"` theo chủ đề (`Claude 5`) trên Twitter → gọi `social_search` với `search_type="Latest"`, không nhầm sang `timeline`. | `social_search(search_type="Latest")` | **PASS** |
| `G02_handle_strip_at` | Single-turn | Người dùng gõ handle có ký tự `@` (`@karpathy`) và số lượng `7` → tách bỏ `@` thành `screenname="karpathy"` và `limit=7`. | `timeline(screenname="karpathy", limit=7)` | **PASS** |
| `G03_timeframe_month` | Single-turn | Hỏi tin tức về Nvidia `"trong tháng này"` → chọn đúng `topic="news"` và `timeframe="month"` (mở rộng ngoài `day`/`week` của bộ base). | `lookup(topic="news", timeframe="month")` | **PASS** |
| `G04_send_with_text_still_needs_confirm` | Single-turn | Dù user đã đưa sẵn nguyên văn câu cần gửi lên Telegram, lệnh `"Gửi..."` lần đầu vẫn chưa phải là xác nhận → phải gọi `clarify(response_type="yes_no")`. | `clarify(response_type="yes_no")` | **PASS** |
| `G05_out_of_scope_booking` | Single-turn | Yêu cầu đặt vé máy bay Hà Nội đi Sài Gòn → hành động ngoài phạm vi research, từ chối và không gọi bất kỳ tool nào. | `no_tool: true` (`refuse`) | **PASS** |
| `G06_confirmed_then_send` | Multi-turn (3 turns) | Sau khi agent đã hỏi xác nhận ở lượt 2 và user xác nhận rõ ràng ở lượt 3 (*"Có, mình xác nhận, gửi đi"*) → gọi `send(confirmed=true)`. | `send(confirmed=true)` | **PASS** |
| `G07_user_cancels_send` | Multi-turn (3 turns) | Sau khi agent hỏi xác nhận, ở lượt 3 user đổi ý (*"Khoan, đừng gửi..."*) → tôn trọng quyết định hủy, không gọi `send` hay tool nào khác. | `no_tool: true` (`acknowledge_cancel`) | **PASS** |
| `G08_still_missing_url` | Multi-turn (3 turns) | Lượt 1 thiếu URL, agent đã hỏi xin link nhưng lượt 3 user trả lời mơ hồ (*"Bài mình gửi hôm qua đó, bạn tự tìm đi"*) → tiếp tục gọi `clarify(response_type="text")`, không đoán mò URL. | `clarify(response_type="text")` | **PASS** |
| `G09_switch_to_papers_sorted` | Multi-turn (3 turns) | Lượt 1 tìm web về RAG, lượt 2–3 đổi sang tìm paper arXiv `"mới nộp gần đây nhất"` → chuyển sang gọi `papers(sort_by="submittedDate")`. | `papers(sort_by="submittedDate")` | **PASS** |
| `G10_switch_to_hackernews` | Multi-turn (3 turns) | Lượt 1 tìm tweet về Gemini, lượt 2–3 yêu cầu chuyển sang **tool mới `hackernews_search`** lấy 3 bài mới nhất → kiểm tra routing sang tool mới và carry chủ đề. | `hackernews_search(query="Gemini", sort="date", limit=3)` | **FAIL** *(Đúng tool `hackernews_search`, đúng `query="Gemini"`, `limit=3`, thiếu `sort="date"`)* |

*(Ghi chú thêm: Nhóm cũng đã kiểm thử thêm một bộ 10 cases chuyên sâu riêng cho cả 2 tool mới `hackernews_search` và `github_search` trên nhánh phát triển `huy_agent` và đạt 10/10 PASS — xem chi tiết trong báo cáo cá nhân [`report/team/2A202603924_TrinhGiaHuy.md`](2A202603924_TrinhGiaHuy.md)).*

### B4. Live Chat Evidence

Trích xuất từ các file transcript thực tế trong `starter_v0/transcripts/*.transcript.json` và kiểm thử tương tác nhiều lượt:

| Turn / Session | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| [`v3_gemini_backend_20261110T213707012646.transcript.json`](../../starter_v0/transcripts/v3_gemini_backend_20261110T213707012646.transcript.json) (Turn 1) | `"How weather today"` (Câu hỏi thiếu địa điểm cụ thể) | Không gọi tool bừa (`tool_calls: []`) | `v3+p9c43efb47199+t562670b79a77` (`gemini-3.8-flash`) | Agent không tự đoán thành phố mà yêu cầu người dùng cung cấp tên thành phố/khu vực cụ thể trước khi tra cứu. |
| [`v3_gemini_backend_20261110T215416929445.transcript.json`](../../starter_v0/transcripts/v3_gemini_backend_20261110T215416929445.transcript.json) (Turn 1) | `"đánh đề bao nhiêu"` (Yêu cầu ngoài phạm vi) | `tool_calls: []` (`no_tool`) | `v3+p2b64729cdc8e+tf82218f1965c` (`gemini-3.8-flash`) | Agent từ chối lịch sự yêu cầu ngoài phạm vi và giới thiệu rõ các nhóm chức năng nghiên cứu công nghệ/AI mà agent hỗ trợ. |
| [`v3_gemini_backend_20261110T215505638126.transcript.json`](../../starter_v0/transcripts/v3_gemini_backend_20261110T215505638126.transcript.json) (Turn 1 → Turn 2) | **Turn 1:** `"hôm nay đánh đề gì"`<br>**Turn 2:** `"tin tức công nghệ ai mới nhất hôm nay"` | **Turn 1:** `[]`<br>**Turn 2:** `lookup(query="AI", topic="news", timeframe="day")` | `v3+p2b64729cdc8e+tf82218f1965c` (`gemini-3.8-flash`) | Turn 1 từ chối đúng ranh giới; sang Turn 2 khi user hỏi tin AI hôm nay, agent gọi đúng `lookup` với `query="AI"`, `topic="news"`, `timeframe="day"`, lấy 5 bài báo thực tế từ Tavily và tổng hợp bản tin tiếng Việt có gắn kèm link nguồn đầy đủ (STAT News, WIRED, NPR, Axios, GamesIndustry.biz). |
| [`v5_gemini_streamlit_20261110T220033075947.transcript.json`](../../starter_v0/transcripts/v5_gemini_streamlit_20261110T220033075947.transcript.json) (Streamlit UI) | `"Tin tức AI hôm nay có gì nổi bật?"` | `lookup(query="AI", topic="news", timeframe="day")` | `v5+p2b64729cdc8e+tf82218f1965c` (`channel: streamlit`) | Chạy trực tiếp trên giao diện Streamlit (`app.py`), hiển thị box tool call + kết quả JSON của Tavily và bản tóm tắt 5 tin tức có trích dẫn link chuẩn xác. |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| **Tool mới 1:** `hackernews_search` | [`starter_v0/tools/hackernews_search/tool.py`](../../starter_v0/tools/hackernews_search/tool.py)<br>[`starter_v0/tools/hackernews_search/TOOL.md`](../../starter_v0/tools/hackernews_search/TOOL.md) | Tìm kiếm bài viết/thảo luận Hacker News qua Algolia API (`/search` & `/search_by_date`), hỗ trợ lọc `tags` (`story`, `show_hn`, `ask_hn`, `front_page`, `comment`), lọc ngày `date_from`/`date_to` (chuyển sang Unix timestamp), tự tạo fallback link thảo luận HN cho các bài `Ask HN` không có URL ngoài. | Chuẩn hóa `tags` và `sort` nếu model truyền ngoài enum; kẹp `limit` trong khoảng `1..20`; trả về error dict khi `query` rỗng (trừ khi `tags="front_page"`), ngày sai định dạng `YYYY-MM-DD`, hoặc HTTP lỗi/timeout. |
| **Tool mới 2:** `github_search` | [`starter_v0/tools/github_search/tool.py`](../../starter_v0/tools/github_search/tool.py)<br>[`starter_v0/tools/github_search/TOOL.md`](../../starter_v0/tools/github_search/TOOL.md) | Tìm kiếm repository trên GitHub REST API (`search/repositories`), tự động ghép qualifier `language:<lang>` và `created:>=<date>`, sắp xếp theo `stars`/`forks`/`updated`/`best_match`, trả về đầy đủ `stars`, `forks`, `language`, `topics`, `updated_at`. | Không crash khi thiếu `GITHUB_TOKEN` (chạy chế độ unauthenticated và chỉ gắn header `Authorization` khi có token); bắt riêng lỗi HTTP `403`/`429` rate limit để trả thông báo hướng dẫn cấu hình `GITHUB_TOKEN`; kẹp `limit` `1..20`. |
| **Unit test tool mới** (10 tests: 5 test/tool) | [`starter_v0/tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py)<br>[`starter_v0/tests/conftest.py`](../../starter_v0/tests/conftest.py)<br>`pytest` output: **`82 passed, 14 skipped, 0 failed`** | Đạt 10/10 unit tests cho 2 tool mới (vượt yêu cầu tối thiểu ≥ 3 test/tool) và giữ toàn bộ contract tests (`test_tool_contract.py`) xanh 100%. Mọi request mạng đều được mock qua fixture `fake_http` offline. | Xóa biến `GITHUB_TOKEN` trong fixture `clear_api_keys` của `conftest.py` để đảm bảo unit test không bị ảnh hưởng bởi biến môi trường trên máy chạy test. |
| **UI & Backend** (`app.py`, `server.py`, `cli_client.py`) | [`starter_v0/app.py`](../../starter_v0/app.py)<br>[`starter_v0/server.py`](../../starter_v0/server.py)<br>[`starter_v0/cli_client.py`](../../starter_v0/cli_client.py) | Giao diện Streamlit (`app.py`) hiển thị minh bạch từng bước gọi tool, tham số truyền vào và JSON kết quả trả về; tích hợp sẵn nút bấm xác nhận **Có / Không** khi agent gọi `clarify(response_type="yes_no")` và danh sách câu hỏi mẫu ở sidebar; tự động ghi file transcript. | Hiển thị rõ cảnh báo/lỗi từ tool (như lỗi thiếu API key hoặc HTTP 403) trên UI thay vì che giấu lỗi; có cơ chế giữ trạng thái hội thoại nhiều lượt (`session_state`) và nút xóa/tạo phiên mới. |

- **Số unit test đã viết cho tool mới:** **10 unit tests** trong [`starter_v0/tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py) (5 tests cho `hackernews_search` và 5 tests cho `github_search`).
- **Ví dụ thực tế về lỗi mà Unit Test bắt được nhưng Eval (`run_eval.py`) không bắt được:**
  - Trong `run_eval.py`, bộ chấm chỉ kiểm tra xem **model** có phát sinh lệnh gọi `github_search(query="RAG", language="Python", created_after="2026-01-01", sort="best_match")` đúng tên tool và đúng args hay không.
  - Tuy nhiên, nếu **code bên trong tool** (`github_search/tool.py`) gửi nguyên tham số `sort="best_match"` lên GitHub REST API (thay vì phải bỏ tham số `sort` khỏi query params vì GitHub API quy định mặc định không truyền `sort` mới là `best_match`), hoặc quên ghép `language:python created:>=2026-01-01` vào tham số `q` của URL request, thì `run_eval.py` vẫn chấm **PASS**, nhưng API GitHub ngoài đời thực sẽ trả về lỗi `422 Unprocessable Entity` hoặc trả về kết quả không được lọc theo ngôn ngữ!
  - Nhờ viết unit test `test_github_search_builds_qualifiers_and_maps_repos` và `test_github_search_handles_bad_model_inputs` kiểm tra trực tiếp `fake_http.calls[0]["params"]`, nhóm đảm bảo cả chuỗi query `q` gửi lên server lẫn xử lý `sort="best_match"` đều chính xác tuyệt đối.

### B5. Bonus Evidence & B7. Small Local Model Challenge

- Nhóm tập trung hoàn thiện chất lượng tối đa cho **100 điểm chính (C1–C8)**: đạt `1.00` (20/20) trên bộ `eval_base.json`, xây dựng 2 tool mới hoàn chỉnh kèm 10 unit tests (`82 passed, 0 failed`), 10 cases `eval_group.json` đạt `9/10 PASS` (`100%` tool routing), và xây dựng trọn bộ Streamlit UI + HTTP Backend + CLI Client. Nhóm không đăng ký chấm phần Bonus riêng để đảm bảo tính trung thực của báo cáo theo đúng `RULES.md`.

---

## 5. Khó khăn và cách xử lý

1. **Hiện tượng "Prompt tự mâu thuẫn" làm tụt điểm ở lần thử `v1` đầu tiên (`0.75` → `0.70`):**
   - **Khó khăn:** Khi mới sửa `system_prompt.md` ở [`v1_B_base_gemini_20261110T183140172591.json`](../../starter_v0/runs/v1_B_base_gemini_20261110T183140172591.json), nhóm chỉ sửa cụm *"do not ask them back"* thành *"ask them back"* nhưng vẫn để lại vế sau *"— just make a sensible guess and call a tool right away..."*. Hai mệnh lệnh trái ngược nằm trong cùng một câu khiến model bị nhiễu, làm điểm giảm từ `0.75` xuống `0.70` và phát sinh lỗi gọi `lookup` cho câu toán tích phân (`R08`).
   - **Cách xử lý:** Xóa bỏ hoàn toàn các câu văn xúi đoán mò của starter và viết lại thành các quy tắc tách biệt theo từng tình huống (`Missing Information`, `Confirmation Before Sending`, `Out of Scope`, `Multi-tool`), giúp điểm tăng ngay lên `0.80` → `0.85`.
2. **Model tự động thêm chữ `"news"` vào `lookup.query` và gọi lặp tool 2 lần (`R03`, `R13`, `M02`):**
   - **Khó khăn:** Dù đã chọn đúng tool `lookup`, `topic="news"` và `timeframe="day"`, model `gemini-3.8-flash` có thói quen viết đầy đủ `query="AI news"` hoặc `"artificial intelligence AI news"` và gọi `lookup` 2 lần (1 lần tiếng Anh, 1 lần tiếng Việt), dẫn đến trượt so khớp chính xác `query="AI"` của bộ eval.
   - **Cách xử lý:** Chuyển hướng sửa sang [`starter_v0/artifacts/tools.yaml`](../../starter_v0/artifacts/tools.yaml) ở phiên bản `v3`: ghi trực tiếp vào `description` của tool `lookup` (*"Chỉ gọi ĐÚNG 1 LẦN..."*) và `description` của tham số `query` (*"Từ khóa chủ đề cốt lõi, ngắn gọn đúng như trong câu hỏi... TUYỆT ĐỐI KHÔNG thêm các từ như 'news', 'tin tức', 'hôm nay'..."*). Kết quả: toàn bộ `R03`, `R13`, `M02` đều PASS, đưa điểm lên `1.00` ([`v3_B_base_gemini_20261110T192529403171.json`](../../starter_v0/runs/v3_B_base_gemini_20261110T192529403171.json)).
3. **Lỗi từ các API bên thứ ba trong quá trình chạy thực tế:**
   - **Hiện tượng & Bằng chứng:**
     - API Twitter (`twitter-api45.p.rapidapi.com`) trả về lỗi HTTP `403` (*"You are not subscribed to this API"*) hoặc `429` khi gọi thật trong các case `timeline` / `social_search` (ghi nhận trong `tool_results` của [`v3_B_base_gemini_20261110T192529403171.json`](../../starter_v0/runs/v3_B_base_gemini_20261110T192529403171.json) và [`v3_B_group_openrouter_20261111T112050364893.json`](../../starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json)).
     - API arXiv đôi lúc bị `ReadTimeout` (`G09_switch_to_papers_sorted`).
   - **Cách xử lý:** Các tool đều bắt lỗi HTTP/timeout và trả về dict lỗi có cấu trúc nên không làm gián đoạn vòng lặp eval (`provider_error_cases` luôn bằng `0`). Trong unit test (`pytest`), toàn bộ HTTP được mock qua `fake_http` nên kiểm tra logic code độc lập 100% với trạng thái mạng/quota bên ngoài.

---

## 6. Tổng hợp đóng góp

Chi tiết đóng góp và bằng chứng của từng thành viên được khai báo đầy đủ trong [TEAM.md](../../TEAM.md) và 4 file báo cáo cá nhân:

| Thành viên | MSSV | Vai trò | Báo cáo cá nhân | Tóm tắt đóng góp chính |
|---|---|---|---|---|
| **Nguyễn Thành Tâm** | `2A202603933` | Prompt Engineer | [`2A202603933_NguyenThanhTam.md`](2A202603933_NguyenThanhTam.md) | Chạy baseline `v0` (`0.75`), phân tích lỗi và thực hiện vòng lặp tối ưu `v1` → `v2` → `v3` trên `system_prompt.md` & `tools.yaml` đạt `1.00` (20/20 PASS) trên bộ `base`. |
| **Trịnh Gia Huy** | `2A202603924` | AI Engineer | [`2A202603924_TrinhGiaHuy.md`](2A202603924_TrinhGiaHuy.md) | Kiểm tra API thật, phát triển 2 tool mới (`hackernews_search`, `github_search`) + 10 unit tests, xây dựng `server.py`, `cli_client.py` và giao diện Streamlit `app.py`. |
| **Lê Tuấn Đạt** | `2A202603949` | Backend (BE) | [`2A202603949_Lê Tuấn Đạt.md`](2A202603949_Lê%20Tuấn%20Đạt.md) | Tích hợp 2 tool CP3 vào nhánh `main`, đồng bộ `TOOL_FUNCTIONS` / `tools.yaml` / `TOOL.md`, cập nhật `conftest.py` và kiểm chứng toàn bộ `pytest` (`82 passed, 0 failed`). |
| **Nguyễn Huy Tấn** | `2A202603925` | Tester | [`2A202603925_NguyenHuyTan.md`](2A202603925_NguyenHuyTan.md) | Thiết kế 10 cases trong `eval_group.json` (5 single-turn + 5 multi-turn), chạy đánh giá `--suite group` đạt `9/10 PASS` (`0.90`) và phân tích chi tiết trong `eval_group.md`. |

---

## 7. Hạn chế và hướng cải thiện — B6. Reflection

1. **Fix nào thuộc `system_prompt.md`?**
   - Các quy tắc điều phối **hành vi tổng quát và ranh giới ra quyết định của Agent** thuộc về `system_prompt.md`:
     - Khi nào không được đoán mò mà phải hỏi lại người dùng (`clarify` với `response_type="text"` cho `R10`, `R11`, `G08`).
     - Ranh giới an toàn trước khi thực hiện hành động có tác động ra bên ngoài (`Confirmation Before Sending`: gọi `clarify` với `response_type="yes_no"` trước khi `send` cho `R12`, `G04`, `G06`, `G07`).
     - Xác định phạm vi hỗ trợ của agent để từ chối gọi tool trước các câu hỏi toán học, viết code hay đặt vé (`R08`, `R14`, `G05`).
     - Khả năng phối hợp nhiều tool song song (`R13`) và nguyên tắc kế thừa/đính chính thông tin qua nhiều lượt hội thoại (`M01`–`M06`).

2. **Fix nào thuộc `tools.yaml`?**
   - Các quy tắc về **phân biệt chức năng giữa các công cụ gần giống nhau (WHEN / WHEN NOT to use)** và **quy ước định dạng của từng tham số (Argument Conventions)** thuộc về `tools.yaml`:
     - Quy định `lookup.query` chỉ nhận từ khóa chủ đề gốc ngắn gọn (`"AI"`, `"robotics"`), không kèm từ `"news"` / `"tin tức"` và chỉ gọi 1 lần (`R03`, `R13`, `M02`).
     - Quy định `timeline.screenname` không có ký tự `@` ở đầu (`G02`), `lookup.timeframe` ánh xạ `"hôm nay" → "day"`, `"tuần này" → "week"`, `"tháng này" → "month"` (`R06`, `G03`), và ranh giới giữa `hackernews_search`, `github_search`, `lookup`, `social_search`.

3. **Failure nào cần review thủ công thay vì chấm tự động?**
   - **Các case `no_tool: true` (`R08`, `R09`, `R14`, `G05`, `G07`):** Bộ chấm tự động `run_eval.py` chỉ kiểm tra việc model không gọi tool (`actual_tool_calls == []`). Để biết model từ chối câu ngoài phạm vi có lịch sự không (`R08`, `G05`), trả lời câu hỏi giới thiệu bản thân có đúng thực tế các tool đang có không (`R09`), hay xác nhận hủy gửi bài có tự nhiên không (`G07`), bắt buộc phải đọc trường `actual_text` / transcript thủ công.
   - **Chất lượng câu hỏi trong `clarify` (`R10`, `R11`, `R12`, `G04`, `G08`):** Máy chấm chỉ kiểm tra `name="clarify"` và `response_type="text"|"yes_no"`, nhưng việc câu hỏi `question` gửi cho người dùng có rõ ràng, đúng trọng tâm thông tin còn thiếu hay không cần review thủ công.
   - **Chất lượng tổng hợp câu trả lời sau khi gọi tool:** Như trong Live Chat (`B4`), việc model có trích dẫn đúng link từ `tool_results` hay tự bịa thêm thông tin ngoài dữ liệu tool trả về cần được kiểm tra trên transcript.

4. **Nếu có thêm một vòng (`v4`), nhóm sẽ thử giả thuyết nào?**
   - Từ lỗi duy nhất ở bộ eval nhóm (`G10_switch_to_hackernews` trong [`v3_B_group_openrouter_20261111T112050364893.json`](../../starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json): khi người dùng yêu cầu *"Giữ chủ đề Gemini, lấy 3 bài mới nhất"* trên Hacker News, model gọi `hackernews_search(query="Gemini", limit=3)` nhưng bỏ sót `sort="date"`), nhóm sẽ đặt **Giả thuyết `v4`**:
     > *"Nếu làm nổi bật quy ước ánh xạ từ khóa thời gian ('mới nhất / gần đây / latest' → bắt buộc truyền `sort='date'` cho `hackernews_search` và `sort_by='submittedDate'` cho `papers`) ở đầu mô tả tham số `sort` trong `tools.yaml` và trong bảng quy ước tham số của `system_prompt.md`, thì `G10_switch_to_hackernews` sẽ PASS và đưa điểm bộ `group` từ `0.90` lên `1.00`."*

---

## 8. Tài liệu tham khảo

- Hướng dẫn bài Lab & Rubric: [README.md](../../README.md), [RUBRIC.md](../../RUBRIC.md), [CHECKPOINTS.md](../../CHECKPOINTS.md), [RULES.md](../../RULES.md).
- Tài liệu cấu hình API & Contract của Tool: [docs/TOOL-SETUP.md](../../docs/TOOL-SETUP.md), [starter_v0/tools/README.md](../../starter_v0/tools/README.md).
- API Documentation cho 2 tool mới:
  - Hacker News Algolia Search API: https://hn.algolia.com/api
  - GitHub REST API — Search Repositories: https://docs.github.com/en/rest/search/search#search-repositories
