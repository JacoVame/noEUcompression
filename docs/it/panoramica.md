# Panoramica

← [Indice](./README.md)

## Cos'è (in una frase)

`HyperbolicTextCompressor` è un piccolo prototipo in JavaScript che prende un testo, mappa le parole in uno spazio curvo (il disco di Poincaré), le raggruppa in famiglie semantiche e poi calcola un *indice di compressione* per misurare quanta ridondanza è riuscito a riassorbire.

## Perché «iperbolico»?

La geometria che impariamo a scuola è euclidea: linee dritte, somma degli angoli del triangolo a 180°, distanze che si sommano in modo prevedibile. Ma il linguaggio non è piatto: ha gerarchie, alberi di significati, parole-genitore e parole-figlie. Per rappresentare strutture ad albero la geometria iperbolica è una scelta più naturale, perché il volume disponibile cresce esponenzialmente avvicinandosi al bordo del disco — esattamente come crescono i nodi di un albero a ogni livello.

In altre parole: nello spazio piatto le parole si pestano i piedi; nello spazio curvo c'è posto per organizzare le famiglie con calma.

## Perché «non EU»?

«Non EU» nel nome è una battuta: sta per *non-Euclidean compression*. Niente a che vedere con regolamenti europei o normative sui dati. È solo geometria.

## Per chi è pensato

- **Curiosi**: chi vuole farsi un'idea di come la matematica può rappresentare il significato delle parole, senza diventare matematico.
- **Studenti e docenti**: il codice è leggibile, deterministico, senza dipendenze obbligatorie. Si presta a lezioni su matrici sparse, union-find, embedding, visualizzazione.
- **Ricercatori**: chi vuole sperimentare con proiezioni euclidee semplici prima di passare a embedding addestrati come Poincaré GloVe.
- **Sviluppatori curiosi di NLP**: chi non vuole tirare giù un modello da gigabyte solo per vedere cluster ragionevoli su un paragrafo.

## Per chi *non* è pensato

- Non è un sostituto di `gzip`, `brotli` o `zstd`. La «compressione» qui è una stima giocattolo basata sul numero di cluster trovati: serve per capire la qualità semantica, non per spedire file più piccoli su rete.
- Non c'è un decompressore: la mappatura non è invertibile in maniera lossless.
- Non è ottimizzato per produzione: i benchmark hanno costo O(V²) sul vocabolario.

## Cosa fa di diverso rispetto a un compressore classico

Un compressore tradizionale (LZ77, Huffman, codifica aritmetica) cerca pattern *sintattici*: stringhe che si ripetono, simboli più frequenti che ricevono codici più corti. Funziona benissimo, ma «non capisce» cosa significhino le parole.

Qui invece l'idea è opposta: cerchiamo pattern *semantici*. Due parole sono «simili» se compaiono nei dintorni delle stesse altre parole. Le accomuniamo in cluster, e usiamo il cluster come riassunto del loro significato. Il risultato non è un file più piccolo, ma un dizionario più piccolo — una specie di compressione del *vocabolario*.

## Stato del progetto

- **Versione**: 0.1.0 (prototipo).
- **Linguaggio**: JavaScript (Node.js 16+).
- **Dipendenze obbligatorie**: nessuna.
- **Dipendenze opzionali**: `ml-matrix` o `svd-js` (solo se vuoi usare la proiezione SVD).
- **Test**: smoke test integrati nel modulo principale (`HTC_RUN_TESTS=1 node compressionTest.js`).
- **Determinismo**: completo, dato un seed.
- **Licenza**: MIT.

## Continua

➡️ [La pipeline in otto passi](./pipeline.md)
