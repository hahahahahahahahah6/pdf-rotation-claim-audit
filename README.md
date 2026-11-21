# Documentation claim auditor

This offline static auditor compares documentation of the checked capability with Python source patterns. It scans the root README and Markdown under docs. Fenced code is excluded; inline code counts. Source is parsed without execution. Tests are reported separately; fixtures, examples, documentation and symlinks are excluded from production evidence.

```sh
pdf-rotation-claim-audit audit . --json --fail-on medium --ignore vendor/
python3 -m pdf_rotation_claim_audit --version
```

Exit 0 means PASS, 2 means a finding meets the threshold, and 1 means a usage or I/O error. The default threshold is high. Ignore prefixes can be repeated.

```
documented-pdf-rotation-claim-false
documented-no-pdf-rotation-claim-false
```

## Differentiation

The checked operation is distinct from document extraction, generation, merging, splitting and encryption. It is also distinct from spreadsheet, word processing and presentation reading and generation. Table extraction, specialized document extraction, invoice separation, multiple receipt detection, document cropping, image operations, electronic signatures, payment processing and OCR are outside the phrase lists.

## Limitations

- A phrase may describe the status of a file that is only read.
- A phrase may describe an image embedded inside a document.
- A phrase may describe a wrapper that never performs the checked operation.
- A phrase may describe setting a value in a viewer session.
- A phrase may describe deskewing a scanned image.
- A phrase may describe an external command, which is not detected and causes a high finding when no other evidence exists.
- A phrase may describe only reporting a file's status.
- A reader or writer construction and an unrelated rotate call in one module count together.
- A reader or writer construction and an unrelated rotation attribute assignment in one module count together.
- A PyMuPDF opener and an unrelated set_rotation call in one module count together.
- A pikepdf opener or pdfrw reader and an unrelated Rotate assignment in one module count together.
- A pikepdf JobBuilder construction and an unrelated rotate call in one module count together.
- A PyMuPDF annotation's set_rotation call counts the same as a page call.
- A reader or writer pair counts when the angle is zero.
- A reader or writer pair counts when the angle is not a multiple of 90.
- A PyMuPDF pair counts when the value is zero.
- A pikepdf or pdfrw assignment pair counts when the value is zero.
- A JobBuilder pair counts when the angle is zero.
- A reader or writer construction alone is not detected.
- A reader or writer construction and write call alone are not detected.
- A rotate call alone is not detected without a matching construction in the same module.
- A rotation attribute assignment alone is not detected without a matching reader or writer in the same module.
- A set_rotation call alone is not detected without a PyMuPDF opener in the same module.
- A Rotate assignment alone is not detected without a pikepdf opener or pdfrw reader in the same module.
- A PyMuPDF opener and save call alone are not detected.
- A JobBuilder construction alone is not detected.
- A transformation and add_transformation call alone are not detected because they change the content matrix.
- A transfer_rotation_to_content call is not detected because it bakes the value into the content.
- PIL and OpenCV image rotation and transpose calls alone are not detected.
- A reader or writer and add_page call alone are not detected.
- A writer and append or merge call alone are not detected.
- A PyMuPDF opener and insert_pdf call alone are not detected.
- A pikepdf pages.extend call alone is not detected.
- A pdfrw addpage call alone is not detected.
- A pdfrw addpages call alone is not detected.
- A writer and encrypt call alone are not detected.
- A reader call alone is not detected.
- Document generation alone is not detected.
- Document merging alone is not detected.
- Document splitting alone is not detected.
- Document encryption alone is not detected.
- Document extraction alone is not detected.
- qpdf, pdftk and Ghostscript subprocess calls are not detected.
- Mindee parsing with any product is not detected.
- Azure document analysis with any model ID is not detected.
- Veryfi calls of any kind are not detected.
- Google Document AI processing with any processor is not detected.
- Eden AI universal-ai calls with any model ID are not detected.
- Textract calls of any kind are not detected.
- LlamaParse calls are not detected.
- Nanonets calls are not detected because their model IDs are opaque.
- Docsumo calls are not detected because their endpoints are generic.
- ABBYY Vantage calls are not detected because their skill IDs are opaque.
- Rossum calls are not detected because their queue IDs are opaque.
- Klippa calls are not detected because their identifiers are opaque.
- Parseur calls are not detected because their template IDs are opaque.
- Extend calls are not detected because their workflow IDs are opaque.
- Hand-written dictionary editing without a listed call is not detected.
- Detection cannot establish whether the chosen angle produces the correct orientation.
- Static matching cannot judge semantics.
- Dead code counts.
- Alias chains beyond the tracer are missed.
- Only exact phrases count.
- Denial handling depends on the listed phrases.
- Each paired route must occur in a single module.
