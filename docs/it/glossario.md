# Glossario

← [Indice](./README.md)

Termini tecnici che compaiono nel progetto, tradotti in parole.

| Termine | Spiegazione |
|---------|-------------|
| **NFKC** | Forma di normalizzazione Unicode che uniforma diacritici, legature e varianti tipografiche. Serve a far sì che «caffè» e «caffè» siano la stessa parola. |
| **Tokenizzazione** | Spezzare il testo in parole. Qui usiamo solo sequenze di lettere Unicode di lunghezza ≥ 2. |
| **Co-occorrenza** | Quante volte due parole appaiono vicine, dentro una finestra scorrevole. È una misura di «contesto comune». |
| **Matrice sparsa** | Matrice in cui la maggior parte delle celle è zero, e quindi memorizziamo solo quelle non-zero. Risparmio di memoria, accesso più lento. |
| **Embedding** | Una rappresentazione numerica (vettore) di una parola, che dovrebbe catturarne il significato. Più due parole sono simili, più i loro vettori dovrebbero essere vicini. |
| **Random projection** | Tecnica per ridurre la dimensione di un vettore proiettandolo su poche direzioni casuali. Veloce, semplice, sorprendentemente efficace. |
| **SVD (Singular Value Decomposition)** | Decomposizione matriciale che trova le direzioni «più importanti» di una matrice. Cuore di tante tecniche di riduzione della dimensione. |
| **Disco di Poincaré** | Modello di geometria iperbolica che vive in un cerchio di raggio 1. Da fuori sembra finito; da dentro la sua frontiera è infinitamente lontana. |
| **Geometria iperbolica** | Geometria a curvatura negativa costante. Il volume disponibile cresce esponenzialmente con la distanza dal centro: ottima per rappresentare alberi. |
| **Distanza di Möbius** | La distanza «vera» nel disco di Poincaré: `acosh(1 + 2‖u−v‖² / ((1−‖u‖²)(1−‖v‖²)))`. |
| **Cluster** | Gruppo di parole considerate simili dal sistema. |
| **Union-find** | Struttura dati per tenere traccia di gruppi di elementi e fonderli velocemente. Usata per estrarre i cluster come componenti connesse di un grafo. |
| **Componente connessa** | In un grafo, un sottoinsieme di nodi tutti raggiungibili gli uni dagli altri. |
| **k-NN (k-nearest neighbours)** | Trovare i k vicini più prossimi di un punto. Qui lo usiamo come prefiltro: se due parole non sono fra i k vicini euclidei, non sprechiamo tempo a calcolarne la distanza iperbolica. |
| **Soglia (threshold)** | Limite oltre il quale due parole *non* vengono collegate. Decide quanto «larghi» sono i cluster. |
| **MAD (Median Absolute Deviation)** | Misura robusta di dispersione: la mediana delle distanze assolute dalla mediana. Resiste agli outlier. |
| **Percentile** | Il valore sotto cui cade una percentuale data dei dati. Il p35 è il valore sotto cui cade il 35% dei campioni. |
| **σ (sigma)** | In questo contesto: una stima della deviazione standard derivata dalla MAD (`σ ≈ 1.4826 · MAD`). |
| **LCG (Linear Congruential Generator)** | Generatore di numeri pseudocasuali semplice, deterministico dato un seed. Usato per la riproducibilità. |
| **Determinismo** | Stessa esecuzione, stesso input, stesso output — sempre. Qui vale dato un `seed` fisso. |
| **ratio** | Indice di compressione del prototipo: `compresso / originale`. Più piccolo, più «risparmio». |
| **savingsPct** | `(1 − ratio) · 100`. Risparmio percentuale stimato. |
| **Toy model** | Modello giocattolo: una semplificazione utile per ragionare, non per produzione. |

## Continua

➡️ [Domande frequenti](./faq.md)
