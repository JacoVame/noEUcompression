<!-- Article-facing material, therefore Italian: this is the one deliberate
     exception to the "agent-facing docs in phase2/ are English" rule, because it
     feeds an Italian article written in a separate Claude project. Numbers are
     language-neutral and all trace to out/ artifacts. -->

# Dossier per carta 02 — "Misurare l'Invisibile"

**Cos'è questo file.** Tutto il materiale verificato che serve a scrivere carta 02,
in un unico documento autonomo: la domanda di partenza, il metodo, i numeri, le
figure, i limiti e le frasi che i numeri autorizzano. Non è una bozza
dell'articolo: è la base di evidenza da cui l'articolo si scrive.

**Provenienza dei numeri.** Ogni cifra qui viene dagli artefatti prodotti dalla
Fase 4 del programma `phase2` e si rigenera con un solo comando (§10). Nessun
numero è stimato, arrotondato a mano o ricordato.

Data: 2026-08-04 · repository `noEUcompression`, branch `phase2` (PR #7) ·
seed set `20260716..20260720`.

---

## 1. La domanda, e da dove viene

Carta 01 — *"Mappare l'Invisibile — SOM e Grandi Modelli Linguistici"* — nel §4
("La questione della curvatura") fa una confessione precisa su questo repository:

> non *apprende* gli embedding (fa una proiezione casuale e un riscalamento
> radiale — usa la metrica curva, ma non colloca le parole per gerarchia)

Nello stesso §4 l'argomento teorico è enunciato: nel piano iperbolico l'area di un
disco cresce esponenzialmente col raggio, quindi «c'è posto per gli alberi», che di
livello in livello si moltiplicano allo stesso modo. Detto con la geometria di
carta 01: nel piatto, vicino all'origine, «le famiglie di concetti si pestano i
piedi».

Carta 02 chiude quella confessione con una misura. La domanda è diventata
falsificabile:

> **Di quanto la geometria iperbolica riduce la distorsione quando si immerge una
> gerarchia semantica nota a bassa dimensione, rispetto alla geometria euclidea,
> a parità di tutto il resto?**

"A parità di tutto il resto" è la parte difficile, ed è dove sta il lavoro.

## 2. Il metro, costruito prima dell'esperimento

L'ordine è deliberato e va raccontato, perché è ciò che rende i numeri credibili:
**l'apparato di misura è stato scritto e congelato prima che esistesse un solo
embedding**. Il metro non può essere modellato dalla cosa che deve misurare.

Tre definizioni, congelate il 2026-08-03:

- **MAP** — la *filtered reconstruction MAP* di Nickel & Kiela (2017): per ogni
  nodo l'insieme d'oro è costituito dai suoi vicini diretti nel grafo (padre e
  figli), ciascuno ordinato contro i soli non-vicini. Un'immersione perfetta vale
  esattamente 1.0.
- **rango medio** — il rango filtrato medio di un vicino d'oro. Perfetto = 1.0.
- **distorsione media** — media su tutte le coppie di |a·d_emb/d_grafo − 1|, alla
  **scala globale `a` che la minimizza**. Il riscalamento non è una cortesia: senza
  di esso il numero misura il raggio arbitrario dell'immersione invece della sua
  forma, e il confronto euclideo-vs-iperbolico diventa un confronto fra unità di
  misura. Il minimo è in forma chiusa (una mediana pesata), quindi nell'apparato
  non entra alcun ottimizzatore e alcun parametro da regolare.

**Il pavimento (controllo nullo).** Punti gaussiani isotropi con metrica euclidea,
d=2, seme 20260716: MAP 0.0188 / rango 181.4 sull'albero sintetico; MAP 0.0064 /
rango 564.7 su WordNet. Qualunque risultato che non batta questi numeri non sta
immergendo nulla.

**I due dataset.**

| dataset | nodi | cos'è |
|---|---|---|
| `synthetic-tree` | 364 | albero bilanciato, ramificazione 3, profondità 5 |
| `wordnet-mammals` | 1170 | `mammal.n.01` e la chiusura dei suoi iponimi |

L'ipernimia di WordNet è un DAG (alcuni synset hanno due ipernimi); una visita in
ampiezza con i figli in ordine di nome la riduce a un albero in modo
deterministico — la prima visita fissa il padre. I due alberi non dipendono dal
seme: il seme cambia l'immersione, mai la verità di riferimento. È questo che rende
verificabile l'affermazione «stesso seme, stesso comando, stessi numeri».

## 3. Il protocollo di equità

Il programma si è dato tre condizioni di fallimento binarie *prima* di guardare i
risultati. Vale raccontarle come tali, perché un articolo che le enuncia dopo
sembra costruito attorno a ciò che ha trovato.

- **F1** — se sull'albero sintetico a d=2 l'immersione iperbolica *non* ottiene una
  distorsione minore di quella euclidea, l'implementazione è rotta: la teoria lo
  garantisce (Sarkar: gli alberi si immergono in H² con distorsione arbitrariamente
  bassa). In quel caso si ferma tutto e non si pubblica nulla.
  → **Non è scattata**: 0.2060 contro 0.3773 (d=2, seme 20260716). Il controllo
  gira automaticamente prima di ogni sweep, ed è lo sweep a essere subordinato a
  esso, non il contrario.
- **F2** — se il confronto usa learning rate o budget di epoche non tarati *per
  geometria*, l'ablazione è iniqua e va invalidata.
  → Il learning rate è tarato per **ogni coppia (geometria, dimensione)**,
  esclusivamente sull'albero sintetico, scegliendo la miglior MAP media sui semi
  {20260716, 12345, 777}, e **congelato prima di qualunque esecuzione su WordNet**.
  Tabella finale: euclideo 0.5 a ogni d; iperbolico 0.005 a d=2, 0.003 a d=5 e
  d=10.
  → **Il fatto che rende F2 sostanziale e non formale**: l'ottimo iperbolico *si
  sposta* con la dimensione. Riusare la costante di d=2 avrebbe penalizzato il lato
  iperbolico esattamente alle dimensioni sotto esame. La MAP media iperbolica
  decresce monotonicamente col learning rate (a d=5: 0.9573 → 0.9530 → 0.9461 →
  0.9357 per lr 0.003 → 0.005 → 0.01 → 0.03; a d=10: 0.9669 → 0.9632 → 0.9552 →
  0.9417), e crolla se si scende troppo (lr 0.001: 0.8065 a d=5, 0.8300 a d=10),
  quindi 0.003 è un massimo interno, non un estremo della griglia.
- **F3** — se i numeri non sono riproducibili da un seme più un solo comando, non
  sono evidenza: sono un aneddoto.
  → §10.

**Il cancello di regressione.** Prima di ogni sweep il driver riproduce i quattro
risultati già pubblicati (Fasi 2 e 3) a d=2 / seme 20260716, su entrambi i dataset,
**alla quarta cifra decimale**, e ricalcola anche i conteggi del vincolo numerico
(149/364 sintetici, 711/1170 WordNet). Se il percorso di calcolo cambia, il
cancello lo dice invece di ereditare la deriva in silenzio.

**Cosa cambia fra le due geometrie, e solo quello.** Identico obiettivo (la loss di
ricostruzione di Nickel & Kiela 2017, con *tutti* i negativi e non un campione),
identica inizializzazione (gaussiana, scala 1e-3), identico `float64`, identico
budget di 6000 epoche. Cambiano due cose: la **metrica** (distanza geodetica
sull'iperboloide, `d(x,y) = arcosh(−⟨x,y⟩_L)`, con i punti vincolati alla falda
superiore) e l'**ottimizzatore** (`RiemannianAdam` di `geoopt` su una
`ManifoldParameter`, contro `Adam`). L'ottimizzazione vive sul modello di **Lorentz**,
non sul disco di Poincaré: la scelta è per stabilità dei gradienti vicino al bordo
(Nickel & Kiela 2018). La dimensione dichiarata è quella **intrinseca**: `--dim 2`
significa H² immerso in R³, cioè gli stessi due gradi di libertà che il baseline
euclideo riceve a d=2.

