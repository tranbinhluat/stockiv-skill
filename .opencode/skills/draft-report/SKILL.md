---
name: draft-report
description: Compile a complete GCCP investment report in Vietnamese from existing analysis files and export to PDF. Use this skill when the user types /report [TICKER], asks to generate or export a report, or wants to convert completed analysis into a formatted document. Requires fundamentals + valuation + sentiment files to already exist. Do NOT use if analysis hasn't been run yet — use the deepdive skill for that.
---

# draft-report

Compiles all analysis outputs into a structured GCCP investment report in Vietnamese, then exports to PDF.

## Depends On

All three analysis outputs must exist:
- `data/processed/synthesizer/{TICKER}/{TICKER}_fundamentals.md`
- `data/processed/synthesizer/{TICKER}/{TICKER}_valuation.md`
- `data/processed/sentiment/ticker/{TICKER}/{YEAR}_W{WW}_sentiment.md`
- Gatekeeper must have returned **APPROVED** (never draft report without gatekeeper approval)

## Report Structure (GCCP Format)

### 1. Hook Line
One italic sentence capturing the investment thesis:
```
*{TICKER} là một công ty {quality} trong ngành {industry}, hiện đang giao dịch ở mức {cheap/fair/expensive} so với giá trị nội tại ước tính.*
```

### 2. Tóm tắt Thị trường & Tâm lý Nhà đầu tư
- Macro regime summary (from sentiment file)
- 2–3 specific ticker news items with **inline citations** (exact URLs from sentiment file)
- Market phase: Crisis/Fair/Bubble based on VNINDEX P/E

### 3. Phân tích Định tính (GCCP Phần II)
From `{TICKER}_fundamentals.md`:
- Ngành và Phân loại Lynch
- Mô hình kinh doanh (Input → Engine → Output)
- Quản trị & Ban lãnh đạo
- Thuận lợi / Rủi ro ngành
- Tín hiệu Vô hiệu hoá Luận điểm

### 4. Phân tích Định lượng (GCCP Phần III)
From `{TICKER}_fundamentals.md`:
- Cấu trúc vốn
- Sinh lời: ROE, ROA (5Y trend table)
- Dòng tiền: OCF, FCF
- Đánh giá Pháp y (Forensic)

Include any charts saved to `data/processed/synthesizer/{TICKER}/charts/` as embedded images.

### 5. Định giá (GCCP Phần IV + V)
From `{TICKER}_valuation.md`:
- Giai đoạn Thị trường (VNINDEX P/E verbatim)
- Graham 9-Point Checklist
- Phương pháp Định giá + Bảng Tính Giá Mục tiêu
- **Khuyến nghị: MUA NGAY / CHỜ / TRÁNH** (bold, prominent)

## Language Style

Write in **Vietnamese** as a native equity research analyst would write — not as a translation of English text. The audience includes non-professional investors who do not have a finance degree: write clearly, keep sentences short, and add a brief plain-Vietnamese inline explanation when you use a complex term for the first time.

**Core principle — PHÓNG TÁC (meaning-based adaptation):** Capture the underlying financial meaning and rewrite it naturally. Never produce word-for-word translations that sound mechanical (e.g., "tăng trưởng ấm áp" for "warm growth" is wrong).

**Specific term anchors (use these, do not improvise):**

| English | Vietnamese |
|---|---|
| Goldilocks Growth / Economy | "Tăng trưởng cân bằng" or "Nền kinh tế lý tưởng (Goldilocks)" |
| Disrupt / Disruption (business) | "Đột phá", "Định hình lại", or "Thay đổi cấu trúc" |
| Disconnect / Painful disconnect | "Sự phân kỳ" / "Sự phân kỳ rủi ro cao" |
| Consensus Fallacy | "Góc nhìn trái chiều về sự đồng thuận" |
| What makes it worse / better | "Rủi ro suy yếu" / "Động lực thúc đẩy" |
| Bull Case / Bear Case / Base Case | "Kịch bản Tích cực / Tiêu cực / Cơ sở" |
| Overweight / Underweight | "Khuyến nghị Tăng tỷ trọng / Giảm tỷ trọng" |
| Hawkish / Dovish | "Thắt chặt (Hawkish) / Nới lỏng (Dovish)" |
| Headwinds / Tailwinds | "Rào cản / Động lực hỗ trợ" |
| BUY NOW / WAIT / AVOID | **MUA NGAY / CHỜ / TRÁNH** (uppercase, non-negotiable) |

**English retention:** Keep globally recognized terms in English (or add Vietnamese in parentheses): AI, FDI, IT Outsourcing, Fed, FTSE Russell, MSCI, ROE, P/E, FCF.

**Preserve exactly as-is:** All numbers, ratios, VND amounts, dates, percentages, and every URL / inline citation `[[n]](URL)` character-for-character.

**Risk language:** Preserve warnings at full force — do not soften or hedge risks that are explicit in the analysis.

## PDF Export

After writing the markdown to `data/report/{TICKER}/{TICKER}_GCCP_report.md`, run:

```
uv run stockiv-report --ticker {TICKER} --format pdf
```

This generates `data/report/{TICKER}/{TICKER}_GCCP_report.pdf` with:
- A4 portrait for the main report
- A3 landscape appendix with the full `financial_summary.md` data tables

## Output Files

- `data/report/{TICKER}/{TICKER}_GCCP_report.md`
- `data/report/{TICKER}/{TICKER}_GCCP_report.pdf`

## Output to User

```
✅ Report drafted and exported:
- data/report/{TICKER}/{TICKER}_GCCP_report.md
- data/report/{TICKER}/{TICKER}_GCCP_report.pdf

Verdict: {BUY NOW / WAIT / AVOID}
Target Buy Price: {value} VND | Current Price: {value} VND

Ready to publish? Run: /publish --file data/report/{TICKER}/{TICKER}_GCCP_report.md --channel ticker
```
