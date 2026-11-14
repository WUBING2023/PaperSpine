"""Optional declared reserved-band text diagnostic; no inferred template or quality pass."""
import argparse,json,re,sys,math,os
from pathlib import Path
try:
    import fitz
except ImportError:
    fitz=None
LIMITATIONS='Requires caller-declared reserved header/footer band in millimetres and optional full-span furniture regex. No universal margin inference. Span bboxes can overstate glyph extent; same-span mixed furniture/body text is not separated. Exemptions may hide legitimate content. Rotated pages are explicitly unsupported and return execution_error, never a clean result. Unrotated cropped pages use extracted crop-relative coordinates. No OCR/image/vector/pagination semantics or scientific review. No candidates is not quality approval.'
def inspect(pdf,footer_mm=None,header_mm=None,allow_regex=None):
    if fitz is None: raise RuntimeError('PyMuPDF is required for this optional diagnostic; install it separately or skip the diagnostic')
    if footer_mm is None and header_mm is None: raise ValueError('Declare at least one reserved band')
    if any(v is not None and (not math.isfinite(v) or v<=0) for v in [footer_mm,header_mm]):raise ValueError('Bands must be finite positive mm')
    rx=re.compile(allow_regex) if allow_regex else None;pages=[]
    with fitz.open(pdf) as doc:
        if doc.needs_pass: raise ValueError('Password-protected PDF is not supported')
        if len(doc)==0: raise ValueError('PDF contains no pages')
        for n,p in enumerate(doc):
            if p.rotation: raise ValueError(f'Page {n+1}: rotated pages are unsupported; reserved bands require unrotated display coordinates')
            if not math.isfinite(p.rect.width) or not math.isfinite(p.rect.height) or p.rect.width<=0 or p.rect.height<=0: raise ValueError(f'Page {n+1}: invalid page size')
            height_mm=p.rect.height*25.4/72
            if any(v is not None and v>=height_mm for v in [header_mm,footer_mm]) or (header_mm or 0)+(footer_mm or 0)>=height_mm: raise ValueError(f'Page {n+1}: declared bands exceed or consume displayed page height')
            candidates=[];exemptions=[]
            for b in p.get_text('dict')['blocks']:
                if b['type']!=0:continue
                for line in b['lines']:
                    for s in line['spans']:
                        text=s['text'].strip()
                        if not text:continue
                        r=fitz.Rect(s['bbox']);hits=[]
                        if header_mm is not None and r.y0<p.rect.y0+header_mm*72/25.4:hits.append('header')
                        if footer_mm is not None and r.y1>p.rect.y1-footer_mm*72/25.4:hits.append('footer')
                        if hits:
                            item={'text':text,'bbox':list(r),'bands':hits}
                            (exemptions if rx and rx.fullmatch(text) else candidates).append(item)
            pages.append({'page':n+1,'page_bbox':list(p.rect),'candidates':candidates,'caller_regex_exemptions':exemptions})
    return {'schema':'pdf-reserved-band-probe/2','input':str(Path(pdf).resolve()),'declared_footer_mm':footer_mm,'declared_header_mm':header_mm,'caller_allow_regex':allow_regex,'execution_error':None,'candidate_count':sum(len(p['candidates']) for p in pages),'quality_approval':False,'pages':pages,'limitations':LIMITATIONS}
def same_input_output(pdf,report):
    source=Path(pdf);target=Path(report)
    if source.resolve()==target.resolve():return True
    if source.exists() and target.exists():return os.path.samefile(source,target)
    return False

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('pdf');ap.add_argument('--footer-mm',type=float);ap.add_argument('--header-mm',type=float);ap.add_argument('--allow-text-regex');ap.add_argument('--report',required=True);ap.add_argument('--fail-on-candidates',action='store_true');a=ap.parse_args()
    # Guard before extraction and before any error-report write, including aliases.
    try:
        if same_input_output(a.pdf,a.report):raise ValueError('Report path aliases the input PDF; refusing to write')
    except Exception as e:
        print(json.dumps({'execution_error':{'type':type(e).__name__,'message':str(e)},'quality_approval':False,'report_written':False}));return 1
    try:r=inspect(a.pdf,a.footer_mm,a.header_mm,a.allow_text_regex)
    except Exception as e:r={'execution_error':{'type':type(e).__name__,'message':str(e)},'quality_approval':False,'limitations':LIMITATIONS}
    try:
        if same_input_output(a.pdf,a.report):raise ValueError('Report path aliases input PDF; refusing to write')
        Path(a.report).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    except Exception as e:
        print(json.dumps({'execution_error':{'type':type(e).__name__,'message':str(e)},'quality_approval':False,'report_written':False}));return 1
    print(json.dumps({'execution_error':r['execution_error'],'candidate_count':r.get('candidate_count'),'quality_approval':False,'report_written':True}))
    return 1 if r['execution_error'] else 2 if a.fail_on_candidates and r['candidate_count'] else 0
if __name__=='__main__':sys.exit(main())
