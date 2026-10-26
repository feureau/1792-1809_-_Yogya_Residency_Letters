/**
 * viewer.js — Render side-by-side manuscript scan + transcription markdown.
 * Configured with mouse zoom/pan, live fetch over http(s), offline bundle fallback,
 * and context-aware GitHub Issue generation.
 */
(function () {
  "use strict";

  // ==========================================
  // CONFIGURATION: Set your GitHub repo here
  // ==========================================
  const GITHUB_REPO = "feureau/1792-1809_-_Yogya_Residency_Letters";

  const OUTPUT_ID     = "transcript-output";
  const TITLE_ID      = "doc-title";
  const SCAN_ID       = "scan";
  const SCAN_LINK_ID  = "scan-link";
  const SCAN_NOTE_ID  = "scan-note";

  function list() { return window.__TRANSCRIPTIONS_DATA__ || []; }

  function getEntry(id) {
    const l = list();
    if (!id) return l[0];
    return l.find(e => e.id === id) || l[0];
  }

  async function getMarkdown(entry) {
    const embedded = (window.__TRANSCRIPTIONS_CONTENT__ || {})[entry.id];
    const src = entry.text;

    if (location.protocol === "http:" || location.protocol === "https:") {
      try {
        const res = await fetch(src, { cache: "no-store" });
        if (res.ok) {
          const text = await res.text();
          if (text.trim()) return text;
        }
      } catch (_) { /* fall through */ }
    }

    if (typeof embedded === "string" && embedded.length) return embedded;

    throw new Error(
      "No transcript source for " + entry.id +
      ". Run `python scripts/build-transcriptions.py` to regenerate fallback content."
    );
  }

  function configureMarked() {
    if (typeof marked === "undefined") return;
    marked.setOptions({ gfm: true, breaks: false, mangle: false });
  }

  function addHeaderIds(root) {
    root.querySelectorAll("h1,h2,h3,h4,h5,h6").forEach(h => {
      h.id = h.textContent.toLowerCase().replace(/[^\w\s-]/g, "").replace(/\s+/g, "-").replace(/-+/g, "-");
    });
  }

  function setupImage(entry) {
    const img  = document.getElementById(SCAN_ID);
    const note = document.getElementById(SCAN_NOTE_ID);
    img.src = entry.image;
    img.alt = "Scan of " + entry.id;
    if (note) note.textContent = entry.id;

    let scale = 1, translateX = 0, translateY = 0;
    const updateTransform = () => {
      img.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    };

    img.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = e.deltaY < 0 ? 1.1 : 0.9;
      const rect = img.getBoundingClientRect();
      const offsetX = e.clientX - rect.left;
      const offsetY = e.clientY - rect.top;
      translateX = (translateX - offsetX) * delta + offsetX;
      translateY = (translateY - offsetY) * delta + offsetY;
      scale = Math.max(0.2, Math.min(5, scale * delta));
      updateTransform();
    }, { passive: false });

    let isPanning = false, startX = 0, startY = 0;
    img.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return;
      isPanning = true;
      startX = e.clientX - translateX;
      startY = e.clientY - translateY;
      img.style.cursor = 'grabbing';
      e.preventDefault();
    });
    document.addEventListener('mousemove', (e) => {
      if (!isPanning) return;
      translateX = e.clientX - startX;
      translateY = e.clientY - startY;
      updateTransform();
    });
    document.addEventListener('mouseup', () => {
      isPanning = false;
      img.style.cursor = 'zoom-in';
    });
  }

  function setupNav(entry) {
    const l = list();
    const idx = l.findIndex(e => e.id === entry.id);
    const prev = idx > 0 ? l[idx - 1] : null;
    const next = idx >= 0 && idx < l.length - 1 ? l[idx + 1] : null;

    document.querySelectorAll('[data-nav="prev"]').forEach(a => {
      if (prev) { a.href = "?id=" + prev.id; a.removeAttribute("aria-disabled"); }
      else { a.href = "#"; a.setAttribute("aria-disabled", "true"); }
    });
    document.querySelectorAll('[data-nav="next"]').forEach(a => {
      if (next) { a.href = "?id=" + next.id; a.removeAttribute("aria-disabled"); }
      else { a.href = "#"; a.setAttribute("aria-disabled", "true"); }
    });
  }

  async function render() {
    const out   = document.getElementById(OUTPUT_ID);
    const title = document.getElementById(TITLE_ID);
    const params = new URLSearchParams(location.search);
    const entry = getEntry(params.get("id"));

    if (!entry) return;

    document.title = entry.id + " — Transcription Viewer";
    if (title) title.textContent = entry.id;

    setupNav(entry);
    setupImage(entry);

    try {
      const md = await getMarkdown(entry);
      if (typeof marked === "undefined") throw new Error("marked.min.js did not load.");

      const buttonHtml = `<div style="margin-bottom: 20px;"><a href="#" id="github-report-btn" class="btn" style="background:#2ea043; border-color:#2ea043; color:white; display:inline-flex; align-items:center; gap:6px;"><svg height="16" viewBox="0 0 16 16" width="16" style="fill:white;"><path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.46-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z"></path></svg> Report Issue on GitHub</a></div>`;

      out.innerHTML = buttonHtml + marked.parse(md);
      addHeaderIds(out);

      const githubBtn = document.getElementById("github-report-btn");
      if (githubBtn) {
        githubBtn.addEventListener("click", (e) => {
          e.preventDefault();
          const sel = window.getSelection();
          let selectionText = "";
          if (sel.rangeCount > 0 && out.contains(sel.anchorNode)) {
            selectionText = sel.toString().trim();
          }
          let body = `**Transcription ID:** ${entry.id}\n\n`;
          if (selectionText) {
            body += `**Original Text:**\n> ${selectionText.replace(/\n/g, '\n> ')}\n\n`;
          }
          body += `**Suggested Correction / Notes:**\n`;
          window.open(`https://github.com/${GITHUB_REPO}/issues/new?title=${encodeURIComponent('Transcription Note: ' + entry.id)}&body=${encodeURIComponent(body)}`, '_blank');
        });
      }
    } catch (err) {
      console.error(err);
      out.innerHTML = `<div class="render-error"><h2>Error Loading Transcription</h2><pre>${err.message}</pre></div>`;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => { configureMarked(); render(); });
  } else {
    configureMarked(); render();
  }
})();