/**
 * HyperbolicTextCompressor
 *
 * Overview
 * - Preprocesses text (Unicode-aware tokenization), builds a sparse co-occurrence matrix,
 *   creates fast heuristic hyperbolic embeddings (Poincaré disk), and clusters words
 *   via a distance threshold to estimate a toy "compression".
 *
 * Usage
 *   const HyperbolicTextCompressor = require('./compressionTest');
 *   const c = new HyperbolicTextCompressor(2, { maxVocab: 3000, seed: 42 });
 *   const res = c.analyzeAndCompress('your text here');
 *
 * Options
 *   - dimension: embedding dimensions (>=2)
 *   - maxVocab: cap vocabulary size to avoid O(V^2) blowups (default 5000)
 *   - seed: seeded RNG for reproducibility of fallback vectors
 *
 * Dev notes
 *   - Co-occurrence matrix is sparse (row: Map<col,count>).
 *   - Clustering is naive O(V^2) with a threshold in Poincaré distance.
 *   - For large corpora, consider k-NN prefilter, adaptive thresholds, and better embeddings (e.g., SVD+projection).
 *
 * Built-in test harness
 *   Run with environment variable HTC_RUN_TESTS=1 to execute basic assertions.
 *     PowerShell:
 *       $env:HTC_RUN_TESTS='1'; node .\compressionTest.js; Remove-Item Env:HTC_RUN_TESTS
 */

class HyperbolicTextCompressor {
    /**
     * @param {number} dimension Numero di dimensioni dell'embedding (>=2 consigliato)
     * @param {object} options Opzioni varie
      *  - maxVocab: limite massimo del vocabolario per evitare esplosioni di memoria (default 5000)
      *  - windowSize: ampiezza finestra co-occorrenze (default 3)
      *  - clusterThreshold: soglia distanza iperbolica per clustering (default 0.4)
      *  - projection: 'firstD' (storico) | 'random' (default, proiezioni casuali robuste)
      *                | 'svd' (SVD densa su matrici piccole)
      *  - randomFeaturesPerDim: quante colonne random sommare per ogni dimensione (default 16)
      *  - weighting: 'uniform' | 'distance' (peso 1/(1+|i-j|) nella finestra) (default 'uniform')
      *  - normalize: normalizza Unicode in NFKC prima della tokenizzazione (default true)
      *  - verbose: logga passaggi e tempi su console (default true)
      *  - svdMaxN: usa SVD solo se n <= svdMaxN (default 800)
      *  - clusterK: se >0, prefiltra con k-NN euclideo prima del controllo iperbolico (default 0 = disabilitato)
    *  - autoThreshold: se true, auto-seleziona la soglia di clustering da un percentile delle distanze (default false)
    *  - autoThresholdPercentile: percentile in [0,1] per stimare la soglia (default 0.35)
    *  - autoThresholdSample: numero massimo di coppie campionate per stimare la soglia (default 3000)
    *  - autoThresholdMethod: 'percentile' | 'mad' (default 'percentile')
    *  - autoThresholdMADK: K per soglia = median - K * 1.4826 * MAD (default 0.5)
      */
    constructor(dimension = 2, options = {}) {
        this.dimension = Math.max(2, dimension | 0);
        this.maxVocab = options.maxVocab ?? 5000;
        this.seed = (options.seed ?? Math.floor(Math.random() * 0x7fffffff)) | 0;
          this.windowSize = Math.max(0, options.windowSize ?? 3);
          this.clusterThreshold = typeof options.clusterThreshold === 'number' ? options.clusterThreshold : 0.4;
          this.projection = options.projection || 'random';
          this.randomFeaturesPerDim = Math.max(1, options.randomFeaturesPerDim ?? 16);
          this.weighting = options.weighting || 'uniform';
          this.normalize = options.normalize !== false; // default true
          this.verbose = options.verbose !== false; // default true
          this.svdMaxN = Math.max(50, options.svdMaxN ?? 800);
          this.clusterK = Math.max(0, options.clusterK ?? 0);
          this.approxKNN = !!options.approxKNN; // approximate kNN prefilter for clustering
          this.approxKCandidates = Math.max(1, options.approxKCandidates ?? 50);
        this.autoThreshold = !!options.autoThreshold;
        this.autoThresholdPercentile = Math.min(1, Math.max(0, options.autoThresholdPercentile ?? 0.35));
        this.autoThresholdSample = Math.max(100, options.autoThresholdSample ?? 3000);
          this.autoThresholdMethod = ['mad','percentile','hybrid'].includes(options.autoThresholdMethod) ? options.autoThresholdMethod : 'percentile';
          this.autoThresholdMADK = Math.max(0, options.autoThresholdMADK ?? 0.5);
          this.autoThresholdHistogramBins = Math.max(0, options.autoThresholdHistogramBins ?? 0); // 0 disables
          this.diagnosticsOnly = !!options.diagnosticsOnly; // skip clustering, return only stats
        this.wordVectors = {};
        this.compressionStats = {};
        this._EPS = 1e-8;
    // Diagnostics for auto-thresholding
    this._autoStats = null;
    this._lastAutoChosen = undefined;
    }

