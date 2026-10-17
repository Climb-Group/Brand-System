// Turns a laid-out brand page (absolutely positioned HTML, as the print builds write it) into a layered SVG
// that people can edit in Inkscape or Affinity. Runs inside the page, after fonts load and text has been fitted.
//
// Grouping comes from the page: every element with data-layer="back/reasons/reason-1/title" becomes a group at
// that path (back > reasons > reason-1 > title), so related parts of the design stay together. data-label gives a
// group a readable name, data-copy names the copy file section its words come from. Elements without data-layer
// stay inside their nearest ancestor's group. The top level groups become Inkscape layers.
//
// Images are written with their file URL and data-* geometry; layered_svg.py links photos from the pack (with
// their crop and fades as editable SVG) and embeds generated textures.
(() => {
  const NS = "http://www.w3.org/2000/svg";
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  const n = (v) => Math.round(v * 1000) / 1000;
  let clipCount = 0;
  let defs = [];

  const transparent = (c) => !c || c === "transparent" || /rgba\([^)]*,\s*0\)$/.test(c);
  const radius = (cs) => parseFloat(cs.borderTopLeftRadius) || 0;

  function polygon(cs, r) {
    const m = /^polygon\((.*)\)$/.exec(cs.clipPath || "");
    if (!m) return null;
    return m[1].split(",").map((pair) => {
      const [x, y] = pair.trim().split(/\s+/);
      const v = (s, size) => (s.endsWith("%") ? (parseFloat(s) / 100) * size : parseFloat(s));
      return [n(r.left + v(x, r.width)), n(r.top + v(y, r.height))];
    });
  }

  function clipFor(cs, r) {
    const poly = polygon(cs, r);
    const rx = radius(cs);
    if (!poly && !rx) return "";
    const id = "clip-" + ++clipCount;
    const shape = poly
      ? '<polygon points="' + poly.map((p) => p.join(",")).join(" ") + '"/>'
      : '<rect x="' + n(r.left) + '" y="' + n(r.top) + '" width="' + n(r.width) + '" height="' + n(r.height) + '" rx="' + n(rx) + '"/>';
    defs.push('<clipPath id="' + id + '">' + shape + "</clipPath>");
    return ' clip-path="url(#' + id + ')"';
  }

  function fontMetrics(cs) {
    const c = fontMetrics.ctx || (fontMetrics.ctx = document.createElement("canvas").getContext("2d"));
    c.font = cs.fontStyle + " " + cs.fontWeight + " " + cs.fontSize + " " + cs.fontFamily;
    const m = c.measureText("Hg");
    return { ascent: m.fontBoundingBoxAscent, descent: m.fontBoundingBoxDescent };
  }

  function runStyle(cs) {
    const a = [];
    a.push('font-family="' + esc(cs.fontFamily.replace(/"/g, "'")) + '"');
    a.push('font-size="' + n(parseFloat(cs.fontSize)) + '"');
    a.push('font-weight="' + cs.fontWeight + '"');
    if (cs.fontStyle !== "normal") a.push('font-style="' + cs.fontStyle + '"');
    const ls = parseFloat(cs.letterSpacing);
    if (ls) a.push('letter-spacing="' + n(ls) + '"');
    const stroke = parseFloat(cs.webkitTextStrokeWidth) || 0;
    if (stroke) {
      a.push('fill="none" stroke="' + cs.webkitTextStrokeColor + '" stroke-width="' + n(stroke) + '"');
    } else {
      a.push('fill="' + cs.color + '"');
    }
    return a.join(" ");
  }

  // Text: one <text> per element, one <tspan> per line, one nested <tspan> per change of style.
  function text(el) {
    const lines = [];
    let jumped = false; // a box (an inline logo) sat in the flow: the next run starts at its own x
    let gap = false; // a text node of only spaces sat between two styled runs: keep one space
    const walk = (node) => {
      for (const child of node.childNodes) {
        if (child.nodeType === 3) {
          const cs = getComputedStyle(child.parentElement);
          const upper = cs.textTransform === "uppercase";
          const re = /(\s*)(\S+\s*)/g;
          if (!/\S/.test(child.data)) {
            if (child.data.length) gap = true;
            continue;
          }
          let m;
          while ((m = re.exec(child.data))) {
            const start = m.index + m[1].length;
            const range = document.createRange();
            range.setStart(child, start);
            range.setEnd(child, start + m[2].trimEnd().length);
            const rects = range.getClientRects();
            if (!rects.length) continue;
            const rc = rects[0];
            const fm = fontMetrics(cs);
            const lead = m[1] || gap ? " " : "";
            gap = false;
            const raw = upper ? m[2].toUpperCase() : m[2];
            const base = rc.top + (rc.height - fm.ascent - fm.descent) / 2 + fm.ascent;
            let line = lines.find((l) => Math.abs(l.top - rc.top) < rc.height * 0.5);
            if (!line) lines.push((line = { top: rc.top, x: rc.left, base, runs: [] }));
            line.x = Math.min(line.x, rc.left);
            line.base = Math.max(line.base, base);
            const style = runStyle(cs);
            const last = line.runs[line.runs.length - 1];
            // A space before this word that the previous run did not already end with.
            const word = (last && lead && !/\s$/.test(last.text) ? " " : "") + raw;
            if (last && last.style === style && !jumped) last.text += word;
            else line.runs.push({ style, text: word, x: rc.left, fixed: jumped && line.runs.length > 0 });
            jumped = false;
          }
        } else if (child.nodeType === 1 && child.tagName === "BR") {
          continue;
        } else if (child.nodeType === 1 && !isBox(child)) {
          walk(child);
        } else if (child.nodeType === 1) {
          jumped = true;
        }
      }
    };
    walk(el);
    if (!lines.length) return "";
    lines.sort((a, b) => a.top - b.top);
    const out = lines.map((l) => {
      const runs = l.runs.map((r, i) => {
        const t = i === l.runs.length - 1 ? r.text.trimEnd() : r.text;
        const x = r.fixed ? ' x="' + n(r.x) + '"' : "";
        return "<tspan " + r.style + x + ">" + esc(t) + "</tspan>";
      });
      return '<tspan x="' + n(l.x) + '" y="' + n(l.base) + '">' + runs.join("") + "</tspan>";
    });
    return '<text xml:space="preserve">' + out.join("") + "</text>";
  }

  // A child that draws its own box (an image, an inline SVG, a block with a ground) is converted on its own.
  function isBox(el) {
    if (el.tagName === "IMG" || el.tagName.toLowerCase() === "svg") return true;
    const cs = getComputedStyle(el);
    if (cs.display === "inline-block" || cs.display === "block" || cs.position === "absolute") return true;
    return !transparent(cs.backgroundColor);
  }

  function svgChild(el, color) {
    const r = el.getBoundingClientRect();
    const clone = el.cloneNode(true);
    clone.removeAttribute("style");
    clone.removeAttribute("class");
    clone.setAttribute("x", n(r.left));
    clone.setAttribute("y", n(r.top));
    clone.setAttribute("width", n(r.width));
    clone.setAttribute("height", n(r.height));
    if (!clone.getAttribute("viewBox")) clone.setAttribute("viewBox", "0 0 " + n(r.width) + " " + n(r.height));
    clone.setAttribute("xmlns", NS);
    let s = new XMLSerializer().serializeToString(clone);
    return s.replace(/currentColor/g, color);
  }

  function convert(el) {
    const cs = getComputedStyle(el);
    if (cs.display === "none" || cs.visibility === "hidden") return "";
    const saved = el.style.transform;
    const transform = cs.transform !== "none" ? cs.transform : null;
    let origin = null;
    if (transform) {
      el.style.transform = "none";
    }
    const r = el.getBoundingClientRect();
    if (transform) {
      const [ox, oy] = cs.transformOrigin.split(" ").map(parseFloat);
      origin = [r.left + ox, r.top + oy];
    }
    const parts = [];
    const tag = el.tagName.toLowerCase();
    if (tag === "img") {
      const clip = clipFor(cs, r);
      const data = el.dataset.photo ? " data-photo='" + el.dataset.photo.replace(/'/g, "&apos;") + "'" : "";
      parts.push(
        '<image href="' + esc(el.src) + '" x="' + n(r.left) + '" y="' + n(r.top) + '" width="' + n(r.width) + '" height="' + n(r.height) +
          '" preserveAspectRatio="xMidYMid slice"' + clip + data + "/>"
      );
    } else if (tag === "svg") {
      parts.push(svgChild(el, cs.color));
    } else {
      if (!transparent(cs.backgroundColor)) {
        const poly = polygon(cs, r);
        if (poly) parts.push('<polygon points="' + poly.map((p) => p.join(",")).join(" ") + '" fill="' + cs.backgroundColor + '"/>');
        else
          parts.push(
            '<rect x="' + n(r.left) + '" y="' + n(r.top) + '" width="' + n(r.width) + '" height="' + n(r.height) + '"' +
              (radius(cs) ? ' rx="' + n(radius(cs)) + '"' : "") + ' fill="' + cs.backgroundColor + '"/>'
          );
      }
      const t = text(el);
      if (t) parts.push(t);
      for (const child of el.children) {
        if (child.dataset && child.dataset.layer) continue;
        if (isBox(child) && child.tagName !== "BR") parts.push(convert(child));
      }
    }
    if (transform) el.style.transform = saved;
    let body = parts.join("");
    const op = parseFloat(cs.opacity);
    if (op < 1) body = '<g opacity="' + op + '">' + body + "</g>";
    if (transform) {
      const m = /matrix\(([^)]*)\)/.exec(transform);
      const mx = m ? m[1].split(",").map((v) => n(parseFloat(v))).join(" ") : "1 0 0 1 0 0";
      body =
        '<g transform="translate(' + n(origin[0]) + " " + n(origin[1]) + ") matrix(" + mx + ") translate(" + n(-origin[0]) + " " + n(-origin[1]) + ')">' +
        body + "</g>";
    }
    return body;
  }

  const label = (seg) => {
    const s = seg.replace(/-/g, " ");
    return s.charAt(0).toUpperCase() + s.slice(1);
  };

  window.layeredSVG = function (title) {
    clipCount = 0;
    defs = [];
    const root = { name: "", kids: [], byName: {} };
    const node = (path) => {
      let cur = root;
      const ids = [];
      for (const seg of path) {
        ids.push(seg);
        if (!cur.byName[seg]) {
          const k = { name: seg, id: ids.join("."), kids: [], byName: {}, body: "" };
          cur.byName[seg] = k;
          cur.kids.push(k);
        }
        cur = cur.byName[seg];
      }
      return cur;
    };
    for (const el of document.querySelectorAll("[data-layer]")) {
      const g = node(el.dataset.layer.split("/"));
      if (el.dataset.label) g.label = el.dataset.label;
      if (el.dataset.copy) g.copy = el.dataset.copy;
      g.body += convert(el);
    }
    const emit = (g, depth) => {
      const attrs =
        ' id="' + esc(g.id) + '" inkscape:label="' + esc(g.label || label(g.name)) + '"' +
        (depth === 0 ? ' inkscape:groupmode="layer"' : "") + (g.copy ? ' data-copy="' + esc(g.copy) + '"' : "");
      return "<g" + attrs + ">" + g.body + g.kids.map((k) => emit(k, depth + 1)).join("") + "</g>";
    };
    const b = document.body.getBoundingClientRect();
    const layers = root.kids.map((k) => emit(k, 0)).join("\n");
    const mm = (px) => n((px * 25.4) / 96);
    return (
      '<svg xmlns="' + NS + '" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"' +
      ' width="' + mm(b.width) + 'mm" height="' + mm(b.height) + 'mm" viewBox="0 0 ' + n(b.width) + " " + n(b.height) + '">' +
      "<title>" + esc(title || document.title) + "</title><defs>" + defs.join("") + "</defs>\n" + layers + "\n</svg>\n"
    );
  };
})();
