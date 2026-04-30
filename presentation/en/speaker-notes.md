# Speaker notes — HyperbolicTextCompressor (EN, 30 min)

> Discursive script for the presenter. Indicative timings beside each section.
> The same notes are embedded in the reveal.js deck (press `S` during presentation); this file is the cold-read version.

## 0. Before you start (2′)

- Open `presentation/en/index.html` in a browser.
- Pre-open `docs/diagram/pipeline.html` in another tab for slides 6 and 18.
- Have the terminal ready with `out/bench.jsonl` for the live demo (slide 16).
- Project a QR code of the repo during pauses.

## 1. Opening (slides 1–3, ~3′)

Greet, introduce yourself, briefly thank Profs. Di Gesù and Tegolo (their work on geometry, perception and language is the cultural broth from which the idea grew). Spell out the name immediately: "non-EU" is a play on words — it means non-Euclidean. Start from a question, not a formula: "can I compress meaning, not bytes?". Close with the leap: from *syntactic* compression to *semantic* compression.

## 2. The motivation (slides 4–5, ~3′)

Schoolbook geometry is flat. Language is tree-shaped. Use the small-notebook metaphor: you run out of room. Cite Nickel & Kiela 2017 without going into details — it's a popular and robust motivation. Show the animated pipeline already on slide 5 to anchor the audience: "by the end you'll understand all of this". Don't slow down here — it is just a taste.

## 3. What the prototype does, in one slide (slide 6, ~1′)

Eight steps. Read the list aloud, slowly. Important for people standing or watching online: they will see the same list eight more times.

## 4. Intro demo (slide 7, ~2′)

Let the animated pipeline autoplay for about a minute and talk over it. Point at the yellow dot moving across stages, the Poincaré disk, the histogram, the three colored clusters. Close with: "now we go into the details".

## 5. Technical steps (slides 8–15, ~10′)

About a minute per slide. Brisk pace, no dramatic formulas. Key beats:

- **Preprocess**: NFKC + regex, looks like nothing but it's foundational.
- **Co-occurrence**: sparse matrix, highlight `Map<col, count>` per row.
- **Embedding**: random projection, mention Johnson-Lindenstrauss.
- **Poincaré**: `‖x‖ < 1`, 0.85 factor.
- **Distance**: I show the `acosh(...)` formula but don't explain it term-by-term. I just say: "near the centre, normal; near the boundary, it explodes".
- **Auto-threshold**: emphasise no magic number, then show the dashboard (slide 13).
- **Clustering**: union-find, order-invariant, k-NN prefilter.
- **Estimate**: ratio + 50% mapping. **Immediately** call it "toy" because otherwise the 54.5% looks like a victory.

## 6. Live demo (slide 16, ~3′)

Run `npm run bench -- --file ./samples/sample.txt --auto --autoMethod hybrid --autoStats` in front of the audience. Show the JSON line. Open `out/report.html` to show the charts.

## 7. The actual clusters (slide 17, ~1′)

Three clusters. The big one is interesting because it contains articles, prepositions, auxiliaries: a "de-facto stop-word" group. The two singletons show the system is cautious with rarities.

## 8. The honesty section (slides 18–19, ~3′)

Crucial slide: what it is **not**. Without it someone in the audience could think they saw a gzip replacement. Rule that out immediately. Honest limits on slide 19: read them as a list.

## 9. Use cases & roadmap (slides 20–21, ~3′)

Quick pace. The roadmap is honest: none of the items is trivial. Specifically, the decompressor is the first block to build before any gzip comparison.

## 10. Why this way (slide 22, ~1′)

Design choices serve a public audience: zero deps, deterministic, readable. Stress the word "teachable".

## 11. Compact architecture (slide 23, ~30″)

Almost a visual slide. Compactness is a feature.

## 12. Reference numbers and lessons learned (slides 24–25, ~2′)

Numbers are for those who want to reproduce. The five lessons learned are the rhetorical summary.

## 13. Pre-empted FAQ + Q&A (slides 26–28, ~5–7′)

Pre-empting questions buys time for the real ones. Stay available on the animated pipeline if anyone wants a visual prompt.

---

## Total budget

| Section | Min |
|---------|-----|
| Opening | 3 |
| Motivation | 3 |
| Synthesis | 1 |
| Intro demo | 2 |
| Technical steps | 10 |
| Live demo | 3 |
| Real clusters | 1 |
| Honesty | 3 |
| Use cases + roadmap | 3 |
| Design | 1 |
| Architecture | 0.5 |
| Numbers + lessons | 2 |
| FAQ + Q&A | 5–7 |
| **Total** | **~30** |

## Final tips

- Keep the animated pipeline open in a separate tab, always available.
- Have `out/bench.jsonl` open to copy real numbers if questioned.
- If time is short: cut the architecture slide (23) and the reference numbers (24).
- If the audience asks *"is this AI?"*, answer: "no, it's a geometry experiment. No neural networks, no training, no GPUs".
