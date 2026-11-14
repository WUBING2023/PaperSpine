"""Render a trusted Matplotlib producer and report text geometry for review.

This reruns the specified producer with its normal file side effects. It is a
diagnostic, not a visual/scientific approval or an execution sandbox.
"""
from pathlib import Path
import argparse
import contextlib
import io
import json
import runpy
import sys
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
from matplotlib.text import Text
from matplotlib.collections import PathCollection
import numpy as np

def inspect(fig):
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    width,height=fig.bbox.width,fig.bbox.height
    objects=[]
    for text in fig.findobj(Text):
        label=text.get_text().strip()
        if not label or not text.get_visible() or (text.axes is not None and not text.axes.get_visible()):
            continue
        try:
            b=text.get_window_extent(renderer)
        except (ValueError,RuntimeError):
            continue
        if b.width<=0 or b.height<=0: continue
        objects.append({'text':label[:100],'bounds_pt':[round(v*72/fig.dpi,2) for v in b.extents],
                        'font_pt':text.get_fontsize(),'box':b,'owner':id(text.axes)})
    outside=[];overlap=[]
    for obj in objects:
        b=obj['box']
        if b.x0 < -1 or b.y0 < -1 or b.x1 > width+1 or b.y1 > height+1:
            outside.append({k:v for k,v in obj.items() if k not in ('box','owner')})
    # Axis-aligned boxes of rotated labels can overlap without glyph collisions.
    # Report candidates; leave classification to actual-image inspection.
    for i,a in enumerate(objects):
        for b in objects[i+1:]:
            if a['text']==b['text'] and a['bounds_pt']==b['bounds_pt']: continue
            x=max(0,min(a['box'].x1,b['box'].x1)-max(a['box'].x0,b['box'].x0))
            y=max(0,min(a['box'].y1,b['box'].y1)-max(a['box'].y0,b['box'].y0))
            small=min(a['box'].width*a['box'].height,b['box'].width*b['box'].height)
            if small>0 and x*y/small>0.15 and min(x,y)*72/fig.dpi>1:
                overlap.append({'first':a['text'],'second':b['text'],'smaller_box_fraction':round(x*y/small,3),
                                'different_axes':a['owner']!=b['owner']})
    scatter=[]
    for axis_index,ax in enumerate(fig.axes):
        if not ax.get_visible(): continue
        for collection_index,col in enumerate(ax.collections):
            if not isinstance(col,PathCollection) or not col.get_visible(): continue
            offsets=np.ma.asarray(col.get_offsets())
            mask=np.ma.getmaskarray(offsets)
            points=[];counts={k:0 for k in ('inside_axes','outside_axes','masked','nonfinite','transform_nonfinite','transform_error')}
            finite_indices=[i for i,o in enumerate(offsets)
                            if not np.any(mask[i]) and np.all(np.isfinite(o))]
            transformed={};transform_error=None
            if finite_indices:
                try:
                    batch=np.asarray(offsets[finite_indices],dtype=float).reshape(-1,2)
                    display_batch=np.asarray(col.get_offset_transform().transform(batch),dtype=float)
                    if display_batch.shape != batch.shape:
                        raise ValueError('offset transform returned unexpected shape')
                    transformed=dict(zip(finite_indices,display_batch))
                except Exception as exc:
                    transform_error={'type':type(exc).__name__,'message':str(exc)[:400]}
            for index,offset in enumerate(offsets):
                record={'index':index}
                if np.any(mask[index]):
                    status='masked'
                elif not np.all(np.isfinite(offset)):
                    status='nonfinite'
                else:
                    xy=np.asarray(offset,dtype=float)
                    record['offset']=xy.tolist()
                    display=transformed.get(index)
                    if transform_error is not None:
                        status='transform_error';record['diagnostic_error']=transform_error
                    elif not np.all(np.isfinite(display)):
                        status='transform_nonfinite'
                    else:
                        record['display_pt']=(display*72/fig.dpi).tolist()
                        status='inside_axes' if ax.bbox.contains(*display) else 'outside_axes'
                record['status']=status;counts[status]+=1;points.append(record)
            scatter.append({'axes_index':axis_index,'collection_index':collection_index,
                            'offset_count':len(offsets),'counts':counts,'points':points,
                            'axes_bounds_pt':(ax.bbox.extents*72/fig.dpi).tolist(),
                            'clip_on':bool(col.get_clip_on())})
    return {'scatter_offset_candidates':scatter,'width_mm':round(fig.get_figwidth()*25.4,3),'height_mm':round(fig.get_figheight()*25.4,3),
            'text_count':len(objects),'min_text_pt':min((o['font_pt'] for o in objects),default=None),
            'outside_canvas':outside,'overlap_candidates':overlap,
            'limitations':'Bounding boxes can produce false positives for rotated labels and miss line-over-text, data errors, semantic errors and aesthetics. Scatter checks cover visible PathCollection offset centers against rectangular axes bounds, not marker extents, custom clip paths, occlusion, lines or bars. Transform failures remain explicit unverified diagnostics and do not stop normal exports; pre-save geometry may differ from final export DPI/cropping. Outside centers may be intentional zoom or unclipped annotations. Input counts do not establish visible data; reconcile full source scope, exclusions and actual pixels. Inspect actual rendered pixels and verify numbers/caption separately.'}

def run(script,report):
    script=Path(script).resolve();report=Path(report).resolve()
    if not script.is_file(): raise FileNotFoundError(script)
    observed={};original=Figure.savefig
    def savefig(fig,*args,**kwargs):
        observed[id(fig)]=inspect(fig)
        return original(fig,*args,**kwargs)
    Figure.savefig=savefig
    output=io.StringIO()
    error=None
    try:
        with contextlib.redirect_stdout(output):
            runpy.run_path(str(script),run_name='__main__')
    except Exception as exc:
        error={'type':type(exc).__name__,'message':str(exc)[:400]}
    finally:
        Figure.savefig=original
    result={'schema':'figure-layout-probe/1','producer':str(script),'producer_error':error,'figures':list(observed.values()),
            'producer_stdout_tail':output.getvalue()[-2000:], 'quality_approval':False}
    report.parent.mkdir(parents=True,exist_ok=True)
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    summary={'producer_error':error,'figures':[{'outside_count':len(x['outside_canvas']),
                'outside_examples':x['outside_canvas'][:4],'overlap_count':len(x['overlap_candidates']),
                'overlap_examples':x['overlap_candidates'][:4]} for x in observed.values()],
                'full_report':str(report),'quality_approval':False}
    print(json.dumps(summary,ensure_ascii=False))
    return 1 if error else 0

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--script',required=True);p.add_argument('--report',required=True)
    args=p.parse_args()
    sys.exit(run(args.script,args.report))