## 4. Il risultato

`wordnet-mammals`, media ± σ su 5 semi (20260716..20260720), σ con ddof=1:

| d | geometria | lr | MAP | rango medio | distorsione media |
|---|---|---|---|---|---|
| 2 | euclidea | 0.5 | 0.7538 ± 0.0028 | 5.5719 ± 0.6383 | 0.3441 ± 0.0155 |
| 2 | iperbolica | 0.005 | **0.8957 ± 0.0032** | 13.8542 ± 1.4477 | **0.2609 ± 0.0043** |
| 5 | euclidea | 0.5 | **0.9812 ± 0.0019** | **1.0606 ± 0.0124** | **0.2593 ± 0.0074** |
| 5 | iperbolica | 0.003 | 0.9780 ± 0.0009 | 4.1747 ± 0.2240 | 0.2605 ± 0.0009 |
| 10 | euclidea | 0.5 | **1.0000 ± 0.0000** | **1.0000 ± 0.0000** | 0.2927 ± 0.0015 |
| 10 | iperbolica | 0.003 | 0.9853 ± 0.0011 | 2.4549 ± 0.1805 | **0.2606 ± 0.0009** |

Il divario di distorsione (euclidea − iperbolica, positivo = vince l'iperbolica):
**+0.0831 a d=2, −0.0012 a d=5, +0.0320 a d=10**. Non si chiude in modo monotono:
attraversa lo zero a d=5 e torna.

Per riferimento, `synthetic-tree` a d=2 / seme 20260716: euclidea MAP 0.8304,
rango 4.2617, distorsione 0.3773; iperbolica MAP 0.9220, rango 9.5661, distorsione
0.2060.

**Il fatto scomodo, che va raccontato.** Sull'albero sintetico il baseline euclideo
**satura** a d≥5: MAP 1.0000 *e* rango 1.0000 per ogni learning rate della griglia.
L'albero bilanciato smette di discriminare appena la dimensione non è avara, e
resta solo la distorsione a separare le geometrie (ai learning rate congelati:
euclidea 0.2189 a d=5 e 0.2433 a d=10, contro 0.1953 e 0.1959 iperboliche). È per
questo che il set di riferimento è
WordNet e non l'albero sintetico — e la scelta era già stata dichiarata prima di
sapere che il sintetico saturasse.

## 5. Il meccanismo: il crowding, misurato

Carta 01 parla di *crowding* in modo qualitativo. Qui ha un numero. La grandezza è
σ/media della distribuzione delle distanze fra coppie, dopo il riscalamento alla
scala ottimale, confrontata con la stessa grandezza sulla metrica del grafo
(0.2927, costante perché il grafo non dipende dal seme):

| d | euclidea | iperbolica | grafo |
|---|---|---|---|
| 2 | 0.5130 ± 0.0122 | 0.1353 ± 0.0010 | 0.2927 |
| 5 | 0.2929 ± 0.0061 | 0.1188 ± 0.0001 | 0.2927 |
| 10 | 0.1835 ± 0.0004 | 0.1160 ± 0.0003 | 0.2927 |

Le due geometrie sbagliano in direzioni **opposte**, e questo è il cuore
narrativo. A d=2 l'euclidea è *troppo dispersa* (0.5130 contro 0.2927): allunga una
coda di coppie lontanissime, che è il modo piatto di non avere spazio. L'iperbolica
è *troppo compressa* (0.1353): stipa quasi tutte le coppie in un guscio stretto —
alla dimensione 5 la sua distribuzione è ancora più stretta dell'euclidea a
dimensione 10.

Da qui si spiega il paradosso della tabella: **il rango medio iperbolico è peggiore
a ogni dimensione**, mentre la MAP a d=2 è molto migliore. In un guscio stretto i
non-vicini si trovano a una distanza quasi identica a quella del vicino d'oro,
quindi bastano poche collocazioni infelici per rovinare il rango. La MAP media la
precisione su tutto l'insieme d'oro di un nodo; il rango medio è dominato dal vicino
d'oro peggio collocato. Le due metriche possono divergere, e qui divergono: non è un
artefatto che la dimensione ripara — a d=5 e d=10 l'euclidea guida su entrambe.

La curva distorsione-vs-profondità aggiunge il *dove*, e il dettaglio è più
interessante di un semplice «meglio in profondità». A d=2, distorsione media per
profondità dell'estremo più profondo, media sui 5 semi:

| profondità | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| euclidea | 0.596 | 0.617 | 0.511 | 0.402 | 0.367 | 0.343 | 0.326 | 0.329 | 0.307 |
| iperbolica | 1.533 | 1.258 | 0.812 | 0.440 | 0.231 | 0.184 | 0.246 | 0.290 | 0.326 |

L'iperbolica è molto **peggiore sulle coppie superficiali** (1.533 contro 0.596 a
profondità 1), incrocia **fra profondità 4 e 5**, e il suo vantaggio vive in una
**fascia** (5-7, con il minimo 0.184 contro 0.343 a profondità 6) che poi si
esaurisce: a profondità 9 le due curve si sono richiuse e l'iperbolica è
leggermente peggiore (0.326 contro 0.307). È la forma che l'argomento di carta 01
prevede — lo spazio serve dove l'albero si moltiplica — ma va raccontata come
fascia e non come monotonia, perché la coda profonda di WordNet è fatta di rami
lunghi e sottili, dove l'esponenziale dell'area non ha più molto da offrire.