    // PRNG semplice (LCG) per riproducibilità
    _rand() {
        // Parametri LCG classici (Numerical Recipes)
        this.seed = (1664525 * this.seed + 1013904223) >>> 0;
        // [0,1)
        return this.seed / 0x100000000;
    }

    // Tokenizzazione robusta con supporto Unicode: prende solo sequenze di lettere (>=2)
    preprocessText(text) {
        const s = (typeof text === 'string') ? text : String(text ?? '');
        const base = this.normalize && s.normalize ? s.normalize('NFKC') : s;
        const tokens = (base.toLowerCase().match(/\p{L}{2,}/gu) || []);
        return tokens;
    }

    // Costruisce una matrice di co-occorrenza sparsa (array di Map: riga -> {col:count})
    createCooccurrenceMatrix(words, windowSize = this.windowSize) {
        // Frequenze per limitare il vocabolario
        const freq = new Map();
        for (const w of words) freq.set(w, (freq.get(w) || 0) + 1);

        let uniqueWords = Array.from(freq.keys());
        uniqueWords.sort((a, b) => (freq.get(b) - freq.get(a)) || a.localeCompare(b));
        if (uniqueWords.length > this.maxVocab) {
            uniqueWords = uniqueWords.slice(0, this.maxVocab);
        }

        const wordToIndex = Object.create(null);
        uniqueWords.forEach((w, i) => (wordToIndex[w] = i));

        const n = uniqueWords.length;
        // Matrice sparsa: ogni riga è una Map<colIndex, count>
        const matrix = Array.from({ length: n }, () => new Map());

        if (n === 0) {
            return { matrix: [], uniqueWords, wordToIndex };
        }

        for (let i = 0; i < words.length; i++) {
            const idx1 = wordToIndex[words[i]];
            if (idx1 === undefined) continue; // parola fuori dal top vocabolario

            const start = Math.max(0, i - windowSize);
            const end = Math.min(words.length, i + windowSize + 1);
            for (let j = start; j < end; j++) {
                if (i === j) continue;
                const idx2 = wordToIndex[words[j]];
                if (idx2 === undefined) continue;
                const row = matrix[idx1];
                // Peso opzionale in funzione della distanza nella finestra
                const wgt = (this.weighting === 'distance') ? (1 / (1 + Math.abs(i - j))) : 1;
                row.set(idx2, (row.get(idx2) || 0) + wgt);
            }
        }

        return { matrix, uniqueWords, wordToIndex };
    }

