# Module Specifications

This document sets out the starting mathematical and technical design of the four IFIS modules. Think of these as well-reasoned first drafts. They will be revised once we've picked algorithms and seen what the experiments tell us.

## 1. Module 1: Cohort Synthesizer

### What it does
It finds groups of similar observations using features alone, so we can check whether the model behaves differently for groups that nobody labelled in advance.

### Input
A feature vector for each incoming observation:

\[
x_i = [x_{i1}, x_{i2}, \ldots, x_{ip}]
\]

By default, protected attributes (such as race and sex) are **left out** of this vector, so cohorts come from other features. A variant that includes them can be run as a comparison, but it must be clearly labelled.

### Preparing the data
Features usually need preparing before clustering: scaling numeric features, and encoding categorical ones (the Adult dataset has many). The choice of encoding or distance measure can change the cohorts a lot, so it is recorded as part of every experiment.

### Operation
Apply a clustering or subgroup-discovery method to the prepared features. As one example, K-Means minimizes the within-cluster sum of squared distances:

\[
J = \sum_{i=1}^{n} \|x_i - \mu_{c_i}\|^2
\]

where:

- \(x_i\) is an observation.
- \(c_i\) is the cluster it is assigned to.
- \(\mu_{c_i}\) is the centroid of that cluster.

K-Means is only one candidate. The experiments compare it with DBSCAN and HDBSCAN rather than assuming it is best.

### Output
A cohort identifier and an assignment status. What "status" means depends on the method:

| Method | What it can report |
|---|---|
| K-Means | Cluster ID and distance to centroid. This is a proximity measure, not a probability. |
| DBSCAN | Cluster ID, or *unassigned* for noise points |
| HDBSCAN | Cluster ID and a membership strength, or *unassigned* for noise points |

Unassigned observations stay unassigned. We don't force them into a cohort.

### Research questions

- Can useful subgroups be found without directly using protected attributes?
- How stable are the cohorts across time windows? (For example, measured by how well cohort labels match between consecutive windows.)
- Do the cohorts reveal performance gaps that aggregate monitoring misses?

## 2. Module 2: Intersectional Scanner

### What it does
It watches performance and fairness across groups, and across time.

### Defining groups
An intersectional group combines attributes, for example:

\[
\mathcal{G} = \text{Race} \times \text{Sex}
\]

Each element \(g \in \mathcal{G}\) is one group, such as one race–sex combination. Cohorts from Module 1 can be monitored in the same way.

### Per-group metrics
For each group \(g\):

**True positive rate**

\[
TPR_g = \frac{TP_g}{TP_g + FN_g}
\]

**False positive rate**

\[
FPR_g = \frac{FP_g}{FP_g + TN_g}
\]

**Selection rate** (the share of the group predicted positive)

\[
SR_g = P(\hat{Y}=1 \mid G=g)
\]

Both TPR and FPR are undefined when their denominators are zero, for example, a group with no actual positives in the window. In that case the metric is reported as *not computable*, not as zero.

### Fairness gaps
For two groups \(a\) and \(b\):

\[
DPD_{a,b} = SR_a - SR_b \qquad
EOD_{a,b} = TPR_a - TPR_b \qquad
FPRD_{a,b} = FPR_a - FPR_b
\]

- **Demographic parity difference (DPD)** compares selection rates.
- **Equal opportunity difference (EOD)** compares true positive rates.
- Reporting EOD and FPRD together covers *equalized odds*.

With many intersectional groups, pairwise comparisons multiply quickly. A practical summary is the largest gap across all groups, for example:

\[
\max_{g \in \mathcal{G}} TPR_g \;-\; \min_{g \in \mathcal{G}} TPR_g
\]

computed only over groups that meet the minimum sample size. Which fairness definitions matter most is a policy choice, and these definitions can't all be satisfied at once in general, so the configuration should state which ones are being used.

### Uncertainty and sample size
Small groups produce noisy numbers, so every metric must come with:

- The sample size (and for TPR, the number of actual positives; for FPR, the number of actual negatives).
- A confidence interval. A Wilson interval works for single proportions, and a bootstrap works for differences.
- A minimum-sample rule: a group below the threshold is flagged and **cannot trigger an automatic intervention**.

