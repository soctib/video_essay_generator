# Video Essay Generator — Plan

A local pipeline that turns a research document into a self-running, narrated slideshow
that plays in a browser. No video encoding at any stage. Personal use only.

The output is a folder: one `index.html`, a stylesheet, audio files, images. Open it and
it plays itself.

This supersedes the earlier build plan. The main structural change is that **images are
gathered first and the narration is written against them**, rather than the narration
being written first and images fetched to match it.

---

## 1. Pipeline

```
research.md
    │
    ▼  phase 1 — gather          subagents: search, download, view, triage, describe
images/ + descriptions
    │
    ▼  phase 2 — author          main context, working from descriptions
narration.json
    │
    ├──▼  phase 3 — audio        script, mechanical
    │   audio/NN.mp3
    │
    └──▼  phase 4 — deck         AI, creative
        index.html
                ▲
      music/library.json         curated once by hand, reused across essays
```

Phases 3 and 4 both consume `narration.json` and are independent of each other. One is a
script, the other is not, and that split is deliberate — per-essay design is the point,
so it can't be templated away.

---

## 2. Phase 1 — gather

Driven by `research.md`. This pass collects **what already exists**; generated charts and
collages are a later, separate round.

Runs in subagents, for two reasons: images are enormously expensive in context, and
something has to actually *look* at them to judge them. The subagent downloads, views,
discards, and writes a description. Only the descriptions come back.

Each kept image needs:

- **What is literally depicted** — enough that narration can be written from the
  description alone.
- **Specific visual detail worth narrating.** The point of seeing the image is to be able
  to write "the men are standing well back from the spray" instead of "an industrial
  scene."
- **Any text visible in the image.**
- **Resolution and orientation.** Portrait images in a 16:9 deck are a real constraint and
  authoring needs to know beforehand.
- **Source URL and licence**, captured at download time. Unrecoverable later, and the deck
  shows per-image credits.

**Filter loosely.** The subagent doesn't know what the essay will argue, so it rejects only
objective junk: wrong subject entirely, watermarked, too small, corrupt. Editorial and
aesthetic calls belong to phase 2, which has context the subagent lacks. A pool that is too
thin can't be recovered at that point; a pool with some duds can.

### Retrieval — measured against the live APIs

**Use Commons categories, not text search.** This is the single most important finding in
phase 1. Full-text search silently ignores qualifiers:

- `"Golden Gate Bridge construction 1935"` → top hit is the **25 de Abril Bridge in
  Lisbon**. Wrong continent.
- `"Golden Gate Bridge under construction"` → six results, **all photographed in 2022**.
  The words "under construction" did nothing.
- `Category:Construction of the Golden Gate Bridge` → **10 of 10** genuinely
  construction-era, dated 1933–1936, all public domain.

So retrieval is two calls, both trivial:

1. `list=search&srnamespace=14` — find candidate categories for the topic.
2. `generator=categorymembers&gcmtype=file&prop=imageinfo` — pull the files.

Text search is the fallback for when no good category exists, not the default.

**One call returns everything.** `prop=imageinfo&iiprop=url|size|mime|extmetadata` with
`iiurlwidth=N` gives the full URL, a **server-side thumbnail at width N**, dimensions, mime,
licence and attribution together. No second lookup, and no local downscaling step — asking
for `iiurlwidth=1200` means the 8000px original is never transferred at all. `sips` is
unnecessary.

**Set a `User-Agent` with contact info.** 10 req/min without, 200 with (2026 limits, real
and enforced).

### Source status

| Source | State |
|---|---|
| Wikimedia Commons | **Primary for historical.** Keyless, rich metadata, categories give high precision. |
| Wikipedia article images | **Best default for a known subject.** One call, 27 usable rasters for the bridge, curated by editors — opening day, cable cross-section, a 1937 rivet, the anniversary plaque. No query tuning needed. |
| Flickr | **Fills both gaps.** `is_commons=1` gives institutional archives (15 precise historical hits). And crucially, plain Flickr covers *recent* subjects: the 2024 suicide-deterrent net, which Commons has nothing at all for, returns two on-topic photographs from July 2024. Key already held. |
| Internet Archive | Keyless, 115 results, decent breadth. Maps and ephemera. |
| Commons / Flickr text search | Unusable alone — both silently drop qualifiers. "under construction" returned 2022 photos; Flickr's CC search returned the Noyo River Bridge and the Embassy of Argentina. |
| Openverse | Thin: 13 results, most under 500px, mostly `by-nc-nd`, one in Galway. |
| Library of Congress | **403** on every endpoint and User-Agent tried. HAER is unavailable, which is a real loss for US infrastructure. |
| DuckDuckGo / headless browser | Not needed. Flickr covered the recent tier we thought required it. Revisit only on a concrete failure. |
| Brave / Google CSE | Dead ends. Brave killed its free tier in Feb 2026 and bills a card on file; Google's Custom Search JSON API is closed to new customers. |

