# Knowledge checks

These mirror the interactive checks embedded in the Streamlit app
(`revenue_prediction.education`). Answers are at the bottom.

1. **What is the prediction grain of the default demonstration?**
   - a) Patient × encounter × diagnosis
   - b) Facility × accounting month × snapshot date
   - c) Facility × calendar day
   - d) Payer × service line × year

2. **Why is random row splitting avoided for evaluation?**
   - a) It is slower than temporal splitting
   - b) It leaks future months into training and inflates metrics
   - c) scikit-learn does not support it
   - d) It requires a GPU

3. **Which best describes the target, `actual_month_end_net_revenue`?**
   - a) Sum of gross charges to date
   - b) Known in real time at every snapshot
   - c) Only known after accounting close
   - d) A patient-level billing amount

4. **How does the accelerator access OneLake?**
   - a) A proprietary Fabric-only protocol
   - b) The ADLS Gen2 endpoint with `DefaultAzureCredential`
   - c) By copying data to a local SQL Server
   - d) Through anonymous public URLs

5. **When is a challenger model promotable over the champion?**
   - a) Whenever it has any lower error at all
   - b) Only when it beats the incumbent by the configured margin
   - c) Never — the champion is fixed
   - d) When it uses a deep neural network

6. **Billing amount vs net revenue — which reduces gross charges to net?**
   - a) Adding bad debt back in
   - b) Contractual adjustments, denials, bad debt, charity care
   - c) Multiplying by the case-mix index
   - d) Nothing; they are the same

7. **Which is NOT an appropriate use of this accelerator?**
   - a) Early finance planning input
   - b) Operational decision support
   - c) Autonomous financial decisions without human review
   - d) A teaching example on synthetic data

## Answer key

1: b  2: b  3: c  4: b  5: b  6: b  7: c
