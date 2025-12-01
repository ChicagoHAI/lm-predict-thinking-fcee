# Research Plan: Can LMs Predict Their Own Response Length?

## 1. Research Question
Can Large Language Models (LLMs) accurately predict the length of their own responses (token count) before generating them?

## 2. Background and Motivation
Users often experience uncertainty regarding the latency of LLM responses. Knowing the expected response length ("thinking time" or "generation time") beforehand can improve user experience (e.g., by showing a progress bar or "estimated time") and system scheduling (as proposed in ELIS). While external models (BERT) have been used for this, self-prediction offers a simpler, architecture-agnostic approach.

## 3. Hypothesis Decomposition
*   **H1 (Quantitative)**: LLMs can predict the exact number of tokens they will generate with lower Mean Absolute Error (MAE) than a static baseline (dataset mean).
*   **H2 (Qualitative)**: LLMs can classify their expected response length into bins (Short, Medium, Long) with accuracy significantly better than random chance.
*   **H3 (Calibration)**: LLMs are calibrated estimators of their own complexity (i.e., they know when a task requires a long answer).

## 4. Methodology

### Approach
We will use a "Perception in Advance" (PiA) prompting strategy. We will ask the model to predict the length *before* generating the response. To ensure the prediction doesn't condition the response length artificially (self-fulfilling prophecy), we will ideally use two separate contexts or a strict "Predict then Ignore" format, but the most realistic setting is a single pass where the model plans its length. However, to avoid the model shortening its answer just to match a prediction, we will try a **Two-Stage Approach**:
1.  **Stage 1 (Prediction)**: Prompt model with instruction. Ask "Estimate the number of tokens you would need to answer this."
2.  **Stage 2 (Generation)**: Prompt model with instruction. Ask "Answer this." (New context).
3.  **Correlation**: Compare Stage 1 prediction with Stage 2 actual length.

### Dataset
*   **Source**: `databricks-dolly-15k` (subset of 100 samples for experiment efficiency).
*   **Preprocessing**: Filter for "open_qa" or "general_qa" categories to ensure variability.

### Models
*   **Target Model**: `gpt-4o-mini` (via OpenRouter/OpenAI API). It is a modern, capable model representing current "fast" LLMs.
*   **Baseline**: `mean_baseline` (Average length of responses in the dataset).

### Evaluation Metrics
1.  **MAE (Mean Absolute Error)**: $|Predicted - Actual|$.
2.  **Pearson Correlation ($r$)**: Correlation between predicted and actual lengths.
3.  **Bin Accuracy**: Accuracy of classifying into Short (<50), Medium (50-200), Long (>200).

## 5. Experimental Steps
1.  **Setup**: Install dependencies (`openai`, `datasets`, `pandas`, `scipy`).
2.  **Data Loading**: Load `dolly_15k` from local JSON.
3.  **Inference**:
    *   Loop through 100 samples.
    *   Call API for Prediction (Temperature=0 to minimize variance).
    *   Call API for Generation (Temperature=0 to minimize variance).
    *   Record results.
4.  **Analysis**: Compute metrics and visualize.

## 6. Timeline (Single Session)
*   **Phase 2 (Setup)**: 10 mins.
*   **Phase 3 (Impl)**: 30 mins.
*   **Phase 4 (Exp)**: 30 mins (API calls).
*   **Phase 5 (Analysis)**: 20 mins.
*   **Phase 6 (Report)**: 20 mins.

## 7. Potential Challenges
*   **Hallucination**: Model outputs random numbers.
*   **Format adherence**: Model adds text around the number. (Mitigation: Regex parsing).
*   **Stochasticity**: Response length varies (addressed by Castillo paper), so perfect prediction is impossible. We aim for *better than baseline*.

## 8. Success Criteria
*   Positive correlation ($r > 0.3$) between predicted and actual length.
*   MAE lower than the standard deviation of the dataset lengths.