Downloading locally matches Wikimedia and Pixabay's terms but conflicts with Unsplash's
requirement to serve from their CDN. Moot for personal use, but Unsplash is the odd one out
if one consistent path is ever wanted.

### Scripting

Less than expected. The triage step needs no code — the subagent downloads a file and reads
it; vision is the agent looking at a local image. The two Wikimedia calls are simple enough
to issue directly. A thin helper normalising `(query, source) → [{url, thumb, dims, licence,
attribution}]` is worth having once a second source is added, but it's tens of lines, not a
component.

### Generated imagery — the third tier

For subjects where no photograph exists, the deck being HTML means a slide need not be a
photograph at all. Three distinct things, and they want different tools:

- **Diagrams: hand-write the SVG.** Do not generate them. A generated diagram bakes its
  text in at fixed resolution — it can't match the essay's typography, respond to theme, or
  scale. Written SVG is a few KB, infinitely scalable, and every label is styleable. Tested:
  Gemini produces a genuinely good labelled bridge cross-section, and it is still the wrong
  artefact for this pipeline.
- **Illustration and texture: generate.** Where precision doesn't matter and hand-authoring
  is impractical. 52 image-output models are on the existing OpenRouter account — no new
  signup, priced per image token.
- **Charts: from the research document's own numbers.** Toll history, traffic volume, cost
  breakdown. Inline SVG or a chart library, live in the DOM.

**ZDR constraint:** the account has zero-data-retention enabled, which excludes providers
that don't offer it — Recraft and Flux both fail with *"ZDR violation (account settings)"*.
Google and OpenAI image models work. Consequence: Recraft's **vector** models are
unavailable, so whether they emit real SVG is untested. Configurable at
`openrouter.ai/settings/privacy`, but it's a deliberate privacy choice, not an oversight.

**The line:** nothing generated may read as evidence. A diagram of how a suspension bridge
works is fine. A generated photograph of the 1937 opening is a fabrication, and personal use
doesn't change that — it makes the output untrustworthy to your own future self.

---

## 3. Phase 2 — author

Main context, working from the image descriptions rather than the images themselves,
pulling up specific ones when a closer look is needed. That's what keeps a hundred-image
pool tractable.

Output is `narration.json`: an ordered list of chunks.

```json
[
  { "text": "In 1981, a journalist at the Washington Post drew a map that ignored every border on the continent." },
  { "text": "Not one state line survived.", "style": "flatter, slower" }
]
```

`text` is verbatim narration. `voice` and `style` are optional per-chunk overrides.

**Chunks are prosodic units, not slides.** Each TTS call starts with cold prosody — pitch
and emphasis reset at every boundary — so boundaries are audible and have to fall where a
narrator would actually breathe. They're authored, not auto-split on sentence count.

Chunks and visuals are decoupled in both directions: five minutes on a single image is many
chunks, and a fast montage is several images inside one chunk. Nothing in the JSON refers
to images.

Why JSON and not markdown: chunks carry optional metadata, so the shape is a list of
objects. It also stores text verbatim through one well-defined encoding layer, which
matters for something being fed to a speech API.

---

## 4. Phase 3 — audio

Small Python script. OpenRouter `POST /api/v1/audio/speech`, OpenAI-compatible in shape,
returns a raw byte stream.

Model: `google/gemini-3.1-flash-tts-preview`, voice `Charon`. 18 speech models are on the
roster; free tiers exist (`deepgram/flux-tts:free`, `fish-audio/s2.1-pro-free:free`) and
`hexgrad/kokoro-82m` is cheap enough to be free in practice, which makes iteration costless.

**Measured against the live API, not from documentation.** The generic OpenRouter TTS
guidance is written for OpenAI's speech models, which are not on this roster, and it is
actively wrong for Gemini:

- **Gemini accepts `pcm` only.** Requesting `mp3` returns a 400: *"Gemini TTS only supports
  response_format=\"pcm\"."* Output is raw s16le, 24 kHz, mono. Converting with ffmpeg is
  therefore a required step, not an optional one:
  `ffmpeg -f s16le -ar 24000 -ac 1 -i in.pcm out.mp3`
