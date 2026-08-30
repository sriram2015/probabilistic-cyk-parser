const $ = (id) => document.getElementById(id);

function pct(x) {
  return (x * 100).toFixed(2) + "%";
}

function renderTree(node) {
  const wrap = document.createElement("div");
  wrap.className = "tree";

  const box = document.createElement("div");
  box.className = "node";
  box.innerHTML = `<div class="node-label">${node.label}</div>
                   <div class="node-prob">${pct(node.probability)}</div>`;
  wrap.appendChild(box);

  if (node.children && node.children.length) {
    const children = document.createElement("div");
    children.className = "children";
    node.children.forEach(child => {
      const childWrap = document.createElement("div");
      childWrap.className = "child";
      if (typeof child === "string") {
        childWrap.innerHTML = `<div class="node"><div class="node-label">${child}</div></div>`;
      } else {
        childWrap.appendChild(renderTree(child));
      }
      children.appendChild(childWrap);
    });
    wrap.appendChild(children);
  }
  return wrap;
}

function renderChartTable(chart) {
  let html = `<table><thead><tr><th>Span</th><th>Words</th><th>Non-terminals and best probabilities</th></tr></thead><tbody>`;
  chart.forEach(cell => {
    const values = cell.entries.length
      ? cell.entries.map(e => `${e.symbol} = ${pct(e.probability)}`).join("<br>")
      : "—";
    html += `<tr><td>[${cell.start}, ${cell.end})</td><td>${cell.text}</td><td>${values}</td></tr>`;
  });
  html += "</tbody></table>";
  $("chartTable").innerHTML = html;
}

function drawProbabilityChart(chart) {
  const canvas = $("probChart");
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const data = chart
    .map(c => ({
      label: c.text.length > 13 ? c.text.slice(0, 13) + "…" : c.text,
      value: c.entries.length ? Math.max(...c.entries.map(e => e.probability)) : 0
    }))
    .filter(x => x.value > 0);

  const pad = 45, bottom = 65, top = 20;
  const w = canvas.width - pad * 2, h = canvas.height - bottom - top;
  const barW = Math.max(9, w / Math.max(data.length, 1) - 5);

  ctx.strokeStyle = "#d6dce7";
  ctx.beginPath(); ctx.moveTo(pad, top); ctx.lineTo(pad, top + h); ctx.lineTo(pad + w, top + h); ctx.stroke();

  data.forEach((d, i) => {
    const x = pad + i * (w / data.length) + 2;
    const bh = Math.max(2, d.value * h);
    ctx.fillStyle = "#3b5ccc";
    ctx.fillRect(x, top + h - bh, barW, bh);

    ctx.fillStyle = "#344054";
    ctx.font = "10px Arial";
    ctx.save();
    ctx.translate(x + barW / 2, top + h + 13);
    ctx.rotate(-0.55);
    ctx.textAlign = "right";
    ctx.fillText(d.label, 0, 0);
    ctx.restore();
  });

  ctx.fillStyle = "#667085";
  ctx.font = "11px Arial";
  ctx.fillText("Best cell probability", 5, 14);
}

function renderMetrics(m) {
  $("metrics").innerHTML = `
    <div class="metric-row"><span>Algorithm</span><strong>${m.algorithm}</strong></div>
    <div class="metric-row"><span>Complexity</span><strong>${m.complexity}</strong></div>
    <div class="metric-row"><span>Tokens</span><strong>${m.tokens}</strong></div>
    <div class="metric-row"><span>CKY chart cells</span><strong>${m.chart_cells}</strong></div>
    <div class="metric-row"><span>Candidate operations</span><strong>${m.candidate_operations}</strong></div>`;
}

async function parseSentence() {
  const sentence = $("sentence").value.trim();
  $("error").classList.add("hidden");
  if (!sentence) return;

  try {
    const response = await fetch("/api/parse", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({sentence})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Parsing failed.");

    $("prob").textContent = pct(data.most_likely_probability);
    $("tokens").textContent = data.metrics.tokens;
    $("cells").textContent = data.metrics.chart_cells;
    $("ops").textContent = data.metrics.candidate_operations;

    $("tree").innerHTML = "";
    $("tree").appendChild(renderTree(data.tree));
    $("brackets").textContent = data.bracketed_tree;

    renderChartTable(data.chart);
    drawProbabilityChart(data.chart);
    renderMetrics(data.metrics);
  } catch (err) {
    $("error").textContent = err.message;
    $("error").classList.remove("hidden");
  }
}

async function loadGrammar() {
  const response = await fetch("/api/grammar");
  const data = await response.json();
  $("grammar").innerHTML = data.rules.map(r =>
    `<div class="rule"><span>${r.lhs} → ${r.rhs}</span><strong>${r.probability}</strong></div>`
  ).join("");
}

$("parseBtn").addEventListener("click", parseSentence);
$("sentence").addEventListener("keydown", e => {
  if (e.key === "Enter") parseSentence();
});
document.querySelectorAll(".example").forEach(btn => {
  btn.addEventListener("click", () => {
    $("sentence").value = btn.dataset.sentence;
    parseSentence();
  });
});

loadGrammar();
parseSentence();
