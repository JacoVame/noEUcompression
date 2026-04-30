<!-- ITALIANO · slide source for reveal.js (markdown plugin). Separator: ---, vertical: -- -->

<!-- .slide: class="title" -->
# HyperbolicTextCompressor
## Comprimere il senso, non i byte
<div class="author">Gianluca Gagliano · ringraziamenti a Vito Di Gesù e Domenico Tegolo</div>
<div class="muted small">Una presentazione di ~30 minuti · ITALIAN</div>

---

## La domanda di partenza

> «Posso *comprimere* un testo non accorciando i simboli, ma raggruppando le parole che si somigliano?»

<span class="pill">non-EU</span> *non-Euclidean*, non «non-europeo». È solo geometria.

note:
Apertura morbida. Spiego il nome del progetto subito, perché altrimenti tutti pensano alla UE. Il punto chiave è il salto: dalla compressione *sintattica* (Huffman, LZ) a quella *semantica*.

---

## Da dove arriva l'idea

- Le parole prendono significato dai loro **vicini**.
- I vocabolari sono **alberi**: «animale → mammifero → cane → labrador».
- Per gli alberi, la geometria iperbolica è più adatta dell'euclidea.

note:
Spiegare con una metafora: «persone in una piccola città, che si conoscono per le strade che frequentano». Citare Nickel & Kiela 2017.

---

## Spazio piatto vs spazio curvo

<div class="columns">
<div>

**Piatto (Euclide)**
- Volume cresce come *r^d*
- Linee parallele uniche
- Triangoli a 180°

</div>
<div>

**Curvo (iperbolico)**
- Volume cresce **esponenzialmente**
- Infinite parallele
- Triangoli più «magri»

</div>
</div>

note:
La crescita esponenziale del volume è il punto: serve spazio infinito per gli alberi. Esempio Escher dei pesci che rimpiccioliscono.

---

## Il disco di Poincaré

<img src="../shared/pipeline.svg" alt="Pipeline" style="max-width: 95%;"/>

note:
Mostro la pipeline animata in apertura per far vedere subito la destinazione. Sotto la disco si vede crescere infinito il bordo.

---

## In una slide: cosa fa il prototipo

1. **Pulisce** il testo
2. **Conta** chi compare vicino a chi
3. **Riduce** ogni parola a un piccolo vettore
4. **Spinge** i vettori dentro al disco di Poincaré
5. **Misura** distanze iperboliche
6. **Sceglie** da solo una soglia
7. **Raggruppa** in cluster
8. **Stima** un indice di compressione

note:
Otto passi. Tengo lo schema in testa per tutte le slide successive. Ogni step avrà la sua slide.

---

## Vediamolo girare (animato)

<iframe class="pipeline-frame" src="../../docs/diagram/pipeline.html" loading="lazy"></iframe>

note:
Apro la pagina interattiva all'interno di un iframe. Mostro un giro completo prima di entrare nei dettagli.

---

## 1 · Preprocess

```text
"Gregorio Samsa si svegliò una mattina..."
↓ NFKC normalize
↓ /\p{L}{2,}/gu
[gregorio, samsa, si, svegliò, una, mattina, ...]
```

- NFKC: uniforma diacritici e varianti tipografiche
- Solo sequenze di lettere ≥ 2

note:
Sembra banale ma è il filtro più importante. Senza pulizia il resto è rumore.

---

## 2 · Co-occurrence

<div class="columns">
<div>

- Finestra scorrevole `windowSize` (default 3)
- Conteggio per ogni coppia in finestra
- Pesato (`uniform` o `1/(1+|i−j|)`)

</div>
<div>

```js
// matrice sparsa
row[wordIdx] = Map<colIdx, count>;
// vocabolario cap maxVocab
```

</div>
</div>

note:
Mostrare che la matrice è sparsa. Per il sample.txt: 65 parole uniche, ~150 coppie con count > 0.

---

## 3 · Embedding (riduzione)

| Strategia | Quando |
|-----------|--------|
| `random` | Default, robusta, sparse OK |
| `firstD` | Storica, riproducibile |
| `svd` | Vocab piccolo, qualità (deps opt.) |