## 6. Le figure

Tre PNG, tutte a media ± σ sui 5 semi, nessuna con un seme scelto a mano. Vivono in
`out/` (rigenerabile, non versionato) con questi nomi:

1. `ablation_map_vs_dimension_wordnet-mammals_dims2-5-10_seedset20260716x5.png`
   — **la figura principale**, quella che il §4 di carta 02 deve contenere. MAP
   contro dimensione intrinseca, barre d'errore ± σ, due curve.
   *Didascalia pronta:* «MAP di ricostruzione filtrata su WordNet-mammals (1170
   synset) contro la dimensione intrinseca. Media ± σ su 5 semi. Il vantaggio
   iperbolico a d=2 (0.8957 contro 0.7538) si annulla a d=5 e si inverte a d=10,
   dove il baseline euclideo ricostruisce perfettamente.»

2. `ablation_distortion_vs_depth_wordnet-mammals_dims2-5-10_seedset20260716x5.png`
   — tre pannelli (d=2, 5, 10), distorsione media per profondità dell'estremo più
   profondo, banda ± σ.
   *Didascalia pronta:* «Distorsione media per profondità. A d=2 le curve si
   incrociano fra profondità 4 e 5: la geometria iperbolica paga sulle coppie
   superficiali e recupera nella fascia intermedio-profonda, dove l'albero si
   moltiplica, per poi richiudersi sulle coppie più profonde. A d=10 le due curve
   quasi coincidono.»

