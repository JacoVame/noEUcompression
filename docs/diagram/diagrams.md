# Diagrammi · Diagrams

Pagina indice dei diagrammi di supporto. La pipeline animata principale è in [`pipeline.html`](./pipeline.html) (richiede un browser).

Index of supporting diagrams. The main animated pipeline lives in [`pipeline.html`](./pipeline.html) (browser required).

---

## Pipeline (statica · static)

![Pipeline statica](./pipeline.svg)

Versione interattiva con riproduzione, pausa e didascalie bilingue: [`pipeline.html`](./pipeline.html).

Interactive version with play, pause and bilingual captions: [`pipeline.html`](./pipeline.html).

---

## Limiti · Limitations

```mermaid
mindmap
  root((HyperbolicTextCompressor<br/>Limiti · Limits))
    Compressione "giocattolo"
      Stima = cluster + 50% mappatura
      Non è un codec a livello byte
      Niente confronto con gzip / Brotli
    Costo
      Distanze a coppie O(V²)
      Mitigato da k-NN prefilter (O(V·K))
      Ancora niente streaming
    Sensibilità ai parametri
      windowSize
      clusterThreshold
      projection (random / firstD / svd)
      randomFeaturesPerDim
    Corpora piccoli
      Distanze collassano vicino a 0
      Auto-threshold tende a 1e-6
      Cluster banali
    Lingua e dominio
      Testato su italiano
      Comportamento su altre lingue non validato
      Niente lemmatizzazione, niente stop-words
    Dipendenze opzionali
      SVD richiede ml-matrix o svd-js
      Fallback grazioso se mancano
    Niente decompressore
      Solo stima
      Mappatura non invertibile lossless
```

Sorgente: [`limitations.mmd`](./limitations.mmd).

---

## Casi d'uso · Use cases

```mermaid
flowchart LR
  Root([HyperbolicTextCompressor])
  Root --> R[Ricerca · Research]
  Root --> D[Didattica · Teaching]
  Root --> N[NLP esplorativo · Exploratory NLP]
  Root --> B[Benchmarking pipeline]
  Root --> E[Sandbox embedding]

  R --> R1[Geometria iperbolica per il linguaggio]
  R --> R2[Confronti con Poincaré GloVe]
  R --> R3[Esperimenti su gerarchie semantiche]

  D --> D1[Lezioni su union-find]
  D --> D2[Lezioni su matrici sparse]
  D --> D3[Visualizzare il disco di Poincaré]

  N --> N1[Trovare famiglie di parole]
  N --> N2[Riassunto di vocabolario]
  N --> N3[Pulizia dataset · cluster di stop-words]

  B --> B1[Sweep parametri e proiezioni]
  B --> B2[Diagnostica auto-threshold]
  B --> B3[Confronto k-NN vs full O V²]

  E --> E1[Provare seed e robustezza]
  E --> E2[Testare nuove distanze]
  E --> E3[Plug-in di nuovi proiettori]
```

Sorgente: [`use-cases.mmd`](./use-cases.mmd).

---

## Roadmap di miglioramenti · Improvement roadmap

```mermaid
flowchart TB
  S[Stato attuale · Today] --> P1
  S --> P2
  S --> P3

  subgraph P1[Compressione reale · Real compression]
    direction TB
    A1[Codifica entropica:<br/>Huffman / Arithmetic / ANS]
    A2[Confronto vs gzip · Brotli · zstd]
    A3[Decompressore · lossless mapping]
  end

  subgraph P2[Scalabilità · Scalability]
    direction TB
    B1[Streaming co-occurrence builder]
    B2[Truncated SVD / randomized PCA]
    B3[Approximate hyperbolic k-NN<br/>HNSW / IVF]
    B4[GPU · WebAssembly acceleration]
  end

  subgraph P3[Qualità semantica · Semantic quality]
    direction TB
    C1[TF-IDF · PMI re-weighting]
    C2[Embedding addestrati<br/>Poincaré GloVe / hyperbolic word2vec]
    C3[Multi-lingua · validation suite]
    C4[Cluster repr. semantici<br/>medoide invece del primo indice]
  end

  P1 --> Goal([Compressore semantico utilizzabile<br/>Usable semantic compressor])
  P2 --> Goal
  P3 --> Goal
```

Sorgente: [`improvements.mmd`](./improvements.mmd).
