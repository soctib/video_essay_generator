---
name: write-narration
description: Phase 2 of the video essay pipeline. Turns a research document and a gathered image pool into narration.json — the spoken script, in prosodic chunks. This is where the essay is actually written, and where its quality is decided. Use after gather-images, before generating audio.
---

# Write the narration

Input: `essays/<slug>/research.md`, `essays/<slug>/images/pool/*.json`, and the target
length in minutes.
Output: `essays/<slug>/outline.md` (pass 1) and `essays/<slug>/narration.json` (passes 2–3)

**This is not a summary of the research document.** It's an essay written from it. Compress,
omit, reorder, take a position. A research doc is written to be read; narration is written
to be heard, and read aloud verbatim it sounds like a briefing.

Budget ~150 words per minute. A 4-minute essay is ~600 words.

## Read the image pool first

**Read `pool/*.json` before writing a word.** The whole pipeline is built on images being an
*input* to authoring rather than an output of it — writing from the research document alone
throws that away, and produces narration that asks for pictures nobody has.

Work from the descriptions, not the images. Three things to take from them:

- **What can actually be shown.** Don't write a passage whose only illustration doesn't exist.
- **Specific detail to write toward.** The `details` field is why the gather phase looked at
  every image. "Both towers up, catwalks strung, no deck between them yet" is a sentence
  waiting to happen. This is what "front-load the concrete" means in practice.
- **Where the pool is thin.** Those are the passages that will need a hand-written SVG
  diagram, a chart from the research document's own numbers, or a typographic slide.

Occasionally an image is good enough to earn its own beat. The 1936 aerial dated one day
before cable spinning finished is a better opening for a construction passage than anything
written from the prose. Let that happen.

If you need to see something, open the 1200px file. To compare several, contact-sheet the
320px thumbs (`gather-images/contact_sheet.py`) rather than opening each one.

## Pass 1 — Shape

Decide the argument before writing prose. Produce a short outline: the beats, and one line
on what each does.

**Find the angle.** A chronology is not an essay. The research document usually contains a
thesis if you look — for the Golden Gate Bridge it's that the bridge is credited to the man
who promoted it rather than the man who designed it, which turns five facts into an argument
with an ending. Take a position where the material supports one.

Write it to `essays/<slug>/outline.md` and show it to the user before pass 2. It's thirty
seconds to read and it's the cheapest point to change direction.

**Record candidate images per beat, by id.** Not as a layout — that's phase 4's decision —
but as a record of what the prose was written against:

```markdown
## beat: credit
The bridge is credited to the man who promoted it, not the man who designed it.
Turns the piece from chronology into argument, and sets up the ending.

images: people-11 (Strauss statue, "THE MAN WHO BUILT THE BRIDGE" legible)
        people-04 (1937 dedication plaque, Ellis absent from it)
        people-22 (LoC drawing sheet, signature visible)
thin:   no free portrait of Ellis exists — the argument has to be carried by
        objects rather than faces
```

This is the one piece of authoring knowledge that otherwise evaporates. You will have read
the whole pool and formed opinions; phase 4 should not have to re-derive them and hope it
lands on the same photograph. The `thin` line is equally load-bearing — it's what tells
phase 4 to reach for a diagram, a chart or a typographic slide.

`narration.json` itself stays a flat list of `text` and `style`. Chunks and visuals are
decoupled in both directions, so a per-chunk image field would assert a relationship that
doesn't exist, and the audio script wants nothing but the words.

## Pass 2 — Write it continuously

Write the whole thing as continuous prose, not chunk by chunk. Flow across the essay is
easier to get right in one pass than to assemble from fragments; chunking comes after.

- **Break rhythm deliberately.** Vary sentence length hard. Fragments are fine.
- **Contractions and second person.** "You'd expect", not "one would expect".
- **Concrete first.** Names, dates, objects. Abstraction after, if at all.
- **Compress numbers for the ear.** `145,057 to 46,954` becomes "three to one". Precision
  that can't be held in the head is noise when spoken.
- **Never narrate a citation.** Sources go on screen, not into the voice.
- **No parenthetical asides.** They read fine and narrate terribly.
- **Nothing that isn't in the research document.** The tempting embellishment is usually a
  half-remembered detail from training data. If it isn't in the doc, it doesn't go in.
- **End on an object, not a summation.** "The drawings, in the Library of Congress, are
  signed by Charles Ellis" beats any sentence explaining what it means.

## Pass 3 — Chunk, then audit

**Chunk on breath.** Each TTS call starts with cold prosody — pitch and emphasis reset at
every boundary — so boundaries are audible. Put them where a narrator would actually pause,
never mid-thought. Chunks are not slides: one image can carry many chunks, and one chunk can
span a montage.

Keep chunks under ~70 words.

Then run the audit:

```bash
python3 .claude/skills/write-narration/audit_narration.py essays/<slug>/narration.json
```

It counts em dashes, negative parallelisms ("not just X, it's Y"), rule-of-three lists,
trailing "-ing" analysis clauses, known AI vocabulary, and sentence-length uniformity.
See `docs/ai-writing-signs.txt` for the field guide behind it.

**The audit is a floor, not a verdict.** It works on regexes and misses anything structural.
A three-part parallel spread across separate sentences — "credited to X. Designed by Y. Built
by Z." — passes it cleanly and is still the most obvious tell in the piece. Read the draft
again yourself, looking for:

- Rhetorical scaffolding: the pivot sentence, the reversal, the closer that lands too neatly.
- Every paragraph the same shape.
- Statements about significance, legacy, or what something "represents".
- Vague attribution — "was considered", "is regarded as". By whom?
- An ending that rises into uplift.

Fixing the countable tells while leaving the structural ones only makes the writing harder
to diagnose. Fix the writing.

## Format

A flat list of chunks. `text` is verbatim narration. `style` is optional and steers delivery
for that chunk — it's prepended to the TTS input as a direction line and is *not* spoken.
`beat` is an optional authoring aid that groups chunks for the deck; the audio script ignores it.

```json
[
  { "beat": "credit",
    "text": "In late 1931, Strauss dismissed him. He said Ellis was wasting time and money.",
    "style": "Flatter. Slower. State it plainly and do not lean on it." }
]
```

Use `style` sparingly — a handful of chunks, where delivery carries meaning the words don't.
Marking everything is the same as marking nothing.
