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

Data: 2026-08-04 · repository `noEUcompression`, commit [`c7f95bc`](https://github.com/JacoVame/noEUcompression/commit/c7f95bc35de81022778c6ceba28da9462fea581a) (PR #7, branch since deleted) ·
seed set `20260716..20260720`. **Aggiornato il 2026-08-04 con la Fase 4b e il suo
addendum** (§4b): la scansione del budget di epoche è stata eseguita, ha prodotto
prima una riserva sul ribaltamento a d≥5 e poi — estesa sopra 6000 lo stesso
giorno — l'ha **ritrattata**: 6000 sta su un plateau racchiuso, quindi la riserva
cade. Si legga §4b, addendum compreso, prima di §4.
**Aggiornato il 2026-08-11 con le Fasi 5, 5b, 5c e 5d** (§4c): la riconnessione
alla pipeline di compressione — che §8 dichiarava bloccata su una premessa — è
stata eseguita e misurata. Il suo esito non è un rapporto di compressione: è un
risultato *sulla metrica*, e riscrive il primo punto di §7 e il secondo di §8.

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
  → **Dove F2 resta scoperta, e adesso lo sappiamo di quanto**: l'altro asse che
  F2 nomina — il budget di epoche — *non* è tarato per dimensione. La Fase 4b l'ha
  scansionato: le due geometrie vogliono budget diversi alla stessa dimensione
  (1500 l'euclidea, 6000 l'iperbolica), ma il budget usato è racchiuso da entrambi
  i lati, quindi F2 è limitata e non aperta. §4b, addendum compreso.
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

## 4b. Il budget di epoche, scansionato (Fase 4b, 2026-08-04)

Il §7 dichiara che il budget di epoche non è tarato per dimensione: 6000 per
entrambe le geometrie a ogni d, perché 6000 era l'ottimo a d=2 per entrambe. La
Fase 4b l'ha scansionato su {1500, 3000, 4500, 6000}, **solo sull'albero
sintetico** (il set di riferimento è speso e non può informare una manopola), ai
learning rate congelati — si muove un asse, non due — sui semi {20260716, 12345,
777}, media ± σ. **d=2 non è stato riscansionato**: il suo budget era già stato
cercato sullo stesso intervallo *insieme* al learning rate nelle Fasi 2 e 3, sugli
stessi semi, ed è pubblicato.

**Il primo esito non è quello comodo: il budget sembra vincolare.** (Ritrattato
dall'addendum in fondo a questa sezione — la tabella qui sotto resta valida, la sua
interpretazione no.)

| d | geometria | metrica | 1500 | 3000 | 4500 | 6000 (Fase 4) |
|---|---|---|---|---|---|---|
| 5 | euclidea | MAP | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 |
| 5 | euclidea | distorsione | 0.2208 ± 0.0048 | 0.2198 ± 0.0042 | 0.2193 ± 0.0040 | **0.2189 ± 0.0038** |
| 5 | iperbolica | MAP | 0.7793 ± 0.0120 | 0.8281 ± 0.0023 | 0.9129 ± 0.0022 | **0.9573 ± 0.0016** |
| 5 | iperbolica | distorsione | 0.2034 ± 0.0029 | 0.1922 ± 0.0020 | **0.1884 ± 0.0016** | 0.1953 ± 0.0013 |
| 10 | euclidea | MAP | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 |
| 10 | euclidea | distorsione | **0.2387 ± 0.0006** | 0.2409 ± 0.0007 | 0.2423 ± 0.0007 | 0.2433 ± 0.0007 |
| 10 | iperbolica | MAP | 0.8045 ± 0.0104 | 0.8405 ± 0.0069 | 0.9566 ± 0.0046 | **0.9669 ± 0.0025** |
| 10 | iperbolica | distorsione | 0.1956 ± 0.0066 | 0.1893 ± 0.0044 | **0.1861 ± 0.0034** | 0.1959 ± 0.0028 |

**La prima risposta, in una frase — poi ritrattata lo stesso giorno, si legga
l'addendum sotto prima di citarla.** Ai learning rate congelati, 6000 epoche non
sono un ottimo interno per il lato iperbolico a nessuna delle due dimensioni — la
MAP media guadagna ancora +0.0444 (d=5) e +0.0103 (d=10) negli ultimi 1500 epoche,
contro σ fra i semi di 0.0016 e 0.0025, quindi 6000 sembrava un **estremo non
racchiuso** della scansione e non un picco — mentre il lato euclideo non può
rispondere sulla MAP, essendo saturo a 1.0000 già da 1500 epoche su questo albero.

**Tre fatti, non tre note a piè di pagina.**

- **Le due geometrie vogliono budget diversi alla stessa dimensione**, che è
  esattamente ciò di cui parla F2. Il budget più economico indistinguibile dal
  miglior valore della cella (stessa regola a un σ) è **1500 per l'euclidea** a
  entrambe le d e **6000 per l'iperbolica** a entrambe. Il budget condiviso è il
  **soffitto della geometria che perde e il surplus di quella che vince**. (Che
  6000 sia anche *sufficiente* per l'iperbolica non era dimostrato da questa
  scansione, essendone il tetto; l'addendum sotto lo dimostra.)
- **Sulla distorsione 6000 è oltre il minimo in tre celle su quattro**: iperbolica
  d=5 (0.1884 a 4500 → 0.1953 a 6000), iperbolica d=10 (0.1861 a 4500 → 0.1959),
  euclidea d=10 (0.2387 a 1500 → 0.2433). Tutti e tre i divari superano la σ di
  entrambi gli estremi. Solo l'euclidea a d=5 ha il minimo a 6000. Quindi MAP e
  distorsione chiedono spostamenti **opposti** del budget sul lato iperbolico: più
  epoche per la MAP, meno per la distorsione.
- **La MAP non informa sull'euclidea sopra d=2 su questo albero** — 1.0000 a ogni
  budget, la stessa saturazione già incontrata dalla ricerca del learning rate. Il
  suo verdetto piatto non è prova che il budget le vada bene: è prova che l'albero
  sintetico smette di misurare la ricostruzione. È la stessa ragione per cui il set
  di riferimento è WordNet.

### Addendum alla Fase 4b (2026-08-04, stesso giorno) — il buco sopra 6000 è chiuso, e la lettura di sopra è ritrattata

Il comando che la prima scansione dichiarava di **non** voler eseguire è stato
autorizzato dal PM ed eseguito senza modifiche: stesso banco (`synthetic-tree`),
learning rate congelati, semi di taratura {20260716, 12345, 777}, un solo asse in
movimento, set di riferimento intatto. Entrambi i cancelli del driver sono passati
alla cifra prima della scansione; le dodici celle a 6000 epoche sono state riusate
dalla ricerca del learning rate. 24 esecuzioni nuove, 35,8 minuti.

| d | geometria | metrica | 6000 (Fase 4) | 7500 | 9000 |
|---|---|---|---|---|---|
| 5 | euclidea | MAP | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 |
| 5 | euclidea | distorsione | 0.2189 ± 0.0038 | 0.2186 ± 0.0036 | 0.2184 ± 0.0035 |
| 5 | iperbolica | MAP | 0.9573 ± 0.0016 | **0.9578 ± 0.0016** | 0.9577 ± 0.0014 |
| 5 | iperbolica | distorsione | **0.1953 ± 0.0013** | 0.1980 ± 0.0012 | 0.1981 ± 0.0013 |
| 10 | euclidea | MAP | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 | 1.0000 ± 0.0000 |
| 10 | euclidea | distorsione | **0.2433 ± 0.0007** | 0.2442 ± 0.0008 | 0.2450 ± 0.0008 |
| 10 | iperbolica | MAP | 0.9669 ± 0.0025 | **0.9683 ± 0.0026** | 0.9680 ± 0.0026 |
| 10 | iperbolica | distorsione | **0.1959 ± 0.0028** | 0.1996 ± 0.0027 | 0.1997 ± 0.0026 |

**La risposta buona, in una frase.** L'argmax della MAP iperbolica è **interno**, a
7500 per entrambe le dimensioni, ma non è un picco degno del nome: 6000 gli sta
sotto di +0.0005 (d=5) e +0.0014 (d=10), entrambi *dentro* la σ fra semi
all'argmax (0.0016 e 0.0026), e il passo successivo scende (−0.00005 e −0.0002 da
7500 a 9000). **6000 sta su un plateau, ora racchiuso da sopra: il budget di
epoche è limitato, non vivo, e la conclusione della Fase 4 non ne dipende.**

**Cosa questo ritratta.** L'extrapolazione della prima scansione era sbagliata, e di
molto: dai +0.0444 (d=5) e +0.0103 (d=10) attribuiti agli ultimi 1500 epoche, i
1500 *successivi* hanno comprato +0.0005 e +0.0014 — circa 90 e 7 volte meno. Il
guadagno non è proseguito: è crollato appena passato il valore congelato.
Extrapolare una singola differenza finita era l'errore, ed è registrato invece che
fatto sparire.

**Cosa questo libera, e cosa carta 02 può quindi scrivere.** Il ribaltamento a d≥5
**non è più a rischio di budget**. I divari di MAP su WordNet a d≥5 (0.0032 e
0.0147) sono ora **più grandi** dei guadagni residui misurati (0.0005 e 0.0014),
quindi il ribaltamento non si spiega con un addestramento iperbolico incompiuto.
La riserva sul budget **cade**: la frase sul ribaltamento a d≥5 si scrive senza di
essa. Resta l'unica riserva che c'era già prima e che non riguarda le epoche: la
scansione vive sull'albero sintetico, e il trasferimento a WordNet è un'inferenza
fra dataset.

**Cosa resta in piedi.** Le due geometrie continuano a volere budget diversi — 1500
per l'euclidea, 6000 per l'iperbolica — e la novità è solo che l'iperbolica non
vuole *più* di 6000: F2 è ora limitata da entrambi i lati invece che aperta sopra.
Sulla distorsione la storia non cambia e continua a puntare nell'altra direzione:
per l'iperbolica 6000 è il minimo *dentro questa finestra* e più epoche peggiorano
(0.1953 → 0.1980 a d=5; 0.1959 → 0.1996 a d=10), coerente col vero minimo a 4500
trovato dalla prima scansione, e l'euclidea a d=10 continua a degradare
(0.2433 → 0.2450). MAP e distorsione vogliono ancora spostamenti opposti del
budget sul lato iperbolico: questa scansione limita quanto la MAP possa chiedere,
non riconcilia le due.

**Una riga del referto generato non va citata da sola.** Il paragrafo F2 del driver
conclude che «i due lati sono soddisfatti dallo stesso budget a ogni d scansionata»,
vero solo dentro una finestra il cui **pavimento è 6000** — il budget più economico
che quella finestra possa nominare. La lettura congiunta delle due scansioni è che i
budget richiesti sono diversi (euclidea 1500, iperbolica 6000) e limitati sopra.

## 4c. La pipeline riconnessa, e la metrica che premia il degrado (Fasi 5-5d, 2026-08-05 → 2026-08-11)

§8 dichiarava la Fase 5 «opzionale, bloccata su una premessa reale»: serviva una
mappatura lemma→synset e un corpus il cui vocabolario intersecasse davvero il
sottoalbero dei mammiferi. **La premessa è stata risolta e, soprattutto, misurata**,
e la fase è stata eseguita in quattro tempi: 5 (d=2), 5b (d=5 e d=10), 5c (il
decodificatore e il suo cancello di andata-e-ritorno), 5d (il nome corretto e il
referto). L'esito non è il rapporto di compressione che §8 non poteva promettere.
È un risultato **sulla metrica stessa**, e per carta 02 vale più del rapporto.

Referto completo, in inglese, con ogni cifra legata al suo artefatto:
[`../FINDINGS.md`](../FINDINGS.md).

**Prima di qualunque numero: la copertura.** Ogni cifra di questa sezione descrive
**l'1,55% del corpus**, e nient'altro.

| quantità | valore | artefatto |
|---|---|---|
| token codificati (N) | 4616 su 297_697 (**1,55%**) | `out/compress_mapping_pg2300_wordnet-mammals.json` |
| token scartati perché non mappati | 293_081 (98,45%) | idem |
| tipi mappati (V) | 259 su 13_565 | idem |
| synset raggiunti = nodi raggruppati | 166 su 1170 (14,2%) | idem |
| entropia dei tipi sul flusso mappato | 5,696 bit/token | idem |

Corpus: Darwin, *The Descent of Man* (Project Gutenberg #2300), sha256 fissato e
verificato a ogni esecuzione. Un rapporto calcolato sull'1,55% di un testo è
un'affermazione su quell'1,55%.

**Il risultato in una frase.** *Il rapporto che questa pipeline riporta è una
metrica che premia il degrado*: su tutta la griglia misurata, migliore è il
rapporto, più lontano viaggiano le fusioni nella gerarchia d'oro — e il rapporto
migliore fra i tre lati appartiene all'embedding **più degenere** dello studio.
Nessuno stava barando la metrica: la metrica era barabile.

**(a) Il rapporto anticorrela con la fedeltà.** Pearson *r* su ogni cella (lato,
percentile) della griglia — 3 lati × 12 percentili = **36 celle per dimensione**,
ciascuna media sui 5 semi:

| d | r(rapporto, salti d'oro) | r(rapporto, quota di token del cluster più grande) | celle |
|---|---|---|---|
| 2 | **−0,841** | **−0,949** | 36 |
| 5 | **−0,992** | **−0,712** | 36 |
| 10 | **−0,984** | **−0,654** | 36 |

Artefatti: `out/compress_wordnet-mammals_d{2,5,10}_seedset20260716x5.json`,
ricalcolabili con `compress.ratio_fidelity_correlation(<aggregato>)`. Il
`ratio` scende quando il codice si accorcia, quindi un *r negativo* contro i salti
d'oro dice: **le celle col rapporto migliore sono quelle le cui fusioni attraversano
più salti nella gerarchia congelata**. Lo stesso segno vale contro la quota di
token del cluster più grande — i rapporti migliori sono quelli che rovesciano più
corpus in un solo secchio.

**Le dimensioni più alte non indeboliscono il risultato: lo sdoppiano.**
L'anticorrelazione sui salti d'oro *rafforza* a d=5 (−0,992) e d=10 (−0,984);
quella sulla quota del cluster più grande *si attenua* (−0,712, −0,654). Il
risultato-titolo è il primo, ed è quello che sopravvive alla scansione dimensionale.

*Cautela definizionale, che muove le cifre e non la conclusione:* il verbale della
Fase 5 e il riassunto della 5b citano per d=2 la coppia **−0,88 / −0,92**, calcolata
sul `ratio (no ceil)` a bit frazionari, mentre le cifre di d=5 e d=10 usano il
`ratio` intero a larghezza fissa. Ricalcolata alla pari sul rapporto intero, d=2
legge **−0,841 / −0,949**. Stesso segno, stesso ordine di grandezza, stessa
conclusione: si spostano due decimali. La tabella sopra è il confronto alla pari.

**Le tre celle che rendono concreta l'astrazione** (d=2):

| cella | K | rapporto | salti d'oro | cluster più grande | che cos'è |
|---|---|---|---|---|---|
| lorentz, p=0,35 | 6,40 ± 2,65 | **0,3286 ± 0,1150** | 7,49 ± 0,12 | **0,8734** | miglior rapporto del lato appreso |
| js-cooccurrence, p=0,01 | 19,20 ± 8,26 | **0,5633 ± 0,1150** | 7,65 ± 0,02 | 0,5129 | miglior rapporto dei tre lati |
| euclidea, p=0,01 | 85,20 ± 1,72 | 0,8214 ± 0,0000 | **1,74 ± 0,06** | 0,3388 | fusioni più fedeli, rapporto peggiore |

- **Il miglior rapporto dei tre lati appartiene all'euristica non appresa.** Nel
  baseline js-cooccurrence l'**84,9% ± 7,9%** delle distanze fra coppie è
  *esattamente zero* a d=2 — la sua proiezione a 16 feature casuali manda
  all'origine ogni riga di massa piccola — quindi il suo raggruppamento è «fondi i
  punti coincidenti», e le sue fusioni attraversano 7,65 ± 0,02 salti contro il
  **riferimento cieco alla gerarchia, 7,654**. È l'embedding più degenere dello
  studio e vince la metrica.
- **Il miglior rapporto del lato iperbolico mette l'87,3% dei token in un solo
  cluster**, con fusioni a 7,49 salti: statisticamente indistinguibile da un
  raggruppamento che ignori la gerarchia.
- Il riferimento 7,654 è la media dei cammini minimi su tutte le coppie dei
  medesimi 166 synset nella gerarchia congelata, **ri-derivata** (non trascritta)
  dal comando della figura (§10).

**(b) La diagonale a costo costante — contabilità interna, non confronto.** Sotto il
codice che questo repository dichiara (larghezza fissa, nessun codificatore
entropico), ogni cella ha un codice di ⌈log2 K⌉ bit/token e un residuo misurato
`H(tipo | cluster)` bit/token che un decodificatore dovrebbe comunque trasmettere.
La loro **somma**:

| d | celle | codice + residuo, min … max | prima di ogni raggruppamento |
|---|---|---|---|
| 2 | 36 | 7,967 … 8,885 bit/token | 9,00 bit/token, perdita zero |
| 5 | 36 | 8,136 … 9,950 bit/token | 9,00 bit/token, perdita zero |
| 10 | 36 | 8,135 … 10,004 bit/token | 9,00 bit/token, perdita zero |

Ogni configurazione cade sulla stessa diagonale: **i bit vengono spostati dal
codice alla perdita, quasi uno a uno, non risparmiati.** Il rapporto riporta solo
la prima coordinata. Non serve nessun codec rivale per dirlo: è aritmetica interna
alla contabilità che il repository già pubblica — ed è per questo che il risultato è
enunciato in questa forma.

**E in 18 celle su 108 lo spostamento è in perdita netta.** A d=5 e d=10 le nove
celle lorentz a p ≥ 0,02 costano 9,95 / 10,00 bit/token, *più* dei 9,00 che lo
stesso codice spende senza raggruppare nulla. Un codice più corto, un totale più
lungo.

**(c) Il pavimento di riferimento, e il confronto che si evita di proposito.** Il
codice dichiarato spende **9 bit/token** (⌈log2 259⌉) prima del raggruppamento; la
stessa distribuzione dei tipi mappati ha entropia **5,696 bit/token**. La
differenza, **3,304 bit/token, è il gioco del baseline dichiarato**, identica su
ogni lato perché N e V sono identici su ogni lato per costruzione. Conseguenza per
la lettura di qualunque rapporto: **un rapporto misurato contro `size_before`
misura in parte quel gioco, non la geometria.**

Il non-obiettivo «nessun confronto con `gzip` o con un codificatore entropico»
resta vincolante, e vincola anche questa sezione. Le due forme, perché la
differenza non è pedanteria:

- «la pipeline è peggiore di X» — **fuori perimetro**: viola un non-obiettivo
  dichiarato e richiede un rivale che non è stato eseguito;
- «il baseline dichiarato ha 3,3 bit/token di gioco, quindi il rapporto misura in
  parte il baseline» — **dentro il perimetro**: è il risultato vero, non richiede
  rivali, è verificabile dagli artefatti.

Una lettura precedente della stessa aritmetica l'aveva enunciata nella prima forma.
L'aritmetica era giusta, l'inquadramento no; la diagonale di (b) dice la stessa
cosa senza rivali.

**(d) La contabilità è verificata da un vero giro di andata e ritorno.** In
**tutte le 180 celle** (3 lati × 12 percentili × 5 semi, d=2) il costo ricostruito
da un vero encode→decode coincide con `bits_per_token_after + residual` entro
**1,066e-14 bit/token**, contro una tolleranza dichiarata di 1e-9; il comando esce
non-zero al primo fallimento, ed esce 0
(`out/decode_verify_wordnet-mammals_d2_seedset20260716x5.{json,md}`).

**Il tasso di corrispondenza esatta è quella perdita fatta concreta** — la quota di
token che un decodificatore riproduce alla lettera:

| cella | corrispondenza esatta | con rappresentante casuale del cluster |
|---|---|---|
| euclidea, p=0,01 | 0,6811 ± 0,0124 | 0,3051 |
| lorentz, p=0,01 | 0,6250 ± 0,0264 | 0,2182 |
| js-cooccurrence, p=0,01 | 0,5138 ± 0,0626 | 0,4820 |
| euclidea, p=0,35 | 0,5017 ± 0,0716 | 0,1312 |
| **lorentz, p=0,35** (il rapporto migliore) | **0,2867 ± 0,0179** | 0,0076 |

La regola del rappresentante canonico (il tipo più frequente del cluster) vale
circa un fattore 2 dove un raggruppamento vero esiste e un fattore 38 dentro un
cluster gigante: la seconda colonna è quindi il limite di quanto della prima sia
merito della regola di spareggio e non della geometria.

**Cosa costa un buon rapporto, in una cella sola** (lato lorentz, p=0,35, seme
20260716): **6 codici distinti** per 259 tipi, dunque un codice da **3 bit**;
rapporto **0,3286**, il migliore fra i lati appresi; **il 73,2% dei token decodificati
è la parola sbagliata** (corrispondenza esatta 0,2680); residuo misurato sul giro
stesso **5,656 bit/token**. I tre bit risparmiati costano 5,7, e il totale torna
sulla diagonale a 8,656.

Il verbale della Fase 5 mostra che aspetto hanno quelle fusioni quando un
raggruppamento vero sopravvive: a p=0,01, seme 20260716, il secondo cluster più
grande del lato euclideo è il clade delle scimmie antropomorfe (`anthropoid, ape,
chimpanzee, gibbon, gorilla, orang, siamang, simian`), mentre il lato di Lorentz
fonde i canidi **con gli elefanti** (`dog, dogs, jackal, cur, canine, elephant,
elephants`, 24 tipi) — ed è il lato di Lorentz quello col rapporto frazionario
migliore in quel punto di lavoro (0,8133 contro 0,8448). Vincere il rapporto e
raggruppare fedelmente sono qui due cose opposte.

**Il nome corretto (Fase 5d).** Questa pipeline **non è compressione**: è
**quantizzazione semantica** — i tipi vengono quantizzati su identificatori di
cluster — e il piano di valutazione onesto è **tasso-distorsione**: bit per token
contro danno semantico, entrambi misurati, nessuno dei due scambiato in silenzio.
La parola «compress» sopravvive nei nomi dei file (`compress.py`, `out/compress_*`)
e in ogni comando di rigenerazione perché quelle stringhe portano la riproducibilità
F3: sono etichette storiche, non affermazioni.

**I limiti, dichiarati.** Un corpus, una gerarchia, **1,55% di copertura**,
d ∈ {2, 5, 10}, 5 semi. Il clamp dell'auto-soglia del prototipo
(`compressionTest.js:531-535`, limiti `[1e-6, 10]`) vincola su diverse celle: dove
vincola, è il clamp e non il percentile a decidere il raggruppamento, e a d=5/d=10
il lato euclideo non fonde quasi nulla (K = 165,6 / 166,0 su 166 nodi, rapporto
0,9388 = il pavimento del non-raggruppare). Quelle celle non dicono nulla sulla
geometria — **ed è per questo che la Fase 5e (2026-08-11) le ha rimisurate a
numero di cluster fissato**, fuori dal percorso percentile: costretto a fondere a
K = 80…20 il lato euclideo produce 1,85-7,06 salti d'oro invece di ~0. Nessuna
cifra di questa sezione cambia — sono tutte indicizzate per percentile — ma la
lettura «l'euclidea fonde fedelmente a d≥5» era un artefatto e non va scritta. Il risultato riguarda **questa metrica su questa pipeline**: generalizza
come **cautela** — *una metrica di qualità che migliora monotonamente mentre si
butta informazione verrà ottimizzata buttando informazione* — non come misura di
qualcosa fuori da questa griglia.

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
   dove il baseline euclideo ricostruisce perfettamente. Entrambe le geometrie a
   6000 epoche, budget racchiuso da entrambi i lati dalla scansione della Fase 4b
   (§4b, addendum): il risultato non dipende da quella manopola.»

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

Una quarta figura arriva dalle Fasi 5-5d (§4c) e vive in `report/` invece che in
`out/`, perché non misura nulla: legge gli aggregati già presenti.

4. `report/rate_distortion_wordnet-mammals_d2-5-10_seedset20260716x5.png`
   — due pannelli, 108 celle (3 lati × 12 percentili × 3 dimensioni), colore =
   lato, marcatore = dimensione.
   *Didascalia pronta:* «Il piano tasso-distorsione della quantizzazione
   semantica. A sinistra la lunghezza del codice contro la perdita residua, con le
   diagonali a costo costante e i due riferimenti a perdita zero (il codice
   dichiarato da 9 bit/token e l'entropia dei tipi, 5,696 bit/token, che ne misura
   il gioco): ogni configurazione sposta bit dal codice alla perdita invece di
   risparmiarli. A destra la lunghezza del codice contro i salti nella gerarchia
   d'oro, con la retta del riferimento cieco alla gerarchia (7,654): i codici più
   corti sono quelli le cui fusioni sono più lontane dal significato. Media sui 5
   semi.»

## 7. Cosa carta 02 non deve affermare

Questa sezione esiste perché carta 01 ne ha una ("Cosa questo articolo *non*
afferma") e perché è il motivo per cui l'affermazione su d=2 può sopravvivere a una
revisione.

- **Non è compressione — e ora si sa perché, non solo che.** Le Fasi 2-4 sono una
  misura di geometria su una gerarchia d'oro: nessun rapporto di compressione,
  nessun confronto con `gzip`, entrambi esclusi dagli obiettivi del programma. La
  riconnessione alla pipeline **è stata eseguita** (Fasi 5-5d, §4c) e ha reso il
  divieto più forte invece di revocarlo: il rapporto che quella pipeline riporta
  **anticorrela con la fedeltà semantica** (r fra −0,84 e −0,99 sui salti d'oro,
  108 celle), la contabilità mostra che i bit **si spostano dal codice alla
  perdita** invece di essere risparmiati, e in 18 celle su 108 il totale è
  peggiore del non fare nulla. Quindi: carta 02 **non può citare nessun rapporto
  come compressione**; può — e dovrebbe — citare il risultato sulla metrica.
  Restano vietati il confronto con `gzip` o con qualunque codificatore entropico
  (non-obiettivo dichiarato: il rivale non è mai stato eseguito) e ogni frase della
  forma «la pipeline è peggiore di X»; la forma dentro perimetro è quella interna
  alla contabilità (§4c(b), §4c(c)).
- **Nessuna cifra della Fase 5 va citata senza la copertura.** Ogni numero di §4c
  descrive **l'1,55% del corpus** (4616 token su 297_697, 259 tipi su 13_565, 166
  synset su 1170). Un rapporto su quell'1,55% non è un rapporto sul testo.
- **E c'è un numero che sembra un rapporto di compressione e non lo è.** Gli
  aggregati portano una terza quantità adimensionale eredita dal prototipo, che
  divide una grandezza di taglia-vocabolario per un conteggio di token: letta
  ingenuamente sembra una compressione sopra il 90%. Numeratore e denominatore
  contano cose diverse: non compare in §4c e nessuna cifra di §4c ne deriva. Se
  entra in una bozza, è un errore.
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
- **Il budget di epoche non è tarato per dimensione — ma è racchiuso, e questo non
  vincola più il risultato.** 6000 per entrambe le geometrie a ogni d, che era
  l'ottimo a d=2 per entrambe: è l'unico asse su cui l'ablazione è più debole della
  lettura ideale di F2, ed è dichiarato come tale. Le due geometrie chiedono budget
  diversi (1500 l'euclidea, 6000 l'iperbolica), quindi il budget condiviso è
  soffitto per una e surplus per l'altra. Ma la scansione estesa (§4b, addendum) ha
  racchiuso l'argmax iperbolico da sopra — plateau a 6000, +0.0005 e +0.0014 nei
  1500 epoche successivi, dentro la σ fra semi — e quei guadagni residui sono più
  piccoli dei divari WordNet a d≥5 (0.0032 e 0.0147). **Conseguenza per il testo:**
  il ribaltamento a d≥5 si può affermare come proprietà della geometria **senza**
  riserva sul budget; l'unica riserva che resta è quella di sempre, che la
  scansione vive sul sintetico e il trasferimento a WordNet è un'inferenza fra
  dataset. Un'affermazione da non fare al suo posto: che la Fase 4b abbia mostrato
  un budget vincolante — è la sua *prima* lettura, ritrattata lo stesso giorno.

## 8. Cosa manca ancora

- **Fase 4b** — **eseguita il 2026-08-04, e chiusa lo stesso giorno dal suo
  addendum**, §4b. Risposta finale: **no**, il risultato non dipende dalle epoche.
  La prima scansione {1500…6000} sembrava dire il contrario; l'estensione
  {6000, 7500, 9000} ha racchiuso il plateau e ritrattato quella lettura. Non resta
  aperta nessuna decisione sul budget: rifare il set di riferimento a un budget più
  grande non ha più una ragione, perché non c'è guadagno da inseguire. Se carta 02
  va in revisione tecnica, §4b va allegato **per intero, addendum compreso**: è la
  risposta alla prima domanda che un revisore farà, e la ritrattazione è la parte
  che rende credibile la risposta.
- **Fase 5** — **eseguita fra il 2026-08-05 e il 2026-08-11** in quattro tempi (5,
  5b, 5c, 5d), §4c. La premessa che la bloccava era di sostanza e non tecnica — le
  Fasi 2-4 immergono *synset* inglesi, la pipeline raggruppa *parole* di un testo,
  e serviva una mappatura lemma→synset più un corpus la cui intersezione col
  sottoalbero dei mammiferi fosse **misurata**. Ora lo è: 1,55% dei token. Il
  risultato non è il rapporto di compressione che questa voce non poteva promettere
  ed è meglio di così: è la dimostrazione che quel rapporto è una metrica che
  premia il degrado. Resta aperto ciò che quella misura non copre: copertura
  dell'1,55% su **un solo** corpus (un corpus con più mammiferi cambierebbe le
  cifre, non necessariamente il segno), le celle dove il clamp del prototipo e non
  il percentile decide il raggruppamento, e — per scelta, non per lacuna — nessun
  codec rivale.

## 9. Frasi che i numeri autorizzano

Da usare come spina dorsale, ciascuna con la sua evidenza. Se una frase non è in
questa tabella, non è ancora sostenuta.

| Affermazione | Evidenza |
|---|---|
| A dimensione 2 la curvatura paga, e paga molto | MAP 0.7538 → 0.8957 (+18.8% relativo), distorsione 0.3441 → 0.2609 (−24.2%), σ non sovrapposte su 5 semi |
| Il vantaggio è un fenomeno di *bassa* dimensione | da d=5 l'euclidea guida MAP e rango; a d=10 ricostruisce perfettamente (1.0000 / 1.0000). Si scrive **senza riserva sul budget**: §4b addendum racchiude il plateau a 6000 e i guadagni residui (0.0005, 0.0014) sono più piccoli dei divari WordNet a d≥5 (0.0032, 0.0147) |
| Il vantaggio sulla distorsione però non svanisce | divario +0.0320 a d=10, con σ 0.0015 e 0.0009: piccolo ma fuori dal rumore |
| L'euclidea a d=10 ricostruisce meglio *e* distorce di più | MAP 1.0000 con distorsione 0.2927, contro 0.9853 e 0.2606: ordinare bene i vicini non è preservare le distanze |
| Le due geometrie sbagliano in direzioni opposte | σ/media 0.5130 (euclidea) e 0.1353 (iperbolica) contro 0.2927 del grafo, a d=2 |
| Il prezzo della curvatura è il rango | rango iperbolico peggiore a ogni d: 13.85 vs 5.57, 4.17 vs 1.06, 2.45 vs 1.00 |
| Il vantaggio vive in una fascia di profondità, non cresce con essa | a d=2: profondità 1 → 1.533 (iperbolica) vs 0.596 (euclidea); profondità 6 → 0.184 vs 0.343; profondità 9 → 0.326 vs 0.307, richiuso |
| Il confronto è equo per costruzione | lr tarato per (geometria, dimensione) sul solo albero sintetico e congelato prima di WordNet; l'ottimo iperbolico si sposta (0.005 → 0.003) |
| I numeri non sono un aneddoto | cancello di regressione a quattro decimali su quattro celle; 5 semi; un comando |
| L'albero sintetico non basta come banco di prova | euclidea satura a MAP 1.0000 e rango 1.0000 a d≥5 per ogni lr della griglia — e, §4b, per ogni budget di epoche della scansione |
| Le due geometrie non vogliono lo stesso budget di calcolo | §4b: budget minimo indistinguibile dal proprio ottimo 1500 per l'euclidea a d=5 e d=10, 6000 per l'iperbolica alle stesse dimensioni — e l'addendum mostra che l'iperbolica non ne vuole nemmeno di più: F2 è limitata da entrambi i lati |
| Ordinare bene i vicini e preservare le distanze si allenano in modo diverso | §4b: sul lato iperbolico l'argmax della MAP è a 7500 mentre la distorsione ha il minimo a 4500 e peggiora fino a 9000, a d=5 e a d=10 |
| L'onestà del programma è verificabile, non dichiarata | il limite dichiarato in Fase 4 è stato scansionato in Fase 4b; la prima lettura era sfavorevole a metà della conclusione ed è stata pubblicata come tale, poi l'estensione sopra 6000 ha mostrato che quella lettura era un'extrapolazione sbagliata di 90× e **la ritrattazione è stata scritta accanto**, non sostituita al posto dell'originale |
| Il rapporto di compressione di questa pipeline premia il degrado | §4c(a): r(rapporto, salti d'oro) = −0,841 (d=2), −0,992 (d=5), −0,984 (d=10) su 36 celle per dimensione; il rapporto migliore dei tre lati è quello dell'embedding con l'84,9% delle distanze esattamente nulle |
| I bit non vengono risparmiati: vengono spostati | §4c(b): codice + residuo misurato sta fra 7,967 e 10,004 bit/token su tutte le 108 celle, contro i 9,00 bit/token dello stesso codice senza raggruppare nulla — e in 18 celle il totale è più alto |
| Il costo di un buon rapporto è dicibile in una frase concreta | §4c(d): al miglior rapporto del lato appreso (0,3286) il 73,2% dei token decodificati è la parola sbagliata, verificato da 180 giri di andata-e-ritorno che chiudono entro 1,066e-14 bit/token |
| Vincere una metrica e raggruppare fedelmente possono essere cose opposte | §4c: a p=0,01 il lato euclideo forma il clade delle scimmie antropomorfe mentre quello iperbolico fonde canidi ed elefanti — e il secondo ha il rapporto frazionario migliore (0,8133 contro 0,8448) |
| Il nome giusto non è compressione | §4c: quantizzazione semantica valutata sul piano tasso-distorsione; i nomi di file con «compress» sono etichette storiche tenute per riproducibilità |
| A numero di cluster fissato il rapporto non dice **nulla** sulla fedeltà | Fase 5e: a K uguale il rapporto è identico sui due lati appresi per costruzione (stesso K, stessi N e V), mentre i salti d'oro differiscono fino a 1,65 (d=10, K=40: 4,856 ± 1,189 contro 6,506 ± 0,152) |
| A d=2 la geometria iperbolica vince le tre metriche geometriche e raggruppa peggio comunque | Fase 5e, a K uguale: l'euclidea è avanti su tutti e quattro i gradini (a K=80 1,830 ± 0,106 contro 2,356 ± 0,308, bande a un σ disgiunte), mentre a d=2 l'iperbolica vince MAP, distorsione e confronto degli spread. Il confronto pubblicato in Fase 5 era a K diverso (72 contro 85) e quindi confuso; questo non lo è |
| La qualità semantica a valle non segue la distorsione | Fase 5e a d=10, l'unica dimensione dove MAP e distorsione dissentono: l'euclidea produce meno salti d'oro a tutti e quattro i gradini (1,854 contro 2,048 a K=80; 4,856 contro 6,506 a K=40, bande disgiunte). Era una **previsione registrata prima** della misura (commit `dc88cda`) ed è confermata. Quale metrica governi al posto della distorsione resta aperto: MAP e spread ordinano identicamente a d ∈ {2,5,10} e il disegno non le separa |

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

La scansione della Fase 4b (§4b) si rigenera con un secondo comando, indipendente
dal primo:

```
python ablation.py --epoch-scan 1500 3000 4500 6000 --dataset synthetic-tree --dims 5 10 --out out/
```

Semi {20260716, 12345, 777} — quelli di taratura, non quelli del set di
riferimento, ed è deliberato: il budget è una manopola. 36 esecuzioni nuove, circa
35 minuti sullo stesso host; le dodici celle a 6000 epoche vengono riusate dalla
ricerca del learning rate, che le aveva prodotte con identici lr, epoche, seme e
dataset. Tabella e testo:
`out/ablation_epochscan_synthetic-tree_dims5-10_epochs1500-3000-4500-6000_seedset20260716-12345-777.md`
e il JSON omonimo, con le 48 celle per singolo seme.

L'addendum che racchiude il plateau da sopra (§4b) è un terzo comando, sugli stessi
semi di taratura, 24 esecuzioni nuove e circa 36 minuti:

```
python ablation.py --epoch-scan 6000 7500 9000 --dataset synthetic-tree --dims 5 10 --out out/
```

Tabella e testo:
`out/ablation_epochscan_synthetic-tree_dims5-10_epochs6000-7500-9000_seedset20260716-12345-777.md`
e il JSON omonimo.

Le Fasi 5-5d (§4c) si rigenerano con quattro comandi indipendenti, nell'ordine:

```
python compress.py --dataset wordnet-mammals --dim 2 --seeds 5 --out out/
python compress.py --dataset wordnet-mammals --dims 5 10 --seeds 5 --out out/
python decode.py --dataset wordnet-mammals --d 2 --seeds 5 --verify --out out/
python compress.py --figure rate-distortion --out report/
```

Costi misurati sullo stesso host a 22 core, a vuoto: ~40 min il primo (dieci
addestramenti, 246-251 s euclidei e 374-654 s iperbolici; saltati del tutto se
`out/compress_coords_*.npz` esiste già, e ogni file caricato viene ri-passato al
cancello), ~48 min il secondo (venti nuovi insiemi di coordinate, ciascuno
verificato a delta massimo 0,0e+00 contro il checkpoint di Fase 4), ~2 min il terzo
(nessun addestramento; esce non-zero se una cella fallisce), ~1 min il quarto
(nessuna misura: legge gli aggregati e ri-deriva il solo riferimento cieco alla
gerarchia, 7,6540). Artefatti principali:
`out/compress_wordnet-mammals_d{2,5,10}_seedset20260716x5.{json,md}`,
`out/compress_dims_wordnet-mammals_dims5-10_seedset20260716x5.{json,md}`,
`out/compress_mapping_pg2300_wordnet-mammals.json`,
`out/decode_verify_wordnet-mammals_d2_seedset20260716x5.{json,md}` e la figura in
`report/`. Il corpus viene scaricato una volta da Project Gutenberg e il suo sha256
è verificato a ogni esecuzione; `--corpus-file` lo esegue offline da una copia
locale.

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
   dimensione è avara». Il ribaltamento a d≥5 si enuncia senza riserve sul budget,
   ed è §4b a permetterlo: un'ablazione che dichiara dove è debole, va a misurarlo,
   pubblica una prima lettura sfavorevole e poi la ritratta con i numeri dice del
   metodo più di quanto direbbe un risultato pulito. Quella sequenza è un capitolo,
   non una nota.
5. **Il crowding, misurato** — la figura degli spread e la doppia direzione
   dell'errore; il paradosso rango-contro-MAP spiegato dal guscio stretto; la curva
   in profondità come conferma localizzata dell'argomento di carta 01.
6. **Cosa non afferma** — §7 di questo dossier, praticamente per intero.
7. **La metrica che premia il degrado** — §4c, e il capitolo che carta 02 non
   avrebbe avuto se la Fase 5 fosse rimasta bloccata. La copertura (1,55%) prima di
   ogni cifra, l'anticorrelazione, la diagonale a costo costante, e la cella in cui
   tre bit risparmiati costano il 73% delle parole. Il nome corretto —
   quantizzazione semantica, non compressione — appartiene qui. La morale è
   trasferibile fuori dall'esperimento: una metrica di qualità che migliora mentre
   si butta informazione verrà ottimizzata buttando informazione.
8. **Cosa verrebbe dopo** — il budget iperbolico da racchiudere sopra 6000, che è
   la lacuna più vicina e la più economica da chiudere; e per la Fase 5, la
   copertura da allargare oltre l'1,55% su un corpus con più mammiferi. E i comandi,
   perché chi legge possa rifarli.
