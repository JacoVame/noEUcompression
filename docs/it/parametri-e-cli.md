# Parametri e CLI

← [Indice](./README.md)

Tutte le manopole disponibili per chi vuole sperimentare. Per il dettaglio chirurgico tieni aperto il [`README.md`](../../README.md) inglese: questa pagina lo riassume e lo traduce.

## Installazione

```bash
git clone <repo>
cd noEUcompression
# nessuna dipendenza obbligatoria
node ./compressionTest.js
```

Per la proiezione SVD (opzionale):

```bash
npm install ml-matrix svd-js cross-env --save
# oppure: pnpm add ml-matrix svd-js cross-env
```

## Script `npm`

| Comando | Cosa fa |
|---------|---------|
| `npm run demo` | Esegue il prototipo su un paragrafo italiano integrato. |
| `npm test` | Lancia gli smoke test integrati. |
| `npm run bench` | Avvia il benchmark (vedi sotto). |
| `npm run report` | Genera un report HTML in `out/report.html` a partire da `out/bench.jsonl`. |

## Costruttore (uso programmatico)

```js
const HyperbolicTextCompressor = require('./compressionTest');

const c = new HyperbolicTextCompressor(2 /* dimensione */, {
  maxVocab: 3000,
  seed: 42,
  windowSize: 3,
  clusterThreshold: 0.4,
  projection: 'random',          // 'random' | 'firstD' | 'svd'
  randomFeaturesPerDim: 16,
  weighting: 'distance',         // 'uniform' | 'distance'
  normalize: true,
  verbose: true,
  svdMaxN: 800,
  clusterK: 0,
  approxKNN: false,
  approxKCandidates: 50,
  autoThreshold: true,
  autoThresholdPercentile: 0.35,
  autoThresholdSample: 3000,
  autoThresholdMethod: 'hybrid', // 'percentile' | 'mad' | 'hybrid'
  autoThresholdMADK: 0.5,
  autoThresholdHistogramBins: 20,
  diagnosticsOnly: false
});

const r = c.analyzeAndCompress(testo);
console.log(r.compressionRatio, r.clusters.length);
```

### Le opzioni che contano davvero

| Opzione | Cosa controlla | Quando toccarla |
|---------|----------------|-----------------|
| `dimension` | Quanti assi ha l'embedding (default 2) | 2 per visualizzare; 3–8 per qualità |
| `windowSize` | Quanto è larga la finestra di co-occorrenza | Più larga ⇒ contesto più diffuso |
| `clusterThreshold` | Soglia distanza (manuale) | Se non usi l'auto-threshold |
| `projection` | Strategia di riduzione | `random` per stabilità; `svd` per qualità su corpus piccoli |
| `clusterK` | Prefiltro k-NN | Su vocabolari grandi (V > 1000) |
| `autoThreshold` | Sceglie la soglia da sola | Quasi sempre conviene |
| `autoThresholdMethod` | Strategia auto-soglia | `hybrid` se non vuoi pensarci |
| `seed` | Riproducibilità | Sempre, per benchmark seri |

## CLI di benchmark

`bench.js` è uno script che stampa una riga JSON per esecuzione. Si presta bene a sweep di parametri.

### Esempi pratici

```bash
# Singolo file con auto-soglia ibrida e diagnostica completa
npm run bench -- --file ./samples/sample.txt --auto --autoMethod hybrid --autoStats

# Sweep su dimensioni, proiezioni e k-NN
npm run bench -- --file ./samples/sample.txt \
  --dimensions 2,3 --projection random,svd --k 0,10,25 \
  --auto --outJson ./out/bench.jsonl

# Cluster JSON salvati su disco + report HTML
npm run bench -- --file ./samples/sample.txt --auto --autoMethod hybrid \
  --autoStats --emitClusters ./out/clusters --outJson ./out/bench.jsonl
npm run report
```

### Tutti i flag

| Flag | Descrizione |
|------|-------------|
| `--file PATH` | File di testo singolo |
| `--dir PATH` | Cartella di file `.txt` |
| `--dimension N` | Dimensione dell'embedding |
| `--dimensions a,b,c` | Sweep su più dimensioni |
| `--projection x,y` | `random`, `firstD`, `svd` (anche multi) |
| `--k a,b,c` | Valori di k-NN da provare |
| `--threshold X` | Soglia fissa (esclude auto) |
| `--auto` | Abilita auto-soglia |
| `--autoMethod m` | `percentile` · `mad` · `hybrid` |
| `--percentile p` | Percentile per `percentile`/`hybrid` |
| `--madK K` | Costante per il metodo MAD |
| `--sample N` | Massime coppie campionate |
| `--autoStats` | Aggiunge diagnostica nel JSON |
| `--diagOnly` | Niente clustering, solo diagnostica |
| `--histBins N` | Istogramma delle distanze |
| `--approxKNN 0\|1` | Attiva k-NN approssimato |
| `--approxKCandidates N` | Candidati per nodo |
| `--emitClusters PATH` | Scrive i cluster su disco |
| `--outJson PATH` | JSONL invece di stdout |
| `--weighting w` | `uniform` · `distance` |
| `--window N` | Raggio finestra co-occorrenza |
| `--maxVocab N` | Cap del vocabolario |
| `--seed N` | RNG seed |
| `--svdMaxN N` | Vocab massimo per SVD |
| `--normalize 0\|1` | NFKC on/off |
| `--verbose 0\|1` | Log estesi |

## Cosa si ottiene dal benchmark

Esempio di una riga in `out/bench.jsonl` (eseguita su `samples/sample.txt`):

```json
{
  "input": "sample.txt",
  "dimension": 2,
  "projection": "random",
  "clusterK": 0,
  "autoThreshold": true,
  "clusterThresholdUsed": 0.5097,
  "uniqueWords": 65,
  "clusters": 3,
  "ratio": 0.4551,
  "savingsPct": "54.5",
  "timingsMs": { "preprocessMs": 1, "coocMs": 7, "embedMs": 1, "clusterMs": 3, "totalMs": 13 },
  "autoThresholdStats": {
    "sampleSize": 2080, "percentile": 0.35, "chosenMethod": "percentile",
    "median": 0.6803, "mad": 0.2607, "sigma": 0.3866,
    "p10": 0.2727, "p50": 0.6803, "p95": 1.4910,
    "histogram": { "bins": 20, "min": 0, "max": 2.3979, "counts": [/*...*/] }
  }
}
```

E il report HTML (`npm run report` → `out/report.html`) ti dà tabelle, grafici a barre, istogrammi, e il confronto fra `K` e proiezioni.

## Suggerimenti rapidi per la soglia

| Dimensione del corpus | Percentile suggerito | K per MAD |
|------------------------|----------------------|-----------|
| ≤ 200 parole uniche | 0.25–0.35 | 0.20–0.40 |
| 200–2000 | 0.30–0.45 | 0.40–0.70 |
| ≥ 2000 | 0.35–0.55 | 0.50–0.90 |

Se i cluster sono **troppo pochi** (uno gigantesco): abbassa il percentile o alza K.
Se i cluster sono **troppi e minuscoli**: alza il percentile o abbassa K.
Se la soglia esce a `1e-6`: il corpus è troppo piccolo, prova percentile alto o aumenta `windowSize`/`maxVocab`.

## Continua

➡️ [Cosa il prototipo non fa: i limiti onesti](./limitazioni.md)
