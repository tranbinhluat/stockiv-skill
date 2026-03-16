# VN-Index Market Context Protocol

1. Read the current `VN-Index P/E`.
2. Match it against the table below to determine the `Market Phase`.
3. Apply the `Required Margin of Safety (MoS)` to all valuations before issuing an [APPROVED] decision.

| VN-Index P/E | Market Phase | Action Rule | Required Margin of Safety (MoS) | Qualitative Sign (Lynch's Cocktail Party) |
|--------------|--------------|-------------|---------------------------------|-------------------------------------------|
| **< 11x** | **Crisis (Khủng hoảng)** | Aggressive Buying. Focus on surviving companies. | **15%** (Lower MoS acceptable due to systemic undervaluation) | **Phase 1:** Market is down, nobody talks about stocks. Dentists/neighbors change the subject. |
| **11x - 15x** | **Fair Value (Định giá hợp lý)** | Normal Buying. Focus on stock-picking. | **20%** (Standard MoS) | **Phase 2:** Market up 15%. People linger slightly before changing the subject. Risk appears. |
| **15x - 20x** | **Expensive (Đắt đỏ)** | Selective Buying. Avoid cyclical peaks. | **30%** (Higher MoS required) | **Phase 3:** Market up 30%. People ignore the dentist and surround the fund manager for stock tips. |
| **> 20x** | **Bubble (Bong bóng)** | DO NOT BUY. Hold cash or sell overvalued assets. | **50%** (Extreme MoS required) | **Phase 4:** Peak. People surround the fund manager to *GIVE* the manager stock tips. Everyone is buying. |

**Code Representation:**
```python
current_pe = 14.2  # From Section 1
if current_pe < 11.0:
    phase = "Crisis"
    required_mos = 0.15
elif 11.0 <= current_pe <= 15.0:
    phase = "Fair Value"
    required_mos = 0.20
elif 15.0 < current_pe <= 20.0:
    phase = "Expensive"
    required_mos = 0.30
else:
    phase = "Bubble"
    required_mos = 0.50
    # Add anomaly flag for extreme risk
```

---

## 3. Margin of Safety (MoS) Adjustments

The baseline MoS determined by the Market Phase (above) must be adjusted for **Business Risk**.

**Agent Logic:** Add the following penalties to the `Required MoS` based on qualitative findings:

| Risk Factor | MoS Penalty Add-On | Reason |
|-------------|--------------------|--------|
| **High Indebtedness** (D/E > 2) | +10% | Bankruptcy risk in high interest rate environments. |
| **Cyclical Peak** (E.g. High Steel Prices)| +15% | Earnings are exaggerated; P/E is artificially low. |
| **Weak Governance / Restatements** | +30% | Financials may not reflect reality. (Director should likely REJECT) |
| **Emerging Growth / No Free Cash Flow** | +20% | High uncertainty of future execution. |

*Example: If Market Phase is 'Fair Value' (20% MoS) but the company is highly indebted (+10%), the final Required MoS is 30%.*
