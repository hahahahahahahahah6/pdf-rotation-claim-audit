EXPECTED_YES = ('rotate pdf', 'rotates pdf', 'rotating pdf', 'rotate pdfs', 'rotates pdfs', 'rotating pdfs', 'rotate pdf file', 'rotates pdf file', 'rotating pdf file', 'rotate pdf files', 'rotates pdf files', 'rotating pdf files', 'rotate pdf document', 'rotates pdf document', 'rotating pdf document', 'rotate pdf documents', 'rotates pdf documents', 'rotating pdf documents', 'rotate pdf pages', 'rotates pdf pages', 'rotating pdf pages', 'rotate pdf page', 'rotates pdf page', 'rotating pdf page', 'rotate pdf by 90 degrees', 'rotate pdf by 180 degrees', 'rotate pdf by 270 degrees', 'rotate a pdf', 'rotates a pdf', 'rotating a pdf', 'rotate one pdf', 'rotate pdf clockwise', 'rotates pdf clockwise', 'rotating pdf clockwise', 'rotate pdf counterclockwise', 'rotates pdf counterclockwise', 'rotating pdf counterclockwise', 'set pdf rotation', 'sets pdf rotation', 'setting pdf rotation', 'pdf rotator', 'pdf rotation', 'fix pdf rotation', 'fixes pdf rotation', 'fixing pdf rotation', 'correct pdf orientation', 'corrects pdf orientation', 'correcting pdf orientation', 'change pdf orientation', 'changes pdf orientation')
EXPECTED_NO = ('no pdf rotation', 'does not rotate pdf', 'does not rotate pdfs', 'does not rotate pdf files', 'does not rotate pdf document', 'does not rotate pdf documents', 'does not rotate pdf pages', 'does not rotate pdf page', 'no pdf rotator', 'does not support pdf rotation', 'without pdf rotation', 'pdf rotation not supported', 'no pdf rotation support', 'does not rotate a pdf', 'does not rotate pdf clockwise', 'does not set pdf rotation', 'does not rotate one pdf', 'does not rotate pdf file', 'does not rotate pdf counterclockwise', 'does not rotate pdf by 90 degrees', 'does not fix pdf rotation', 'does not correct pdf orientation', 'does not change pdf orientation', 'pdf rotation not available')
EXPECTED_NAMES = ('rotate_pdf', 'rotate_pdfs', 'rotate_pdf_file', 'rotate_pdf_files', 'rotate_pdf_document', 'rotate_pdf_documents', 'rotate_pdf_pages', 'rotate_pdf_page', 'rotate_pdf_with_angle', 'rotate_pdf_by_angle', 'set_pdf_rotation', 'set_pdf_page_rotation', 'rotate_all_pdf_pages', 'rotate_pdf_clockwise', 'rotate_pdf_counterclockwise', 'rotate_pdf_90', 'rotate_pdf_180', 'rotate_pdf_270', 'rotate_pdf_page_90', 'fix_pdf_rotation', 'fix_pdf_orientation', 'correct_pdf_rotation', 'correct_pdf_orientation', 'pdf_rotator')
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from pdf_rotation_claim_audit.audit import audit, evidence
from pdf_rotation_claim_audit.phrases import PDFROTATION, NOPDFROTATION, GENERIC_NAMES
from pdf_rotation_claim_audit.__main__ import main

