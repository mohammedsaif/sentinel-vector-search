# How Vector Search Finds Meaning — Concept Explainer Script (about 4 minutes)

A code-free companion to `cosine_video_script.md`. Use it as the intro video, or as the "why" before the walkthrough.
Visual: the concept Excalidraw diagram (three zones: direction, score, HNSW layers). Zoom into one zone per section.

| # | Section | Time | Zone on screen |
|---|---------|------|----------------|
| 1 | The problem | 0:00–0:30 | Title |
| 2 | Meaning is direction | 0:30–1:30 | Zone 1 |
| 3 | The cosine score | 1:30–2:30 | Zone 2 |
| 4 | Why not just distance? | 2:30–3:00 | Zone 1 again |
| 5 | Making it fast: HNSW | 3:00–3:45 | Zone 3 |
| 6 | Takeaway | 3:45–4:00 | Full diagram |

## 1. The problem (0:00–0:30)

> "An investigator types: 'SIM swap fraud'. The best answer may say 'SIM cloning' and never use those exact words.
> Keyword search misses it. Vector search finds it. Let me show you how, in four minutes, no code."

## 2. Meaning is direction (0:30–1:30)

*Zoom to zone 1. Draw the three arrows one at a time.*

> "First, an embedding model turns every piece of text into a list of numbers — in our project, 3,072 of them. Think of that list as an arrow pointing into space.
> Texts that mean similar things point the same way. Our query, 'SIM swap fraud', is the black arrow. A short note about SIM cloning is the green arrow: shorter, but pointing the same way. The weather report is the red arrow, pointing somewhere else.
> Notice: the green one is shorter, yet it's the closest *in meaning*. Length doesn't matter. Direction does."

## 3. The cosine score (1:30–2:30)

*Zoom to zone 2. Point at the scale.*

> "Cosine similarity measures the angle between two arrows. Multiply the matching numbers and add them up — that's the dot product — then divide by the two arrow lengths.
> The result sits between minus one and one. One means the same direction: same idea. Zero means unrelated. Minus one means opposite.
> One shortcut: if we scale every arrow to length one, the division disappears. Cosine becomes just the dot product. Same ranking, less math. That's why embeddings are often stored normalised."

## 4. Why not just distance? (2:30–3:00)

*Back to zone 1; hold a finger on the green arrow's tip and the query's tip.*

> "Why not measure the straight-line distance between arrow tips? Because that punishes length. The short green arrow's tip is far from the long black one, even though they point the same way.
> In our worked example, the point that lies exactly on the query's line is last by distance — and first by cosine. Different ruler, different winner. For meaning, direction is the right ruler."

## 5. Making it fast: HNSW (3:00–3:45)

*Zoom to zone 3. Trace the red path.*

> "Now scale. Comparing the query against every vector — brute force — is fine for thousands, painful for millions.
> HNSW builds a graph in layers. The top layer has just a few nodes with long hops. We enter there, jump to the closest node, drop a layer, jump again, and drop again. By the bottom layer we're already next to the answer, having checked only a handful of nodes.
> The price: extra memory for the graph, and answers that are approximate — occasionally you miss a true neighbor. In practice, that's a great trade."

## 6. Takeaway (3:45–4:00)

> "Text becomes arrows. Cosine compares angles. Normalise it and it's a dot product. HNSW makes it fast. That's the whole engine under Sentinel's search."

## Production notes

- About 480 spoken words, roughly 130 words per minute.
- Animate the Excalidraw drawing in order; the camera zooms match the section table.
- Don't quote HNSW speedups in this video; the concept is the point (see the benchmark caveat in `cosine_video_script.md`).