    // Riduzione dimensionale e mapping nel disco di Poincaré (euristico ma più robusto)
    embedInHyperbolic(matrix) {
        const n = matrix.length;
        const embeddings = new Array(n);

        // SVD path (small matrices only)
        if (this.projection === 'svd' && n <= this.svdMaxN) {
            let SVDLib = null;
            try {
                // Prefer ml-matrix if available
                SVDLib = { type: 'ml', SVD: require('ml-matrix').SVD, Matrix: require('ml-matrix').Matrix };
            } catch (_) {
                try {
                    const SvdJs = require('svd-js');
                    SVDLib = { type: 'svdjs', SVD: SvdJs };
                } catch (_) {
                    if (this.verbose) console.warn('SVD library not found. Falling back to random projection.');
                }
            }

            if (SVDLib) {
                // Build dense n x n matrix with small epsilon smoothing
                const eps = 1e-8;
                if (SVDLib.type === 'ml') {
                    const { Matrix, SVD } = SVDLib;
                    const dense = Matrix.zeros(n, n);
                    for (let i = 0; i < n; i++) {
                        const row = matrix[i];
                        if (row && row.size) {
                            let sum = 0; for (const v of row.values()) sum += v;
                            const denom = Math.max(sum, this._EPS);
                            for (const [j, v] of row.entries()) {
                                dense.set(i, j, v / denom + eps);
                            }
                        } else {
                            // leave eps smoothing via later add
                        }
                    }
                    dense.add(eps);
                    const svd = new SVD(dense, { autoTranspose: true });
                    // U: n x r, S: vector length r
                    const U = svd.leftSingularVectors;
                    const S = svd.diagonal;
                    for (let i = 0; i < n; i++) {
                        const emb = new Array(this.dimension).fill(0);
                        for (let d = 0; d < this.dimension && d < U.columns; d++) {
                            const s = (Array.isArray(S) ? S[d] : S.get ? S.get(d, d) : 1) || 1;
                            emb[d] = U.get(i, d) * s;
                        }
                        // Project to Poincaré
                        let norm2 = 0; for (let d = 0; d < this.dimension; d++) norm2 += emb[d] * emb[d];
                        const norm = Math.sqrt(norm2);
                        const scale = 0.85 / Math.max(norm, this._EPS);
                        const scaleFactor = Math.min(scale, 1.0);
                        for (let d = 0; d < this.dimension; d++) emb[d] *= scaleFactor;
                        embeddings[i] = emb;
                    }
                    return embeddings;
                } else if (SVDLib.type === 'svdjs') {
                    // svd-js expects plain JS matrix: array of arrays
                    const dense = Array.from({ length: n }, () => new Array(n).fill(eps));
                    for (let i = 0; i < n; i++) {
                        const row = matrix[i];
                        if (row && row.size) {
                            let sum = 0; for (const v of row.values()) sum += v;
                            const denom = Math.max(sum, this._EPS);
                            for (const [j, v] of row.entries()) {
                                dense[i][j] = v / denom + eps;
                            }
                        }
                    }
                    const svd = SVDLib.SVD.SVD ? SVDLib.SVD.SVD(dense) : SVDLib.SVD(dense);
                    const U = svd.u || svd.U || svd.left || svd.leftSingularVectors || dense; // best-effort
                    const S = svd.q || svd.s || svd.S || [];
                    for (let i = 0; i < n; i++) {
                        const emb = new Array(this.dimension).fill(0);
                        for (let d = 0; d < this.dimension && U[i] && U[i].length > d; d++) {
                            const s = Array.isArray(S) ? (S[d] ?? 1) : 1;
                            emb[d] = U[i][d] * s;
                        }
                        let norm2 = 0; for (let d = 0; d < this.dimension; d++) norm2 += emb[d] * emb[d];
                        const norm = Math.sqrt(norm2);
                        const scale = 0.85 / Math.max(norm, this._EPS);
                        const scaleFactor = Math.min(scale, 1.0);
                        for (let d = 0; d < this.dimension; d++) emb[d] *= scaleFactor;
                        embeddings[i] = emb;
                    }
                    return embeddings;
                }
            }
            // If SVD not possible, fallthrough to random/firstD below
        }

        // Prepara proiezioni per features: 'firstD' (compat) o 'random' (robusto)
        let randomCols = null;
        if (this.projection === 'random') {
            // Per ogni dimensione, scegli un sottoinsieme di colonne da sommare
            randomCols = Array.from({ length: this.dimension }, () => new Set());
            const targetPerDim = Math.min(Math.max(1, this.randomFeaturesPerDim), Math.max(1, n));
            for (let d = 0; d < this.dimension; d++) {
                // Scegli colonne pseudo-casuali senza ripetizioni
                while (randomCols[d].size < targetPerDim) {
                    const idx = Math.floor(this._rand() * n);
                    randomCols[d].add(idx);
                }
            }
        }

        for (let i = 0; i < n; i++) {
            const row = matrix[i]; // Map o undefined
            let sum = 0;
            if (row && row.size) {
                for (const v of row.values()) sum += v;
            }

            let embedding = new Array(this.dimension).fill(0);
            if (sum > 0 && row && row.size) {
                if (this.projection === 'firstD') {
                    // Compatibilità con versione precedente: prime D colonne
                    for (let d = 0; d < this.dimension; d++) {
                        const val = row.get(d) || 0;
                        embedding[d] = val / sum;
                    }
                } else {
                    // Proiezioni random: per ogni dimensione somma conteggi di un gruppo casuale di colonne
                    for (let d = 0; d < this.dimension; d++) {
                        let acc = 0;
                        for (const col of randomCols[d]) {
                            const v = row.get(col);
                            if (v) acc += v;
                        }
                        embedding[d] = acc / sum; // normalizza per la massa della riga
                    }
                }
            } else {
                // Vettore casuale piccolo per righe senza co-occorrenze
                embedding = Array.from({ length: this.dimension }, () => (this._rand() - 0.5) * 0.1);
            }

            // Proiezione nel disco di Poincaré con r < 1
            let norm2 = 0;
            for (let d = 0; d < this.dimension; d++) norm2 += embedding[d] * embedding[d];
            const norm = Math.sqrt(norm2);
            const scale = 0.85 / Math.max(norm, this._EPS);
            const scaleFactor = Math.min(scale, 1.0);
            for (let d = 0; d < this.dimension; d++) embedding[d] *= scaleFactor;

            embeddings[i] = embedding;
        }

        return embeddings;
    }

