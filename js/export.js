/**
 * export.js — On-the-fly single-file collection exporter (Transcription Only & Manuscript Only)
 * Supports: .md, .html, .doc, .pdf, .zip
 */
(function (global) {
  "use strict";

  const GITHUB_REPO = "feureau/1792-1809_-_Yogya_Residency_Letters";
  const RAW_BASE = `https://raw.githubusercontent.com/${GITHUB_REPO}/main/`;
  const COLLECTION_TITLE = "1792–1809 Yogyakarta Residency Letters";
  const BASE_FILENAME = "1792-1809_Yogya_Residency_Letters";
  const FETCH_CONCURRENCY = 6;

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function downloadBlob(filename, content, mimeType) {
    const blob = content instanceof Blob ? content : new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 10000);
  }

  function uint8ToBase64(bytes) {
    const chunkSize = 0x8000;
    const parts = [];
    for (let i = 0; i < bytes.length; i += chunkSize) {
      parts.push(String.fromCharCode.apply(null, bytes.subarray(i, i + chunkSize)));
    }
    return btoa(parts.join(""));
  }

  function yieldFrame() {
    return new Promise((resolve) => setTimeout(resolve, 0));
  }

  async function fetchPool(items, worker, signal, onProgress) {
    const results = new Array(items.length);
    let nextIndex = 0;
    let completed = 0;

    async function runWorker() {
      while (true) {
        if (signal && signal.aborted) {
          throw new DOMException("Export cancelled", "AbortError");
        }
        const idx = nextIndex++;
        if (idx >= items.length) break;
        results[idx] = await worker(items[idx], idx);
        completed++;
        if (onProgress) onProgress(completed, items.length);
      }
    }

    const workers = [];
    const count = Math.min(FETCH_CONCURRENCY, items.length);
    for (let i = 0; i < count; i++) {
      workers.push(runWorker());
    }
    await Promise.all(workers);
    return results;
  }

  async function loadIndex(signal) {
    const res = await fetch("data.json", { cache: "no-store", signal });
    if (!res.ok) throw new Error(`Could not load data.json (HTTP ${res.status})`);
    return await res.json();
  }

  async function fetchAllTranscriptions(list, mdCache, signal, onProgress) {
    return await fetchPool(
      list,
      async (entry) => {
        if (mdCache && typeof mdCache[entry.id] === "string" && mdCache[entry.id].length > 0) {
          return { id: entry.id, textPath: entry.text, md: mdCache[entry.id] };
        }
        const res = await fetch(entry.text, { cache: "no-store", signal });
        if (!res.ok) {
          throw new Error(`Failed to fetch ${entry.text} (HTTP ${res.status})`);
        }
        const md = await res.text();
        if (mdCache) mdCache[entry.id] = md;
        return { id: entry.id, textPath: entry.text, md };
      },
      signal,
      onProgress
    );
  }

  async function fetchAllManuscripts(list, signal, onProgress) {
    return await fetchPool(
      list,
      async (entry) => {
        const res = await fetch(entry.image, { cache: "no-store", signal });
        if (!res.ok) {
          throw new Error(`Failed to fetch ${entry.image} (HTTP ${res.status})`);
        }
        const buf = await res.arrayBuffer();
        return { id: entry.id, imagePath: entry.image, bytes: new Uint8Array(buf) };
      },
      signal,
      onProgress
    );
  }

  function buildTranscriptionHtmlBody(items) {
    if (typeof marked === "undefined") {
      throw new Error("marked.min.js is not loaded.");
    }
    marked.setOptions({ gfm: true, breaks: false, mangle: false });

    const toc = items
      .map((item, i) => `<li><a href="#folio-${escapeHtml(item.id)}">${i + 1}. ${escapeHtml(item.id)}</a></li>`)
      .join("\n");

    const sections = items
      .map((item) => {
        const rendered = marked.parse(item.md);
        return `<section class="folio" id="folio-${escapeHtml(item.id)}">
  <h1 class="folio-title">${escapeHtml(item.id)}</h1>
  <div class="folio-body">${rendered}</div>
</section>`;
      })
      .join("\n<hr class=\"folio-sep\">\n");

    return { toc, sections };
  }

  function printHtmlViaIframe(htmlDoc) {
    const existing = document.getElementById("collection-print-frame");
    if (existing) existing.remove();

    const iframe = document.createElement("iframe");
    iframe.id = "collection-print-frame";
    iframe.style.position = "fixed";
    iframe.style.right = "0";
    iframe.style.bottom = "0";
    iframe.style.width = "0";
    iframe.style.height = "0";
    iframe.style.border = "0";
    document.body.appendChild(iframe);

    const doc = iframe.contentWindow.document;
    doc.open();
    doc.write(htmlDoc);
    doc.close();

    setTimeout(() => {
      iframe.contentWindow.focus();
      iframe.contentWindow.print();
    }, 300);
  }

  async function exportTranscriptions(format, options, setStatus) {
    const { mdCache, signal } = options;
    setStatus("Loading collection index…", 0);
    const list = await loadIndex(signal);

    const items = await fetchAllTranscriptions(list, mdCache, signal, (done, total) => {
      const pct = Math.round((done / total) * 85);
      setStatus(`Fetching transcriptions: ${done} / ${total}…`, pct);
    });

    setStatus(`Building ${format.toUpperCase()} file…`, 90);
    await yieldFrame();

    if (format === "md") {
      const combined = [
        `# ${COLLECTION_TITLE} — Complete Transcriptions`,
        "",
        `Total folios: ${items.length}`,
        "",
        "---",
        "",
        ...items.map((item) => `<!-- Folio: ${item.id} -->\n\n${item.md.trim()}\n\n---`)
      ].join("\n");
      downloadBlob(`${BASE_FILENAME}_Transcriptions.md`, combined, "text/markdown;charset=utf-8");
    } else if (format === "html") {
      const { toc, sections } = buildTranscriptionHtmlBody(items);
      const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${COLLECTION_TITLE} — Complete Transcriptions</title>
<style>
  body { font-family: Georgia, "Times New Roman", serif; max-width: 900px; margin: 0 auto; padding: 30px 24px; line-height: 1.65; color: #1f2328; background: #fff; }
  h1, h2, h3 { font-family: Arial, sans-serif; color: #111; }
  .toc { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 16px 24px; margin-bottom: 32px; column-count: 3; column-gap: 20px; font-size: 0.85rem; }
  .toc li { break-inside: avoid; margin-bottom: 4px; }
  .toc a { color: #0969da; text-decoration: none; }
  .toc a:hover { text-decoration: underline; }
  .folio-title { border-bottom: 2px solid #0969da; padding-bottom: 6px; margin-top: 36px; }
  blockquote { border-left: 4px solid #d0d7de; margin-left: 0; padding-left: 14px; color: #57606a; }
  table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 0.92rem; }
  th, td { border: 1px solid #d0d7de; padding: 6px 10px; text-align: left; }
  th { background: #f6f8fa; }
  .folio-sep { border: none; border-top: 1px solid #d0d7de; margin: 36px 0; }
  @media print { .toc { column-count: 2; } .folio { break-after: page; } .folio-sep { display: none; } }
</style>
</head>
<body>
  <h1>${COLLECTION_TITLE} — Complete Transcriptions</h1>
  <p>Total folios: ${items.length}</p>
  <h2>Table of Contents</h2>
  <ol class="toc">${toc}</ol>
  ${sections}
</body>
</html>`;
      downloadBlob(`${BASE_FILENAME}_Transcriptions.html`, html, "text/html;charset=utf-8");
    } else if (format === "doc") {
      const { sections } = buildTranscriptionHtmlBody(items);
      const doc = `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">
<head>
<meta charset="utf-8">
<title>${COLLECTION_TITLE} — Complete Transcriptions</title>
<style>
  body { font-family: Arial, sans-serif; line-height: 1.5; }
  h1.folio-title { border-bottom: 1px solid #999; padding-bottom: 4px; page-break-before: always; }
  h1.folio-title:first-of-type { page-break-before: auto; }
  blockquote { border-left: 3px solid #666; padding-left: 12px; color: #444; }
  table { width: 100%; border-collapse: collapse; margin: 10px 0; }
  th, td { border: 1px solid #999; padding: 5px 8px; text-align: left; }
</style>
</head>
<body>
  <h1>${COLLECTION_TITLE} — Complete Transcriptions</h1>
  <p>Total folios: ${items.length}</p>
  ${sections}
</body>
</html>`;
      downloadBlob(`${BASE_FILENAME}_Transcriptions.doc`, doc, "application/msword");
    } else if (format === "pdf") {
      const { sections } = buildTranscriptionHtmlBody(items);
      const printHtml = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${COLLECTION_TITLE} — Complete Transcriptions</title>
<style>
  @page { margin: 18mm 16mm; }
  body { font-family: Georgia, "Times New Roman", serif; line-height: 1.55; color: #111; font-size: 10.5pt; }
  h1, h2, h3 { font-family: Arial, sans-serif; color: #000; }
  .folio { break-after: page; page-break-after: always; }
  .folio:last-child { break-after: auto; page-break-after: auto; }
  .folio-title { border-bottom: 1.5px solid #333; padding-bottom: 4px; margin-top: 0; font-size: 14pt; }
  blockquote { border-left: 3px solid #888; margin-left: 0; padding-left: 10px; color: #333; }
  table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 9pt; }
  th, td { border: 1px solid #999; padding: 4px 6px; text-align: left; }
  th { background: #eee; }
  .folio-sep { display: none; }
</style>
</head>
<body>
  <h1>${COLLECTION_TITLE} — Complete Transcriptions</h1>
  <p>Total folios: ${items.length}</p>
  ${sections}
</body>
</html>`;
      printHtmlViaIframe(printHtml);
    } else if (format === "zip") {
      if (typeof fflate === "undefined") {
        throw new Error("fflate.min.js is not loaded.");
      }
      const files = {};
      for (const item of items) {
        files[item.textPath] = fflate.strToU8(item.md);
      }
      files["data.json"] = fflate.strToU8(JSON.stringify(list, null, 2));
      const zipped = fflate.zipSync(files, { level: 6 });
      downloadBlob(`${BASE_FILENAME}_Transcriptions.zip`, zipped, "application/zip");
    }

    setStatus(`Exported ${items.length} transcriptions (${format.toUpperCase()}).`, 100);
  }

  async function exportManuscripts(format, options, setStatus) {
    const { signal } = options;

    if (format === "html" || format === "doc") {
      const proceed = window.confirm(
        `Warning: Embedding all 413 manuscript scans (~291 MB) into a single ${format.toUpperCase()} file produces a ~390 MB document that may be very slow to open in a browser or Word.\n\nFor viewing or archiving all scans, .zip or .pdf is recommended.\n\nContinue anyway?`
      );
      if (!proceed) {
        setStatus("Export cancelled.", 0);
        return;
      }
    }

    setStatus("Loading collection index…", 0);
    const list = await loadIndex(signal);

    if (format === "md") {
      const lines = [
        `# ${COLLECTION_TITLE} — Manuscript Scans Index`,
        "",
        `Total scans: ${list.length}`,
        "",
        ...list.map((entry, idx) => `## ${idx + 1}. ${entry.id}\n\n![${entry.id}](${RAW_BASE}${entry.image})\n\n*Local path:* \`${entry.image}\`\n`)
      ];
      downloadBlob(`${BASE_FILENAME}_Manuscripts.md`, lines.join("\n"), "text/markdown;charset=utf-8");
      setStatus(`Exported ${list.length} manuscript links (MD).`, 100);
      return;
    }

    const items = await fetchAllManuscripts(list, signal, (done, total) => {
      const pct = Math.round((done / total) * 80);
      setStatus(`Fetching manuscript scans: ${done} / ${total}…`, pct);
    });

    if (format === "zip") {
      if (typeof fflate === "undefined") {
        throw new Error("fflate.min.js is not loaded.");
      }
      setStatus("Packaging ZIP archive (STORE mode)…", 90);
      await yieldFrame();
      const files = {};
      for (const item of items) {
        files[item.imagePath] = item.bytes;
      }
      const zipped = fflate.zipSync(files, { level: 0 });
      downloadBlob(`${BASE_FILENAME}_Manuscripts.zip`, zipped, "application/zip");
    } else if (format === "pdf") {
      if (typeof PDFLib === "undefined") {
        throw new Error("pdf-lib.min.js is not loaded.");
      }
      const pdfDoc = await PDFLib.PDFDocument.create();
      for (let i = 0; i < items.length; i++) {
        if (signal && signal.aborted) {
          throw new DOMException("Export cancelled", "AbortError");
        }
        const item = items[i];
        let img;
        try {
          img = await pdfDoc.embedJpg(item.bytes);
        } catch (_) {
          img = await pdfDoc.embedPng(item.bytes);
        }
        const page = pdfDoc.addPage([img.width, img.height]);
        page.drawImage(img, { x: 0, y: 0, width: img.width, height: img.height });

        if (i % 10 === 0 || i === items.length - 1) {
          const pct = 80 + Math.round(((i + 1) / items.length) * 18);
          setStatus(`Embedding scan ${i + 1} / ${items.length} into PDF…`, pct);
          await yieldFrame();
        }
      }
      setStatus("Finalizing PDF…", 99);
      await yieldFrame();
      const pdfBytes = await pdfDoc.save();
      downloadBlob(`${BASE_FILENAME}_Manuscripts.pdf`, pdfBytes, "application/pdf");
    } else if (format === "html" || format === "doc") {
      const parts = [];
      for (let i = 0; i < items.length; i++) {
        if (signal && signal.aborted) {
          throw new DOMException("Export cancelled", "AbortError");
        }
        const item = items[i];
        const b64 = uint8ToBase64(item.bytes);
        parts.push(
          `<section class="scan-page"><h2>${i + 1}. ${escapeHtml(item.id)}</h2><img src="data:image/jpeg;base64,${b64}" alt="${escapeHtml(item.id)}" style="max-width:100%;height:auto;" /></section>`
        );
        if (i % 10 === 0 || i === items.length - 1) {
          const pct = 80 + Math.round(((i + 1) / items.length) * 18);
          setStatus(`Encoding scan ${i + 1} / ${items.length}…`, pct);
          await yieldFrame();
        }
      }

      if (format === "html") {
        const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>${COLLECTION_TITLE} — Manuscript Scans</title>
<style>
  body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 24px; background: #1a1a1a; color: #e0e0e0; }
  .scan-page { margin-bottom: 40px; border-bottom: 1px solid #333; padding-bottom: 24px; }
  img { display: block; border-radius: 4px; }
</style>
</head>
<body>
  <h1>${COLLECTION_TITLE} — Manuscript Scans (${items.length} folios)</h1>
  ${parts.join("\n")}
</body>
</html>`;
        downloadBlob(`${BASE_FILENAME}_Manuscripts.html`, html, "text/html;charset=utf-8");
      } else {
        const doc = `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40">
<head><meta charset="utf-8"><title>${COLLECTION_TITLE} — Manuscript Scans</title></head>
<body>
  <h1>${COLLECTION_TITLE} — Manuscript Scans (${items.length} folios)</h1>
  ${parts.join("\n")}
</body>
</html>`;
        downloadBlob(`${BASE_FILENAME}_Manuscripts.doc`, doc, "application/msword");
      }
    }

    setStatus(`Exported ${items.length} manuscript scans (${format.toUpperCase()}).`, 100);
  }

  function injectStyles() {
    if (document.getElementById("collection-exporter-styles")) return;
    const style = document.createElement("style");
    style.id = "collection-exporter-styles";
    style.textContent = `
      .export-bar {
        background: #222222;
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 20px;
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      .export-bar-title {
        font-size: 0.92rem;
        color: #cccccc;
        font-weight: bold;
      }
      .export-controls {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
      }
      .export-select {
        background: #2d2d2d;
        color: #e0e0e0;
        border: 1px solid #444444;
        border-radius: 5px;
        padding: 8px 12px;
        font-family: inherit;
        font-size: 0.88rem;
        cursor: pointer;
        transition: border-color 0.2s ease;
      }
      .export-select:hover:not(:disabled) { border-color: #4a9eff; }
      .export-select:disabled { opacity: 0.5; cursor: not-allowed; }
      .export-progress-wrap {
        width: 100%;
        display: none;
        align-items: center;
        gap: 10px;
        margin-top: 4px;
      }
      .export-progress-wrap.active { display: flex; }
      .export-progress-track {
        flex: 1;
        height: 8px;
        background: #1a1a1a;
        border: 1px solid #333333;
        border-radius: 4px;
        overflow: hidden;
      }
      .export-progress-fill {
        height: 100%;
        width: 0%;
        background: #4a9eff;
        transition: width 0.15s ease;
      }
      .export-progress-text {
        font-size: 0.84rem;
        color: #9a9a9a;
        min-width: 210px;
      }
      .export-cancel-btn {
        background: #3a1f1f;
        color: #ff9b9b;
        border: 1px solid #6e2c2c;
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 0.82rem;
        cursor: pointer;
      }
      .export-cancel-btn:hover { background: #5a2828; }
    `;
    document.head.appendChild(style);
  }

  function mount(container, options) {
    if (!container) return;
    const opts = options || {};
    injectStyles();

    container.innerHTML = `
      <div class="export-bar">
        <div class="export-bar-title">📦 Download Entire Set (413 Folios)</div>
        <div class="export-controls">
          <select id="export-transcription-select" class="export-select" title="Download all transcriptions as one file">
            <option value="" selected disabled>📄 Transcription Only…</option>
            <option value="md">Markdown (.md)</option>
            <option value="html">Webpage (.html)</option>
            <option value="doc">Word (.doc)</option>
            <option value="pdf">PDF (Print / Save as PDF)</option>
            <option value="zip">ZIP Archive (.zip)</option>
          </select>
          <select id="export-manuscript-select" class="export-select" title="Download all manuscript scans as one file (~291 MB)">
            <option value="" selected disabled>🖼️ Manuscript Only…</option>
            <option value="zip">ZIP Archive (.zip — ~291 MB)</option>
            <option value="pdf">PDF Book (.pdf — ~292 MB)</option>
            <option value="md">Markdown Links (.md)</option>
            <option value="html">Webpage (.html — ~390 MB)</option>
            <option value="doc">Word (.doc — ~390 MB)</option>
          </select>
        </div>
        <div id="export-progress-wrap" class="export-progress-wrap">
          <div class="export-progress-track"><div id="export-progress-fill" class="export-progress-fill"></div></div>
          <span id="export-progress-text" class="export-progress-text">Ready</span>
          <button type="button" id="export-cancel-btn" class="export-cancel-btn">Cancel</button>
        </div>
      </div>
    `;

    const tSelect = container.querySelector("#export-transcription-select");
    const mSelect = container.querySelector("#export-manuscript-select");
    const pWrap = container.querySelector("#export-progress-wrap");
    const pFill = container.querySelector("#export-progress-fill");
    const pText = container.querySelector("#export-progress-text");
    const cancelBtn = container.querySelector("#export-cancel-btn");

    let activeController = null;

    function setBusy(busy) {
      tSelect.disabled = busy;
      mSelect.disabled = busy;
      cancelBtn.style.display = busy ? "inline-block" : "none";
    }

    function setStatus(msg, pct) {
      pWrap.classList.add("active");
      pText.textContent = msg;
      pFill.style.width = `${Math.max(0, Math.min(100, pct))}%`;
    }

    cancelBtn.addEventListener("click", () => {
      if (activeController) {
        activeController.abort();
      }
    });

    async function handleExport(mode, format) {
      if (!format) return;
      activeController = new AbortController();
      setBusy(true);
      try {
        const runOpts = {
          mdCache: opts.getMdCache ? opts.getMdCache() : null,
          signal: activeController.signal
        };
        if (mode === "transcription") {
          await exportTranscriptions(format, runOpts, setStatus);
        } else {
          await exportManuscripts(format, runOpts, setStatus);
        }
      } catch (err) {
        if (err && err.name === "AbortError") {
          setStatus("Export cancelled.", 0);
        } else {
          console.error("Export failed:", err);
          setStatus(`Error: ${err.message || err}`, 0);
        }
      } finally {
        activeController = null;
        setBusy(false);
      }
    }

    tSelect.addEventListener("change", (e) => {
      const fmt = e.target.value;
      e.target.value = "";
      handleExport("transcription", fmt);
    });

    mSelect.addEventListener("change", (e) => {
      const fmt = e.target.value;
      e.target.value = "";
      handleExport("manuscript", fmt);
    });
  }

  global.CollectionExporter = { mount };
})(window);
