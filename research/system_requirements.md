# System Requirements

## 1. Purpose

This document spells out what the Integrated Fairness Intelligence System (IFIS) takes in, what it gives back, and what it must do in between.

In plain terms: IFIS watches a supervised binary-classification model while the world around it changes. It notices when performance or fairness starts to slip, helps work out why, and suggests safe fixes. It suggests; it never quietly acts on its own.

## 2. Key Terms

A few words get used in several ways across a project like this, so here is how we use them throughout all IFIS documents.

| Term | Meaning in IFIS |
|---|---|
| **Cohort** | A group of observations found by the system from their features alone. A cohort is a statistical grouping, not a claim about anyone's identity. |
| **Intersectional group** | A group defined by combining recorded attributes, such as race × sex. |
| **Diagnostic test** | A controlled experiment on our own pipeline (for example, re-running it with one upstream step reverted) to see whether a suspected cause matters. |
| **Corrective action** | A change meant to fix a problem. In the initial scope, this means a change to the decision threshold. |
| **Pending metric** | A metric that cannot be computed yet because the labels it needs haven't arrived. |
| **Monitoring window** | The slice of time or data a given result is based on. |

Keeping "diagnostic test" and "corrective action" separate matters. Earlier drafts used "intervention" for both, which made it unclear whether something was an experiment or a real change to the system.

## 3. System Inputs

| Input | Why we need it |
|---|---|
| Trained ML model | Produces predictions |
| Reference dataset | Sets the baseline distributions we compare against |
| Incoming data | Lets us monitor continuously |
| Sensitive attributes | Enable fairness auditing, where their use is permitted |
| Actual labels | Enable performance and fairness evaluation (they often arrive late) |
| Model predictions | Are compared with actual outcomes |
| Pipeline metadata | Describes transformations and lineage |
| Model version | Identifies which model produced which predictions |
| Configuration and constraints | Define thresholds, minimum sample sizes, maximum allowed threshold change, and alert rules |

Sensitive attributes are used to *audit* the model. In the initial scope they are not model inputs, and IFIS does not assume that leaving them out makes the model fair.

### Delayed feedback

In real deployments, a prediction is usually made right away, while the true outcome shows up days or weeks later. IFIS has to treat this as normal, not as an edge case. Specifically, it should:

- Record each prediction when it is made.
- Match later-arriving labels to the right prediction record.
- Compute label-dependent metrics only from predictions whose labels have actually arrived.
- Clearly separate results built on complete labels from results built on partial or missing labels.

## 4. System Outputs

| Output | Purpose |
|---|---|
| Cohort assignments | Show which discovered group each observation belongs to, with a status or confidence |
| Performance metrics | Measure predictive quality |
| Fairness metrics | Measure differences between groups |
| Uncertainty and sample sizes | Show how much each group-level number can be trusted |
| Metric status | Mark each metric as *complete*, *partial*, or *pending* |
| Drift scores | Measure how much incoming data has shifted |
| Diagnostic findings | List suspected contributors and the type of evidence behind each |
| Diagnostic test results | Record the outcome of each controlled experiment |
| Threshold recommendations | Propose validated adjustments, never applied automatically |
| Failure reports | Say plainly which component failed and what that affects downstream |
| Audit records | Preserve what the system saw, concluded, proposed, and did |

## 5. Functional Requirements

### FR-01: Model and version tracking
Every prediction and every monitoring result must identify the model version that produced it.

### FR-02: Reference and incoming data
The system must accept a reference dataset and a stream of incoming observations so the two can be compared over time.

### FR-03: Cohort assignment
The system must assign observations to discovered cohorts. Where the chosen method supports it, it must also report an assignment status or confidence (for example, "unassigned" for noise points in density-based methods).

### FR-04: Performance monitoring
The system must calculate predictive-performance metrics whenever the needed actual labels are available.

### FR-05: Fairness monitoring
The system must calculate group-level and intersectional fairness metrics when the needed attributes and labels are available and their use is permitted.

### FR-06: Drift monitoring
The system must calculate drift scores that show when incoming data distributions move away from the reference.

### FR-07: Pipeline lineage
The system must represent datasets, features, and transformations as a dependency graph so upstream changes can be investigated.

### FR-08: Diagnostic findings
The system must report suspected contributors to degradation. Each finding must be labelled by evidence type: *dependency only*, *observed change*, or *supported by a diagnostic test*. Dependency evidence must never be presented as proven cause.

### FR-09: Threshold evaluation
The system must evaluate candidate thresholds against configured performance, fairness, sample-size, and maximum-change constraints.

### FR-10: Human approval
The system must never apply a threshold change without both successful validation and human approval.

### FR-11: Audit logging
The system must record monitoring results, diagnostic evidence, proposed corrective actions, approvals, rejections, and configuration changes.

### FR-12: Failure handling
A failure in one component must be reported clearly. It must never be shown as a successful analysis.

### FR-13: Delayed-label handling
The system must store predictions separately from labels, match labels to predictions when they arrive, and mark label-dependent metrics as *pending* or *partial* until enough labels are available.

### FR-14: Uncertainty and sample-size guard
Every group-level metric must be reported with its sample size and an uncertainty estimate. Groups below the configured minimum sample size must be flagged and must not trigger a corrective action.

### FR-15: Rollback
The system must keep the previous approved configuration and support restoring it, with the rollback itself recorded in the audit log.

### FR-16: Diagnosis-aware recommendations
If diagnostic evidence points to a data or pipeline fault, the system must flag this for engineers instead of proposing a threshold change that would only hide the problem.

## 6. Non-Functional Requirements

- **Reliability:** Missing labels and failed components are handled explicitly, never skipped silently.
- **Traceability:** Every output links back to a model version and a data window.
- **Privacy:** Sensitive information is stored only when needed, and never "just in case."
- **Transparency:** Diagnostic outputs state their uncertainty and the limits of their evidence.
- **Safety:** Recommendations must pass validation and approval before anyone relies on them.
- **Reproducibility:** Experiments record their datasets, scenarios, baselines, random seeds, and evaluation metrics.
- **Testability:** The safeguards in this document (no unvalidated changes, small-sample guards, rollback, and so on) should be enforced by automated tests, not just described in prose.
- **Overhead:** The cost of running IFIS (compute and latency) is measured, because the research compares it against simpler monitoring.

## 7. Initial Scope and Assumptions

- The first task is supervised binary classification.
- Experiments use simulated temporal data streams.
- The Adult Census Income dataset is the starting dataset. It is a single snapshot with no real time dimension, so all "drift" in the first experiments is deliberately simulated.
- The first implementation is a controlled research simulation. It does not make or change live production decisions.
- Algorithm choices are provisional and may change as the research progresses.

### Out of scope for now

- Live production deployment.
- Multi-class or regression models.
- Fully automatic threshold changes without human review.