    // Distanza di Poincaré con clamp numerico
    poincareDistance(u, v) {
        let uNorm2 = 0, vNorm2 = 0, diffNorm2 = 0;
        for (let i = 0; i < u.length; i++) {
            const ui = u[i], vi = v[i];
            uNorm2 += ui * ui;
            vNorm2 += vi * vi;
            const d = ui - vi;
            diffNorm2 += d * d;
        }

        // clamp per evitare divisioni per zero/negativi
        const oneMinusUNorm = Math.max(1 - uNorm2, this._EPS);
        const oneMinusVNorm = Math.max(1 - vNorm2, this._EPS);
        const denominator = oneMinusUNorm * oneMinusVNorm;
        const numerator = 2 * diffNorm2;

        const argument = 1 + numerator / denominator;
        if (argument <= 1) return 0; // acosh(1) = 0
        return Math.acosh(argument);
    }

    analyzeAndCompress(text) {
        if (this.verbose) console.log("=== ANALISI E COMPRESSIONE TESTO ===");

        // Reset stato per esecuzioni multiple
        this.wordVectors = {};
        this.compressionStats = {};
        const t0 = Date.now();

        if (this.verbose) console.time("1) Preprocessing");
        const words = this.preprocessText(text);
        const t1 = Date.now();
        const uniqueCountPre = new Set(words).size;
        if (this.verbose) console.timeEnd("1) Preprocessing");
        if (this.verbose) console.log(`1. Parole processate: ${words.length} (${uniqueCountPre} uniche prima del cutoff)`);

        if (this.verbose) console.time("2) Co-occorrenza");
        const { matrix, uniqueWords } = this.createCooccurrenceMatrix(words, this.windowSize);
        const t2 = Date.now();
        if (this.verbose) console.timeEnd("2) Co-occorrenza");
        if (!matrix.length) {
            if (this.verbose) console.warn("2. Nessuna parola valida per costruire la matrice (testo troppo breve o tokenizzazione troppo restrittiva)");
            return {
                originalWords: words.length,
                uniqueWords: 0,
                clusters: 0,
                compressionRatio: { original: words.length, compressed: 0, ratio: 0, savings: "0.0" },
                wordVectors: {},
                semanticClusters: [],
                timings: {
                    preprocessMs: t1 - t0,
                    coocMs: t2 - t1,
                    embedMs: 0,
                    clusterMs: 0,
                    totalMs: Date.now() - t0
                },
                clusterThresholdUsed: this.clusterThreshold
            };
        }
        if (this.verbose) console.log(`2. Matrice di co-occorrenza (sparsa): righe=${matrix.length}`);

        if (this.verbose) console.time("3) Embedding");
        const embeddings = this.embedInHyperbolic(matrix);
        const t3 = Date.now();
        if (this.verbose) console.timeEnd("3) Embedding");
        if (this.verbose) console.log(`3. Embeddings iperbolici creati: ${embeddings.length} vettori`);

        // Mapping parola -> vettore
        for (let i = 0; i < uniqueWords.length; i++) {
            this.wordVectors[uniqueWords[i]] = embeddings[i];
        }

    // Auto-tuning della soglia (opzionale)
        let thresholdToUse = this.clusterThreshold;
    if (this.autoThreshold) {
            const tuned = this._autoTuneThreshold(embeddings);
            if (typeof tuned === 'number' && isFinite(tuned) && tuned > 0) {
                thresholdToUse = tuned;
                if (this.verbose) {
                    if (this.autoThresholdMethod === 'mad') {
                        console.log(`3b. Soglia auto-tarata (MAD): ${thresholdToUse.toFixed(3)} (K=${this.autoThresholdMADK})`);
                        if (this._autoStats) {
                            const s = this._autoStats;
                            console.log(`   ↳ median=${s.median?.toFixed?.(4)}, mad=${s.mad?.toFixed?.(4)}, sigma≈${s.sigma?.toFixed?.(4)}, samples=${s.sampleSize}`);
                        }
                    } else if (this.autoThresholdMethod === 'hybrid') {
                        console.log(`3b. Soglia auto-tarata (hybrid): ${thresholdToUse.toFixed(3)} [method=${this._lastAutoChosen}]`);
                        if (this._autoStats) {
                            const s = this._autoStats;
                            console.log(`   ↳ median=${s.median?.toFixed?.(4)}, mad=${s.mad?.toFixed?.(4)}, sigma≈${s.sigma?.toFixed?.(4)}, p95=${s.p95?.toFixed?.(4)}, samples=${s.sampleSize}`);
                        }
                    } else {
                        console.log(`3b. Soglia auto-tarata (percentile): ${thresholdToUse.toFixed(3)} (p=${this.autoThresholdPercentile})`);
                        if (this._autoStats) {
                            const s = this._autoStats;
                            console.log(`   ↳ p${Math.round((s.percentile ?? this.autoThresholdPercentile)*100)}=${s.thresholdFromPercentile?.toFixed?.(4)}, samples=${s.sampleSize}`);
                        }
                    }
                }
            }
        }

        // Diagnostics-only mode: compute stats even if autoThreshold is disabled
        if (this.diagnosticsOnly) {
            if (!this.autoThreshold) {
                // Populate _autoStats by sampling distances but do not use the threshold
                this._autoTuneThreshold(embeddings);
            }
            const tDiag = Date.now();
            return {
                originalWords: words.length,
                uniqueWords: uniqueWords.length,
                clusters: 0,
                compressionRatio: null,
                wordVectors: {},
                semanticClusters: [],
                timings: {
                    preprocessMs: t1 - t0,
                    coocMs: t2 - t1,
                    embedMs: t3 - t2,
                    clusterMs: 0,
                    totalMs: tDiag - t0
                },
                clusterThresholdUsed: this.autoThreshold ? (this._autoStats?.threshold ?? null) : null,
                autoThresholdStats: this._autoStats || null
            };
        }

        if (this.verbose) console.time("4) Clustering");
        const clusters = this.findSemanticClusters(thresholdToUse);
        const t4 = Date.now();
        if (this.verbose) console.timeEnd("4) Clustering");
        if (this.verbose) console.log(`4. Cluster semantici trovati: ${clusters.length}`);

        // Stima compressione
        const compressionRatio = this.estimateCompression(words.length, clusters);
        this.compressionStats = compressionRatio;
        const t5 = Date.now();

        return {
            originalWords: words.length,
            uniqueWords: uniqueWords.length,
            clusters: clusters.length,
            compressionRatio,
            wordVectors: this.wordVectors,
            semanticClusters: clusters,
            timings: {
                preprocessMs: t1 - t0,
                coocMs: t2 - t1,
                embedMs: t3 - t2,
                clusterMs: t4 - t3,
                totalMs: t5 - t0
            },
            clusterThresholdUsed: thresholdToUse,
            autoThresholdStats: this._autoStats || null
        };
    }

