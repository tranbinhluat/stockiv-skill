"""
Test Director Crew with Dummy Analysis

Validates the Director's decision-making with different analysis scenarios.
"""

from stockiv.crews import DirectorCrew


# Test Case 1: Good Analysis (should APPROVE)
GOOD_ANALYSIS = """
Stock Analysis Report: VCB (Vietcombank)

**Investment Style:** Graham

**Financial Statements Provided:**
- Income Statement: 2020-2024 (5 years)
- Balance Sheet: 2020-2024 (5 years)
- Cash Flow Statement: 2020-2024 (5 years)
- Notes to Financial Statements: Reviewed

**Graham Criteria Evaluation:**

1. Earnings Growth (9/9 criteria evaluated):
   - Positive earnings for past 10 years: ✅ YES
   - EPS growth CAGR: 12.3% (Excellent, >10%)
   - Earnings consistency: No loss years in past decade

2. Financial Strength:
   - Current Ratio: 1.8 (Good, >1.5)
   - Debt/Equity: 0.3 (Excellent, <0.5)
   - Interest Coverage: 8.5x (Excellent, >5x)

3. Valuation:
   - P/E Ratio: 8.2x (Good, <10x)
   - P/B Ratio: 1.2x (Fair, <1.5x)
   - Price relative to NCAV: Trading at 1.8x NCAV

4. Dividend Record:
   - Consistent dividends: 15+ years
   - Payout Ratio: 45% (Sustainable)
   - Dividend Yield: 5.8% (Good)

5. Cash Flow:
   - Operating Cash Flow positive: All 5 years
   - Free Cash Flow positive: All 5 years
   - OCF/Net Income: 1.05 (High quality)

**Peer Comparison (Large Cap Banking):**
- VCB P/E: 8.2x vs Sector Median: 9.5x
- VCB P/B: 1.2x vs Sector Median: 1.4x
- VCB ROE: 18.5% vs Sector Median: 14.2%

**Tier:** Large Cap (>20,000B VND market cap)

**Industry Context:**
- Banking sector benefits from economic recovery
- VCB is top-tier bank with strong NIM (2.8%)
- NPL ratio: 0.9% (Excellent, sector avg: 1.5%)
- CASA ratio: 35% (Excellent)

**Risks Identified:**
- Interest rate pressure on NIM
- Economic slowdown could increase NPLs
- Competition from digital banks

**Red Flags:** None detected

**Downside Scenarios:**
- Bear case: P/E 6x, NPL 2% → Target price 65,000 VND
- Base case: P/E 8x, NPL 1% → Target price 85,000 VND
- Bull case: P/E 10x, NPL 0.8% → Target price 105,000 VND

**Evidence:**
- Annual Reports 2020-2024: Attached as PDFs
- Page references: All key numbers sourced
- Excel model: Included with formulas
- Primary sources: Annual reports, audited financial statements

**Final Assessment:**
VCGP Score: 82/100 (Excellent)
Qualifying Score: 78/100 (Good, above MQS of 70)

Recommendation: BUY - Strong defensive stock with consistent earnings
"""

# Test Case 2: Incomplete Analysis (should REJECT)
BAD_ANALYSIS = """
Stock Analysis Report: XYZ (Unknown Company)

**Investment Style:** Graham

**Financial Statements:**
- Only have 2024 data (1 year)
- Balance Sheet not available
- Cash Flow Statement not available

**Graham Criteria:**
- Price looks cheap: P/E 5x
- Should buy!

**No risks mentioned**
**No peer comparison**
**No industry context**
"""

# Test Case 3: Analysis with Anomalies (should detect issues)
ANOMALY_ANALYSIS = """
Stock Analysis Report: ABC (Suspicious Company)

**Investment Style:** Greenblatt

**Financial Statements Provided:**
- Income Statement: 2022-2024
- Balance Sheet: 2022-2024
- Cash Flow Statement: 2022-2024

**Greenblatt Criteria (5/5 evaluated):**
1. ROC (Return on Capital): 25% (Excellent)
2. Earnings Yield: 15% (Excellent)
3. P/E Ratio: 6.7x (Good)
4. P/B Ratio: 0.8x (Good)
5. Market Cap: 3,000B VND (Small Cap)

**Financial Data:**
- Revenue 2024: 1,000B VND
- Revenue 2023: 500B VND (100% growth!)
- Revenue 2022: 480B VND

- Net Income 2024: 150B VND
- Operating Cash Flow 2024: -50B VND (negative?)
- Receivables 2024: 300B VND
- Receivables 2023: 80B VND

**Interesting Notes:**
- Q4 2024 revenue: 600B VND (60% of full year!)
- One customer accounts for 35% of revenue
- Related party transactions: 8% of revenue (loans to directors)
- Auditor changed in 2024

**Peer Comparison:**
Comparing to VCB (Large Cap) - looks cheaper!

**Recommendation:** STRONG BUY
"""


def test_director(name: str, analysis: str, ticker: str = "VCB"):
    """Run a test case through the Director."""
    print(f"\n{'=' * 80}")
    print(f"TEST: {name}")
    print(f"{'=' * 80}\n")

    crew = DirectorCrew()
    result = crew.crew().kickoff(
        inputs={
            "stock_symbols": ticker,
            "analysis": analysis,
        }
    )

    # Get the Pydantic output
    decision = result.pydantic

    # Display the markdown report
    print(decision.to_markdown())
    print(f"\n{'=' * 80}\n")

    return decision


if __name__ == "__main__":
    import sys

    # Run test cases
    test_cases = [
        ("Good Analysis (should APPROVE)", GOOD_ANALYSIS, "VCB"),
        ("Incomplete Analysis (should REJECT)", BAD_ANALYSIS, "XYZ"),
        ("Anomalies Present (should detect)", ANOMALY_ANALYSIS, "ABC"),
    ]

    # Run specific test or all
    if len(sys.argv) > 1:
        idx = int(sys.argv[1]) - 1
        test_cases = [test_cases[idx]]

    for name, analysis, ticker in test_cases:
        try:
            decision = test_director(name, analysis, ticker)
            print(f"✅ Test completed. Decision: {decision.decision}")
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
