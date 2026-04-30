# Limitazioni

← [Indice](./README.md)

> Una mappa visiva degli stessi limiti, in formato mermaid, è in [`docs/diagram/diagrams.md`](../diagram/diagrams.md).

Le limitazioni qui sotto sono **per costruzione**, non bug. Sapere cosa il prototipo non fa è importante quanto sapere cosa fa.

## 1 · La compressione è giocattolo

La metrica `ratio` non confronta byte: confronta il **numero di parole** del testo con il **numero di cluster + 50% del vocabolario** (overhead di una mappatura fittizia). È un termometro della densità semantica, non un'etichetta di un file `.gz`.

> Per un confronto serio servirebbe una codifica entropica (Huffman / arithmetic / ANS) che usi i cluster come simboli. È nei [miglioramenti possibili](./miglioramenti.md).

## 2 · Niente confronto con `gzip`/`brotli`/`zstd`

Non esiste un `bench` che misura «quanti byte risparmio rispetto a gzip». Il prototipo è esplicitamente esplorativo. Il numero che vedi (`savingsPct`) **non** è confrontabile con strumenti di compressione reali.

## 3 · Costo computazionale O(V²)

Le distanze a coppie nel disco di Poincaré sono costose: con un vocabolario di 5000 parole hai 12,5 milioni di coppie. Il prefiltro `clusterK` (k-NN euclideo) abbassa la cifra a O(V·K), e `approxKNN` la abbassa ancora — ma resta un prototipo, non un sistema su milioni di parole.

> Niente streaming (la matrice di co-occorrenza viene costruita tutta in memoria). Per corpora molto grandi servirebbe un costruttore incrementale.

## 4 · Sensibilità ai parametri

Le manopole importanti (`windowSize`, `clusterThreshold`, `projection`, `randomFeaturesPerDim`) influenzano molto i risultati. Il valore di `savingsPct` può cambiare di decine di punti percentuali al variare della soglia. Senza un seed fisso, la riproducibilità è incompleta.

> L'auto-soglia (percentile / MAD / hybrid) mitiga il problema, ma non lo elimina: su corpus piccoli il campione di distanze è povero e la scelta automatica può fissare una soglia minuscola (≈ 1e-6).

## 5 · Corpora piccoli si comportano male

Sotto le ~200 parole uniche il sistema fatica. Le distanze tendono a collassare vicino a zero, gli istogrammi diventano monomodali, l'auto-soglia degenera. Questo è documentato nel [README inglese](../../README.md) ed è la ragione per cui esiste il *cheat-sheet* dei percentili in [parametri e CLI](./parametri-e-cli.md).

## 6 · Una sola lingua testata davvero

Tutti gli esempi e gli smoke test usano italiano. Il preprocessing è Unicode-aware, quindi *dovrebbe* funzionare anche su altre lingue, ma:

- Niente lemmatizzazione: «correvo» e «corre» sono parole distinte.
- Niente stop-words: gli articoli finiscono nel cluster gigante (vedi `out/clusters/sample.txt__d2__random__k0.clusters.json`).
- Niente analisi morfologica.

## 7 · Dipendenze opzionali per SVD

`projection: 'svd'` richiede `ml-matrix` o `svd-js`. Se non sono installate il sistema decade in modo silenzioso su `random`. Va bene per la robustezza, ma chi cerca «la qualità SVD» potrebbe non accorgersi che non l'ha mai usata.

## 8 · Niente decompressore

Il pipeline è **compressione semantica unidirezionale**: dato un testo, ti dà cluster e una stima. Non c'è un'operazione inversa che, dato il dizionario di cluster, ricostruisca il testo originale.

> Per un decompressore lossless servirebbe almeno: una mappatura parola→ID-cluster, un coder che salvi la sequenza di ID, e un'estrattore canonico per ciascun cluster. Tutto questo è ipotizzato nei [miglioramenti possibili](./miglioramenti.md).

## 9 · Rappresentante = primo indice

Il rappresentante di un cluster è la prima parola che ci finisce dentro. È deterministico ma **non semanticamente significativo**: per uno strumento didattico va bene; per un sistema di sintesi varrebbe la pena calcolare il *medoide* (la parola più centrale).

## 10 · Numeri chiave dal `bench.jsonl` reale

Sul `samples/sample.txt` (Italian, 65 parole uniche), il sistema produce:

- 3 cluster — uno enorme (63 parole), due singoletti.
- Soglia auto = 0.51 (metodo «percentile» scelto dal hybrid).
- `savingsPct` = 54.5%, ma… vedi punto 1: è un termometro.

Letto in un'altra chiave: tre famiglie semantiche emergono, ma due sono troppo piccole per essere utili. È esattamente quello che ci si aspetta da un paragrafo di cinque righe: il prototipo si comporta onestamente.

## Continua

➡️ [Casi d'uso: dove ha senso usarlo davvero](./casi-duso.md)
