# Free / Free-Tier Image APIs — Developer Reference (Sept 2026)

Scope: APIs you can call programmatically to *find* images (and a few to *generate* charts/diagrams) for illustrating articles. Verified limits and terms as of September 2026.

---

## 1. Stock photos

| API | Key? | Limits | License / attribution | Notes |
|---|---|---|---|---|
| **Unsplash** `api.unsplash.com` | Yes | 50 req/h demo → 5,000 req/h after production review (~5 business days) | Unsplash License, commercial OK. License doesn't require attribution, but **the API terms do** — photographer credit with UTM-tagged links | Must serve images from Unsplash's CDN (hotlink) and fire the `/download` endpoint on use — that's how views get counted. The old `source.unsplash.com` random-image endpoint is deprecated. |
| **Pexels** `api.pexels.com/v1` | Yes (instant) | 200 req/h, 20,000 req/month. Unlimited free on request if you demo your attribution | Free commercial use. Requires a prominent "Photos provided by Pexels" link + photographer credit | Explicitly encourages caching responses. `per_page` max 80 — use it. No wallpaper apps. |
| **Pixabay** `pixabay.com/api/` | Yes (instant) | Effectively unlimited, ~100 req/min soft cap | Pixabay Content License. **No attribution required** | Terms require you to *cache* image URLs (24h) rather than hotlink — the opposite of Unsplash. 5.6M+ assets. Three license eras (pre-2019 CC0, post-2023 Content License) and a growing pile of AI-generated content. |
| **Openverse** `api.openverse.org/v1` | No (OAuth optional for higher limits) | Anonymous works fine; **max page depth 20** (~240 results per query) | CC / public domain only, filterable by `license` and `license_type` | WordPress-run. Aggregates Flickr, Wikimedia, museums, Smithsonian, etc. in one call. Best single entry point if you want "free to use" guaranteed. |

**Indemnification note:** Unsplash (free), Pexels and Pixabay all offer **$0** legal indemnification — you indemnify *them*. Fine for a blog, not fine for a national ad campaign.

---

## 2. Historical / archival / museum (the good stuff for landmarks & events)

| API | Key? | Limits | Notes |
|---|---|---|---|
| **Wikimedia Commons / Wikipedia** (Action API + REST) | No, but OAuth 2.0 raises limits | **New in 2026:** 10 req/min unidentified, 200 req/min with a compliant `User-Agent`, higher when authenticated. Bots in Toolforge exempt | The single best source for landmarks and historical photos. **Set a real User-Agent with contact info** or you get throttled hard. Licenses vary per file (PD, CC-BY, CC-BY-SA) — you must parse and attribute per image. |
| **Library of Congress** `loc.gov/...?fo=json` | No | Undocumented, be gentle | Add `?fo=json` to any loc.gov URL. Includes **HABS/HAER** — measured engineering drawings and large-format documentary photos of US infrastructure. Mostly public domain. |
| **Smithsonian Open Access** `api.si.edu` | Yes (free, via api.data.gov) | 1,000 req/h | ~5M CC0 records with images. |
| **Met Museum** `collectionapi.metmuseum.org` | No | ~80 req/s suggested ceiling | Open Access objects are CC0. Art, not news photography. |
| **Rijksmuseum** `data.rijksmuseum.nl` | **No longer required** | — | ⚠️ The legacy JSON API was retired in late 2025. Replaced by Linked Open Data APIs + OAI-PMH. Old tutorials and client libraries are dead. |
| **Europeana** `api.europeana.eu` | Yes | Generous | Aggregates 3,000+ EU institutions. Best source for European history. Rights statements vary — filter on `REUSABILITY=open`. |
| **DPLA** `api.dp.la` | Yes (request by email/curl) | Generous | US aggregator across libraries, museums, archives. |
| **Internet Archive** `archive.org/advancedsearch.php` + metadata API | No | Be gentle | Books, film stills, ephemera. |
| **NARA Catalog** `catalog.archives.gov/api/v2` | Yes (v2 requires one) | — | US federal records, overwhelmingly public domain. |
| **NYPL Digital Collections** | Yes | — | Strong on maps, photography, ephemera. |
| **Flickr** `flickr.com/services/rest/` | Yes (instant) | Generous | ⚠️ Default key is **non-commercial**; commercial use is "by prior arrangement." **Flickr Commons** is the gem: PD archival photos contributed by institutions (national archives, museums, transit agencies). Filter `license=` for CC. |