- **Style steering is a prefix, not a parameter — the reverse of the documented advice.**
  Prepending a direction line to `input` works, and works hard: against a 10.08s baseline,
  "speak extremely slowly, solemnly, with long pauses" gave 24.08s and "speak very fast,
  breathless" gave 6.76s. A 3.5× range.
- **The `instructions` parameter is silently ignored.** Same directions passed that way
  produced 10.16s and 10.00s — baseline, no error, no effect. This is the dangerous failure
  mode: per-chunk style would have appeared to work and done nothing.
- **The direction is not narrated.** Transcribing the steered audio returns the narration
  verbatim with no trace of the direction. The original worry was unfounded — for this
  model, with the direction on its own line before the text.
- **Generation is non-deterministic.** Identical requests differ (464,640 vs 472,320 bytes,
  ~1.6% spread). Steering effects have to clear that band to mean anything; the ones above
  clear it by an order of magnitude.
- **Discover the roster** via `GET /api/v1/models?output_modalities=speech`, which also
  returns `supported_voices` per model. Don't hardcode.
- German is well covered if it comes into scope — `de-DE-Klaus:MAI-Voice-2` and seven
  Aura-2 German voices. Gemini's voices are not language-tagged.

Per-model variation is the real lesson: format support and steering mechanism both differ
by provider. Anything learned here applies to Gemini and should be re-tested if the model
changes.

Output is `audio/01.mp3`, `audio/02.mp3`, … indexed by position in `narration.json`. Index
naming is predictable from the JSON alone, so phase 4 can write `<audio src>` references
without waiting for the audio to exist.

**No cache.** Regeneration is always intentional and always scoped — whoever edited the
JSON knows which chunks changed, and there's no listen-and-re-roll loop because the model
can't judge a take. The script takes "generate these chunks", not "build the essay". A
file-exists check earns its place only for resuming a batch that died partway.

---

## 5. Music

Background music, assigned per slide, usually unobtrusive and occasionally not.

**Music does not need per-essay sourcing.** Images must be topic-specific — that's the
entire reason phase 1 exists. Music isn't. A dozen or two tracks covering a few moods get
reused across every essay, so this is a one-time curation job, not a pipeline stage.

**Curated by hand, not generated.** Google Lyria is on the OpenRouter account and would work,
but human-made music is preferred and manual curation is genuinely the better method here:
selection has to be made by ear, which the model cannot do. Its picks would be guesses from
text descriptions. An hour spent choosing twenty good tracks pays out permanently.

Sources: YouTube's Audio Library (no API — download by hand from Studio), Incompetech,
Musopen, and the Internet Archive, which is already proven keyless from phase 1 testing and
holds a lot of public-domain classical and 78rpm material.

### `music/library.json`

Written once, by hand, at curation time:

```json
{ "id": "sparse-02", "file": "music/sparse-02.mp3",
  "mood": "quiet, unresolved", "intensity": 2, "tempo": "slow",
  "duration": 184, "loops_cleanly": true,
  "credit": "Kevin MacLeod — Incompetech (CC BY)",
  "source_url": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/...",
  "refetchable": true }
```

### The audio files are not checked in

**The public repo is where "personal use" stops being true.** Playing a deck locally is
personal use; committing the tracks to a public GitHub repository is redistribution,
whatever the intent. The same applies to the gathered images, which is the real reason those
are gitignored — repo size is the lesser argument.

So `library.json` is tracked and the audio is not, which makes re-fetchability the thing to
design for. Record `source_url` per track and be honest about `refetchable`:

- **Stable**: Internet Archive (permanent identifiers), Incompetech, Musopen. A URL here
  genuinely brings the file back.
- **Not stable**: YouTube's Audio Library has no permalinks — tracks are downloaded by hand
  from Studio and can only be found again by title. Mark these `refetchable: false` and
  record the exact title.

The library is a local asset, like a font collection — `library.json` is the record of what
it should contain, not a manifest that can rebuild it unattended. Back the audio up
separately from git.

`loops_cleanly` is worth recording while listening; it's far easier to notice then than to
detect later. The judgement stays with the curator — assignment is then mechanical: match a
slide's tone to a tag and write `data-music="sparse-02"` on the slide div.

### Runtime

