/*
 Quick benchmark harness for HyperbolicTextCompressor

 Usage examples (PowerShell):
   node .\bench.js --file sample.txt
   node .\bench.js --dir ./texts --projection random,svd --k 0,15 --percentile 0.35 --sample 3000

 Options:
   --file <path>            Single text file to analyze
   --dir <path>             Directory of .txt files (non-recursive)
   --dimension <int>        Embedding dimensions (default 2)
   --projection <list>      Comma-separated list: random,firstD,svd (default random)
   --k <list>               Comma-separated list of clusterK values (default 0)
   --threshold <number>     Fixed hyperbolic threshold (overrides auto)
   --auto                   Enable auto-threshold (percentile-based)
   --percentile <0..1>      Percentile used for auto threshold (default 0.35)
   --sample <int>           Max pair samples for auto threshold (default 3000)
  --autoMethod <m>         'percentile', 'mad', or 'hybrid' (default 'percentile')
  --madK <number>          K for MAD-based threshold (median - K * 1.4826 * MAD), default 0.5
  --autoStats              Include auto-threshold diagnostics in JSON output
  --diagOnly               Run in diagnostics-only mode (no clustering; emit auto-stats)
  --histBins <int>         Number of histogram bins for distance samples (0 disables)
  --approxKNN <0|1>        Enable approximate k-NN prefilter when --k>0 (default 0)
  --approxKCandidates <n>  Number of candidate neighbors to sample per node (default 50)
  --emitClusters <path>    Write clusters for each run as JSON to the given directory
  --outJson <path>         Append JSON lines output to a file instead of stdout
   --weighting <w>          'uniform' or 'distance' (default 'uniform')
   --window <int>           Co-occurrence window size (default 3)
   --maxVocab <int>         Max vocabulary (default 5000)
   --seed <int>             RNG seed (default random)
   --svdMaxN <int>          Max n for SVD path (default 800)
   --normalize <0|1>        Unicode normalization on/off (default 1)
   --verbose <0|1>          Verbose logging (default 0 in bench)

 Output: JSON lines, one per run configuration and input. Includes timings and cluster stats.
*/

const fs = require('fs');
const path = require('path');
const HyperbolicTextCompressor = require('./compressionTest');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    const n = argv[i + 1];
    switch (a) {
      case '--file': args.file = n; i++; break;
      case '--dir': args.dir = n; i++; break;
      case '--dimension': args.dimension = parseInt(n, 10); i++; break;
  case '--dimensions': args.dimensions = String(n); i++; break;
      case '--projection': args.projection = String(n); i++; break;
      case '--k': args.k = String(n); i++; break;
      case '--threshold': args.threshold = parseFloat(n); i++; break;
      case '--auto': args.auto = true; break;
      case '--percentile': args.percentile = parseFloat(n); i++; break;
      case '--sample': args.sample = parseInt(n, 10); i++; break;
  case '--autoMethod': args.autoMethod = String(n); i++; break;
  case '--madK': args.madK = parseFloat(n); i++; break;
  case '--autoStats': args.autoStats = true; break;
  case '--diagOnly': args.diagOnly = true; break;
  case '--histBins': args.histBins = parseInt(n, 10); i++; break;
  case '--approxKNN': args.approxKNN = parseInt(n, 10) !== 0; i++; break;
  case '--approxKCandidates': args.approxKCandidates = parseInt(n, 10); i++; break;
  case '--emitClusters': args.emitClusters = String(n); i++; break;
  case '--outJson': args.outJson = String(n); i++; break;
      case '--weighting': args.weighting = String(n); i++; break;
      case '--window': args.window = parseInt(n, 10); i++; break;
      case '--maxVocab': args.maxVocab = parseInt(n, 10); i++; break;
      case '--seed': args.seed = parseInt(n, 10); i++; break;
      case '--svdMaxN': args.svdMaxN = parseInt(n, 10); i++; break;
      case '--normalize': args.normalize = parseInt(n, 10) !== 0; i++; break;
      case '--verbose': args.verbose = parseInt(n, 10) !== 0; i++; break;
      default:
        break;
    }
  }
  return args;
}

