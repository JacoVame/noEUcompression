# Nota di cantiere — fase 2

← [Indice](./README.md) · [Il racconto](./racconto.md) (carta 01)

## 1. La domanda che carta 01 lasciava aperta

Il racconto della prima carta poneva una domanda qualitativa: se le parole di un testo, invece di stare in uno spazio piatto, vengono mappate in uno spazio curvo — il disco di Poincaré — la geometria iperbolica riesce a catturare meglio le gerarchie semantiche della lingua? Carta 01 mostrava l'idea con un prototipo giocattolo, senza misurarla.

Carta 02 — questa fase 2 del repository — l'ha misurata. Un harness riproducibile (`eval.py`, congelato dopo la fase 1) confronta un embedding euclideo appreso con un embedding iperbolico appreso (varietà di Lorentz, via `geoopt`), sulla stessa gerarchia — un sottoinsieme di WordNet limitato ai mammiferi — con learning rate scelti per ciascuna geometria, cinque seed, media ± σ ovunque.

## 2. I due risultati che contano

**La curvatura paga solo a d=2, e la classifica si inverte da d=5.** A dimensione 2 l'iperbolico vince senza ambiguità: MAP 0.7538 → 0.8957, distorsione media 0.3441 → 0.2609. Da d=5 in su è l'euclideo a vincere sulla ricostruzione: a d=10, MAP 1.0000 / rango medio 1.0000 contro 0.9853 / 2.4549 dell'iperbolico, mentre sulla distorsione il vantaggio euclideo non è monotono (a d=5 euclideo 0.2593 contro lorentz 0.2605, quasi un pareggio; a d=10 torna avanti lorentz, 0.2606 contro 0.2927). Questa inversione non porta con sé alcuna riserva sul budget di addestramento: una scansione dedicata (fase 4b) ha delimitato dall'alto il plateau del lato iperbolico sopra le 6000 epoche, quindi più addestramento non la ribalterebbe.

**Il secondo risultato riguarda la pipeline a valle, e prima di ogni suo numero va detto quanto testo descrivono: 4616 token su 297.697 — l'1,55% del corpus.** Riconnessa agli embedding appresi (fase 5), quella pipeline calcola un rapporto — il tipo di numero che a prima vista sembra un indice di compressione — che risulta anti-correlato con la fedeltà semantica. Sull'intera griglia (3 lati × 12 percentili), r(rapporto, salti nella gerarchia d'oro) vale −0,841 a d=2, −0,992 a d=5, −0,984 a d=10. Il rapporto migliore delle tre configurazioni (0,5633) appartiene alla baseline js-cooccorrenza, l'embedding più degenerato dello studio — l'84,9% delle sue distanze a coppie è esattamente zero. In bit: lunghezza del codice più perdita residua sta a 7,967–8,885 bit/token a d=2, 8,136–9,950 a d=5, 8,135–10,004 a d=10, contro i 9,00 bit/token dello stesso codice prima di ogni raggruppamento e i 5,696 bit/token di entropia grezza dello stesso flusso di tipi — i bit si spostano, non svaniscono, e in 18 celle il bilancio è peggiore che non raggruppare nulla (9,95 / 10,00 bit/token contro 9,00). Una verifica indipendente per round trip (codifica→decodifica) conferma il conteggio dei bit a 1,066e-14 bit/token su tutte le 180 celle controllate (tolleranza dichiarata 1e-9) — il conteggio è verificato — ma nel punto operativo più fedele (p=0,01) il decoder recupera la parola esatta solo lo 0,6811 delle volte per l'euclideo, lo 0,6250 per il lorentziano e lo 0,5138 per la baseline js-cooccorrenza, e appena 0,2867 nel punto con il rapporto migliore (lorentz, p=0,35).

## 3. Perché si chiama «quantizzazione semantica», e perché i file dicono ancora «compress»

La prosa del repository non chiama più questa pipeline compressione: la chiama **quantizzazione semantica** — i tipi vengono quantizzati su id di cluster — e il piano di lettura onesto è **rate–distortion**, bit per token misurati contro il danno semantico, senza scambiare l'uno per l'altro in silenzio. I nomi dei file (`compress.py`, `out/compress_*`) restano quelli storici: ogni comando di rigenerazione stampato in questo repository dipende da quelle stringhe esatte, e cambiarle invaliderebbe la riproducibilità. Sono etichette, non affermazioni.

## 4. La figura

![Rate-distortion, wordnet-mammals, d=2/5/10](../../phase2/report/rate_distortion_wordnet-mammals_d2-5-10_seedset20260716x5.png)

108 celle (3 lati × 12 percentili × 3 dimensioni). Pannello sinistro: lunghezza del codice contro perdita residua, con le diagonali a costo totale costante e i due punti di riferimento a perdita zero. Pannello destro: lunghezza del codice contro salti nella gerarchia d'oro, con la linea di riferimento «cieca alla gerarchia».

## 5. Cosa questa nota non afferma

Non è un confronto con `gzip` o con un codificatore entropico: quel confronto è escluso per scelta di progetto, e l'entropia di 5,696 bit/token compare solo per mostrare quanto sia largo il codice a lunghezza fissa dichiarato, mai come rivale. Non è una prova che la geometria iperbolica sia «migliore»: vince solo nel regime di dimensione estrema (d=2), su questa gerarchia. Un confronto a numero di cluster forzato uguale (fase 5e) ha confermato una previsione pre-registrata — a d=10 l'euclideo produce meno salti nella gerarchia d'oro del lorentziano a ogni livello della scala, con bande a una σ disgiunte solo al livello K=40 (4,856 contro 6,506): una conferma netta su quattro, non quattro conferme indipendenti. E non è un'affermazione di compressione nel senso comune: il 98,45% dei token del corpus resta fuori mappatura, quindi ogni rapporto descritto qui misura l'1,55% del testo, e nient'altro.

## 6. Dove vivono le prove

I numeri sono in [`FINDINGS.md`](../../phase2/FINDINGS.md) e nelle sezioni Fase-4, Fase-5, Fase-5d e Fase-5e di [`phase2/README-fase2.md`](../../phase2/README-fase2.md). Il metodo — embedding di Lorentz, non il disco di Poincaré, per la stabilità del gradiente — viene da Nickel & Kiela (2017, 2018) e da Ontrup & Ritter (2001); quello che è nostro è la misura. La figura si rigenera con:

```
python compress.py --figure rate-distortion --out report/
```

---

← [Indice](./README.md)