    // Stima automatica della soglia di clustering da un percentile delle distanze
    _autoTuneThreshold(embeddings) {
        const n = embeddings.length;
        if (n < 2) return this.clusterThreshold;
    // reset stats container
    this._autoStats = null;
        const targetSamples = this.autoThresholdSample;
        const maxPairs = (n * (n - 1)) / 2;
        const useAll = maxPairs <= targetSamples;
        const dists = [];

        if (useAll) {
            for (let i = 0; i < n; i++) {
                for (let j = i + 1; j < n; j++) {
                    dists.push(this.poincareDistance(embeddings[i], embeddings[j]));
                }
            }
        } else {
            // Campionamento pseudo-casuale riproducibile
            let count = 0;
            while (count < targetSamples) {
                const i = Math.floor(this._rand() * n);
                let j = Math.floor(this._rand() * n);
                if (j === i) continue;
                const a = Math.min(i, j), b = Math.max(i, j);
                dists.push(this.poincareDistance(embeddings[a], embeddings[b]));
                count++;
            }
        }

        if (!dists.length) return this.clusterThreshold;
    dists.sort((a, b) => a - b);

        const computeMadParams = () => {
            // Mediana
            const mid = Math.floor(dists.length / 2);
            const median = (dists.length % 2 === 0) ? (dists[mid - 1] + dists[mid]) / 2 : dists[mid];
            // MAD = median( |x - median| )
            const devs = new Array(dists.length);
            for (let i = 0; i < dists.length; i++) devs[i] = Math.abs(dists[i] - median);
            devs.sort((a, b) => a - b);
            const mid2 = Math.floor(devs.length / 2);
            const mad = (devs.length % 2 === 0) ? (devs[mid2 - 1] + devs[mid2]) / 2 : devs[mid2];
            const sigma = 1.4826 * mad; // consistency factor for Normal
            return { median, mad, sigma };
        };

    const computePercentile = (p) => {
            // Percentile
            const idx = Math.max(0, Math.min(dists.length - 1, Math.floor(p * (dists.length - 1))));
            return dists[idx];
        };
        // Prepare diagnostics
        const { median, mad, sigma } = computeMadParams();
    const p10 = computePercentile(0.10);
    const p25 = computePercentile(0.25);
    const p50 = median;
    const p75 = computePercentile(0.75);
    const p90 = computePercentile(0.90);
    const p95 = computePercentile(0.95);
    const p99 = computePercentile(0.99);
        let chosen = 'percentile';
        let threshold = null;
        if (this.autoThresholdMethod === 'mad') {
            chosen = 'mad';
            let th = median - this.autoThresholdMADK * sigma;
            if (!isFinite(th)) th = this.clusterThreshold;
            threshold = Math.max(1e-6, Math.min(th, 10));
        } else if (this.autoThresholdMethod === 'hybrid') {
            // Simple rule: if upper tail is far from center, prefer MAD
            const outlieriness = p95 - median;
            const preferMad = isFinite(sigma) && sigma > 0 && outlieriness > 3 * sigma;
            chosen = preferMad ? 'mad' : 'percentile';
            if (preferMad) {
                let th = median - this.autoThresholdMADK * sigma;
                if (!isFinite(th)) th = this.clusterThreshold;
                threshold = Math.max(1e-6, Math.min(th, 10));
            } else {
                const th = computePercentile(this.autoThresholdPercentile);
                threshold = Math.max(1e-6, Math.min(th, 10));
            }
        } else {
            const th = computePercentile(this.autoThresholdPercentile);
            threshold = Math.max(1e-6, Math.min(th, 10));
        }

        // Build histogram if requested
        let histogram = null;
        if (this.autoThresholdHistogramBins > 0) {
            const bins = this.autoThresholdHistogramBins | 0;
            const min = dists[0];
            const max = dists[dists.length - 1];
            const counts = new Array(bins).fill(0);
            const span = Math.max(max - min, this._EPS);
            for (let i = 0; i < dists.length; i++) {
                const x = dists[i];
                let b = Math.floor(((x - min) / span) * bins);
                if (b < 0) b = 0; else if (b >= bins) b = bins - 1;
                counts[b]++;
            }
            histogram = { bins, min, max, counts };
        }

        // Save diagnostics
        this._lastAutoChosen = chosen;
        this._autoStats = {
            sampleSize: dists.length,
            usedAllPairs: useAll,
            percentile: this.autoThresholdPercentile,
            autoMethodConfigured: this.autoThresholdMethod,
            chosenMethod: chosen,
            threshold,
            thresholdFromPercentile: computePercentile(this.autoThresholdPercentile),
            median,
            mad,
            sigma,
            p10, p25, p50, p75, p90, p95, p99,
            histogram
        };

        return threshold;
    }