class AuditTests(unittest.TestCase):
    def test_phrase_oracle(self):
        self.assertEqual(PDFROTATION, EXPECTED_YES)
        self.assertEqual(NOPDFROTATION, EXPECTED_NO)
        self.assertEqual(GENERIC_NAMES, EXPECTED_NAMES)

    def test_audit_scenarios(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); readme=p/'README.md'; src=p/'app.py'
            readme.write_text('rotate pdf files'); r=audit(d); self.assertEqual(r['findings'][0]['rule'],'documented-pdf-rotation-claim-false'); self.assertEqual(r['verdict'],'FAIL')
            src.write_text('import fitz\nfitz.open(); d.rotate_pdf()'); self.assertEqual(audit(d)['verdict'],'PASS')
            readme.write_text('does not rotate pdf files'); r=audit(d); self.assertEqual(r['findings'][0]['rule'],'documented-no-pdf-rotation-claim-false'); self.assertEqual(r['claims'],[])
            src.unlink(); self.assertEqual(audit(d)['verdict'],'PASS')
            readme.write_text('```\nrotate pdf files\n```'); self.assertEqual(audit(d)['verdict'],'PASS')
            readme.write_text('`rotate pdf files`'); self.assertEqual(audit(d)['verdict'],'FAIL')
            (p/'tests').mkdir(); (p/'tests/test_app.py').write_text('import fitz\nfitz.open(); d.rotate_pdf()')
            self.assertEqual(audit(d)['findings'][0]['severity'],'MEDIUM'); self.assertEqual(audit(d)['verdict'],'PASS'); self.assertEqual(audit(d, fail_on='medium')['verdict'],'FAIL')
            src.write_text('import fitz\nfitz.open()'); (p/'other.py').write_text('x.set_rotation(90)'); self.assertEqual(audit(d)['findings'][0]['severity'],'MEDIUM')
            readme.write_text('Nothing claimed'); self.assertEqual(audit(d)['verdict'],'PASS')

    def test_exclusions(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'README.md').write_text('rotate pdf')
            for name in ('fixtures','examples','docs'):
                (p/name).mkdir(); (p/name/'code.py').write_text('x.rotate_pdf()')
            (p/'test_file.py').write_text('x.rotate_pdf()'); (p/'app_test.py').write_text('x.rotate_pdf()')
            (p/'link.py').symlink_to(p/'test_file.py'); (p/'linked').symlink_to(p/'fixtures', target_is_directory=True)
            r=audit(d); self.assertFalse(r['production_evidence']); self.assertEqual(len(r['test_evidence']),2)
            self.assertEqual(audit(d, ignore=('test_', 'app_'))['findings'][0]['severity'],'HIGH')

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'README.md').write_text('rotate pdf')
            cmd=[sys.executable, '-m', 'pdf_rotation_claim_audit']
            r=subprocess.run(cmd+['audit',d,'--json'],capture_output=True,text=True); self.assertEqual(r.returncode,2)
            data=json.loads(r.stdout); self.assertEqual(data['verdict'],'FAIL'); self.assertTrue(data['findings'][0]['message'])
            self.assertEqual(subprocess.run(cmd+['--version'],capture_output=True,text=True).stdout.strip(),'0.1.0')
            self.assertEqual(subprocess.run(cmd+['audit',d,'--fail-on','HIGH'],capture_output=True).returncode,1)
            self.assertEqual(subprocess.run(cmd+['audit',d+'/missing'],capture_output=True).returncode,1)
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(main(['audit',d]),2)
            (p/'README.md').write_text('does not rotate pdf'); (p/'app.py').write_text('x.rotate_pdf()')
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(main(['audit',d]),2)
            (p/'app.py').unlink(); (p/'README.md').write_text('rotate pdf'); (p/'test_app.py').write_text('x.rotate_pdf()')
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(['audit',d]),0); self.assertEqual(main(['audit',d,'--fail-on','medium']),2)
    def test_routes(self):
        cases = []
        for mod in ('pypdf', 'PyPDF2'):
            for name in ('PdfReader', 'PdfWriter'):
                cases += [f'from {mod} import {name} as C\nC(); x.rotate(0)', f'import {mod} as m\nm.{name}(); x.rotate(90)', f'from {mod} import {name}\n{name}(); x.rotation = 0']
        for name in ('PdfFileReader', 'PdfFileWriter'):
            cases.append(f'from PyPDF2 import {name}\n{name}(); x.rotate()')
        for name in ('rotate_clockwise', 'rotateClockwise', 'rotateCounterClockwise'):
            cases.append(f'from PyPDF2 import PdfReader\nPdfReader(); x.{name}()')
        for mod in ('fitz', 'pymupdf'):
            for name in ('open', 'Document'):
                cases += [f'import {mod} as m\nm.{name}(); x.set_rotation(0)', f'from {mod} import {name} as op\nop(); x.set_rotation(90)']
        cases += ['import pikepdf\npikepdf.Pdf.open(x); x.Rotate = 0', 'import pikepdf\npikepdf.Pdf.new(); x.Rotate: int = 90', 'from pikepdf import Pdf as P\nP.new(); x.Rotate = 90', 'from pikepdf import open as op\nop(x); x.Rotate = 90', 'from pikepdf import new as op\nop(); x.Rotate = 90', 'from pdfrw import PdfReader as R\nR(); x.Rotate = 90', 'import pdfrw\npdfrw.PdfReader(); x.Rotate = 90', 'from pikepdf import JobBuilder as J\nJ(); x.rotate(0)', 'import pikepdf\npikepdf.JobBuilder(); x.rotate(90)', 'from other import rotate_pdf as r\nr()']
        cases += ['x.'+name+'()' for name in EXPECTED_NAMES]
        for source in cases:
            with self.subTest(source=source): self.assertTrue(evidence(source))

    def test_not_evidence(self):
        cases = ['import '+x for x in ('pypdf','PyPDF2','fitz','pymupdf','pikepdf','pdfrw')]
        cases += ['import pypdf\npypdf.PdfReader()', 'import pypdf\npypdf.PdfWriter()', 'x.rotate()', 'x.set_rotation()', 'x.Rotate = 90', 'x.rotation = 90', 'import pikepdf\npikepdf.JobBuilder()', 'job.rotate()', 'import pypdf\npypdf.PdfReader().write(x)', 'import pypdf\npypdf.Transformation().rotate(90); page.add_transformation(x)', 'page.transfer_rotation_to_content()', 'Image.rotate(x)', 'Image.transpose(x)', 'cv2.rotate(x)', 'cv2.flip(x)', 'import pypdf\npypdf.PdfReader(); x.add_page(y)', 'import PyPDF2\nPyPDF2.PdfWriter().append(x)', 'import PyPDF2\nPyPDF2.PdfWriter().merge(x)', 'import fitz\nfitz.open().insert_pdf(x)', 'import fitz\nfitz.open().save(x)', 'import pikepdf\npikepdf.open(x); x.pages.extend(y)', 'import pikepdf\npikepdf.open(); x.Rotate=90', 'import pikepdf\npikepdf.new()', 'import pdfrw\npdfrw.PdfReader()', 'import pypdf\npypdf.PdfWriter().encrypt(x)', 'pdfplumber.open(x)', 'pdfminer.extract_text(x)', 'reportlab.Canvas(x).save()', 'fpdf.output()', 'weasyprint.write_pdf()', '"rotate pdf"', 'x.rotate_pdf', 'rotate_pdf()', 'def rotate_pdf(): pass\nx.rotate_pdf()', 'import pypdf\npypdf=1\npypdf.PdfReader(); x.rotate()', 'from pypdf import PdfReader\nwith x as PdfReader: pass\nPdfReader(); x.rotate()', 'import pypdf\npypdf.PdfReader(); x.rotate_counter_clockwise()', 'def broken(']
        cases += ['import subprocess\nsubprocess.run(["'+x+'", "--rotate"])' for x in ('qpdf','pdftk','gs')]
        cases += [x+'(x)' for x in ('mindee.parse','azure.begin_analyze_document','veryfi.Client','documentai.process_document','textract.analyze_document','eden.universal_ai','llamaparse.parse','nanonets.ocr','docsumo.upload','abbyy.process','rossum.process','klippa.parse','parseur.parse','extend.parse')]
        for source in cases:
            with self.subTest(source=source): self.assertFalse(evidence(source))
