# Publication Surface Scrub

Internal IDs, user-interface choices and audit artifacts describe how the paper
was produced. They do not belong in the research article. Apply this boundary
when drafting, assembling another layout and reviewing a revision, including
the title area, abstract, running headers, captions, tables, declarations and
scientific supplements. Do not copy task status or a continuation note into a
template's author note, draft-status block or abstract.

Do not generate standalone "Draft status", "Review status", "Delivery status"
or equivalent explanatory paragraphs in the article, even when the underlying
status is true. Keep that communication in the delivery notes. Removing the
heading while leaving its production narration in ordinary prose does not fix it.

Use saved choices to select the actual figures, not to narrate that the user
confirmed them. Keep figure adoption, pending independent review, visual-check
completion, package readiness and download status in task notes or the local
work-package README. A new layout must not inherit an old production-status
paragraph merely because it preserves the preceding manuscript's text.

Remove bracketed claim/evidence/source/numeric/method/outcome/result tags,
workflow filenames and gate narration from reader-facing prose. Repair the
source and regenerate only the outputs authorized by the current request;
an audit-only request does not authorize replacing the user's paper.

Preserve the scientific boundary in natural prose. Do not delete a real
limitation, author-input requirement, or disclosed uncertainty merely because
it originated in an audit.

Separate a mixed paragraph by its meaning. For example, move "the user confirmed
these figures" to work notes, while retaining an unresolved measurement unit or
study-setting limitation where it affects interpretation. Do not invent author,
ethics or recruitment facts. Use concise academic wording or an explicit author
placeholder when needed; a local draft is not automatically submission-ready.
Reproducibility methods, participant choices in an HCI study and a systematic
review's screening process remain scientific content. Do not remove them merely
because they mention a user, workflow or review. Remove irrelevant production
narration, while preserving factual disclosures requested by the user or required
by the applicable venue, in the location that requirement specifies. Do not
invent a disclosure requirement or silently move a required manuscript disclosure
into private metadata. State unexposed model or tool details as unknown rather
than guessing them. These distinctions do not authorize submission or upload.

Also remove defensive audit voice. The final paper should not repeatedly say
“within the supplied materials,” “user-authoritative,” “the evidence ledger
shows,” or stack `may/might/potentially` around an observed result. Follow
`references/assertive-scientific-writing.md`: state supported findings directly
and keep one clear qualification at the point where the inference changes.

```bash
python scripts/publication_surface_check.py --source "<current-manuscript.tex>" --source "<current-manuscript.pdf>" --json
```

Pass the actual manuscript paths, including requested DOCX/Markdown outputs;
do not rely on the historical output-directory default. The checker reports
located candidates and extraction failures; it does not rewrite the paper or
prove that every paraphrase is absent. Read the full current article and inspect
all rendered pages independently, including text inside figure images that a
text extractor cannot see. Resolve each finding by meaning, preserve legitimate
scientific content, and recheck the affected source and output. Keep work notes
and review reports out of this manuscript-only scan.