    findSemanticClusters(threshold = 0.4) {
        const words = Object.keys(this.wordVectors);
        const vectors = Object.values(this.wordVectors);
        const n = words.length;
        if (n === 0) return [];

        // Union-Find per componenti connesse in base alla soglia
        const parent = new Array(n);
        for (let i = 0; i < n; i++) parent[i] = i;
        const find = (x) => (parent[x] === x ? x : (parent[x] = find(parent[x])));
        const unite = (a, b) => {
            let ra = find(a), rb = find(b);
            if (ra === rb) return;
            // Unione semplice per indice
            if (ra < rb) parent[rb] = ra; else parent[ra] = rb;
        };

        const euclidDist = (a, b) => {
            let s = 0; for (let k = 0; k < a.length; k++) { const d = a[k] - b[k]; s += d * d; }
            return Math.sqrt(s);
        };

        if (this.clusterK > 0) {
            // k-NN prefilter using Euclidean distance; check hyperbolic only on these pairs
            const K = Math.min(this.clusterK, n - 1);
            for (let i = 0; i < n; i++) {
                let candidateIdxs;
                if (this.approxKNN) {
                    const M = Math.min(this.approxKCandidates, n - 1);
                    const set = new Set();
                    while (set.size < M) {
                        const j = Math.floor(this._rand() * n);
                        if (j !== i) set.add(j);
                    }
                    candidateIdxs = Array.from(set);
                } else {
                    // All others
                    candidateIdxs = [];
                    for (let j = 0; j < n; j++) if (j !== i) candidateIdxs.push(j);
                }
                const dists = [];
                for (const j of candidateIdxs) {
                    dists.push([euclidDist(vectors[i], vectors[j]), j]);
                }
                dists.sort((a, b) => a[0] - b[0]);
                const upto = Math.min(K, dists.length);
                for (let t = 0; t < upto; t++) {
                    const j = dists[t][1];
                    if (i < j) { // guard to avoid duplicating symmetric checks too much
                        const distH = this.poincareDistance(vectors[i], vectors[j]);
                        if (distH < threshold) unite(i, j);
                    }
                }
            }
        } else {
            // Full pairwise check
            for (let i = 0; i < n; i++) {
                for (let j = i + 1; j < n; j++) {
                    const dist = this.poincareDistance(vectors[i], vectors[j]);
                    if (dist < threshold) unite(i, j);
                }
            }
        }

        const groups = new Map();
        for (let i = 0; i < n; i++) {
            const r = find(i);
            if (!groups.has(r)) groups.set(r, []);
            groups.get(r).push(i);
        }

        const clusters = [];
        for (const idxs of groups.values()) {
            // Rappresentante: il primo indice (stabile e deterministico)
            const repIdx = idxs[0];
            const cluster = {
                representative: words[repIdx],
                members: idxs.map(k => words[k]),
                center: [...vectors[repIdx]]
            };
            clusters.push(cluster);
        }

        return clusters.sort((a, b) => b.members.length - a.members.length);
    }

