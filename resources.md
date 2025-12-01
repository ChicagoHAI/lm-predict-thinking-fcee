# Resources Catalog

## Summary
This document catalogs resources for researching "Can LMs predict their own thinking tokens?".

### Papers
| Title | ID | Year | File | Key Info |
|-------|----|------|------|----------|
| CASTILLO: Characterizing Response Length... | 2505.16881 | 2025 | `papers/2505.16881v1_...pdf` | Variability analysis |
| ELIS: Efficient LLM Iterative Scheduling... | 2505.09142 | 2025 | `papers/2505.09142v1_...pdf` | Predictor implementation |

### Datasets
| Name | Source | Size | Task | Location |
|------|--------|------|------|----------|
| Databricks Dolly 15k | HuggingFace | 15k | Instruction Tuning | `datasets/dolly_15k/` |

### Code Repositories
| Name | Purpose | Location |
|------|---------|----------|
| CASTILLO | Analysis of length distributions | `code/castillo/` |

### Recommendations for Experiment Design

1.  **Primary Dataset**: **Databricks Dolly 15k**. It is clean, open-license (CC-BY-SA), and manageable in size.
2.  **Baseline Method**: **DistilBERT Regressor**. Train a small encoder (DistilBERT) to predict log(length) from instruction.
3.  **Experimental Method (Hypothesis Test)**: 
    - **Zero-shot Self-Prediction**: Prompt the target LLM (e.g., GPT-2, TinyLlama, or larger) with "How many words will your response be?" followed by the actual prompt. Compare predicted vs actual.
    - **Few-shot Self-Prediction**: Provide examples.
    - **Probing**: If possible, train a probe on the last layer of the LLM to predict length (requires access to activations).
4.  **Evaluation**: Compare Self-Prediction accuracy vs. DistilBERT Regressor accuracy.

