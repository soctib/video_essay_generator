#!/usr/bin/env python3
"""Flag mechanically-detectable AI writing tells in narration.json.

Counts what can be counted, so the revision pass isn't self-assessment.
See docs/ai-writing-signs.txt for the full field guide.

    python3 .claude/skills/write-narration/audit_narration.py essays/<slug>/narration.json
"""
import json, re, statistics, sys

VOCAB = ["testament", "legacy", "pivotal", "underscore", "showcase", "vibrant",
         "tapestry", "delve", "crucial", "enduring", "foster", "landscape",
         "serves as", "stands as", "boasts", "rich history", "seamlessly",
         "navigate", "realm", "profound", "resonate", "intricate", "vital role",
         "beacon", "testify", "highlighting", "reflecting", "emphasizing"]

def audit(path):
    chunks = json.load(open(path))
    text = " ".join(c["text"] for c in chunks)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    lens = [len(s.split()) for s in sents]
    words = len(text.split())
    flags = []

    print(f"{path}\n  {len(chunks)} chunks, {words} words, ~{words/150*60:.0f}s at 150wpm\n")

    em = text.count("—")
    print(f"  em dashes                 {em}")
    if em > words / 200: flags.append(f"{em} em dashes in {words} words")

    negs = re.findall(r"\b(?:not just|not only|isn't just|wasn't just|it's not|no \w+, no)\b[^.]{0,50}", text, re.I)
    print(f"  negative parallelism      {len(negs)}")
    for n in negs: flags.append(f'negative parallelism: "{n.strip()[:60]}"')

    tri = re.findall(r"\b[\w']+,\s+[\w' ]{3,25},\s+and\s+[\w' ]{3,25}", text)
    print(f"  rule-of-three             {len(tri)}  (review each; appositives are false positives)")
    for t in tri: print(f"      · {t[:66]}")
    if len(tri) > 2: flags.append(f"{len(tri)} comma-list tricolons — check they aren't rhetorical")

    parts = re.findall(r",\s+\w+ing\b[^.]{10,}", text)
    print(f"  trailing -ing analysis    {len(parts)}")
    for p in parts: flags.append(f'trailing participle: "{p.strip()[:60]}"')

    hits = sorted({w for w in VOCAB if re.search(rf"\b{w}", text, re.I)})
    print(f"  AI vocabulary             {hits if hits else 'none'}")
    if hits: flags.append(f"AI vocabulary: {', '.join(hits)}")

    sd = statistics.pstdev(lens) if len(lens) > 1 else 0
    print(f"  sentence length           mean {statistics.mean(lens):.1f}, sd {sd:.1f}, range {min(lens)}–{max(lens)}")
    if sd < 4:
        flags.append(f"uniform sentence length (sd {sd:.1f}) — LLM prose is evenly paced; break it")

    long_chunks = [i for i, c in enumerate(chunks) if len(c["text"].split()) > 70]
    short_chunks = [i for i, c in enumerate(chunks) if len(c["text"].split()) < 6]
    if long_chunks:
        print(f"  over-long chunks          {long_chunks} (>70 words)")
    if short_chunks:
        print(f"  very short chunks         {short_chunks} (<6 words)")
        flags.append(f"chunks {short_chunks} are very short — each TTS call starts with cold "
                     f"prosody, so a fragment alone in a chunk lands flat. Fold into a neighbour "
                     f"unless the pause is deliberate.")

    print()
    if flags:
        print("FLAGS")
        for f in flags: print(f"  ! {f}")
    else:
        print("No mechanical flags. The judgement calls are still yours.")
    return 0

if __name__ == "__main__":
    sys.exit(audit(sys.argv[1] if len(sys.argv) > 1 else "narration.json"))
