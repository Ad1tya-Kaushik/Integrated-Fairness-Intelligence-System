# Research Proposal

## Working Title

**Integrated Fairness Intelligence System for Continuous Machine Learning Monitoring, Diagnosis and Adaptation**

## 1. Problem Statement

A machine learning model that works well on the day it ships doesn't stay that way. The data it sees shifts, its accuracy drifts, and it may start serving some groups of people worse than others, sometimes only groups that are small or sit at the intersection of several attributes.

Most teams watch for these problems with separate tools: one for accuracy, one for fairness, one for data drift, one for pipeline health. When something goes wrong, it's hard to tell whether the cause is a changing population, a broken upstream step, or the model itself, and it's hard to know whether a fix is safe.

This research proposes one integrated system that:

1. discovers latent cohorts the model may be treating differently,
2. monitors fairness over time across intersectional groups,
3. uses pipeline lineage and controlled tests to localise likely causes, and
4. evaluates cautious, constrained adjustments to the decision threshold.

Its aim is to notice emerging fairness problems early, investigate why they happen, and judge possible fixes using measurable evidence and honest uncertainty.

## 2. Research Objective

To design, build, and experimentally evaluate an integrated framework for monitoring and diagnosing fairness in machine learning systems that operate under changing data.

## 3. Research Scope

- Supervised **binary classification** models.
- **Simulated** temporal data streams, using the Adult Census Income dataset as the starting point.
- A **controlled simulation**. The system does not change live production decisions.

### Why the Adult dataset, and what to watch out for

Adult is well known and easy to reproduce, which is a real advantage. It also has limits we should be upfront about:

- It is a single snapshot from the 1990s with no genuine time dimension, so any drift must be simulated.
- Its race and sex categories are coarse, and some intersectional groups are very small, which makes group metrics noisy.
- It contains missing values (marked "?") in several columns, which makes it a natural test for upstream data problems.

Results on Adult should be read as a proof of concept, not as evidence about every real-world setting. If time allows, a second dataset would strengthen the conclusions.

## 4. Research Questions

| ID | Research question | Hypothesis (what a positive result would look like) |
|---|---|---|
| RQ1 | Can latent cohort discovery reveal performance disparities that aggregate monitoring misses? | In scenarios with a planted subgroup problem, cohort-based monitoring flags the problem while aggregate metrics stay within normal range. |
| RQ2 | Can temporal intersectional monitoring detect fairness degradation reliably under changing distributions? | Intersectional monitoring detects planted degradation sooner than aggregate monitoring, without a higher false-alert rate. |
| RQ3 | Can combining data lineage with controlled tests improve root-cause localization? | Lineage plus diagnostic tests names the true planted cause more often than lineage alone. |
| RQ4 | Can constrained threshold adaptation improve fairness while keeping predictive performance acceptable? | Adaptive thresholds reduce the chosen fairness gap compared with a fixed threshold, while staying within the stated performance limits. |
| RQ5 | Does the integrated system outperform conventional monitoring in diagnostic reliability? | The full system localises causes more accurately than a conventional setup (separate drift and aggregate fairness monitors), at an acceptable overhead. |

## 5. Experimental Methodology

For every experiment, write down:

1. What is being tested.
2. Which dataset is being used.
3. Which baseline it is being compared against.
4. Which metrics will be calculated.
5. What result would support the hypothesis, and what would count against it.

### Planned experiments

| Experiment | Comparison | Evaluation |
|---|---|---|
| Cohort discovery | K-Means vs DBSCAN vs HDBSCAN | Stability over time; how well discovered cohorts recover planted subgroups (e.g., adjusted Rand index) |
| Fairness monitoring | Aggregate vs intersectional monitoring | Detection delay and false-alert rate |
| Root-cause diagnosis | Lineage alone vs lineage plus diagnostic tests | Root-cause localization accuracy (e.g., is the true cause ranked first, or within the top three?) |
| Threshold adaptation | Fixed vs adaptive thresholds | Fairness–performance trade-off, including disparities the change itself introduces |
| Full integration | Conventional monitoring vs the complete system | Diagnostic accuracy and computational overhead |

### Making the results trustworthy

- Run each scenario with **multiple random seeds** and report averages with confidence intervals, not single runs.
- Where practical, run **ablations** (remove one module at a time) to see what each contributes.
- Use a **no-drift control** so we can measure false alarms, not only detections.
- Keep thresholds and settings fixed *before* looking at test results, to avoid tuning on the answer.

## 6. Simulated Scenarios

| Scenario | What it tests |
|---|---|
| Stable data, no drift | The false-alarm rate (should stay quiet) |
| General feature-distribution drift | Detection of broad covariate shift |
| Group-specific drift | Whether single-group problems are noticed |
| Intersectional drift | Whether problems hidden in group combinations are noticed |
| Changing feature–target relationship (concept drift) | Whether degradation without obvious input drift is caught |
| Upstream data-transformation errors | Root-cause localization in the pipeline (e.g., a faulty imputation step) |
| Delayed or partially missing labels | Whether the system handles pending metrics honestly |
| Multiple simultaneous changes | Whether several causes can be told apart |

In every scenario, we introduce **known** changes and record exactly what was planted and when. Knowing the true cause is what lets us measure whether the system finds it. Without that ground truth, "root-cause accuracy" has no meaning.

## 7. Ethical and Safety Requirements

- Do not treat latent cohorts as proof of demographic identity.
- Do not claim that removing race and sex from the model's inputs removes bias. Other features can act as proxies.
- Avoid storing sensitive information that isn't needed.
- Always report uncertainty and sample sizes for group-specific metrics.
- Never adjust thresholds automatically without validation.
- Keep human approval and rollback in place.
- Record the reasoning behind every corrective action.
- Test whether a change introduces new disparities elsewhere.
- Be cautious about group-specific decision rules, which raise legal and ethical questions of their own.

These safeguards shouldn't live only in a document. Over time each one should become an automated test that fails loudly if the system breaks it.

## 8. Threats to Validity

Being honest about the limits is part of good research. The main ones to keep in view:

- **Simulation realism:** planted drift may be easier to detect than real drift.
- **Dataset limits:** results on one dataset may not carry over to others.
- **Small groups:** intersectional groups can be too small for stable estimates.
- **Fairness definitions:** different definitions can conflict, so conclusions depend on which are chosen.
- **Diagnostic scope:** diagnostic tests support claims about the pipeline, not about causes in the real world.

## 9. Initial Research Position

The four modules and their algorithms are starting design choices, not fixed commitments. They will be revised as the research gap becomes clearer and as experimental evidence comes in.
