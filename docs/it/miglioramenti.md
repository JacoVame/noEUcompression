# Miglioramenti possibili

← [Indice](./README.md)

> Versione visiva: vedi [`docs/diagram/diagrams.md`](../diagram/diagrams.md).

Questa è la roadmap onesta di cosa servirebbe per trasformare il prototipo in qualcosa di più utile. Ogni voce è una sfida vera, non un dettaglio di rifinitura.

## A. Verso una compressione vera

### A1. Codifica entropica

Oggi la compressione è una stima. Per renderla *reale* servirebbe:

1. Codificare ogni parola del testo come ID di cluster (più piccolo del simbolo originale).
2. Applicare un coder entropico (Huffman / arithmetic / ANS) sulla sequenza di ID.
3. Sommare al risultato la dimensione della tabella di mappatura.

Risultato atteso: byte effettivi misurabili, confrontabili con `gzip`.

### A2. Decompressore

Per ricostruire il testo dal flusso compresso, ogni cluster deve avere un *rappresentante canonico* (oggi è il primo indice, troppo arbitrario). Il decompressore poi sostituisce ogni ID con la parola scelta. La compressione sarà **lossy** rispetto al testo originale, ma può essere *reversibile fino a un dizionario*.

### A3. Confronto con i baseline standard

Aggiungere uno script che, dato lo stesso file, riporti:

- byte originali
- byte gzip
- byte brotli
- byte zstd
- byte stimati dal prototipo (con encoder reale)

così da chiudere il cerchio empirico.

## B. Scalabilità

### B1. Costruttore di co-occorrenza streaming

Oggi tutto vive in memoria. Per testi lunghi servirebbe:

- Lettura a blocchi.
- Aggiornamento incrementale della matrice sparsa.
- Eventuale spilling su disco (LMDB, SQLite, o file JSONL).

### B2. SVD troncata / PCA randomizzata

`projection: 'svd'` oggi calcola SVD denso completo (e quindi non scala). Una **truncated SVD** o una **randomized PCA** consentirebbero di lavorare su vocabolari di decine di migliaia di parole con memoria contenuta.

### B3. k-NN approssimato in spazio iperbolico

L'`approxKNN` attuale è un sampling deterministico di candidati. Strutture come **HNSW** o **IVF** possono ridurre drasticamente il costo di trovare vicini iperbolici, mantenendo qualità.

### B4. Accelerazione GPU / WebAssembly

La parte più costosa (distanze a coppie) è ideale per GPU. Una versione WebAssembly farebbe girare il tutto in browser senza dipendenze.

## C. Qualità semantica

### C1. TF-IDF / PMI re-weighting

Le co-occorrenze grezze sopravvalutano le parole frequenti. Una pesatura **TF-IDF** o **PPMI (Positive Pointwise Mutual Information)** dà più voce alle parole rare ma informative.

### C2. Embedding addestrati

Sostituire la proiezione euclidea + scaling con un embedding **iperbolico addestrato** (Poincaré GloVe, hyperbolic Word2Vec, hyperbolic transformers). È un salto di qualità — e di dipendenze — significativo.

### C3. Validazione multi-lingua

Suite di test su corpora in inglese, tedesco, cinese, arabo. Misurare quante volte il sistema trova cluster sensati (es. con cluster gold-standard noti).

### C4. Rappresentanti semantici

Sostituire «primo indice» con il **medoide** del cluster (la parola con minima somma di distanze iperboliche dagli altri membri). Il rappresentante diventa anche un buon riassunto del cluster per il decompressore.

## D. Qualità di vita

- Bindings Python (per chi vuole confrontare con scikit-learn / numpy).
- Plugin per Jupyter Notebook con visualizzazione interattiva del disco.
- Test di non-regressione che fissano cluster attesi su `samples/sample.txt`.
- Modalità `--watch` per il benchmark.

## Come contribuire

Issue e PR sono benvenuti. Idee, segnalazioni, esperimenti: aprire una *discussion* su GitHub è il modo più semplice.

## Continua

➡️ [Glossario dei termini](./glossario.md)