---

## 3. Maps / satellite

- **OpenStreetMap tiles** — `tile.openstreetmap.org` is for casual use only; their tile usage policy forbids production hammering. Use a provider.
- **MapTiler** — free tier ~100k tile requests/month. **Geoapify** — 3,000 credits/day free. **Mapbox** — ~50k static image requests/month free. **Stadia Maps** — free for non-commercial.
- **NASA** `api.nasa.gov` — one key covers APOD, Earth imagery, etc. `DEMO_KEY` = 30 req/h; registered key = 1,000 req/h. `images.nasa.gov` API needs no key. Content is generally public domain.
- **USGS / Landsat** — free via the M2M API, registration required. Heavy; overkill unless you need actual satellite scenes.

---

## 4. Illustrations, icons, vectors

- **Iconify API** `api.iconify.design` — no key, 200k+ icons across 150+ sets, fetch SVG straight from a URL. The default choice.
- **Simple Icons** — brand/company logos via CDN, no key, no auth.
- **Lucide / Feather / Heroicons** — npm or CDN, no API needed.
- **unDraw / Storyset** — flat editorial illustrations. No official public API; unDraw has an unofficial JSON endpoint that breaks periodically. Realistically: download what you need.
- **Noun Project** — has an API but OAuth 1.0a, limited free tier, attribution required unless you pay.

---

## 5. Charts & diagrams (generation, not search)

- **QuickChart** `quickchart.io/chart?c={...}` — Chart.js config in a URL, PNG/SVG/PDF out. Free: **60 charts/min, 1,000/month**. Output is public domain. **GPLv3 and self-hostable via Docker** — do that and the limits disappear. This is the workhorse.
- **Kroki** `kroki.io` — text → diagram for 30+ formats (Mermaid, PlantUML, GraphViz, D2, Vega-Lite, BPMN, Excalidraw). Free public instance, no key, self-hostable. No remote calls on the public instance.
- **Mermaid.ink** — dedicated free Mermaid renderer, best-effort uptime.
- **Image-Charts** — freemium, watermarks the free tier. Skip unless you need the Google Image Charts API shape.

---

## 6. Gotchas worth internalizing

1. **Attribution rules ≠ license rules.** Unsplash and Pexels licenses don't demand credit, but their *API terms* do. Violating the API terms gets your key killed regardless of what the license says.
2. **Hotlinking rules are contradictory across providers.** Unsplash *requires* you to serve from their CDN. Pixabay *requires* you to cache and not hotlink. Don't build one pipeline and apply it to both.
3. **Wikimedia is no longer a free-for-all.** The 2026 global rate limits are real and enforced. Unidentified traffic gets 10 req/min. A compliant `User-Agent` (name/version + contact) buys you 20x.
4. **Cache aggressively.** Every provider on this list explicitly rewards it, and it's the single easiest way to stay inside every limit here.
5. **Museum APIs churn.** Rijksmuseum's legacy API is gone. Check the docs before trusting a tutorial older than a year.
6. **Flickr's default key is non-commercial.** Easy to miss and easy to get wrong at scale.
7. **AI-generated content is now in the stock pools** (Pixabay especially) with unsettled copyright status. Filter or eyeball it if that matters.

---

## 7. Recommended stack for illustrating a general-interest article

Concrete example — the Golden Gate Bridge piece:

| Need | Source |
|---|---|
| 1933–37 construction photos | **Library of Congress** (HAER survey: measured engineering drawings + large-format photos, PD) → **Wikimedia Commons** → **Flickr Commons** |
| Modern tourist / landscape shots | **Unsplash** or **Pexels** — one of the most-photographed objects on earth, supply is not the problem |
| Portraits of Strauss / Ellis / Morrow | **Wikimedia Commons**, **LoC** |
| Engineering cross-sections, cable diagrams | **Kroki** (or hand-rolled SVG) — the HAER drawings also work as-is |
| Charts (toll history 1937→2026, traffic volume, cost breakdown) | **QuickChart**, self-hosted |
| One-call fallback across everything CC | **Openverse** |
| Icons for a UI around it | **Iconify** |

**Minimum viable set:** Openverse for discovery, Wikimedia + LoC for anything historical, Unsplash *or* Pexels for modern photography, self-hosted QuickChart for charts. Four integrations, zero cost, no rate-limit anxiety.
