# FAQ — Domande frequenti

← [Indice](./README.md)

### È un compressore di file?

No. È una **stima di compressione semantica**. Non produce un `.gz`. Per uno schiacciamento reale dei byte usa `gzip`, `brotli` o `zstd`. Vedi [limitazioni](./limitazioni.md) e [miglioramenti](./miglioramenti.md).

### Perché si chiama «non EU»?

«Non EU» = *non-Euclidean*. Niente regolamenti, niente normative: è un nome scherzoso per dire «non euclideo».

### Funziona solo in italiano?

Il preprocessing è Unicode-aware, quindi **tecnicamente** funziona in qualunque lingua scritta con lettere. Tutti gli esempi e i test sono però in italiano. Su lingue molto morfologiche (italiano stesso, tedesco, finlandese) la mancanza di lemmatizzazione si fa sentire.

### Devo installare qualcosa?

No. Funziona con **Node.js 16+**, senza dipendenze obbligatorie. Le librerie `ml-matrix` e `svd-js` servono solo per la proiezione SVD e sono opzionali.

### Posso vederlo girare senza scrivere codice?

Sì:
1. `node compressionTest.js` per il demo testuale.
2. Apri [`docs/diagram/pipeline.html`](../diagram/pipeline.html) in un browser per la pipeline animata.
3. Apri [`presentation/it/index.html`](../../presentation/it/index.html) per la presentazione.

### Cos'è il «disco di Poincaré»?

Un cerchio di raggio 1 in cui la geometria non è quella di Euclide ma quella iperbolica. Vicino al bordo lo spazio si dilata all'infinito, quindi è perfetto per rappresentare strutture ad albero — come il vocabolario di una lingua. Vedi [matematica soft](./matematica-soft.md).

### Perché tre cluster sul `sample.txt`?

Perché su un paragrafo da cinque righe la maggior parte delle parole condivide un contesto simile (cluster grande), e poche parole rare (`pensieri`, `regolare`) finiscono in cluster propri. È esattamente quello che ci si aspetta.

### Come scelgo `clusterThreshold`?

La risposta breve: lascia attivo `autoThreshold: true`, metodo `hybrid`. La risposta lunga è in [parametri e CLI](./parametri-e-cli.md), sezione *Suggerimenti rapidi per la soglia*.

### Posso paragonare i risultati con `gzip`?

Non con `savingsPct`, no — sono due cose diverse. Per un confronto serio servirebbe il decompressore + un coder entropico (vedi [miglioramenti](./miglioramenti.md), sezione A).

### Il risultato è ripetibile?

Sì, dato un `seed` fisso. Senza `seed`, il PRNG fallback può produrre vettori leggermente diversi.

### Funziona offline?

Sì. Tutto il codice e tutti i documenti, inclusa la pipeline animata e le slide, girano in locale senza accesso a Internet (la presentazione carica reveal.js da CDN, ma può essere vendorizzata se serve).

### Posso usarlo per scopi commerciali?

La licenza è MIT, quindi sì — ma considera che è un prototipo di ricerca. Non è ottimizzato, né validato in produzione.

### Chi lo ha scritto?

Gianluca Gagliano. Riconoscimenti speciali ai professori Vito Di Gesù e Domenico Tegolo, che con il loro lavoro hanno seminato le idee da cui questo progetto prende ispirazione.

### Continua

➡️ [Il racconto: cosa significa tutto questo, in prosa](./racconto.md)