    estimateCompression(originalCount, clusters) {
        // Stima semplificata del guadagno di compressione
        const originalSize = Math.max(1, originalCount | 0);

        // Ogni cluster può essere rappresentato dal suo rappresentante
        // + una tabella di mapping (stimata al 50% del totale membership)
        const mappingOverhead = clusters.reduce((sum, c) => sum + c.members.length, 0) * 0.5;
        const compressedSize = clusters.length + mappingOverhead;

        return {
            original: originalSize,
            compressed: Math.round(compressedSize),
            ratio: compressedSize / originalSize,
            savings: (((originalSize - compressedSize) / originalSize * 100)).toFixed(1)
        };
    }
}

// Esposizione modulo e demo condizionale
if (typeof module !== 'undefined') {
    module.exports = HyperbolicTextCompressor;
}

if (typeof require !== 'undefined' && require.main === module) {
    // TEST FINALE (solo quando eseguito direttamente)
    const testText = `
Gregorio Samsa, svegliandosi una mattina da sogni agitati, si trovò trasformato, nel suo letto, in un enorme insetto immondo. Riposava sulla schiena, dura come una corazza, e sollevando un poco il capo vedeva il suo ventre arcuato, bruno e diviso in tanti segmenti ricurvi, in cima a cui la coperta da letto, vicina a scivolar giù tutta, si manteneva a fatica. Le gambe, numerose e sottili da far pietà, rispetto alla sua corporatura normale, tremolavano senza tregua in un confuso luccichio dinanzi ai suoi occhi. Cosa m’è avvenuto? pensò. Non era un sogno. La sua camera, una stanzetta di giuste proporzioni, soltanto un po’ piccola, se ne stava tranquilla fra le quattro ben note pareti. Sulla tavola, un campionario disfatto di tessuti - Samsa era commesso viaggiatore e sopra, appeso alla parete, un ritratto, ritagliato da lui - non era molto - da una rivista illustrata e messo dentro una bella cornice dorata: raffigurava una donna seduta, ma ben dritta sul busto, con un berretto e un boa di pelliccia; essa levava incontro a chi guardava un pesante manicotto, in cui scompariva tutto l’avambraccio. Lo sguardo di Gregorio si rivolse allora verso la finestra, e il cielo fosco (si sentivano battere le gocce di pioggia sullo zinco della finestra) lo immalinconì completamente. Che avverrebbe se io dormissi ancora un poco e dimenticassi ogni pazzia? pensò; ma ciò era assolutamente impossibile, perché Gregorio era abituato a dormire sulla destra, ma non poteva, nelle sue attuali condizioni, mettersi in quella posizione. Per quanto si gettasse con tutta la sua forza da quella parte, tornava sempre oscillando sul dorso: provò per cento volte, chiuse gli occhi per non veder le sue zampine dimenanti, e rinunciò soltanto quando cominciò a sentire nel fianco un dolore sottile e sordo, ancora non mai provato. O Dio,
`;

    const compressor = new HyperbolicTextCompressor(2, { seed: 42 });
    const results = compressor.analyzeAndCompress(testText);

    console.log("\n=== RISULTATI FINALI ===");
    console.log(`📊 Parole totali: ${results.originalWords}`);
    console.log(`📊 Parole uniche: ${results.uniqueWords}`);
    console.log(`📊 Cluster semantici: ${results.clusters}`);
    console.log(`📊 Rapporto di compressione: ${results.compressionRatio.ratio.toFixed(3)}`);
    console.log(`💾 Risparmio stimato: ${results.compressionRatio.savings}%`);

    console.log("\n🎯 CLUSTER SEMANTICI PIÙ INTERESSANTI:");
    results.semanticClusters.filter(c => c.members.length > 1).slice(0, 5).forEach((cluster, i) => {
        console.log(`${i+1}. "${cluster.representative}" → [${cluster.members.join(', ')}]`);
    });
}