Since many groups are tested repeatedly over time, the system should also control for multiple comparisons (for example, with a false-discovery-rate correction), or it will raise false alarms.

### Monitoring over time
Metrics are computed over rolling or sliding windows. The detection rule (fixed threshold, sequential test, or something else) is to be chosen and compared in the experiments. Only predictions with arrived labels are included in label-dependent metrics, and label coverage per group is reported alongside.

## 3. Module 3: Causal Lineage Tracer

### What it does
When something degrades, it helps answer, "what changed upstream, and does it plausibly explain the problem?"

### Representing the pipeline
The pipeline is a directed acyclic graph:

\[
\mathcal{P} = (V, E)
\]

where:

- \(V\) is the set of nodes: datasets, features, and transformations.
- \(E\) is the set of edges: "this node depends on that one."

(We write \(\mathcal{P}\) for the pipeline so it can't be confused with the group set \(\mathcal{G}\) in Module 2.)

Example pipeline:

```text
Raw Dataset
    |
    v
Missing Value Imputation
    |
    v
Feature Encoding
    |
    v
Model Input
    |
    v
Prediction
```

### Operation

1. **Find what changed.** Compare current and reference versions of each node, such as feature statistics, missing-value rates, and transformation settings.
2. **Rank the suspects.** Prioritise changed nodes that sit upstream of the degraded metric.
3. **Test them.** Run controlled diagnostic tests on our own pipeline: for example, replay recent data through the pipeline with one suspect step reverted to its reference behaviour, and see whether the degradation shrinks.

### Output
A ranked list of suspects, each labelled with its evidence type:

| Evidence type | Meaning |
|---|---|
| Dependency only | The node is upstream of the problem. That is all we know. |
| Observed change | The node changed over the relevant period. |
| Test-supported | A controlled diagnostic test moved the degradation in the expected direction. |

### An important distinction
A lineage link shows **dependency, not causation.** Even a diagnostic test only supports claims about *our pipeline*, because we can re-run a pipeline but we can't re-run the real world. Strong causal language needs justified assumptions and validation, and the simulated scenarios, where the true cause is known, are how we check how reliable the method is.

## 4. Module 4: Adaptive Threshold Router

### What it does
For a binary classifier, the predicted class depends on a decision threshold \(t\):

\[
\hat{y} =
\begin{cases}
1 & \text{if } P(Y=1 \mid X) \geq t \\
0 & \text{otherwise}
\end{cases}
\]

The module looks for a better \(t\) when evidence suggests the current one is no longer serving the system well.

### A note on scores
The rule above treats the model score as a probability. If the model's scores are poorly calibrated, a threshold is just a cut-off on an arbitrary scale, and that is fine, but the "probability" wording shouldn't be taken literally. Checking calibration is part of the evaluation.

### Constraints
Each candidate threshold \(t'\) is checked against:

- A minimum acceptable recall.
- A maximum acceptable false-positive rate.
- Fairness constraints (for example, a cap on the largest TPR gap).
- Minimum group sample sizes.
- A maximum change from the current threshold: \(|t' - t_0| \le \delta\).

### Validation
Candidates are chosen on one slice of data and validated on another, to avoid choosing a threshold that merely fits recent noise. A recommendation is made only when the evidence supports it *and* validation passes.

### Group-specific thresholds
Using different thresholds for different groups can reduce gaps, but it can also raise legal and ethical concerns, since people in different groups are treated by different rules. The initial design uses a single global threshold. Group-specific thresholds, if explored, are treated as a separately reviewed variant, and every change is also tested for unintended disparities it may introduce.

### Output
A candidate threshold, its evaluation results against each constraint, and the validation outcome. This is a recommendation only. A human decides.

## 5. Cross-Module Expectations

- Cohort assignments are never proof of anyone's demographic identity.
- Group metrics always include sample size and uncertainty.
- Lineage evidence is never described as causal proof without validation.
- Threshold recommendations are checked against fairness *and* predictive-performance constraints.
- If diagnosis points to a data or pipeline fault, the right response is to fix the source, not to move the threshold.
- Every diagnostic test, proposed corrective action, and result is recorded for audit.