3. `ablation_distance_spread_wordnet-mammals_dims2-5-10_seedset20260716x5.png`
   — distribuzione delle distanze fra coppie, immersione riscalata alla scala dei
   salti, con la distribuzione del grafo in grigio come riferimento.
   *Didascalia pronta:* «Il crowding, misurato. La metrica del grafo ha σ/media
   0.2927. A d=2 l'euclidea è troppo dispersa (0.5130), l'iperbolica troppo
   compressa (0.1353): entrambe sbagliano, in direzioni opposte.»

## 7. Cosa carta 02 non deve affermare

Questa sezione esiste perché carta 01 ne ha una ("Cosa questo articolo *non*
afferma") e perché è il motivo per cui l'affermazione su d=2 può sopravvivere a una
revisione.

- **Non è compressione.** Non c'è alcun rapporto di compressione qui, e nessun
  confronto con `gzip` — entrambi esplicitamente esclusi dagli obiettivi del
  programma. Questa è una misura di geometria su una gerarchia d'oro. La
  riconnessione alla pipeline di compressione è una fase successiva, non ancora
  eseguita (§8).
- **Non è testo naturale.** WordNet è una gerarchia curata da umani, non un corpus.
  La strada delle co-occorrenze (quella del prototipo JS) qui non è toccata: era
  una scelta deliberata, per isolare la domanda geometrica da quella sul segnale.
- **Non è un metodo nuovo.** Non c'è nulla di inedito nel come: l'ottimizzazione
  riemanniana su modello di Lorentz è Nickel & Kiela (2017, 2018), e la SOM
  iperbolica per lo spazio semantico è Ontrup & Ritter (NIPS 2001) — carta 01 già
  li cita, correttamente. Ciò che è nostro è la **misura**: matched per geometria,
  su 5 semi, con controllo nullo pubblicato, cancello di regressione e un comando
  che la rigenera. Il contributo è metodologico e negativo tanto quanto positivo.
- **Non è Poincaré-GloVe**, non c'è addestramento su grandi corpora, e il disco di
  Poincaré compare solo eventualmente in visualizzazione: l'ottimizzazione sta
  sull'iperboloide.
- **Il vincolo numerico va dichiarato, non nascosto.** `MAX_SPATIAL_NORM = 1e4`
  esiste perché l'obiettivo softmax è illimitato nel raggio (gonfiare la scala
  abbassa sempre la loss) e sull'iperboloide le coordinate ambientali crescono come
  cosh(d): senza vincolo la corsa esce da `float64` (a 5500 epoche il residuo del
  vincolo degrada a 2e-4 e la retrazione emette NaN). **Vincola davvero**:
  721.4/1170 nodi vi poggiano a d=2 (61.7%; per seme 711, 709, 738, 722, 727), ma
  solo 83.8 a d=5 (7.2%) e 75.4 a d=10 (6.4%). Non fabbrica il risultato: a d=2 sul
  sintetico la MAP vale 0.9222 / 0.9220 / 0.9222 con vincolo 1e3 / 1e4 / 1e5, e a
  1e5 nessun nodo lo raggiunge. Solo un valore mutilante (1e2, distanza massima
  10.6, sotto il diametro del grafo) cambia la risposta, a 0.7940.
