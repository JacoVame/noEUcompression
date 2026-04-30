# Matematica soft

← [Indice](./README.md)

Questa pagina spiega *perché* il disco di Poincaré ha senso, senza richiedere conoscenze di geometria differenziale. Se odi le formule, salta i blocchi grigi: il filo del discorso è nel testo.

## Geometrie diverse, distanze diverse

In geometria piatta (euclidea) vale il teorema di Pitagora: la distanza fra due punti è sempre la radice quadrata della somma dei quadrati delle differenze. È quella che usiamo a scuola, e descrive bene un foglio di carta o un campo di calcio.

Ma esistono altre geometrie. Se prendi una sfera, due «linee dritte» (cerchi massimi) si intersecano sempre — niente parallele. Se prendi un piano iperbolico, succede l'opposto: da un punto fuori da una retta passano *infinite* parallele. Le distanze, di conseguenza, si comportano diversamente.

## Perché uno spazio iperbolico per il linguaggio?

Il linguaggio ha una struttura ad albero: «animale» è genitore di «mammifero», che è genitore di «cane», di «pastore tedesco»… Ogni livello ha più foglie del precedente, e l'albero esplode in modo *esponenziale*.

In uno spazio piatto a *d* dimensioni, il volume disponibile a distanza *r* dal centro cresce come *r^d*: polinomiale. Per piazzare un albero con tante foglie, ti serve presto un sacco di dimensioni.

In uno spazio **iperbolico**, invece, il volume disponibile cresce *esponenzialmente* con la distanza dal centro. Significa: vicino al centro c'è poco posto, ma allontanandosi dal centro lo spazio si moltiplica. È esattamente la forma di un albero: un padre, qualche figlio, tantissimi nipoti.

Il disco di Poincaré è un *modello* di geometria iperbolica che vive in un cerchio. Sembra finito, ma per chi lo vive da dentro la sua frontiera è infinitamente lontana.

## L'illusione del disco

Immagina un cartone di Escher: pesci che diventano sempre più piccoli avvicinandosi al bordo del cerchio. Visto da fuori, sembrano rimpicciolire. Visto da dentro, sono tutti grandi uguali. È così che funziona il disco di Poincaré: i nostri occhi vedono i punti vicino al bordo come «schiacciati», ma la metrica del disco dice che ognuno di loro ha lo stesso «metro» a disposizione di quelli al centro.

Il prezzo di questa illusione è che le distanze euclidee (quelle che misuriamo con il righello) e le distanze iperboliche (quelle vere) divergono drammaticamente vicino al bordo.

> ```
> d_H(u, v) = acosh(1 + 2 · ‖u − v‖² / ((1 − ‖u‖²)(1 − ‖v‖²)))
> ```
>
> Tradotto: prendi la distanza euclidea al quadrato; dividila per quanto «poco spazio iperbolico» c'è dove stanno *u* e *v* (i due fattori `1 − ‖·‖²`); poi schiaccia il tutto con `acosh`. Il risultato esplode a infinito quando *u* o *v* si avvicinano al bordo del disco.

## Cosa vuol dire per le parole

Se due parole vivono entrambe vicino al centro, sono distanti più o meno come pensavamo (geometria quasi euclidea). Se una scivola verso il bordo, di colpo è lontanissima da tutte le altre — anche se sul righello sembrava a un soffio.

Questa è una buona notizia per la semantica: nel nostro corpus le parole *funzionali* (articoli, preposizioni, ausiliari) tendono a stare nel mezzo, le parole rare e tematiche tendono al bordo. La metrica iperbolica le separa naturalmente.

## L'idea pratica

In poche righe:

1. Costruisco una piccola firma per ogni parola (la riga della matrice di co-occorrenza).
2. La proietto in poche dimensioni.
3. La schiaccio dentro il disco.
4. Calcolo le distanze nel disco.
5. Metto insieme le parole che, in quella metrica, sono vicine.

Niente di esoterico. Quello che cambia rispetto a un classico clustering euclideo è solo il *metro*.

## Per chi vuole leggere di più

- *Poincaré Embeddings for Learning Hierarchical Representations* (Nickel & Kiela, 2017) — la motivazione per usare lo spazio iperbolico per gerarchie.
- *Hyperbolic Word Embeddings* / *Poincaré GloVe* — varianti addestrate, lontane dalle proiezioni euclidee+scaling che usiamo qui.
- I documenti tecnici nel repo: [`docs/en/hyperbolic_compression_analysis.md`](../en/hyperbolic_compression_analysis.md), [`docs/en/ai_research_showcase.md`](../en/ai_research_showcase.md).

## Continua

➡️ [Parametri e CLI: tutte le manopole disponibili](./parametri-e-cli.md)