**Music is a separate timeline from narration.** Slides own narration; music spans *runs* of
slides. Assignment is still per-slide, but the rule at a transition is: if the incoming
slide names the same track, do nothing. Different track, crossfade. Same-track continuity
falls out for free, and a slide with no `data-music` fades the bed out.

This splits the audio implementation:

- **Narration stays plain `<audio>`.** `ended` drives slide advance, exactly as before.
- **Music uses Web Audio.** `<audio loop>` is *not* gapless — MP3 encoder padding makes a
  short bed click audibly every loop. An `AudioBufferSourceNode` with `loop = true` is
  genuinely gapless, and it comes with a `GainNode`.

That gain node then gives three things from one object: independent music volume (a real
control, since a bed is easily too loud), crossfades between tracks, and **ducking** —
ramping music down while a narration chunk plays and back up in the gaps, which is what
makes a bed sit under speech instead of fighting it.

Roughly 60–80 lines of music controller, and it lives in the shared engine, so it's written
once regardless of how many essays follow.

---

## 6. Phase 4 — deck

A template supplies the **engine**; the AI writes the **look**.

Frozen in the template: playback logic, slide windowing, transition mechanics, keyboard
handling. Written fresh per essay: the stylesheet and the markup inside each slide. If the
whole thing is templated, every essay looks identical, which is the failure mode worth
avoiding.

Single `index.html`. Each slide is a top-level `div`.

**Advance on `audio.ended`.** No timing track, no drift, and a failed call costs one retry
instead of the whole deck. Nothing needs durations at build time — if visuals have to be
spread across a long chunk, JS reads `audio.duration` at runtime.

Runtime mechanics that matter:

- **Sliding window.** Only previous / current / next are `display: block`. Everything else
  is `display: none`, so a hundred images are never live at once.
- **Promote on window entry, not at transition time.** You can't animate out of
  `display: none` — the element isn't rendered, so opacity never fires and you get a hard
  cut. By the time a slide is the incoming one it's already rendered at `opacity: 0`.
- **Demote after the transition completes**, not when it starts, or you yank the outgoing
  slide mid-fade.
- Slides stack absolutely positioned in one grid cell; crossfade via `opacity` +
  `visibility`.
- `preload="none"` on every `<audio>`, with slide *n+1* preloaded explicitly. The default
  opens a connection per element on load.
- **Click-to-start title card.** Browsers block programmatic audio without a user gesture.
- Slow Ken Burns on stills, alternating direction. `prefers-reduced-motion` disables it.
- Per-image credit line.
- Keyboard: space, ←/→, F.

---

## 7. Rejected, and why

Recorded so they don't creep back in:

- **`essay.md` with per-beat YAML** (visuals, transitions, duration hints). That format
  existed to feed a deterministic builder. There is no deterministic builder — the AI
  writes the HTML — so the format has no consumer.
- **`manifest.json` as a build/runtime contract.** Same reason: it's a contract between two
  halves that are now the same author.
- **ffprobe durations written at build time.** `audio.ended` and runtime `audio.duration`
  cover it.
- **A TTS cache subsystem.** See phase 3.
- **Generated background music.** Lyria is available and would work, but music selection is
  a by-ear judgement the model can't make, and a curated library is reused across every
  essay rather than rebuilt per essay.
- **Deriving image queries from finished narration.** This is the inversion the whole plan
  turns on. Queries written from committed prose return confident garbage, and the text has
  already promised to describe something that may not exist.

---

## 8. Open

- Language for the two scripts. Python assumed — the shell-out work is pleasant and every
  local-TTS or vision escape hatch is Python-first — but not actually settled.
- Captions. Cheap if the narration text is duplicated into the HTML, and the only cost is
  drift between it and `narration.json`. Depends on whether they'd ever be switched on.
- Target length. 20 minutes is aspirational; 6 minutes is a much easier thing to get
  *good*, and the pipeline is identical.
- German-language essays. Voice availability is no longer the blocker — `de-DE-Klaus` and
  seven Aura-2 German voices exist — but it still shapes the authoring prompt, and Gemini's
  expressiveness outside English is untested.
- Video clips via `yt-dlp`. In the original plan, never discussed.
- Whether Recraft's vector models emit real SVG — blocked by the ZDR account setting, so
  untested. Only matters if hand-written SVG turns out to be too slow for diagrams.
- Scrubbable vs. linear playback. Linear first; the slide index is in the DOM either way,
  so a scrubber stays additive.
- Whether `research.md` lives in the repo. Probably yes — it's small and it's provenance.
- The first essay subject. Having a real one in hand will settle more of these than another
  round of planning.
