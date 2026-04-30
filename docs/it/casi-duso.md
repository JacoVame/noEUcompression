# Casi d'uso

← [Indice](./README.md)

> Versione visiva: vedi [`docs/diagram/diagrams.md`](../diagram/diagrams.md).

Il prototipo non è un compressore di file. È un **piccolo laboratorio** di geometria iperbolica per il testo. Ecco dove ha senso usarlo.

## 1 · Ricerca esplorativa

- **Geometria iperbolica per il linguaggio**: vuoi capire se la curvatura negativa cattura davvero la gerarchia delle parole? Questo è un punto di partenza minimo, deterministico, leggibile.
- **Confronto con embedding addestrati** (Poincaré GloVe, Hyperbolic Word2Vec): le proiezioni euclidee + scaling che usiamo qui sono più veloci, ma ovviamente meno informate. Servono come baseline.
- **Effetto della soglia adattiva** (percentile / MAD / hybrid): il modulo è progettato per misurare l'effetto di queste scelte, e include diagnostica completa.

## 2 · Didattica

- **Lezioni su strutture dati**: la sezione clustering è un esempio chirurgico di union-find con path compression. Ottimo per studenti che vogliono toccare con mano una struttura classica fuori dai soliti esercizi.
- **Matrici sparse**: la rappresentazione `Map<colonna, conteggio>` per riga è leggibile in poche decine di righe.
- **Visualizzazione del disco di Poincaré**: la pipeline animata in `docs/diagram/pipeline.html` rende l'idea senza richiedere conoscenze di geometria differenziale.

## 3 · NLP esplorativo

- **Trovare famiglie di parole**: su un testo non troppo grande, il sistema individua cluster ragionevoli senza bisogno di un modello pre-addestrato.
- **Riassumere il vocabolario**: utile in fase di pulizia di un dataset (capire chi sono le parole funzionali, chi i temi rari).
- **Trovare stop-words «di fatto»**: il cluster gigante che si forma vicino al centro contiene tipicamente articoli e preposizioni.

## 4 · Benchmarking di pipeline

- **Sweep di parametri**: il `bench.js` è progettato per iterare su `dimension`, `projection`, `clusterK`, metodo di auto-soglia, ecc., e produce JSONL pronto per analisi successive.
- **Confronto fra strategie di prefiltro**: full O(V²) vs k-NN esatto vs k-NN approssimato. Il sistema riporta tempi (`timingsMs`) per ogni stadio.
- **Diagnostica della distribuzione delle distanze**: con `--autoStats --histBins 20` ottieni un piccolo cruscotto della distribuzione. Utile per capire perché la soglia automatica si comporta come si comporta.

## 5 · Sandbox per nuovi proiettori

Il modulo isola le tre fasi (riduzione, scaling iperbolico, distanza) in modo abbastanza pulito da poter essere usato come banco di prova per:

- Nuove strategie di proiezione (truncated SVD, randomized PCA, sparse projections).
- Nuove metriche su disco (Lorentz, half-space, distanze approssimate).
- Embedding ibridi (parte euclidea + parte iperbolica).

## Quando *non* usarlo

- Se devi spedire file più piccoli su rete: usa `gzip`/`brotli`/`zstd`.
- Se devi capire il significato di una frase: usa un modello linguistico vero.
- Se devi gestire vocabolari da milioni di parole in produzione: questa O(V²) ti farà piangere.

## Continua

➡️ [Roadmap di miglioramenti](./miglioramenti.md)
