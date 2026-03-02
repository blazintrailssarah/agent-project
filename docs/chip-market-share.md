# Chip Company Market Share Example

This document contains a complex Mermaid example showing the relative market share of major semiconductor companies. It is intended as a teaching example for the repository's Mermaid style conventions.

```mermaid
pie
    accTitle: Semiconductor vendor market share breakdown
    accDescr: Pie chart displaying approximate global market share percentages for NVIDIA, Intel, AMD, Qualcomm, Samsung, TSMC, and others

    title 📊 Global Chip Vendor Market Share (approx.)
    "🟢 NVIDIA" : 25
    "🔵 Intel" : 15
    "🟠 AMD" : 10
    "⚪ Qualcomm" : 8
    "🟣 Samsung" : 12
    "🔶 TSMC" : 20
    "📦 Other" : 10
```

> 🔧 *Tip:* values in a pie chart do not need to sum to 100; they are treated proportionally.

This example uses an emoji prefix, includes `accTitle`/`accDescr` for accessibility, and orders slices roughly largest to smallest.