```js
new HyperbolicTextCompressor(2, { projection: 'random', randomFeaturesPerDim: 16 })
```

note:
Random projection è sorprendentemente efficace. Citare Johnson-Lindenstrauss come motivazione teorica.

---

## 4 · Disco di Poincaré

```
x_poincaré = x · min(0.85 / ‖x‖, 1.0)
```

<span class="pill">vincolo</span> `‖x‖ < 1` — sempre dentro il disco
<span class="pill">margine</span> 0.85 — lontano dal bordo

note:
La radial scaling è banale. Il fattore 0.85 evita le singolarità della metrica.

---

## 5 · Distanza iperbolica (Möbius)

```
d_H(u,v) = acosh(1 + 2·‖u−v‖² / ((1−‖u‖²)(1−‖v‖²)))
```

- Vicino al centro: ≈ euclidea
- Vicino al bordo: **esplode**

note:
La formula è scenografica ma il messaggio è uno: la metrica amplifica le differenze al bordo. È quello che separa le famiglie semantiche.

---

## 6 · Auto-soglia: il sistema decide da solo

| Metodo | Idea | Quando |
|--------|------|--------|
| `percentile` | p35 di un campione | Distribuzioni regolari |
| `mad` | `median − K·1.4826·MAD` | Outlier presenti |
| `hybrid` | sceglie automaticamente | Default consigliato |

note:
Il punto è: niente magic numbers da tunare. Il sistema vede la distribuzione e decide.

---

## 6 · Cruscotto della soglia (esempio reale)

Su `samples/sample.txt`:

| Statistica | Valore |
|-----------|--------|
| Sample size | 2080 coppie |
| Mediana | 0.680 |
| MAD | 0.261 |
| σ ≈ 1.4826·MAD | 0.387 |
| p95 | 1.491 |
| Metodo scelto | `percentile` |
| Soglia effettiva | **0.510** |

note:
Numeri presi dal vero `out/bench.jsonl`. Il sistema sceglie percentile perché la coda non è abbastanza pesante per attivare MAD.

---

## 7 · Clustering

- Grafo: nodo = parola, arco = distanza < soglia
- **Union-find** con path compression
- Ordine-invariante, deterministico
- Optional **k-NN prefilter**: O(V²) → O(V·K)

note:
Union-find è elegante e classico. La k-NN prefilter è opzionale ma cambia la vita su V grandi.

---

## 8 · Stima di compressione

```
size_compresso ≈ #cluster + 0.5 · #parole
ratio = size_compresso / size_originale
```

<span class="danger">Modello giocattolo</span> — non confrontabile con gzip.

note:
Onestà brutale: è un termometro. Il vero confronto richiede entropy coding (Huffman / arithmetic / ANS).

---

## Demo dal vivo · sample.txt

```bash
npm run bench -- --file ./samples/sample.txt --auto \
  --autoMethod hybrid --autoStats
```

| Metrica | Valore |
|---------|--------|
| Parole uniche | 65 |
| Cluster trovati | 3 |
| Tempo totale | 13 ms |
| `savingsPct` | **54.5%** |

note:
Esecuzione live. Mostrare la riga JSON sputata dal bench. Aprire il report HTML accanto.

---

## I cluster trovati (sample.txt)

- <span class="accent">Cluster A</span> (63 parole) — rappresentante: «la»
  - articoli, preposizioni, ausiliari, verbi comuni
- <span class="accent">Cluster B</span> (1) — «pensieri»
- <span class="accent">Cluster C</span> (1) — «regolare»

note:
Sui cinque righi di Kafka (Italian) emergono tre famiglie. Le due singolette mostrano che il sistema sa anche tenere a parte le rarità.

---

## Cosa **non** è

- Non è un compressore di file (no .gz)
- Non capisce frasi, lemmi, morfologia
- Non sa il significato delle parole
- Non confronta byte con gzip/brotli/zstd

note:
La diapositiva più importante. Senza onestà sui limiti, il numero del 54.5% diventa fuorviante.

---

## Limiti onesti

- Modello giocattolo per la compressione
- O(V²) sul vocabolario (mitigato da k-NN)
- Sensibile ai parametri
- Corpora piccoli → distanze collassate
- Una sola lingua testata bene (italiano)

