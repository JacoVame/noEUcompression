# La pipeline in otto passi

← [Indice](./README.md)

> 🎬 Vuoi vederla in movimento? Apri la [pipeline animata](../diagram/pipeline.html). Qui sotto la stessa cosa, raccontata.

## Mappa rapida

| # | Stadio | Cosa fa | File |
|---|--------|---------|------|
| 1 | Preprocess | Normalizza Unicode, tokenizza | `compressionTest.js:90–95` |
| 2 | Co-occurrence | Conta chi compare vicino a chi | `compressionTest.js:98–138` |
| 3 | Embedding | Riduce le dimensioni | `compressionTest.js:141–291` |
| 4 | Poincaré | Sposta i punti nello spazio curvo | `compressionTest.js:279–287` |
| 5 | Distanza | Calcola la distanza iperbolica | `compressionTest.js:294–313` |
| 6 | Auto-soglia | Sceglie da sola il taglio per i cluster | `compressionTest.js:453–573` |
| 7 | Clustering | Raggruppa con union-find | `compressionTest.js:575–659` |
| 8 | Stima | Calcola un *ratio* di compressione | `compressionTest.js:661–676` |

---

## 1 · Preprocess — pulizia e tokenizzazione

Il testo grezzo passa attraverso una **normalizzazione Unicode NFKC** (per uniformare diacritici, legature, varianti tipografiche) e poi viene spezzato in parole. La regex usata è `/\p{L}{2,}/gu`: significa «sequenze di lettere Unicode di almeno due caratteri». Punteggiatura, cifre, simboli e lettere singole vengono scartati.

Si finisce con una lista ordinata di token. Esempio sul nostro `samples/sample.txt`:

```
[gregorio, samsa, si, svegliò, una, mattina, da, sogni, agitati, ...]
```

Senza questo passo, qualunque cosa fatta dopo sarebbe rumore.

## 2 · Co-occurrence — chi compare vicino a chi

Si scorre il testo con una **finestra scorrevole** di raggio `windowSize` (di default 3). Per ogni parola al centro della finestra, si contano quante volte le altre parole della finestra le compaiono accanto. Il risultato è una **matrice sparsa**: ogni riga è una `Map<colonna, conteggio>`. Se due parole non si sono mai sfiorate, la cella resta vuota — niente memoria sprecata.

Due varianti del conteggio:

- **uniform**: ogni vicino vale 1.
- **distance**: i vicini più lontani contano meno (`1 / (1 + |i − j|)`).

Il vocabolario è limitato per frequenza a `maxVocab` parole (default 5000): le parole troppo rare vengono escluse, perché farebbero solo rumore statistico.

## 3 · Embedding — comprimere il vocabolario in poche dimensioni

Ora ogni parola è una riga sparsa lunga *n*. Servono vettori più piccoli, di dimensione `dimension` (in genere 2 o 3), così possiamo (a) calcolare distanze in tempi ragionevoli, (b) eventualmente disegnarli.

Tre strategie disponibili:

- **`random`** (default, robusta): per ogni dimensione del vettore di output, si somma il conteggio su un sotto-insieme casuale di colonne. È rapida, deterministica con un `seed`, e tiene bene anche su righe sparse.
- **`firstD`**: si prendono le prime *D* colonne della matrice. Storica, semplice, va bene quando si vuole riprodurre il comportamento iniziale.
- **`svd`**: SVD denso sulla matrice (per vocabolari piccoli, fino a `svdMaxN`, default 800). Richiede una libreria opzionale (`ml-matrix` o `svd-js`); se manca, il sistema decade in modo gentile su `random` senza interrompere.

Ogni vettore viene poi normalizzato (riga / somma riga) e finisce in `[0,1]^d` o giù di lì.

## 4 · Disco di Poincaré — entriamo nello spazio curvo

I vettori euclidei di prima vengono **scalati radialmente** così da finire dentro il disco unitario:

```
x_poincaré = x · min(0.85 / ‖x‖, 1.0)
```

