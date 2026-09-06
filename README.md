# video_essay_generator

Turns a research document into a narrated, self-playing slideshow that runs in a browser.

Feed it notes on a subject; get back a folder containing an `index.html` you open and walk
away from. It narrates itself, advances its own slides, and plays start to finish without
input. No video is ever encoded — the "video essay" is a web page.

Built for personal use, to watch things I wanted to exist and didn't.

## How it works, roughly

1. **Gather** — read the research document, search for images, look at them, keep the good
   ones with a written description of what's actually in the frame.
2. **Author** — write the narration against the images that were found
3. **Narrate** — synthesise the narration to audio, one file per spoken chunk.
4. **Assemble** — generate the deck: one HTML page, styled for the subject at hand, that
   advances when each audio clip ends.


## Status

Planning. Nothing is implemented yet.

See [plan.md](plan.md) for the actual design, the decisions behind it, and what's still
open.

## Stack

Not settled. Two small scripts (audio synthesis, image fetching), probably Python, plus a
vanilla-JS playback engine with no build step.

## License

TBD