note:
Una slide compatta: chi ascolta vede subito i confini del prototipo.

---

## Casi d'uso (oggi)

<div class="columns">
<div>

- 🎓 **Didattica**
  - Union-find
  - Matrici sparse
  - Disco di Poincaré

</div>
<div>

- 🔬 **Ricerca**
  - Embedding iperbolici
  - Auto-thresholding
  - Sweep di parametri

</div>
</div>

- 🧪 **NLP esplorativo**: famiglie di parole, stop-word de-facto

note:
Tre macro-aree. Tengo presente che è una demo, non un prodotto.

---

## Roadmap di miglioramenti

| Fronte | Mossa |
|--------|-------|
| Compressione vera | Entropy coder (Huffman/arithmetic/ANS) |
| Decompressore | Rappresentanti canonici |
| Scalabilità | SVD truncata, k-NN approssimato (HNSW) |
| Qualità semantica | TF-IDF/PMI, Poincaré GloVe |
| Validazione | Multi-lingua, gold-standard |

note:
Ogni voce è un progetto a sé. Aprire issue/discussion su GitHub se qualcuno vuole contribuire.

---

## Perché l'ho costruito così

- **Zero dipendenze obbligatorie** → leggibile e didattico
- **Determinismo via seed** → ogni esperimento è ripetibile
- **Smoke test integrati** → si fida e si verifica
- **Diagnostica completa** → l'auto-soglia non è una scatola nera

note:
Le scelte di design servono a una community-friendly distribution. Senza dipendenze, gira ovunque.

---

## Architettura, in 5 file

```
compressionTest.js    ← motore (8 fasi)
bench.js              ← CLI di benchmark
tools/pretty-report.js ← report HTML
samples/sample.txt    ← demo italiano
out/bench.jsonl       ← risultati
```

note:
La compattezza è feature, non bug. Tutto il prototipo sta in poche centinaia di righe.

---

## Numeri di riferimento (sample.txt)

```json
{ "uniqueWords": 65, "clusters": 3,
  "ratio": 0.4551, "savingsPct": "54.5",
  "clusterThresholdUsed": 0.5097,
  "median": 0.6803, "mad": 0.261, "p95": 1.491 }
```

<span class="muted small">Eseguito con `--auto --autoMethod hybrid --autoStats`</span>

note:
Una slide di pura tracciabilità. Chi vuole riprodurre lo script ha tutti i numeri davanti.

---

## Lezioni apprese

1. La geometria iperbolica vale la fatica solo su gerarchie.
2. La random projection è sufficiente per un MVP.
3. Il robust thresholding (MAD) protegge da distribuzioni patologiche.
4. La diagnostica vince sul «magic number».
5. Onestà sui limiti > marketing dei numeri.

note:
Cinque take-away che vorrei vedere appuntate sui taccuini del pubblico.

---

## Domande tipiche

> «Comprime davvero?» — *No, stima.*
>
> «Confrontato con gzip?» — *Non ancora, vedi roadmap.*
>
> «Funziona su altre lingue?» — *Tecnicamente sì, ma non validato.*
>
> «Posso usarlo in produzione?» — *No, è ricerca.*

note:
Anticipare le domande del pubblico fa risparmiare tempo nel Q&A.

---

## Risorse

- Repo · `JacoVame/noeucompression`
- Doc IT · [`docs/it/`](../../docs/it/README.md)
- Doc EN · [`docs/en/`](../../docs/en/README.md)
- Pipeline animata · [`docs/diagram/pipeline.html`](../../docs/diagram/pipeline.html)
- Racconto · [`docs/it/racconto.md`](../../docs/it/racconto.md)

note:
Slide finale di link. Se possibile, distribuire QR code che punta al repo.

---

<!-- .slide: class="title" -->
# Grazie

<div class="author">Gianluca Gagliano</div>
<div class="muted small">Domande, esperimenti, contributi: aprite una issue/discussion su GitHub.</div>
<div class="muted small">MIT License · 2026</div>

note:
Lasciare 5–7 minuti di Q&A. Tornare alla pipeline animata se servono spunti visivi.
