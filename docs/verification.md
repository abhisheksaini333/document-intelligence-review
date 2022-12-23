# Verification and measured behavior

The application was exercised through its Python API, HTTP endpoints, browser workstation, installed wheel and Docker runtime. The table records the scope of each check; model scores apply only to the project-owned synthetic fixtures.

| Area | Executed check | Result |
| --- | --- | --- |
| Backend and reliability | `python -m unittest discover -s tests -v` | 107 tests passed on Python 3.10, including actual OCR, SQLite restart/leases, duplicate ingestion, stale edits, private database permissions, backups, artifact integrity, MLflow and BentoML model save/load. |
| Pinned runtime | Same 107 tests with current source mounted read-only into the built image | 107 passed on Python 3.10.6 and Tesseract 5.2.0. The container builds the pinned OCR source and verifies English trained-data hashes. |
| Container HTTP | Fresh nonroot image, one CPU and 1 GB memory; upload a rendered invoice, process it, repeat upload | UI and health returned 200; missing write token returned 401; duplicates returned one document; all six extracted fields matched their source fixture. |
| Browser workflow | `python scripts/browser_check.py` | Four Playwright journeys passed: save/approve/export, source box focus, unsaved draft protection, and stale-tab rejection with draft retention. |
| Feedback retraining | Browser sets the visible document family, approves and exports; harness trains directly from that export | One reviewed example added to 108 base training examples. Fixed 36-document holdout retained; macro F1 1.0. A separate regression rejects exported held-out-family feedback. |
| Baseline and transformer | `python -m docreview benchmark --epochs 3` | Both models genuinely trained; common grouped 108/36/36 split; both raw test macro F1 1.0. Transformer reload predictions matched exactly; no promotion because F1 gain was zero. |
| Raster OCR evaluation | `python scripts/evaluate_ocr.py` | On 36 rendered holdout pages, 216/216 fields matched and both saved classifiers reached OCR-text macro F1 1.0. This report used host Tesseract 5.5.2. |
| MLflow | Real file-backed experiments, metrics, artifact retrieval and comparison logging | Baseline artifact restoration passed; the measured comparison was logged with both model scores and its report artifact. |
| BentoML HTTP | Actual BentoML 1.0 server; activate candidate then roll back | Model version/revision changed, candidate changed a known prediction, rollback restored the original version and identical probabilities. |
| Clean installation | Pinned ops lock into a fresh environment; build/install wheel; run outside checkout | Package imported from site-packages, bundled UI and health served over HTTP, CLI reported 0.1.0. No source checkout or Node runtime needed to serve the wheel. |
| Frontend | Client request/limit checks and production Vite build | Passed; wheel and container include the built workstation. |

## Reproduce

Follow the [README setup](../README.md) first. Full model comparison additionally requires the transformer lock and verified source download. Do not run a full training job just to exercise the browser or backend suite.

```sh
BENTOML_HOME=.bentoml OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 python -m unittest discover -s tests -v
node frontend/tests/client.test.mjs
npm --prefix frontend run build
python scripts/browser_check.py
docker build -t document-intelligence-review:local .
docker run --rm --cpus=1 --memory=1g \
  -e BENTOML_HOME=/tmp/bento -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 \
  -v "$PWD:/work:ro" -w /work document-intelligence-review:local \
  python -m unittest discover -s tests -v
```

The CI workflow performs the host tests, frontend build and real browser journey. A local successful run does not establish a hosted GitHub Actions run; inspect that run after publication. The workflow writes its results to job logs and does not depend on retired artifact-upload actions.

## Measurement boundaries

The [model comparison](evaluation.json) measures classification from clean fixture text. The [OCR report](ocr-evaluation.json) separately measures image pixels, field boxes and classification from OCR output. Both use simple English synthetic templates with a shared controlled vocabulary. Neither establishes production document accuracy.

Runtime review routing uses raw model confidence and fixed thresholds; fitted temperatures and selected coverage thresholds remain offline evaluation, as explained in the [model card](model-card.md). Feedback families require a reviewer to assign stable vendor/template identities. The leakage audit cannot infer an incorrect human family assignment.

Application dependencies are pinned separately from validation tools. The Docker image uses Python 3.10.6, Node 18.12.0 at build time and Tesseract 5.2.0. Host validation used Python 3.10.21, Tesseract 5.5.2 and an installed Chrome browser; this does not change the image's dependency pins. The source-text model comparison used PyTorch 1.12.1 and Transformers 4.19.2.

The workstation supports a single local data store. Network authentication, tenant separation and real customer-document evaluation remain deployment work described in [operations](operations.md).
