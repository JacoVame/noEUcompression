#!/usr/bin/env node
/**
 * Pretty report generator for bench.js JSONL output.
 *
 * Usage:
 *   node ./tools/pretty-report.js --input ./out/bench.jsonl [--html ./out/report.html]
 *   node ./tools/pretty-report.js --glob ./out/*.jsonl [--html ./out/report.html]
 */

const fs = require('fs');
const path = require('path');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    const n = argv[i + 1];
    switch (a) {
      case '--input': args.input = n; i++; break;
      case '--glob': args.glob = n; i++; break;
      case '--html': args.html = n; i++; break;
      default: break;
    }
  }
  return args;
}

function collectFiles(args) {
  if (args.input) return [args.input];
  if (args.glob) {
    const dir = path.dirname(args.glob);
    const patt = new RegExp('^' + path.basename(args.glob).replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*') + '$', 'i');
    return fs.readdirSync(dir)
      .filter(f => patt.test(f))
      .map(f => path.join(dir, f));
  }
  const fallback = path.join(process.cwd(), 'out', 'bench.jsonl');
  if (fs.existsSync(fallback)) return [fallback];
  return [];
}

function readJsonl(files) {
  const rows = [];
  for (const file of files) {
    if (!fs.existsSync(file)) continue;
    const lines = fs.readFileSync(file, 'utf8').split(/\r?\n/).filter(Boolean);
    for (const line of lines) {
      try { rows.push(JSON.parse(line)); } catch (_) {}
    }
  }
  return rows;
}

function toTable(rows) {
  if (rows.length === 0) return 'No data. Run bench first.';
  const cols = ['input','dimension','projection','clusterK','autoThreshold','clusterThresholdUsed','uniqueWords','clusters','ratio','savingsPct'];
  const widths = cols.map(c => Math.max(c.length, ...rows.map(r => String(r[c] ?? '').length)));
  const sep = '+' + widths.map(w => '-'.repeat(w + 2)).join('+') + '+\n';
  const head = '|' + cols.map((c,i) => ' ' + c.padEnd(widths[i]) + ' ').join('|') + '|\n';
  let out = sep + head + sep;
  for (const r of rows) {
    out += '|' + cols.map((c,i) => {
      let v = r[c];
      if (typeof v === 'number') {
        if (c === 'ratio' || c === 'savingsPct' || c === 'clusterThresholdUsed') v = Number(v.toFixed(3));
      }
      v = String(v ?? '');
      return ' ' + v.padEnd(widths[i]) + ' ';
    }).join('|') + '|\n';
  }
  out += sep;
  return out;
}

function smallBar(pct) {
  const n = Math.max(0, Math.min(20, Math.round((pct || 0) / 5)));
  return '█'.repeat(n) + ' '.repeat(20 - n);
}

function groupBy(arr, key) {
  const m = new Map();
  for (const r of arr) {
    const k = r[key];
    if (!m.has(k)) m.set(k, []);
    m.get(k).push(r);
  }
  return m;
}

function svgBarChart(items, { title = '', labelKey = 'label', valueKey = 'value', unit = '', max = undefined, width = 720, barH = 18, gap = 6, color = '#6366f1' } = {}) {
  const data = items.filter(d => Number.isFinite(d[valueKey]));
  if (data.length === 0) return '';
  const maxVal = max ?? Math.max(...data.map(d => d[valueKey]));
  const margin = { top: 30, right: 20, bottom: 24, left: 180 };
  const innerW = width - margin.left - margin.right;
  const height = margin.top + margin.bottom + data.length * (barH + gap);
  const scale = v => (maxVal === 0 ? 0 : (v / maxVal) * innerW);
  let bars = '';
  data.forEach((d, i) => {
    const y = margin.top + i * (barH + gap);
    const w = scale(d[valueKey]);
    const label = String(d[labelKey]);
    const valTxt = unit ? `${d[valueKey].toFixed(1)}${unit}` : `${d[valueKey]}`;
    bars += `\n    <text x="${margin.left - 8}" y="${y + barH * 0.7}" text-anchor="end" fill="#374151" font-size="12">${label}</text>`;
    bars += `\n    <rect x="${margin.left}" y="${y}" width="${w}" height="${barH}" fill="${color}" rx="3"/>`;
    bars += `\n    <text x="${margin.left + w + 6}" y="${y + barH * 0.7}" fill="#374151" font-size="12">${valTxt}</text>`;
  });
  return `\n  <svg width="${width}" height="${height}" class="chart">\n    <text x="${margin.left}" y="20" font-weight="600" fill="#111827">${title}</text>${bars}\n    <line x1="${margin.left}" y1="${height - margin.bottom}" x2="${width - margin.right}" y2="${height - margin.bottom}" stroke="#e5e7eb"/>\n  </svg>`;
}

function svgHistogram(hist, { title = '', width = 720, height = 180, color = '#10b981' } = {}) {
  const { bins, min, max, counts } = hist || {};
  if (!bins || !counts || counts.length === 0) return '';
  const margin = { top: 28, right: 16, bottom: 28, left: 40 };
  const innerW = width - margin.left - margin.right;
  const innerH = height - margin.top - margin.bottom;
  const maxCount = Math.max(...counts);
  const barW = innerW / counts.length;
  let bars = '';
  counts.forEach((c, i) => {
    const h = maxCount === 0 ? 0 : (c / maxCount) * innerH;
    const x = margin.left + i * barW;
    const y = margin.top + (innerH - h);
    bars += `\n    <rect x="${x}" y="${y}" width="${Math.max(1, barW - 1)}" height="${h}" fill="${color}"/>`;
  });
  return `\n  <svg width="${width}" height="${height}" class="chart">\n    <text x="${margin.left}" y="20" font-weight="600" fill="#111827">${title}</text>\n    ${bars}\n    <text x="${margin.left}" y="${height - 8}" font-size="12" fill="#6b7280">${(min ?? '').toString()}</text>\n    <text x="${width - margin.right}" y="${height - 8}" font-size="12" fill="#6b7280" text-anchor="end">${(max ?? '').toString()}</text>\n  </svg>`;
}

function svgGroupedBars(groups, { title = '', unit = '', width = 720, barH = 16, groupGap = 10, barGap = 6, colors = [] } = {}) {
  // groups: [{ label: 'K=0', series: [{ name: 'random', value: 50 }, { name: 'svd', value: 45 }] }]
  if (!groups || groups.length === 0) return '';
  const seriesNames = Array.from(new Set(groups.flatMap(g => g.series.map(s => s.name))));
  const palette = colors.length ? colors : ['#2563eb','#22c55e','#f59e0b','#ef4444','#8b5cf6','#06b6d4'];
  const margin = { top: 30, right: 20, bottom: 24, left: 60 + Math.max(...groups.map(g => g.label.length)) * 6 };
  const innerW = width - margin.left - margin.right;
  const maxVal = Math.max(...groups.flatMap(g => g.series.map(s => s.value || 0)));
  const scale = v => (maxVal === 0 ? 0 : (v / maxVal) * innerW);
  const groupHeight = seriesNames.length * (barH + barGap) - barGap; // bars stacked in a group
  const height = margin.top + margin.bottom + groups.length * (groupHeight + groupGap);
  let svg = `\n  <svg width="${width}" height="${height}" class="chart">\n    <text x="${margin.left}" y="20" font-weight="600" fill="#111827">${title}</text>`;
  groups.forEach((g, gi) => {
    const y0 = margin.top + gi * (groupHeight + groupGap);
    // label
    svg += `\n    <text x="${margin.left - 8}" y="${y0 + barH}" text-anchor="end" fill="#374151" font-size="12">${g.label}</text>`;
    g.series.forEach((s, si) => {
      const y = y0 + si * (barH + barGap);
      const w = scale(s.value || 0);
      const color = palette[seriesNames.indexOf(s.name) % palette.length];
      const valTxt = unit ? `${(s.value||0).toFixed(1)}${unit}` : `${s.value||0}`;
      svg += `\n    <rect x="${margin.left}" y="${y}" width="${w}" height="${barH}" fill="${color}" rx="3"/>`;
      svg += `\n    <text x="${margin.left + w + 6}" y="${y + barH * 0.7}" fill="#374151" font-size="12">${valTxt}</text>`;
    });
  });
  // legend
  let lx = margin.left, ly = height - margin.bottom + 10;
  seriesNames.forEach((name, i) => {
    const color = palette[i % palette.length];
    svg += `\n    <rect x="${lx}" y="${ly}" width="10" height="10" fill="${color}"/>`;
    svg += `\n    <text x="${lx + 14}" y="${ly + 10}" font-size="12" fill="#374151">${name}</text>`;
    lx += 90;
  });
  svg += '\n  </svg>';
  return svg;
}

function toHtml(rows) {
  const css = `
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; color: #1f2937; }
    h1 { font-size: 20px; margin-bottom: 12px; }
    h2 { font-size: 16px; margin: 22px 0 8px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #e5e7eb; padding: 8px 10px; font-size: 13px; }
    th { background: #f9fafb; text-align: left; }
    tr:nth-child(even) { background: #fcfcfd; }
    code { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }
    .bar { font-family: 'Courier New', monospace; white-space: pre; background: #eef2ff; padding: 2px 4px; border-radius: 3px; }
    .muted { color: #6b7280; }
    .chart { margin: 8px 0 2px; display: block; width: 100%; height: auto; }
  </style>`;
  const header = '<h1>Hyperbolic Bench Report</h1>';
  const cols = ['input','dimension','projection','clusterK','autoThreshold','clusterThresholdUsed','uniqueWords','clusters','ratio','savingsPct'];
  const thead = '<tr>' + cols.map(c => `<th>${c}</th>`).join('') + '</tr>';
  const rowsHtml = rows.map(r => {
    const cells = cols.map(c => {
      let v = r[c];
      if (typeof v === 'number') {
        if (c === 'ratio' || c === 'savingsPct' || c === 'clusterThresholdUsed') v = Number(v.toFixed(3));
      }
      if (c === 'savingsPct') {
        return `<td><div class="bar">${smallBar(v)} ${v?.toFixed?.(1) ?? ''}%</div></td>`;
      }
      return `<td>${v ?? ''}</td>`;
    }).join('');
    return `<tr>${cells}</tr>`;
  }).join('\n');

  // Summary charts by input (use run with max savingsPct per input)
  const byInput = groupBy(rows, 'input');
  const bestPerInput = [];
  for (const [inp, arr] of byInput.entries()) {
    const filtered = arr.filter(r => Number.isFinite(r.savingsPct));
    if (filtered.length === 0) continue;
    const best = filtered.reduce((a,b) => (a.savingsPct >= b.savingsPct ? a : b));
    bestPerInput.push({
      label: inp,
      savingsPct: best.savingsPct,
      clusters: best.clusters,
      projection: best.projection,
      clusterK: best.clusterK,
    });
  }
  let chartsHtml = '';
  if (bestPerInput.length) {
    chartsHtml += '<h2>Summary charts</h2>';
    chartsHtml += svgBarChart(bestPerInput.map(d => ({ label: d.label, value: d.savingsPct })), { title: 'Savings by input (best run) — higher is better', unit: '%', color: '#2563eb' });
    chartsHtml += svgBarChart(bestPerInput.map(d => ({ label: d.label, value: d.clusters })), { title: 'Clusters by input (from best run)', color: '#f59e0b' });
  }

  // Savings% by K for each projection
  const byProj = groupBy(rows.filter(r => Number.isFinite(r.savingsPct)), 'projection');
  for (const [proj, arr] of byProj.entries()) {
    const byK = new Map();
    for (const r of arr) {
      const k = r.clusterK ?? 0;
      if (!byK.has(k)) byK.set(k, []);
      byK.get(k).push(r.savingsPct);
    }
    const items = Array.from(byK.entries())
      .map(([k, vals]) => ({ label: `K=${k}`, value: vals.reduce((a,b)=>a+b,0)/vals.length }))
      .sort((a,b) => parseInt(a.label.slice(2),10) - parseInt(b.label.slice(2),10));
    chartsHtml += svgBarChart(items, { title: `Savings by K — projection=${proj}`, unit: '%', color: '#22c55e' });
  }

  // Clusters by K for each projection
  for (const [proj, arr] of byProj.entries()) {
    const byKc = new Map();
    for (const r of arr) {
      const k = r.clusterK ?? 0;
      if (!byKc.has(k)) byKc.set(k, []);
      byKc.get(k).push(r.clusters || 0);
    }
    const items = Array.from(byKc.entries())
      .map(([k, vals]) => ({ label: `K=${k}`, value: vals.reduce((a,b)=>a+b,0)/Math.max(1, vals.length) }))
      .sort((a,b) => parseInt(a.label.slice(2),10) - parseInt(b.label.slice(2),10));
    chartsHtml += svgBarChart(items, { title: `Clusters by K — projection=${proj}`, color: '#f97316' });
  }

  // Grouped: savings% by K across projections
  const rowsWithSP = rows.filter(r => Number.isFinite(r.savingsPct));
  const projNames = Array.from(new Set(rowsWithSP.map(r => r.projection)));
  const kValues = Array.from(new Set(rowsWithSP.map(r => r.clusterK ?? 0))).sort((a,b)=>a-b);
  const groups = kValues.map(k => {
    const series = projNames.map(p => {
      const vals = rowsWithSP.filter(r => (r.clusterK ?? 0) === k && r.projection === p).map(r => r.savingsPct);
      const avg = vals.length ? vals.reduce((a,b)=>a+b,0)/vals.length : 0;
      return { name: p, value: avg };
    });
    return { label: `K=${k}`, series };
  });
  if (groups.length && projNames.length > 1) {
    chartsHtml += svgGroupedBars(groups, { title: 'Savings by K across projections (avg)', unit: '%', width: 760 });
  }

  // Optional diagnostics summary (from the first run that has it)
  const diag = rows.find(r => r.autoThresholdStats)?.autoThresholdStats;
  const diagHtml = diag ? `
    <h2>Auto-threshold diagnostics</h2>
    <div class="muted">method=${diag.chosenMethod}, p=${diag.percentile}, sampleSize=${diag.sampleSize}</div>
    <ul>
      <li>median=${diag.median}, mad=${diag.mad}, sigma=${diag.sigma}</li>
      <li>p10=${diag.p10}, p25=${diag.p25}, p50=${diag.p50}, p75=${diag.p75}, p90=${diag.p90}, p95=${diag.p95}, p99=${diag.p99}</li>
    </ul>
  ` : '';

  // Per-run histograms (when available)
  const histRuns = rows.filter(r => r.autoThresholdStats && r.autoThresholdStats.histogram);
  let histsHtml = '';
  if (histRuns.length) {
    histsHtml += '<h2>Distance histograms (per run)</h2>';
    for (const r of histRuns) {
      const t = `${r.input} — d=${r.dimension}, proj=${r.projection}, k=${r.clusterK}`;
      histsHtml += svgHistogram(r.autoThresholdStats.histogram, { title: t });
    }
  }

  return `<!doctype html><html><head><meta charset="utf-8"/>${css}</head><body>
    ${header}
    <table><thead>${thead}</thead><tbody>${rowsHtml}</tbody></table>
    ${chartsHtml}
    ${diagHtml}
    ${histsHtml}
  </body></html>`;
}

function main() {
  const args = parseArgs(process.argv);
  const files = collectFiles(args);
  const rows = readJsonl(files);

  // Console pretty table
  const table = toTable(rows);
  console.log(table);

  // Optional HTML export
  if (args.html) {
    try {
      const dir = path.dirname(args.html);
      if (dir && dir !== '.' && !fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(args.html, toHtml(rows), 'utf8');
      console.log(`\nHTML report written to ${args.html}`);
    } catch (err) {
      console.error('Failed to write HTML report:', err.message);
    }
  }
}

if (require.main === module) {
  main();
}