Il fattore 0.85 evita che le parole finiscano troppo vicino al bordo (dove la geometria iperbolica ha singolarità). Tutti i punti soddisfano `‖x‖ < 1`. Da fuori sembrano semplicemente spostati; da dentro la metrica del disco trasforma il loro significato di «vicinanza».

## 5 · Distanza iperbolica — Möbius in azione

Per misurare quanto due punti `u`, `v` sono lontani nel disco si usa la **metrica di Möbius**:

```
d_H(u,v) = acosh(1 + 2 · ‖u − v‖² / ((1 − ‖u‖²)(1 − ‖v‖²)))
```

Quello che importa intuitivamente:

- Vicino al centro la distanza si comporta quasi come euclidea.
- Vicino al bordo, una piccola differenza euclidea diventa un'enorme differenza iperbolica. È l'effetto «zoom»: il disco si srotola e il bordo diventa infinito.

Per la stabilità numerica il codice applica piccoli *epsilon clamps* per evitare divisioni vicino a zero.

## 6 · Auto-soglia — un metro che si calibra da solo

Per decidere se due parole stanno «abbastanza vicine» da finire nello stesso cluster servirebbe scegliere a mano una soglia. Il prototipo offre una scelta automatica, basata su un **campione di distanze a coppie** (massimo `autoThresholdSample`, default 3000).

Tre metodi:

- **`percentile`**: la soglia è un percentile (default p35). Semplice, robusto su distribuzioni regolari.
- **`mad`**: usa una *Median Absolute Deviation*: `soglia = mediana − K · 1.4826 · MAD`. Tiene conto degli outlier in modo robusto.
- **`hybrid`**: sceglie automaticamente. Se la coda alta della distribuzione è molto lontana dal centro (p95 lontana dalla mediana rispetto a σ), preferisce MAD; altrimenti percentile.

Se attivi `autoThresholdHistogramBins`, il sistema sputa anche un istogramma delle distanze sampleate. Tutti questi numeri (mediana, MAD, σ, percentili, metodo scelto) vengono restituiti nel JSON di benchmark se passi `--autoStats`.

Su `samples/sample.txt` il sistema sceglie metodo `percentile`, soglia ≈ 0.51, mediana ≈ 0.68, p95 ≈ 1.49.

## 7 · Clustering — union-find

Ora costruiamo un grafo: ogni parola è un nodo, due nodi sono collegati se la loro distanza iperbolica è sotto soglia. Estrarre i cluster significa trovare le **componenti connesse** di questo grafo. Si usa **union-find** (con path compression): ordine dei dati irrilevante, risultato deterministico.

Costo nudo: O(V²) confronti a coppie. Si può mitigare con un **prefiltro k-NN** (`clusterK > 0`): si calcolano i k vicini in spazio euclideo prima e si valuta la distanza iperbolica solo su quelle coppie. Costo: ~O(V·K). Ulteriore ottimizzazione: k-NN approssimato, sampling deterministico (`approxKNN`, `approxKCandidates`).

Per ogni cluster si sceglie un **rappresentante**: oggi è semplicemente il primo indice (la parola che entra prima nel grafo). Il `centro` è la media vettoriale dei membri.

Sul nostro paragrafo italiano, il sistema trova **3 cluster**: uno enorme (63 parole, articoli + preposizioni + verbi comuni, rappresentato da «la»), e due singoletti («pensieri», «regolare»).

## 8 · Stima di compressione — un termometro, non un codec

Modello giocattolo:

```
size_originale  = numero totale di parole
size_compresso  ≈ numero di cluster + 0.5 · numero totale di parole (overhead di mappatura)
ratio           = size_compresso / size_originale
savings (%)     = (1 − ratio) · 100
```

Sul `sample.txt`: ratio ≈ 0.455, savings ≈ 54.5%.

Da prendere come quello che è: una **stima della densità semantica**. Più i cluster sono pochi e ben popolati, più la stima scende. Per un paragone serio con `gzip` servirebbe una codifica entropica vera (vedi [miglioramenti](./miglioramenti.md)).

## Continua

➡️ [Geometria iperbolica con poche formule](./matematica-soft.md)
