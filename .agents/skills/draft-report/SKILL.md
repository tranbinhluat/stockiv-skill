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

Write in **Vietnamese** as a native equity research analyst would write — not as a translation of English text.

**Guiding principles:**
- Choose terms based on how Vietnamese investment professionals use them in practice. If a term has an accepted Vietnamese form (e.g., "biên lợi nhuận gộp" for gross margin), use it. If a term is universally kept in English in Vietnamese finance (e.g., ROE, P/E, FCF), keep it as-is.
- Use hedged but confident analyst language: "chúng tôi đánh giá rằng", "phản ánh xu hướng", "cho thấy tín hiệu tích cực". Avoid mechanical phrase-by-phrase translation.
- Adapt idioms and metaphors contextually — the sentence should sound natural to a Vietnamese reader, not like translated text.
- Preserve all risk language with full force — do not soften or hedge warnings that are explicit in the source analysis.
- Keep all numbers, ratios, and units exactly as-is: VND, %, x (multiples), dates.

**Decision outputs are fixed Vietnamese uppercase (non-negotiable):**
- BUY NOW → **MUA NGAY**
- WAIT → **CHỜ**
- AVOID → **TRÁNH**

## PDF Export

After writing the markdown to `reports/ticker/{TICKER}_GCCP_report.md`, run:

```
uv run stockiv-report --ticker {TICKER} --format pdf
```

This generates `reports/ticker/{TICKER}_GCCP_report.pdf` with:
- A4 portrait for the main report
- A3 landscape appendix with the full `financial_summary.md` data tables

## Output Files

- `reports/ticker/{TICKER}_GCCP_report.md`
- `reports/ticker/{TICKER}_GCCP_report.pdf`

## Output to User

```
✅ Report drafted and exported:
- reports/ticker/{TICKER}_GCCP_report.md
- reports/ticker/{TICKER}_GCCP_report.pdf

Verdict: {BUY NOW / WAIT / AVOID}
Target Buy Price: {value} VND | Current Price: {value} VND

Ready to publish? Run: /publish --file reports/ticker/{TICKER}_GCCP_report.md --channel ticker
```
