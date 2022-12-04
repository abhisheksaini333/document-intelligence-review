# Document type classifier model card

## Intended task

Classify English invoice, purchase-order and receipt text extracted from scanned pages. Predictions support human review. They do not establish the correctness of extracted amounts or approve financial transactions.

## Data and protocol

The project generates 180 synthetic records in 15 declared layout families. Each class has five families of 12 records. Three families per class train the classifiers, one calibrates confidence, and one provides the final holdout. The audit rejects cross-split document identifiers, family identifiers and duplicate normalized text. Calibration temperatures and confidence thresholds never use test labels.

These records share a deliberately limited business vocabulary and simple field layout rules. Perfect synthetic test performance is compatible with substantial real-world error. The fixed split demonstrates reproducibility and the evaluation workflow, not generalization to arbitrary vendors.

## Models

- Baseline: TF-IDF unigrams/bigrams with sublinear term frequencies; logistic regression, C=4, max iterations 300, seed 17.
- Candidate: DistilBERT base uncased at the fixed upstream revision; all parameters fine-tuned for three epochs, batch size four, maximum 128 tokens, AdamW learning rate 0.00003, clipped gradients, seed 17 and two CPU threads.
- Temperature candidates: 0.5, 0.75, 1, 1.5, 2, 3 and 5; selected by calibration negative log likelihood.
- Promotion: require at least 0.01 macro-F1 gain, with at most 0.02 ECE regression.

## Measured outcome

See [the machine-readable report](evaluation.json) for dataset fingerprints, split IDs, family lists, losses, confusion matrices, calibration bins, coverage curves and inference timing. Both models reached 1.0 macro F1 on the 36 held-out synthetic texts. The candidate did not pass the gain requirement, so the faster baseline is retained. Saved transformer predictions matched a fresh load exactly.

The benchmark classifies fixture source text. OCR field evaluation and OCR-to-classifier checks are separate measurements against rendered image pixels. Handwriting, multilingual documents, photographs, severe skew, arbitrary vendor templates and legal or financial verification are outside the demonstrated scope.

Human corrections can become training examples after family assignment and a leakage audit. Reviewers must not move known calibration/test families into training during the same comparison.

## Feedback families and deployed confidence

A reviewer assigns a stable vendor/template family in the visible `Document family` field. Related pages and document variants must share that identifier. The reviewed export preserves it; unassigned families are rejected by `feedback-train`. For the built-in fixture set, `invoice-layout-0` through `invoice-layout-2` (and the equivalent other-class families) are training families, suffix `3` is calibration, and suffix `4` is test. Exported feedback overlapping calibration/test families, IDs or normalized texts is refused.

Run `python -m docreview feedback-train reviewed-labels.json --output artifacts/feedback` after exporting approved records. This trains and evaluates a candidate artifact; it does not activate it. The browser integration test sets the family using the form, exports actual approved records and retrains directly from that export.

The deployed pipeline currently uses raw classifier probabilities with a fixed 0.85 review threshold and 0.75 OCR field threshold. Temperature fitting, coverage curves and selected thresholds in the comparison report are offline evaluation. They do not automatically alter serving or routing policy.