- **Il budget di epoche non è tarato per dimensione.** 6000 per entrambe le
  geometrie a ogni d, che era l'ottimo a d=2 per entrambe. È l'unico asse su cui
  l'ablazione è più debole della lettura ideale di F2, ed è dichiarato come tale.
  La verifica di sensibilità è la Fase 4b, programmata prima della pubblicazione.

## 8. Cosa manca ancora

- **Fase 4b** (in coda, prima della pubblicazione): scansione del budget di epoche
  {1500, 3000, 4500, 6000} ai learning rate congelati, solo sull'albero sintetico,
  per rispondere a «il risultato dipende dalle epoche?». Se carta 02 va in revisione
  tecnica, questa risposta va allegata.
- **Fase 5** (opzionale, bloccata su una premessa reale): l'end-to-end con la
  pipeline di compressione. Il blocco non è tecnico ma di sostanza — la Fase 2-4
  immerge *synset* inglesi di WordNet, la pipeline raggruppa *parole* di un testo, e
  serve una mappatura lemma→synset più un corpus il cui vocabolario intersechi
  davvero il sottoalbero dei mammiferi. Finché quell'intersezione non è misurata,
  carta 02 non può promettere rapporti di compressione.

## 9. Frasi che i numeri autorizzano

Da usare come spina dorsale, ciascuna con la sua evidenza. Se una frase non è in
questa tabella, non è ancora sostenuta.