// Embedded minimal tests (run when HTC_RUN_TESTS=1)
if (typeof process !== 'undefined' && process.env && process.env.HTC_RUN_TESTS === '1') {
    const assert = (cond, msg) => { if (!cond) throw new Error(msg || 'Assertion failed'); };

    (function testTokenization() {
        const c = new HyperbolicTextCompressor(2, { seed: 1 });
        const words = c.preprocessText('Caffè è buono; café aussi! A 1 b.');
        assert(words.includes('caffè'), 'Should keep caffè');
        assert(words.includes('café'), 'Should keep café');
        assert(!words.includes('a'), 'Should drop single-letter tokens');
    })();

    (function testEmpty() {
        const c = new HyperbolicTextCompressor(2, { seed: 1 });
        const res = c.analyzeAndCompress('   ');
        assert(res.uniqueWords === 0, 'Empty input should yield zero uniqueWords');
        assert(res.semanticClusters.length === 0, 'Empty input should yield zero clusters');
    })();

    (function testDeterminism() {
        const c1 = new HyperbolicTextCompressor(2, { seed: 42 });
        const c2 = new HyperbolicTextCompressor(2, { seed: 42 });
        const text = 'uno due tre due tre tre';
        const r1 = c1.analyzeAndCompress(text);
        const r2 = c2.analyzeAndCompress(text);
        const keys1 = Object.keys(r1.wordVectors).join(',');
        const keys2 = Object.keys(r2.wordVectors).join(',');
        assert(keys1 === keys2, 'Same vocab ordering');
    })();

    console.log('Embedded tests passed.');
}