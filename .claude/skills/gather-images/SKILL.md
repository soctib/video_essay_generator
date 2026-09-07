---
name: gather-images
description: Phase 1 of the video essay pipeline. Reads a research document and builds a pool of real, verified images with written descriptions, so narration can later be authored against what actually exists rather than against what we hoped would exist. Use when starting a new essay, or when an existing pool needs topping up.
---

# Gather images

Build an image pool from a research document. **Images are an input to authoring, not an
output of it** — the narration gets written against this pool, so a thin or badly described
pool caps the quality of everything downstream.

Input: `essays/<slug>/research.md` **and the target length in minutes**
Output: `essays/<slug>/images/` (files) and `essays/<slug>/images/pool/*.json` (descriptions)

**Ask for the target length if it wasn't given.** Do not infer it from the research
document — a research doc is written at whatever length the research took, and a
five-minute essay and a twenty-minute essay can share one. Getting this wrong is expensive:
scoping a five-slide piece off a full-length two-part document produced nine themes and 270
images.

## Step 1 — Build a search plan

Read the research document and break it into **visual themes**, scaled to the target
length — roughly one theme per 2 minutes, floor of 2 and ceiling of 10. A 5-minute essay
gets 2–3 themes; a 20-minute one gets closer to 10. Don't pad to hit a number, and don't
cover material the essay won't reach.

A theme is a stretch of subject matter that wants its own imagery, not a section heading
copied across. A full-length Golden Gate Bridge essay would run roughly: origins and the
ferries; political opposition and financing; the people; construction and engineering;
labour and safety; opening day; the bridge as icon; present-day issues. A short one might
collapse all of that into construction, opening, and icon.

For each theme write:
- 2–4 **specific** queries. "Bessemer converter Sheffield 1895" is a query. "An image
  representing industrialisation" is a failure.
- Which sources to try, in order (see the recipes below).

Write the plan to `essays/<slug>/images/plan.md` before dispatching anything. It is the
record of what was looked for, which matters when something turns out to be missing.

## Step 2 — Dispatch one subagent per theme

**Run the theme subagents on a cheap model** (Haiku). Their job is "is this the right
subject" plus a written description — not analysis. Running them on the largest model is
what exhausted a session limit on the first attempt.

Run at most **4 concurrently**. Each handles one theme end to end and writes
`essays/<slug>/images/pool/<theme>.json`. **One file per subagent** — never have two agents
writing the same file.

Only the descriptions come back to the main context. Images are enormously expensive in
context and there is no reason for them to arrive here.

Give each subagent: the theme, its queries, the relevant excerpt of the research document
(not the whole thing), the output path, and the two specs below verbatim.

## The subagent's job

**Never look at a full-resolution image.** The pipeline is deliberately cheap-first: each
stage costs more than the last, so throw work away as early as possible.

```
search  →  filter on metadata  →  contact sheet  →  describe survivors  →  fetch full-res
 free         free, no tokens      ~137 tok/img     one call each        no tokens
```

Run at a cheap model. This is "is that the right subject", not analysis.

### Stage 1 — Metadata filter (free)

The search APIs return dimensions, mime, licence and **date** before anything is downloaded.
Reject on those first, at zero token cost:

- **Long edge under 800px.** From the API response, not after downloading.
- **Outside the theme's date range.** The single highest-value filter. A construction theme
  rejects anything dated after 1937 outright — which is exactly the failure that motivated
  all of this, since "Golden Gate Bridge under construction" returns photographs taken in
  2022. Wikimedia carries this in `extmetadata.DateTimeOriginal`, Flickr in `datetaken`.
- **Duplicates**, by Commons page id or Flickr photo id.

Write the date range into the search plan per theme. Themes with no meaningful range
(icon views, present day) simply skip this filter.

### Stage 2 — Contact-sheet triage (~137 tokens/image)

Fetch the survivors as **320px thumbnails** — `iiurlwidth=320` on Wikimedia, `url_s`/`url_q`
on Flickr — into `images/.candidates/`. Then tile them:

```bash
python3 .claude/skills/gather-images/contact_sheet.py \
    sheet.jpg --dir essays/<slug>/images/.candidates
```

Look at the sheet — **one vision call for sixteen images** — and shortlist by label. This is
plenty to tell a genuine 1930s build photograph from an architectural rendering or a modern
tourist shot.

### Stage 3 — Describe the shortlist

Fetch shortlisted images at ~1200px and look at them individually to write the description.
Everything not shortlisted is deleted from `.candidates/` unlooked-at.

**There is no full-resolution stage.** The 1200px copy is the deck asset, the file you
describe from, and the copy a later pass re-examines. One file, three uses — the 8000px
original is never fetched.

**Keep the 320px triage thumbnail** in `images/thumbs/<id>.jpg`. It costs nothing (it's
already on disk from Stage 2) and it lets the authoring pass build contact sheets to
compare candidates at ~137 tokens each, instead of reopening full images.

So two resolutions survive per keeper, for two different questions:

- *"Which of these five works best here?"* — comparison. Contact-sheet the thumbs.
- *"What does that sign actually say?"* — detail. Open the 1200px copy.

Neither requires re-fetching anything.

### Stage 4 — Stop early

Stop searching a theme once it has **enough**: roughly 6–10 keepers for a short essay,
12–20 for a long one. Then stop — don't work through remaining queries for completeness.

This is a stopping rule, not a quality target: it never makes you *reject* anything, so the
triage bar below stays exactly as loose. It only makes you stop looking.

Because you stop early, **source order matters** — work best-first (Wikipedia article →
Commons category → Flickr Commons → Flickr → Internet Archive) so that stopping early means
stopping on the good material rather than on whatever answered first.

If a theme can't reach its number, stop anyway and report it as thin. That's a finding.

### Where files go


```
essays/<slug>/
  images/
    .candidates/            scratch — 320px thumbs; emptied when done
    construction-01.jpg     keepers at ~1200px, named <theme>-NN
    opening-day-01.jpg
    thumbs/
      construction-01.jpg   320px, kept for cheap re-comparison
    pool/
      construction.json     one file per theme, written by one subagent
```

Binaries are gitignored; `pool/*.json` and `plan.md` are tracked.

Download every candidate into `images/.candidates/` under any temporary name, look at it
there, and only then decide. A keeper gets **moved** to `images/<theme>-NN.<ext>` — theme
slug, zero-padded counter, original extension. Everything left in `.candidates/` is deleted
before you finish.

The `id` in the JSON is the filename without extension (`construction-04`), and `file` is
the path **relative to the essay directory** (`images/construction-04.jpg`) so the deck can
reference it directly.

Your theme owns its filename prefix, so concurrent subagents never collide.

Looking at the image is the entire point. Metadata lies by omission: a file whose complete
description was `Golden Gate Bridge -- 2022 -- 3023 (bw)` turned out to be a strong
composition of Fort Point in fog with the flag flying. Nothing but looking would have found
that.

### Triage bar — reject loosely

You do not know what the essay will argue. Reject **only** objective junk:

- Not the subject at all (a different bridge, a different person of the same name)
- Under 800px on the long edge
- Corrupt, or a stock-photo placeholder
- A near-duplicate of something already kept — keep the better one

Watermarks are fine. This is for personal viewing and a watermark costs nothing.

**Do not** reject on aesthetic or editorial grounds. "Not very interesting" and "probably
won't be used" are not your calls; the authoring pass has essay context you lack. A pool
with some duds is recoverable. A pool that is too thin is not.

**The bar never tightens.** Everything you actually look at and that passes gets kept. The
stopping rule in Stage 4 governs when you stop *searching*, never how harshly you judge —
if it were allowed to leak into the bar it would reintroduce exactly the editorial
judgement you don't have the context to make.