| Affermazione | Evidenza |
|---|---|
| A dimensione 2 la curvatura paga, e paga molto | MAP 0.7538 → 0.8957 (+18.8% relativo), distorsione 0.3441 → 0.2609 (−24.2%), σ non sovrapposte su 5 semi |
| Il vantaggio è un fenomeno di *bassa* dimensione | da d=5 l'euclidea guida MAP e rango; a d=10 ricostruisce perfettamente (1.0000 / 1.0000) |
| Il vantaggio sulla distorsione però non svanisce | divario +0.0320 a d=10, con σ 0.0015 e 0.0009: piccolo ma fuori dal rumore |
| L'euclidea a d=10 ricostruisce meglio *e* distorce di più | MAP 1.0000 con distorsione 0.2927, contro 0.9853 e 0.2606: ordinare bene i vicini non è preservare le distanze |
| Le due geometrie sbagliano in direzioni opposte | σ/media 0.5130 (euclidea) e 0.1353 (iperbolica) contro 0.2927 del grafo, a d=2 |
| Il prezzo della curvatura è il rango | rango iperbolico peggiore a ogni d: 13.85 vs 5.57, 4.17 vs 1.06, 2.45 vs 1.00 |
| Il vantaggio vive in una fascia di profondità, non cresce con essa | a d=2: profondità 1 → 1.533 (iperbolica) vs 0.596 (euclidea); profondità 6 → 0.184 vs 0.343; profondità 9 → 0.326 vs 0.307, richiuso |
| Il confronto è equo per costruzione | lr tarato per (geometria, dimensione) sul solo albero sintetico e congelato prima di WordNet; l'ottimo iperbolico si sposta (0.005 → 0.003) |
| I numeri non sono un aneddoto | cancello di regressione a quattro decimali su quattro celle; 5 semi; un comando |
| L'albero sintetico non basta come banco di prova | euclidea satura a MAP 1.0000 e rango 1.0000 a d≥5 per ogni lr della griglia |

## 10. Riproducibilità

```
python ablation.py --dataset wordnet-mammals --dims 2 5 10 --seeds 5 --out out/
```

Interprete: quello registrato in `phase2/.venv-path`, con `PYTHONSAFEPATH=1`.
Il set di semi è indicato dall'etichetta `seedset20260716x5`, che denota
esattamente `20260716, 20260717, 20260718, 20260719, 20260720`; la lista è scritta
anche per esteso nel JSON aggregato.

Costo misurato: 3.72 h di calcolo per le 30 esecuzioni del set di riferimento
(~430 s per esecuzione euclidea su WordNet, 500-1100 s per quella iperbolica), su
un host a 22 core, CPU only per scelta. Ogni esecuzione è salvata come checkpoint
in `out/ablation_run_<geometria>_<dataset>_d<dim>_seed<seme>.json` e riusata quando
learning rate ed epoche combaciano, quindi una rigenerazione parziale è
economica. Gli artefatti non sono versionati per decisione: si rigenerano.

Tabella e testo completi: `out/ablation_table_wordnet-mammals_dims2-5-10_seedset20260716x5.md`
e il JSON omonimo, che contiene anche i 30 risultati per singolo seme.

## 11. Una struttura possibile per carta 02

Proposta, non prescrizione. Segue la logica per cui l'articolo è credibile: prima il
metro, poi la misura, poi i limiti.

1. **Da dove riparte** — il §4 di carta 01 e la sua confessione: la metrica curva
   c'era, la gerarchia appresa no. Cosa significa passare da «uso uno spazio curvo»
   a «colloco i concetti in uno spazio curvo».
2. **Misurare vuol dire costruire il metro prima** — l'apparato congelato, le tre
   definizioni, il controllo nullo. Questo capitolo è quello che distingue un
   esperimento da una demo.
3. **Rendere il confronto onesto** — F1, F2, F3 enunciate prima; la taratura per
   geometria e dimensione; il cancello di regressione. Con il dettaglio che l'ottimo
   iperbolico si sposta con la dimensione: senza tararlo si sarebbe misurato un
   handicap invece di una geometria.
4. **Il risultato, con il grafico** — la figura MAP-vs-dimensione, la tabella, e
   subito dopo il fatto scomodo: da d=5 l'euclidea riprende il comando sulla
   ricostruzione. La tesi non è «l'iperbolico vince», è «la curvatura paga dove la
   dimensione è avara».
5. **Il crowding, misurato** — la figura degli spread e la doppia direzione
   dell'errore; il paradosso rango-contro-MAP spiegato dal guscio stretto; la curva
   in profondità come conferma localizzata dell'argomento di carta 01.
6. **Cosa non afferma** — §7 di questo dossier, praticamente per intero.
7. **Cosa verrebbe dopo** — la Fase 5 e la sua premessa non risolta, detta come
   lacuna e non come promessa. E il comando, perché chi legge possa rifarlo.
