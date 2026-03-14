# Evidence Standards & Audit Protocols

> **🧠 CORE RESOURCE — For Director Crew**
> *Use these standards to evaluate the `evidence_traceable` and `numbers_accurate` fields of your `DirectorDecision` output.*

## 1. Zero Trust Policy

The Director Crew operates on a **ZERO TRUST** baseline.

* The Synthesizer's claims are considered *hypothesis* until proven by *evidence*.
* An analysis that fails to cite Tier 1 or Tier 2 evidence for its quantitative claims **MUST BE REJECTED**.

---

## 2. Evidence Tier System

All data presented must be traced back to its source tier.

| Tier | Source Type | Trust Level | Allowed Usage | Examples / Placeholders |
|------|-------------|-------------|---------------|-------------------------|
| **Tier 1** | **Primary Financial Data** | **Absolute Trust** | The sole basis for quantitative valuation frameworks, scoring, and margin of safety calculations. | Audited Annual Reports (BCTC Kiểm toán), HOSE/HNX official filings, `[Data Source: VNStock API]`. |
| **Tier 2** | **Institutional Analysis** | **Verification Only** | Used to cross-check qualitative themes (industry growth, management reputation). Cannot override Tier 1 quantitative data. | Brokerage Reports (SSI, VNDirect, HSC), Official SEC/SSC Announcements, Respected Financial News (CafeF verified, VnEconomy). |
| **Tier 3** | **Secondary / Opinion** | **AUTO-REJECT** | Must NEVER be used as the basis for an investment thesis or anomaly clearance. | Facebook Groups, Zalo chat rumors, unverified blogs, anonymous analyst forecasts. |

---

## 3. Data Triangulation Rules (Director Instructions)

Before marking `numbers_accurate=True` and `evidence_traceable=True`, the Director must execute these semantic checks on the Synthesizer's output:

1. **The Time-Series Rule:** Is the valuation based on a single quarter (TTM) or a verified 5-10 year history? Graham criteria requires 10 years. If analyzing a single year, flag it under `failures`.
2. **The Source Linking Rule:** Does every specific number (e.g., "ROE is 22%") explicitly attribute where it came from (e.g. "According to the 2025 Audited Annual Report")? If absent, flag under `failures`.
3. **The Contradiction Rule:** If a broker report (Tier 2) predicts 30% revenue growth, but the `[Data Source: VNStock API]` (Tier 1) shows 3 consecutive quarters of revenue decline, the Director **MUST ALARM** and reject the optimistic thesis. Tier 1 overrides Tier 2.

**Action Matrix:**

```python
# Pseudo-code for Director evidence validation

def validate_evidence(thesis):
    if "Facebook" in thesis.sources or "Rumor" in thesis.sources:
        return "REJECTED", "Tier 3 sources detected. Auto-reject."

    if not has_tier_1_sources(thesis.metrics):
        return "MORE_INFO_NEEDED", "Quantitative claims lack Tier 1 sourcing (e.g., Audited BCTC, VNStock API)."

    if tier_1_data_contradicts_tier_2_claims(thesis):
        return "REJECTED", "Anomaly: Broker optimism contradicts primary financial data trend."

    return "APPROVED", "Evidence meets standards."
```