If a theme comes up short, keep what you have and report it as thin. That's a finding the
authoring pass needs, not a failure to hide — it's the signal to reach for a hand-written
SVG diagram, a chart, or a typographic slide instead of a photograph.

### Description spec

This is the interface to the authoring pass, which will work from your words without
seeing the image. A vague description is as useless as a bad image.

```json
{
  "id": "construction-04",
  "file": "images/construction-04.jpg",
  "source": "commons-category",
  "source_url": "https://commons.wikimedia.org/wiki/File:...",
  "license": "Public domain",
  "attribution": "US Army Air Corps",
  "date": "1936-05-19",
  "width": 2594, "height": 2016, "orientation": "landscape",
  "depicts": "Aerial view looking north across the strait. Both towers complete, catwalks strung between them, cable spinning underway. The Presidio and Fort Point in the foreground; the Marin Headlands behind.",
  "details": "The deck does not exist yet — there is nothing between the towers but the catwalk and the first cable strands. Barracks and a pier are visible bottom right. Bare, treeless hills.",
  "visible_text": "Caption burned into lower left: (0154-32-I-15)(5-19-36-12N)(12-1500) GOLDEN GATE BRIDGE, CALIF.",
  "notes": "Dated one day before cable spinning completed on 20 May 1936."
}
```

- **`depicts`** — what is literally in the frame, enough to write narration from blind.
- **`details`** — specific things a narrator could point at. The purpose of having looked.
  "The men are standing well back from the spray", not "an industrial scene".
- **`visible_text`** — any text burned into the image. Often carries dates and provenance.
- **`orientation`** — the deck is 16:9. Portrait images are a real constraint and authoring
  needs to know in advance.
- **`license` / `attribution` / `source_url`** — captured now or lost forever. The deck
  shows per-image credits, and a bad pick has to be traceable.

## Source recipes

All verified working. Set a real `User-Agent` with contact info on Wikimedia requests —
10 req/min without it, 200 with.

**Wikipedia article images** — best default for a known subject. Curated by editors, one call:

```
https://en.wikipedia.org/w/api.php?format=json&action=query
  &titles=<ARTICLE>&generator=images&gimlimit=50
  &prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1600
```

**Commons categories** — best for a specific historical subtopic. Two calls:

```
1. ...&list=search&srnamespace=14&srsearch=<TOPIC>        # find categories
2. ...&generator=categorymembers&gcmtitle=<CATEGORY>&gcmtype=file&gcmlimit=50
     &prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1600
```

**Flickr** — the only source that covers *recent* subjects. `is_commons=1` for institutional
archives; drop it for anything from the last few years.

```
https://api.flickr.com/services/rest/?format=json&nojsoncallback=1
  &method=flickr.photos.search&api_key=$FLICKR_CONSUMER_KEY
  &text=<QUERY>&is_commons=1&per_page=20
  &extras=url_l,url_o,license,owner_name,date_taken
```

**Internet Archive** — maps and ephemera.

```
https://archive.org/advancedsearch.php?q=<QUERY>+AND+mediatype:image&output=json&rows=20
```

`iiurlwidth` and Flickr's `url_l` return **server-side thumbnails**, so the 8000px original
is never transferred. Do not download originals and resize locally.

### Do not use

- **Full-text search as the primary strategy.** It silently drops qualifiers. "Golden Gate
  Bridge under construction" returns photographs taken in 2022; "…construction 1935" returns
  a bridge in Lisbon. Use it only as a fallback when no category or article exists.
- **Library of Congress.** 403s on every endpoint and User-Agent.
- **Openverse.** Thin and small — 13 results for a query Commons answered with 10 good ones.

## Step 3 — Report

Merge the per-theme files and report to the user: how many kept per theme, and — more
importantly — **which themes came up empty or thin**. That list is what tells the authoring
pass where it will need to reach for a hand-written SVG diagram, a chart from the research
document's own numbers, or a typographic slide instead of a photograph.

Do not generate images in this phase. This pass collects what exists.
