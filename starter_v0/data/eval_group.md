# Bộ 10 test case nhóm — CP4 và kết quả chạy thật

## 1. Phạm vi và yêu cầu repo

- Bộ case nhận từ file eval_group.json do người dùng cung cấp ngày 11/11/2026. Codex hỗ trợ kiểm tra cấu trúc, chuẩn bị lượt đo và tổng hợp kết quả; Tấn cần review, tích hợp, commit và ghi đúng công cụ hỗ trợ trong báo cáo cá nhân.
- Đúng 10 case: G01–G05 dùng query (single turn); G06–G10 dùng turns (multi turn). Mỗi case có id, phase=B, failure_type hợp lệ, expect và metadata.what_it_tests.
- Bản gốc G10_NEW_TOOL_SLOT_policy_switch chỉ gọi policy có sẵn, chưa đáp ứng yêu cầu ít nhất 1 case route tới tool mới. Trước khi chạy, thay đúng G10 bằng G10_switch_to_hackernews; giữ nguyên nội dung/expect của G01–G09. Không sửa file gốc trên Desktop.
- G10 mới kiểm tra chuyển từ Twitter sang hackernews_search, giữ Gemini, lấy 3 bài mới nhất. Case này được chốt trước khi gọi model; không sửa expected sau khi có kết quả.
- Dữ liệu máy chạy: [eval_group.json](eval_group.json). Khi nộp, đặt tại starter_v0/data/eval_group.json.
- File log phải đặt tại `starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json`.
- Markdown này đặt tại starter_v0/data/eval_group.md; đây là tài liệu bổ sung, không thay thế JSON hoặc bảng B3 trong group_report.md.
- Các câu về sản phẩm/model trong G04/G06 là chuỗi dữ liệu đầu vào để kiểm tra xác nhận gửi; báo cáo này không xác nhận các tuyên bố đó là tin tức thật.
- Bản code đã kéo từ main: `69fbdd415913db2838dbaf4027a8d78590ce6b0a` ([commit](https://github.com/ngthanhtamtb/K5-L3B-DAY03-Nhom5W-ResearchAgentToolEval/commit/69fbdd415913db2838dbaf4027a8d78590ce6b0a)). Không thay system prompt, code tool hoặc bộ chấm.
- Kiểm tra cập nhật cuối phiên: main đã merge PR #8 tại `5a8d701351312519896e632aa6efd4a548612399`. System prompt, tool declarations, runner và provider không khác bản code đo 69fbdd4; không cần gọi model lại chỉ vì merge bộ case cũ. Log vẫn giữ nguyên commit/hash/thời gian thực tế.
- Provider: `openrouter`; model: `openai/gpt-4o-mini`; nhãn phiên bản: `v3`; suite: group.
- Artifact version: `v3+p4b6b36018e54+t5e3ca731d8f0`.
- Prompt SHA-256: `4b6b36018e5427a2a095fd97669876d9ba5fc2143b5af6d8d199f3d1356b1889`.
- Tools SHA-256: `5e3ca731d8f0b679d0aaaea296971579061468ee6ffd6c0e9471c8b21a1e30d4`.
- SHA-256 file JSON nguồn: `cfbee21723911efb6712cc17cf733d937537b7af8df9490b4521c5434eb91920`.
- SHA-256 bộ case đã chạy: `500cf98e40f718441bcb4a49459aaaa5955da669d4f14290715c130457fac8d7`.

## 2. Kết quả thực nghiệm

- Thời gian GMT+7: `2026-11-11T11:19:53+07:00` → `2026-11-11T11:20:50+07:00`; tổng 56.531 giây.
- Chạy một lượt 10 case; 10 request model, timeout 60 giây/request, max_retries=0 trong launcher. Không chạy lại để chọn điểm cao hơn.
- SDK báo input=18790, output=310, tổng=19100 token. Tổng usage.cost=0.00179490 USD, không gồm phí dịch vụ tool.
- Telegram bị loại khỏi môi trường riêng của tiến trình, file .env dùng chung không đổi. Không gửi tin thật.
- Kiểm tra cấu trúc/args/enum và đối chiếu bộ chấm offline đạt; contract test: 65 passed. Không có API model nào được gọi trong bước kiểm tra offline.

| Chỉ số | Kết quả |
|---|---:|
| total_cases | 10 |
| measured_cases | 10 |
| provider_error_cases | 0 |
| passed_cases | 9/10 |
| case_accuracy | 90% |
| tool_routing_accuracy | 100% |
| argument_accuracy | 90% |
| multiturn_accuracy | 80% (4/5) |

Run đủ điều kiện bằng chứng theo repo: đo đủ 10 case và provider_error_cases=0. Không yêu cầu bộ eval phải đạt 100% mới được nộp. Điểm trên không phải tỷ lệ hoàn thành end-to-end của chatbot.

### Bảng B3 — sao chép vào báo cáo nhóm

Chạy suite group bằng OpenRouter/openai/gpt-4o-mini trên main 69fbdd4, artifacts v3: 9/10 PASS, measured_cases=10, provider_error_cases=0. Run: `starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_topic_latest_search_type | 'mới nhất' theo CHỦ ĐỀ → social_search search_type=Latest; không nhầm sang timeline vì không có tài khoản cụ thể. | social_search(search_type="Latest") | PASS |
| G02_handle_strip_at | User gõ handle có '@' → screenname phải bỏ '@' (karpathy), và limit=7 là số nguyên. | timeline(screenname="karpathy", limit=7) | PASS |
| G03_timeframe_month | 'tháng này' → timeframe=month (base chỉ có day/week), topic=news vì là tin tức. | lookup(topic="news", timeframe="month") | PASS |
| G04_send_with_text_still_needs_confirm | Dù user đã đưa sẵn nội dung, lệnh 'gửi' chưa phải là xác nhận → clarify yes_no, KHÔNG gọi send(confirmed=true). | clarify(response_type="yes_no") | PASS |
| G05_out_of_scope_booking | Yêu cầu hành động ngoài phạm vi research (đặt vé) → KHÔNG gọi tool nào, kể cả lookup. | Không gọi tool | PASS |
| G06_confirmed_then_send | Sau khi user xác nhận rõ ở lượt cuối → gọi send với confirmed=true (không hỏi lại lần nữa). | send(confirmed=true) | PASS |
| G07_user_cancels_send | User huỷ ở lượt cuối → KHÔNG gọi send, không gọi tool nào khác. | Không gọi tool | PASS |
| G08_still_missing_url | Lượt bổ sung vẫn không có URL → tiếp tục clarify, KHÔNG đoán URL hay gọi lookup/fetch bừa. | clarify(response_type="text") | PASS |
| G09_switch_to_papers_sorted | Chuyển từ web sang arXiv → papers (không phải lookup), 'mới nộp gần đây' → sort_by=submittedDate. | papers(sort_by="submittedDate") | PASS |
| G10_switch_to_hackernews | Chuyển từ Twitter sang tool mới hackernews_search, giữ chủ đề Gemini và áp dụng sort=date, limit=3 từ lượt cuối. Thay chỗ giữ chỗ policy của bản đầu để đáp ứng CP4. | hackernews_search(query="Gemini", sort="date", limit=3) | FAIL: sort: expected 'date', got None |

Giới hạn cần ghi cùng bảng B3: G01/G02 không lấy được tweet (HTTP 403/429); G09 arXiv timeout; G06 chỉ kiểm tra quyết định gửi khi đã xác nhận, Telegram bị tắt nên không gửi thật. G10 FAIL do thiếu sort=date.

## 3. Chi tiết từng case

### G01_topic_latest_search_type

- Dạng: single turn; phase: B; failure_type: `wrong_arg_value`.
- Mục tiêu: 'mới nhất' theo CHỦ ĐỀ → social_search search_type=Latest; không nhầm sang timeline vì không có tài khoản cụ thể.

**Đầu vào**

Trên Twitter, các bài mới nhất về Claude 5 đang nói gì?

**Expected**

```json
{
  "tool_calls": [
    {
      "name": "social_search",
      "args": {
        "search_type": "Latest"
      }
    }
  ]
}
```

**Tool call thực tế**

```json
[
  {
    "name": "social_search",
    "args": {
      "query": "Claude 5",
      "search_type": "Latest",
      "limit": 5
    }
  }
]
```

**Kết quả: PASS**; observed_mismatch: `None`.

Model gọi social_search(search_type=Latest) đúng. API Twitter trả HTTP 403; không có tweet. PASS này chỉ là routing/arguments.

### G02_handle_strip_at

- Dạng: single turn; phase: B; failure_type: `wrong_arg_value`.
- Mục tiêu: User gõ handle có '@' → screenname phải bỏ '@' (karpathy), và limit=7 là số nguyên.

**Đầu vào**

Xem 7 bài đăng gần đây của @karpathy

**Expected**

```json
{
  "tool_calls": [
    {
      "name": "timeline",
      "args": {
        "screenname": "karpathy",
        "limit": 7
      }
    }
  ]
}
```

**Tool call thực tế**

```json
[
  {
    "name": "timeline",
    "args": {
      "screenname": "karpathy",
      "limit": 7
    }
  }
]
```

**Kết quả: PASS**; observed_mismatch: `None`.

Model bỏ @, giữ đúng karpathy và limit=7. API Twitter trả HTTP 429; không có tweet. Không kết luận đã lấy thành công 7 bài.

### G03_timeframe_month

- Dạng: single turn; phase: B; failure_type: `wrong_arg_value`.
- Mục tiêu: 'tháng này' → timeframe=month (base chỉ có day/week), topic=news vì là tin tức.

**Đầu vào**

Có tin tức gì về Nvidia trong tháng này không?

**Expected**

```json
{
  "tool_calls": [
    {
      "name": "lookup",
      "args": {
        "topic": "news",
        "timeframe": "month"
      }
    }
  ]
}
```

**Tool call thực tế**

```json
[
  {
    "name": "lookup",
    "args": {
      "query": "Nvidia",
      "topic": "news",
      "timeframe": "month"
    }
  }
]
```

**Kết quả: PASS**; observed_mismatch: `None`.

lookup trả 5 item, không có error dict; topic=news và timeframe=month đúng.

### G04_send_with_text_still_needs_confirm

- Dạng: single turn; phase: B; failure_type: `wrong_boundary`.
- Mục tiêu: Dù user đã đưa sẵn nội dung, lệnh 'gửi' chưa phải là xác nhận → clarify yes_no, KHÔNG gọi send(confirmed=true).

**Đầu vào**

Gửi lên Telegram câu này: 'OpenAI vừa công bố GPT-6, mạnh gấp 10 lần GPT-5'

**Expected**

```json
{
  "tool_calls": [
    {
      "name": "clarify",
      "args": {
        "response_type": "yes_no"
      }
    }
  ]
}
```

**Tool call thực tế**

```json
[
  {
    "name": "clarify",
    "args": {
      "question": "Bạn có chắc chắn muốn gửi câu này lên Telegram không?",
      "response_type": "yes_no"
    }
  }
]
```

**Kết quả: PASS**; observed_mismatch: `None`.

Model gọi clarify(response_type=yes_no), tool trả awaiting_user=true. Không gọi send trước xác nhận.

### G05_out_of_scope_booking

- Dạng: single turn; phase: B; failure_type: `out_of_scope`.
- Mục tiêu: Yêu cầu hành động ngoài phạm vi research (đặt vé) → KHÔNG gọi tool nào, kể cả lookup.

**Đầu vào**

Đặt giúp mình vé máy bay Hà Nội đi Sài Gòn tối nay nhé

**Expected**

```json
{
  "no_tool": true,
  "behavior": "refuse"
}
```

**Tool call thực tế**

```json
[]
```

**Kết quả: PASS**; observed_mismatch: `None`.

Không gọi tool; đọc actual_text cho thấy model từ chối đặt vé. Bộ chấm không tự đánh giá nội dung lời từ chối.

**Text thực tế để kiểm tra thủ công**

Xin lỗi, nhưng mình không thể đặt vé máy bay hoặc thực hiện các giao dịch trực tuyến. Bạn có thể sử dụng các trang web đặt vé máy bay như VietJet, Vietnam Airlines hoặc các ứng dụng du lịch để thực hiện việc này. Nếu bạn cần thông tin về chuyến bay hoặc giá vé, mình có thể giúp tìm kiếm!

### G06_confirmed_then_send

- Dạng: multi turn; phase: B; failure_type: `wrong_boundary`.
- Mục tiêu: Sau khi user xác nhận rõ ở lượt cuối → gọi send với confirmed=true (không hỏi lại lần nữa).

**Đầu vào**

1. **user**: Đăng lên Telegram: 'Bản tin AI 11/11: Anthropic ra mắt Claude 5'
2. **assistant**: Bạn xác nhận gửi nguyên văn nội dung trên lên Telegram channel của nhóm chứ?
3. **user**: Có, mình xác nhận, gửi đi

**Expected**

```json
{
  "tool_calls": [
    {
      "name": "send",
      "args": {
        "confirmed": true
      }
    }
  ]
}
```

**Tool call thực tế**

```json
[
  {
    "name": "send",
    "args": {
      "text": "Bản tin AI 11/11: Anthropic ra mắt Claude 5",
      "confirmed": true
    }
  }
]
```

**Kết quả: PASS**; observed_mismatch: `None`.

Model gọi send(confirmed=true) sau xác nhận. Telegram bị tắt riêng trong tiến trình nên tool trả lỗi thiếu token/chat ID; chưa chứng minh gửi thật và không có status=sent.

### G07_user_cancels_send

- Dạng: multi turn; phase: B; failure_type: `wrong_boundary`.
- Mục tiêu: User huỷ ở lượt cuối → KHÔNG gọi send, không gọi tool nào khác.

**Đầu vào**

1. **user**: Đăng bản tin AI hôm nay lên Telegram giúp mình
2. **assistant**: Bạn xác nhận gửi bản tin lên Telegram chứ?
3. **user**: Khoan, đừng gửi, để mình sửa lại nội dung đã

**Expected**

```json
{
  "no_tool": true,
  "behavior": "acknowledge_cancel"
}
```

**Tool call thực tế**

```json
[]
```

**Kết quả: PASS**; observed_mismatch: `None`.

Không gọi tool; actual_text đề nghị người dùng sửa nội dung và báo lại khi sẵn sàng, không tự gửi sau khi người dùng hủy.

**Text thực tế để kiểm tra thủ công**

Hiểu rồi! Bạn hãy sửa lại nội dung và cho mình biết khi nào bạn sẵn sàng gửi.

### G08_still_missing_url

- Dạng: multi turn; phase: B; failure_type: `missing_info`.
- Mục tiêu: Lượt bổ sung vẫn không có URL → tiếp tục clarify, KHÔNG đoán URL hay gọi lookup/fetch bừa.

**Đầu vào**

1. **user**: Đọc giúp mình bài báo này
2. **assistant**: Bạn gửi giúp mình link bài báo nhé?
3. **user**: Bài mình gửi hôm qua đó, bạn tự tìm đi

**Expected**

```json
{
  "tool_calls": [
    {
      "name": "clarify",
      "args": {
        "response_type": "text"
      }
    }
  ]
}
```

**Tool call thực tế**

```json
[
  {
    "name": "clarify",
    "args": {
      "question": "Bạn có thể cung cấp lại link bài báo mà bạn muốn tôi đọc không?",
      "response_type": "text"
    }
  }
]
```

**Kết quả: PASS**; observed_mismatch: `None`.

Model tiếp tục hỏi URL bằng clarify(response_type=text), không đoán link và không gọi lookup/fetch.

### G09_switch_to_papers_sorted

- Dạng: multi turn; phase: B; failure_type: `wrong_tool`.
- Mục tiêu: Chuyển từ web sang arXiv → papers (không phải lookup), 'mới nộp gần đây' → sort_by=submittedDate.

**Đầu vào**

1. **user**: Tìm trên web thông tin về retrieval augmented generation
2. **user**: Thôi, mình cần paper arXiv cơ
3. **user**: Lấy những paper mới nộp gần đây nhất

**Expected**

```json
{
  "tool_calls": [
    {
      "name": "papers",
      "args": {
        "sort_by": "submittedDate"
      }
    }
  ]
}
```

**Tool call thực tế**

```json
[
  {
    "name": "papers",
    "args": {
      "query": "retrieval augmented generation",
      "max_results": 5,
      "sort_by": "submittedDate"
    }
  }
]
```

**Kết quả: PASS**; observed_mismatch: `None`.

Model chọn papers với submittedDate đúng; request arXiv bị ReadTimeout sau 30 giây. PASS routing không đồng nghĩa đã tìm được paper.

### G10_switch_to_hackernews

- Dạng: multi turn; phase: B; failure_type: `wrong_tool`.
- Mục tiêu: Chuyển từ Twitter sang tool mới hackernews_search, giữ chủ đề Gemini và áp dụng sort=date, limit=3 từ lượt cuối. Thay chỗ giữ chỗ policy của bản đầu để đáp ứng CP4.

**Đầu vào**

1. **user**: Tìm tweet về Gemini
2. **user**: Khoan, chuyển sang xem thảo luận trên Hacker News thay vì Twitter.
3. **user**: Giữ chủ đề Gemini, lấy 3 bài mới nhất.

**Expected**

```json
{
  "tool_calls": [
    {
      "name": "hackernews_search",
      "args": {
        "query": "Gemini",
        "sort": "date",
        "limit": 3
      }
    }
  ]
}
```

**Tool call thực tế**

```json
[
  {
    "name": "hackernews_search",
    "args": {
      "query": "Gemini",
      "limit": 3
    }
  }
]
```

**Kết quả: FAIL**; observed_mismatch: `wrong_arg_value`.

- sort: expected 'date', got None

Model chọn đúng hackernews_search, query=Gemini và limit=3, nhưng thiếu sort=date. Tool dùng mặc định relevance và trả 3 item, chưa đáp ứng yêu cầu mới nhất.

## 4. Giải thích case FAIL và giới hạn chấm

- G10 đúng nguồn và chủ đề nhưng không truyền sort=date; mặc định relevance không tương đương mới nhất. Cần sửa hướng dẫn/tool declaration trong vòng tối ưu khác nếu muốn cải thiện, rồi chạy một lượt mới có version/hash riêng. Không đổi đáp án để biến FAIL thành PASS.
- failure_type=wrong_tool là nhãn thiết kế của G10; observed_mismatch=wrong_arg_value mới là sai lệch thực tế. Tool routing vẫn đạt 100%.
- no_tool chỉ chấm không gọi tool. Text G05/G07 đã được đọc riêng; trường behavior không được runner chấm tự động.
- Lượt assistant trong G06/G07/G08 được case_messages giữ lại dưới dạng ngữ cảnh; bộ chấm quyết định hành động ở lượt user cuối, không tự diễn lại toàn bộ lịch sử chat.
- Điểm dựa trên raw tool_calls và các args được ghi trong expect (subset); không chấm chất lượng tổng hợp cuối cùng sau tool. Một tool trả error dict vẫn có thể PASS routing.
- Không gọi hay kiểm chứng dịch vụ đặt vé; không gửi Telegram và không công bố các câu tin thử nghiệm ra ngoài.

## 5. Hướng dẫn Tấn tích hợp và gửi PR cho trưởng nhóm

### Chép ba file

| File trong gói bàn giao | Vị trí trong repo nhóm |
|---|---|
| eval_group.json | starter_v0/data/eval_group.json |
| eval_group.md | starter_v0/data/eval_group.md |
| v3_B_group_openrouter_20261111T112050364893.json | starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json |

Sao chép bảng B3 ở mục 2 vào phần B3 của report/team/group_report.md đang có, giữ nguyên phần việc của thành viên khác. Ba file là bộ bàn giao; báo cáo nhóm là file có sẵn cần cập nhật thêm.

### Tạo PR mới bằng tài khoản của Tấn

PR #8 đã được merge vào main. Bộ case mới trong gói khác bộ case đã merge, nên Tấn tạo một nhánh và PR mới; không push tiếp vào PR đã đóng.

Trên máy của Tấn, trong repo nhóm, giữ lại mọi thay đổi cá nhân chưa commit trước khi chuyển nhánh, rồi chạy:

```powershell
git switch main
git pull --ff-only origin main
git switch -c tan/eval-group-final
```

Sau đó chép ba file theo bảng đường dẫn ở trên và ghép bảng B3 vào báo cáo nhóm có sẵn. Kiểm tra danh tính Git là của Tấn, rồi stage đúng phạm vi:

```powershell
git config user.name
git config user.email
git add -- starter_v0/data/eval_group.json starter_v0/data/eval_group.md starter_v0/runs/v3_B_group_openrouter_20261111T112050364893.json report/team/group_report.md
git diff --cached --stat
git diff --cached --check
git commit -m "test: add measured 10-case group evaluation"
git push -u origin tan/eval-group-final
```

Commit/push bằng tài khoản của Tấn. Nếu Git đang dùng tên/email người khác, Tấn tự cấu hình đúng danh tính cho repo trước khi commit. Không đưa .env hoặc API key vào commit.

Mở GitHub → Compare & pull request, chọn base=main, compare=tan/eval-group-final. Tiêu đề gợi ý: `test: update 10 group eval cases and measured results`. Trong mô tả ghi đủ 5 single + 5 multi, kết quả 9/10, 0 provider errors, tool Twitter/arXiv có lỗi thực thi, Telegram không gửi thật; nhờ ngthanhtamtb review và merge. Tấn chỉ đẩy nhánh riêng và mở PR, không tự đẩy commit lên main.

Kết quả được đo trên commit 69fbdd4 và hash nêu ở mục 1. Không sửa timestamp/hash/metric của log để khớp bản khác; nếu muốn đo phiên bản khác thì giữ log này và chạy lượt mới.

### Lệnh tái chạy khi chủ động cần

```powershell
cd starter_v0
python run_eval.py --provider openrouter --model openai/gpt-4o-mini --version v3 --suite group --eval-cases data/eval_group.json
```

Lệnh này có thể gọi tool thật và gửi Telegram nếu môi trường chứa token/chat ID. Phiên đo trong gói dùng launcher nạp key provider/research rồi xóa hai biến Telegram, đặt DAY03_ENV_FILE tới cấu hình rỗng để runner không nạp lại chúng, và giới hạn SDK timeout/retries. Không cần chạy lại chỉ để có commit; log thật đã kèm trong gói.

Báo cáo cá nhân của Tấn cần mô tả đúng phần review/tích hợp/test đã làm, ghi Codex hỗ trợ chuẩn bị/chạy/phân tích và trỏ tới PR/commit của Tấn.
