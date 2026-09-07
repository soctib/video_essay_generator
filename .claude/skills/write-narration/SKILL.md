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

Budget ~150 words per minute, and aim ~10% under target: a 4-minute essay is ~540 words,
not 600. The word count measures speech only, while the render adds a pause at every chunk
boundary, so a script that computes to exactly 4:00 runs over.

## Read the image pool first

**Read `pool/*.json` before writing a word.** The whole pipeline is built on images being an
*input* to authoring rather than an output of it — writing from the research document alone
throws that away, and produces narration that asks for pictures nobody has.

### What's in a pool file

`images/pool/<theme>.json` is a JSON array, one record per kept image:

| field | use |
|---|---|
| `id` / `file` | the id goes in the outline; the path is what the deck references |
| `depicts` | the composition — what the frame contains |
| `details` | the specific, narratable things. Written by someone who looked. |
| `visible_text` | text inside the image. Often carries dates, names, inscriptions. |
| `notes` | **the gatherer's warnings. Read every one.** They flag stand-ins, near-misses and things that must not be captioned as what they resemble — e.g. a modern net that is not the 1936 net, or a signing photograph not documented as bridge-related. Writing against one of these produces a confident false claim. |
| `license` | see below |
| `orientation` / `width` / `height` | portrait images are a constraint in a 16:9 deck |

### Reconcile the pool before writing

The pool may not be complete. Check, and report the gaps in the outline:

```bash
ls essays/<slug>/images/*.jpg | sed 's/.*\///; s/-[0-9]*\.jpg//' | sort -u   # themes with files
ls essays/<slug>/images/pool/*.json                                          # themes with descriptions
cat essays/<slug>/images/plan.md                                             # themes that were planned
```

A theme with files but no JSON is **invisible to you** — those images exist and cannot be
used, because nothing describes them. A theme in the plan with neither is a gather failure.
Either way, say so before writing rather than silently producing an essay that avoids a
third of its subject. Whether to write toward a missing theme anyway is the user's call.

### Licence

Some records are All Rights Reserved or `by-nc-nd`. For personal viewing that's fine, and
the deck is not distributed. Prefer freely-licensed images where the choice is even, note
in the outline when a beat leans on a restricted one, and treat no-derivatives images as
uncroppable.

### Reading the pool

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

If you need to see something, open its file. To compare several, build a contact sheet
rather than opening each one — it costs about 137 tokens per image instead of ~3,400:

```bash
python3 .claude/skills/gather-images/contact_sheet.py sheet.jpg IMG IMG IMG ...
```

Pools gathered before thumbnails were introduced have no `thumbs/` directory. The script
downscales whatever you give it, so point it at the full-size files instead.

## Pass 1 — Shape

Decide the argument before writing prose. Produce a short outline: the beats, and one line
on what each does.

**Find the angle yourself.** A chronology is not an essay. Research documents usually
contain a thesis if you look for one: a tension, an injustice, a thing that turned out other
than intended. Finding it is the job, and no worked example is given here on purpose — an
example thesis would just get adopted instead of the right one for this material.

**Test the angle against the pool before committing to it.** An argument the images cannot
illustrate is the wrong argument, however good it reads. Two candidate angles are common:
the one the research document emphasises, and the one the pool is richest in. When they
disagree, say so in the outline and let the user choose — that disagreement is worth
surfacing, not resolving silently.

Write it to `essays/<slug>/outline.md` and put it in front of the user before pass 2. It's
thirty seconds to read and it's the cheapest point to change direction.

If you're running unattended and can't pause, carry on into pass 2 — but lead your final
report with the angle you chose, the angle you rejected, and any gap you found, so the
decision is reviewable after the fact rather than buried.

**Record candidate images per beat, by id.** Not as a layout — that's phase 4's decision —
but as a record of what the prose was written against:

```markdown
## beat: <slug>
One or two lines: what this beat argues and what it sets up.

images: <theme>-NN (why this one — the specific thing visible in it)
        <theme>-NN (…)
thin:   what this beat needs and the pool does not have
```

**Use real ids, copied from the pool files.** Do not write ids from memory or pattern —
they look plausible and are wrong, and whoever reads the outline next will burn time
discovering that rather than assuming it.

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
- **Two sources, and only two: the research document and the image descriptions.** The pool
  is a citable source, not just a picture library — `visible_text` and `details` routinely
  carry facts the research doc lacks: what a plaque actually says, who is listed on it, what
  is and isn't in the frame. Those are often the best lines in the essay, because they are
  things the writer observed rather than read.
  What is banned is the third source: your own memory. The tempting embellishment is a
  half-remembered detail from training data, and it is usually plausible, specific, and
  wrong. If it is in neither the research document nor a description, it does not go in.
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
