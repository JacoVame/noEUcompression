# Speaker notes — HyperbolicTextCompressor (IT, 30 min)

> Copione discorsivo per il presentatore. Tempi indicativi accanto a ogni sezione.
> Le note sono già incluse nelle slide reveal.js (visibili con `S` durante la presentazione); qui c'è la versione discorsiva, da rileggere a freddo.

## 0. Prima di iniziare (2′)

- Aprire `presentation/it/index.html` nel browser.
- Pre-aprire `docs/diagram/pipeline.html` in un'altra scheda per le slide 6 e 18.
- Avere il terminale pronto su `out/bench.jsonl` per la demo live (slide 16).
- QR code del repo proiettato nelle pause.

## 1. Apertura (slide 1–3, ~3′)

Saluto, presentazione personale, brevissimo ringraziamento ai professori Di Gesù e Tegolo (le loro ricerche su geometria, percezione e linguaggio sono il «brodo culturale» da cui nasce l'idea). Spiegare subito il nome: «non-EU» è un gioco di parole, sta per non-Euclidean. Parto da una domanda, non da una formula: «posso comprimere il senso, non i byte?». Chiudere con il salto: dalla compressione *sintattica* a quella *semantica*.

## 2. La motivazione (slide 4–5, ~3′)

La geometria della scuola è piatta. Il linguaggio è ad albero. Esempio del mappa-quadernino: si rimane senza spazio. Citare Nickel & Kiela 2017 senza scendere nei dettagli: la motivazione è popolare e robusta. Mostrare la pipeline animata già in slide 5 per ancorare il pubblico: «alla fine della presentazione capirete tutto questo». Non rallentare qui — è solo un assaggio.

## 3. Cosa fa il prototipo, in una slide (slide 6, ~1′)

Otto passi. Ripeto la lista a voce, lentamente. Importante per chi ascolta in piedi o al PC: rivedrà la stessa lista per altre 8 volte.

## 4. Demo introduttiva (slide 7, ~2′)

Lascio la pipeline animata in autoplay per circa un minuto e parlo sopra. Indico il punto giallo che si sposta, il disco di Poincaré, l'istogramma, i tre cluster colorati. Chiudo con: «adesso entriamo nei dettagli».

## 5. I passi tecnici (slide 8–15, ~10′ totali)

Un minuto per slide circa. Tono rapido, niente formule scenografiche. Punti chiave:

- **Preprocess**: NFKC + regex, non sembra niente ma fa la differenza.
- **Co-occurrence**: matrice sparsa, evidenziare il word `Map<col, count>`.
- **Embedding**: random projection, citare Johnson-Lindenstrauss.
- **Poincaré**: `‖x‖ < 1`, fattore 0.85.
- **Distanza**: la formula `acosh(...)` la mostro ma non la spiego punto per punto. Dico solo: «vicino al centro, normale; vicino al bordo, esplode».
- **Auto-soglia**: enfatizzo che non c'è magic number, e mostro il cruscotto (slide 13).
- **Clustering**: union-find, ordine-invariante, k-NN prefilter.
- **Stima**: ratio + 50% mappatura. **Subito** la chiamo «giocattolo» perché altrimenti il 54.5% sembra una conquista.

## 6. Demo live (slide 16, ~3′)

Eseguo `npm run bench -- --file ./samples/sample.txt --auto --autoMethod hybrid --autoStats` davanti al pubblico. Mostro la riga JSON. Apro `out/report.html` per far vedere i grafici.

## 7. I cluster reali (slide 17, ~1′)

Tre cluster. Il grande è interessante perché contiene articoli, preposizioni, ausiliari: una «stop-word di fatto». I due piccoli mostrano che il sistema è prudente con le rarità.

## 8. La parte di onestà (slide 18–19, ~3′)

Slide cruciale: cosa **non** è. Senza questa slide, una persona del pubblico potrebbe pensare di aver visto un sostituto di gzip. Lo escludo subito. I limiti onesti sono in slide 19: leggo per punti.

## 9. Casi d'uso e roadmap (slide 20–21, ~3′)

Rapide. La roadmap è onesta: nessuna delle voci è triviale. Specifico che il decompressore è il primo blocco da costruire per fare confronti con gzip.

## 10. Perché così (slide 22, ~1′)

Le scelte di design servono un'audience pubblica: zero deps, deterministico, leggibile. Sottolineo la parola «didattico».

## 11. Architettura compatta (slide 23, ~30″)

Slide quasi visiva. La compattezza è feature.

## 12. Numeri di riferimento e lezioni apprese (slide 24–25, ~2′)

I numeri sono per chi vuole riprodurre. Le cinque lezioni apprese sono il riassunto retorico.

## 13. FAQ anticipate e Q&A (slide 26–28, ~5–7′)

Anticipare le domande lascia tempo per quelle vere. Restare disponibili sulla pipeline animata se qualcuno vuole spunti visivi.

---

## Tempi totali

| Sezione | Min |
|---------|-----|
| Apertura | 3 |
| Motivazione | 3 |
| Sintesi | 1 |
| Demo intro | 2 |
| Passi tecnici | 10 |
| Demo live | 3 |
| Cluster reali | 1 |
| Onestà | 3 |
| Casi d'uso + roadmap | 3 |
| Design | 1 |
| Architettura | 0.5 |
| Numeri & lezioni | 2 |
| FAQ + Q&A | 5–7 |
| **Totale** | **~30** |

## Tips finali

- Tenere la pipeline animata aperta in una scheda separata, sempre pronta.
- Avere a disposizione `out/bench.jsonl` per copiare numeri reali se domandano dettagli.
- Se il tempo stringe: tagliare la slide architettura (23) e i numeri di riferimento (24).
- Se il pubblico chiede *«ma è AI?»*, rispondo: «no, è un esperimento di geometria. Niente reti neurali, niente training, niente GPU».
