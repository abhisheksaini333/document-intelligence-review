# Third-party notices and model provenance

Original Folio application code is MIT licensed. Dependency and model licenses remain with their respective authors.

| Component / asset | License | Provenance |
|---|---|---|
| Tesseract 5.2.0 | Apache-2.0 | [Tagged release](https://github.com/tesseract-ocr/tesseract/releases/tag/5.2.0), source archive checksum in Dockerfile |
| English `tessdata_fast` | Apache-2.0 | [Revision 65727574dfcd264acbb0c3e07860e4e9e9b22185](https://github.com/tesseract-ocr/tessdata_fast/tree/65727574dfcd264acbb0c3e07860e4e9e9b22185); asset checksum in Dockerfile |
| DistilBERT base uncased | Apache-2.0 | [Revision 043235d6088ecd3dd5fb5ca3592b6913fd516027](https://huggingface.co/distilbert/distilbert-base-uncased/tree/043235d6088ecd3dd5fb5ca3592b6913fd516027); exact file digests in `model-sources.json` |
| Transformers / Tokenizers | Apache-2.0 | Hugging Face runtime packages; versions in transformer lock |
| PyTorch | BSD-style | PyTorch 1.12.1 distribution notices |
| scikit-learn | BSD-3-Clause | scikit-learn 1.1.1 distribution notices |
| MLflow | Apache-2.0 | MLflow 1.26.1 distribution notices |
| BentoML | Apache-2.0 | BentoML 1.0.0 distribution notices |
| React / Vite | MIT | Locked npm distributions |
| DejaVu fonts | DejaVu / Bitstream Vera terms | Debian `fonts-dejavu-core`; only rendered fixture pixels are application output |

Downloaded model directories retain their upstream LICENSE and model card. The [DistilBERT license](licenses/DistilBERT-APACHE-2.0.txt) and [Tesseract license](licenses/Tesseract-APACHE-2.0.txt) are retained here for reference. Model binaries, source archives and installed distributions remain ignored by Git; acquisition scripts verify content hashes before use.

Synthetic document text and layout fixtures are created by this project and contain no customer information. This repository is an original application using the upstream packages listed above.