function readInputs(args) {
  const inputs = [];
  if (args.file) {
    inputs.push({ name: path.basename(args.file), text: fs.readFileSync(args.file, 'utf8') });
  }
  if (args.dir) {
    const files = fs.readdirSync(args.dir).filter(f => f.toLowerCase().endsWith('.txt'));
    for (const f of files) {
      const p = path.join(args.dir, f);
      const text = fs.readFileSync(p, 'utf8');
      inputs.push({ name: f, text });
    }
  }
  if (inputs.length === 0) {
    // Fallback: use the demo paragraph embedded in compressionTest.js
    const demo = `Gregorio Samsa, svegliandosi una mattina da sogni agitati...`;
    inputs.push({ name: 'demo', text: demo });
  }
  return inputs;
}

function main() {
  const args = parseArgs(process.argv);
  const inputs = readInputs(args);
  const dims = args.dimensions ? args.dimensions.split(',').map(x => parseInt(x,10)).filter(Number.isFinite) : [args.dimension || 2];
  const projections = (args.projection ? args.projection.split(',') : ['random']).map(s => s.trim());
  const ks = (args.k ? args.k.split(',').map(x => parseInt(x, 10)) : [0]);

  for (const inp of inputs) {
    for (const dim of dims) {
      for (const proj of projections) {
        for (const k of ks) {
          const options = {
            maxVocab: args.maxVocab ?? 5000,
            seed: isFinite(args.seed) ? args.seed : 42,
            windowSize: args.window ?? 3,
            clusterThreshold: isFinite(args.threshold) ? args.threshold : 0.4,
            projection: proj,
            randomFeaturesPerDim: 16,
            weighting: args.weighting || 'uniform',
            normalize: args.normalize !== false,
            verbose: !!args.verbose,
            svdMaxN: args.svdMaxN ?? 800,
            clusterK: isFinite(k) ? k : 0,
            approxKNN: !!args.approxKNN,
            approxKCandidates: isFinite(args.approxKCandidates) ? args.approxKCandidates : 50,
            autoThreshold: !!args.auto,
            autoThresholdPercentile: isFinite(args.percentile) ? args.percentile : 0.35,
            autoThresholdSample: isFinite(args.sample) ? args.sample : 3000,
            autoThresholdMethod: (['mad','percentile','hybrid'].includes(args.autoMethod) ? args.autoMethod : 'percentile'),
            autoThresholdMADK: isFinite(args.madK) ? args.madK : 0.5,
            autoThresholdHistogramBins: isFinite(args.histBins) ? args.histBins : 0,
            diagnosticsOnly: !!args.diagOnly,
          };

          const c = new HyperbolicTextCompressor(dim, options);
          const start = Date.now();
          const res = c.analyzeAndCompress(inp.text);
          const end = Date.now();

          const out = {
            input: inp.name,
            dimension: dim,
            projection: proj,
            clusterK: k,
            autoThreshold: !!args.auto,
            clusterThresholdUsed: res.clusterThresholdUsed,
            uniqueWords: res.uniqueWords,
            clusters: res.clusters,
            ratio: res.compressionRatio?.ratio ?? null,
            savingsPct: res.compressionRatio?.savings ?? null,
            timingsMs: res.timings ?? { totalMs: end - start },
          };
          if (args.autoStats && res.autoThresholdStats) {
            out.autoThresholdStats = res.autoThresholdStats;
          }
          const line = JSON.stringify(out);
          if (args.outJson) {
            try {
              const outDir = path.dirname(args.outJson);
              if (outDir && outDir !== '.' && !fs.existsSync(outDir)) {
                fs.mkdirSync(outDir, { recursive: true });
              }
            } catch (_) {}
            fs.appendFileSync(args.outJson, line + '\n');
          } else {
            console.log(line);
          }

          if (args.emitClusters && res.semanticClusters && res.semanticClusters.length) {
            try {
              if (!fs.existsSync(args.emitClusters)) fs.mkdirSync(args.emitClusters, { recursive: true });
              const base = `${inp.name}__d${dim}__${proj}__k${k}`.replace(/[^a-zA-Z0-9_.-]+/g,'_');
              const p = path.join(args.emitClusters, base + '.clusters.json');
              fs.writeFileSync(p, JSON.stringify(res.semanticClusters, null, 2));
            } catch(_){}
          }
        }
      }
    }
  }
}

if (require.main === module) {
  try {
    main();
  } catch (err) {
    console.error('Benchmark failed:', err && err.stack || err);
    process.exit(1);
  }
}
