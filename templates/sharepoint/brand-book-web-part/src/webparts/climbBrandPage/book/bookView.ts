// Draws one brand book page into an element. It has no SharePoint parts, so the same code can be tried in any page.
import { initBrandBook } from './brandBook';

export interface IBookViewOptions {
  base: string; // the brand book folder, ending in a slash
  slug: string; // the brand book page, such as "colour"
  className: string;
  statusClass: string;
  loading: string;
  failed: string;
}

// The page address carries the brand book page, so every page has its own link and the browser back button works.
export const PAGE_PARAM = 'brandpage';
export const SLUG = /^[a-z0-9-]+$/;
const BOOK_PAGE = /^([a-z0-9-]+)\.html(#.*)?$/;
const SCHEME = /^([a-z][a-z0-9+.-]*:|\/\/|\/|#)/i;
const FILE = /^[\w./%-]+\.[a-z][a-z0-9]{1,4}([?#].*)?$/i;
const STYLES = ['vendor/tokens.css', 'css/fonts.css', 'css/brand_book.css'];

export function showBookPage(host: HTMLElement, o: IBookViewOptions): Promise<boolean> {
  ensureStyles(o.base);
  host.innerHTML = `<div class="${o.className}"><p class="${o.statusClass}" role="status">${o.loading}</p></div>`;
  return fetch(o.base + o.slug + '.html', { credentials: 'same-origin' })
    .then((r) => (r.ok ? r.text() : Promise.reject(new Error(String(r.status)))))
    .then((html) => {
      show(host, html, o);
      return true;
    })
    .catch(() => {
      host.innerHTML = `<div class="${o.className}"><p class="${o.statusClass}" role="alert">${o.failed}</p></div>`;
      return false;
    });
}

function ensureStyles(base: string): void {
  STYLES.forEach((path) => {
    const id = 'cbb-style-' + path.replace(/\W/g, '-');
    if (document.getElementById(id)) {
      return;
    }
    const link = document.createElement('link');
    link.id = id;
    link.rel = 'stylesheet';
    link.href = base + path;
    document.head.appendChild(link);
  });
}

function show(host: HTMLElement, html: string, o: IBookViewOptions): void {
  const doc = new DOMParser().parseFromString(html, 'text/html');
  const main = doc.getElementById('cbb-main') || doc.body;
  rewrite(main, o.base);

  const frame = document.createElement('div');
  frame.className = o.className;
  while (main.firstChild) {
    frame.appendChild(document.importNode(main.firstChild, true));
    main.removeChild(main.firstChild);
  }
  host.innerHTML = '';
  host.appendChild(frame);

  initBrandBook({
    asset: (url: string) => asset(url, o.base),
    link: (url: string) => link(url),
    frame: (iframe: HTMLIFrameElement, theme: string) => showFrame(iframe, theme, o.failed),
    withoutBrand: () => {
      const u = new URL(window.location.href);
      u.searchParams.delete('brand');
      return u.pathname + u.search + u.hash;
    }
  });

  if (window.location.hash.length > 1) {
    const target = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
    if (target) {
      target.scrollIntoView();
    }
  }
}

// Page links stay on this page; files and pictures load from the brand book folder.
function rewrite(root: HTMLElement, base: string): void {
  const all: Element[] = [root].concat(Array.prototype.slice.call(root.querySelectorAll('*')));
  all.forEach((el) => {
    Array.prototype.slice.call(el.attributes).forEach((a: Attr) => {
      const v = a.value.trim();
      if (a.name === 'srcset') {
        el.setAttribute('srcset', v.split(',').map((part) => {
          const bits = part.trim().split(/\s+/);
          bits[0] = asset(bits[0], base);
          return bits.join(' ');
        }).join(', '));
      } else if (a.name === 'style' && v.indexOf('url(') >= 0) {
        el.setAttribute('style', urls(v, base));
      } else if (a.name === 'href' && BOOK_PAGE.test(v)) {
        el.setAttribute('href', link(v));
      } else if (!SCHEME.test(v) && FILE.test(v) && (a.name === 'href' || a.name === 'src' || a.name === 'poster' ||
          a.name.indexOf('data-') === 0)) {
        el.setAttribute(a.name, asset(v, base));
      }
    });
    if (el.tagName === 'STYLE' && el.textContent) {
      el.textContent = urls(el.textContent, base);
    }
  });
}

function urls(css: string, base: string): string {
  return css.replace(/url\((['"]?)([^'")]+)\1\)/g, (all: string, q: string, url: string) =>
    SCHEME.test(url) || url.indexOf('data:') === 0 ? all : 'url(' + q + asset(url, base) + q + ')');
}

function asset(url: string, base: string): string {
  return SCHEME.test(url) && url.charAt(0) !== '/' ? url : new URL(url, base).href;
}

function link(url: string): string {
  const m = BOOK_PAGE.exec(url);
  if (!m) {
    return url;
  }
  const u = new URL(window.location.href);
  u.searchParams.set(PAGE_PARAM, m[1]);
  u.hash = m[2] || '';
  return u.pathname + u.search + u.hash;
}

// SharePoint downloads .html files from a library rather than showing them, so a live component preview is read
// as text and shown through srcdoc, with a base address so its styles and scripts load from the brand book folder.
function showFrame(iframe: HTMLIFrameElement, theme: string, failed: string): void {
  const src = iframe.getAttribute('data-src') || '';
  if (!src) {
    return;
  }
  fetch(src, { credentials: 'same-origin' })
    .then((r) => (r.ok ? r.text() : Promise.reject(new Error(String(r.status)))))
    .then((html) => {
      iframe.addEventListener('load', () => {
        if (iframe.contentWindow) {
          iframe.contentWindow.postMessage({ cbbTheme: theme }, '*');
        }
      }, { once: true });
      iframe.srcdoc = html.replace(/<head>/i, '<head><base href="' + new URL('.', src).href + '">');
    })
    .catch(() => {
      iframe.title = failed;
    });
}
