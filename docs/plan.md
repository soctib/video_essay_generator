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

Downscale on save to roughly 2× intended display size. A full-res Commons scan can be
8000px wide, and decoded bitmaps are what actually consume memory at runtime.

Sources: see `free-image-apis-reference.md` for the surveyed landscape. Minimum viable set
is Openverse for discovery, Wikimedia + Library of Congress for anything historical, and
Unsplash or Pexels for modern photography. Wikipedia *article* images are worth trying
before Commons full-text search — they're already curated for the topic.

**Wikimedia enforces rate limits as of 2026**: 10 req/min unidentified, 200 req/min with a
compliant `User-Agent` carrying a name and contact. Set one or phase 1 crawls.

Note that downloading everything locally matches Wikimedia, LoC and Pixabay's terms but
conflicts with Unsplash's requirement to serve from their CDN. Moot for personal use, but
Unsplash is the odd one out if a single consistent path is ever wanted.

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

## 5. Phase 4 — deck

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

## 6. Rejected, and why

Recorded so they don't creep back in:

- **`essay.md` with per-beat YAML** (visuals, transitions, duration hints). That format
  existed to feed a deterministic builder. There is no deterministic builder — the AI
  writes the HTML — so the format has no consumer.
- **`manifest.json` as a build/runtime contract.** Same reason: it's a contract between two
  halves that are now the same author.
- **ffprobe durations written at build time.** `audio.ended` and runtime `audio.duration`
  cover it.
- **A TTS cache subsystem.** See phase 3.
- **Deriving image queries from finished narration.** This is the inversion the whole plan
  turns on. Queries written from committed prose return confident garbage, and the text has
  already promised to describe something that may not exist.

---

## 7. Open

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
- Generated charts and collages — deferred to a second gathering round, shape unknown.
- Scrubbable vs. linear playback. Linear first; the slide index is in the DOM either way,
  so a scrubber stays additive.
- Music bed. Twenty minutes of narration over silence is starker than it sounds.
- Whether `research.md` lives in the repo. Probably yes — it's small and it's provenance.
- The first essay subject. Having a real one in hand will settle more of these than another
  round of planning.
