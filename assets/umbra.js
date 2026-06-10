/* UMBRASEC — shared interactivity
   Injects the ⌘K command palette, mobile menu, back-to-top button, and wires
   scroll-reveal, scrollspy, and code-copy buttons. Pages only need:
     <body data-base="">      (root pages)   or   data-base="../"  (subdirs)
     <script src="assets/umbra.js" defer></script>
*/
(function () {
  "use strict";

  const BASE = (document.body && document.body.dataset.base) || "";
  const url = (p) => (/^(https?:|mailto:|#)/.test(p) ? p : BASE + p);
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── Command palette data ─────────────────────────────────────── */
  const COMMANDS = [
    { group: "Navigate", label: "Home", hint: "overview", icon: "fa-house", href: "index.html" },
    { group: "Navigate", label: "Research", hint: "all writeups", icon: "fa-flask", href: "research/index.html", keywords: "articles posts" },
    { group: "Navigate", label: "Approach", hint: "how this works", icon: "fa-compass", href: "index.html#approach", keywords: "method principles" },
    { group: "Navigate", label: "Open Source", hint: "tools", icon: "fa-code-branch", href: "index.html#opensource", keywords: "tools github kev" },
    { group: "Navigate", label: "About", hint: "the project", icon: "fa-circle-info", href: "about.html" },
    { group: "Navigate", label: "Contact", hint: "get in touch", icon: "fa-envelope", href: "index.html#contact", keywords: "email" },
    { group: "Articles", label: "Detecting Kerberoasting with Sigma", hint: "T1558.003", icon: "fa-shield-halved", href: "research/detecting-kerberoasting.html", keywords: "kerberos rc4 detection sigma active directory 4769" },
    { group: "External", label: "GitHub", hint: "github.com/umbrasec", icon: "fa-github", brand: true, href: "https://github.com/umbrasec", external: true },
    { group: "External", label: "Email 0xdev1@umbrasec.com", hint: "mail", icon: "fa-paper-plane", href: "mailto:0xdev1@umbrasec.com", external: true },
  ];

  /* ── Build command palette DOM ────────────────────────────────── */
  const overlay = document.createElement("div");
  overlay.className = "cmdk-overlay";
  overlay.setAttribute("role", "dialog");
  overlay.setAttribute("aria-modal", "true");
  overlay.innerHTML =
    '<div class="cmdk-panel">' +
      '<div class="cmdk-input-row">' +
        '<i class="fa-solid fa-magnifying-glass"></i>' +
        '<input class="cmdk-input" type="text" placeholder="Search pages, research, links…" aria-label="Command palette search" autocomplete="off" spellcheck="false">' +
        '<span class="cmdk-hintkey">ESC</span>' +
      '</div>' +
      '<div class="cmdk-list" role="listbox"></div>' +
    '</div>';
  document.body.appendChild(overlay);

  const input = $(".cmdk-input", overlay);
  const list = $(".cmdk-list", overlay);
  let activeIndex = 0;
  let filtered = [];

  function renderList(query) {
    const q = query.trim().toLowerCase();
    filtered = COMMANDS.filter((c) => {
      if (!q) return true;
      return (c.label + " " + (c.keywords || "") + " " + c.group).toLowerCase().includes(q);
    });
    activeIndex = 0;

    if (!filtered.length) {
      list.innerHTML = '<div class="cmdk-empty">No matches for “' + escapeHtml(query) + '”</div>';
      return;
    }

    let html = "";
    let lastGroup = null;
    filtered.forEach((c, i) => {
      if (c.group !== lastGroup) {
        html += '<div class="cmdk-group-label">' + c.group + "</div>";
        lastGroup = c.group;
      }
      html +=
        '<div class="cmdk-item' + (i === 0 ? " active" : "") + '" role="option" data-index="' + i + '">' +
          '<span class="ci-icon"><i class="' + (c.brand ? "fa-brands" : "fa-solid") + " " + c.icon + '"></i></span>' +
          '<span class="ci-label">' + escapeHtml(c.label) + "</span>" +
          '<span class="ci-hint">' + (c.external ? "↗ " : "") + escapeHtml(c.hint || "") + "</span>" +
        "</div>";
    });
    list.innerHTML = html;

    $$(".cmdk-item", list).forEach((el) => {
      el.addEventListener("mouseenter", () => setActive(parseInt(el.dataset.index, 10)));
      el.addEventListener("click", () => go(filtered[parseInt(el.dataset.index, 10)]));
    });
  }

  function setActive(i) {
    activeIndex = i;
    $$(".cmdk-item", list).forEach((el) =>
      el.classList.toggle("active", parseInt(el.dataset.index, 10) === i)
    );
    const el = list.querySelector('.cmdk-item[data-index="' + i + '"]');
    if (el) el.scrollIntoView({ block: "nearest" });
  }

  function go(cmd) {
    if (!cmd) return;
    closePalette();
    if (cmd.external) {
      window.open(cmd.href, cmd.href.startsWith("mailto:") ? "_self" : "_blank", "noopener");
    } else {
      window.location.href = url(cmd.href);
    }
  }

  function openPalette() {
    overlay.classList.add("open");
    input.value = "";
    renderList("");
    setTimeout(() => input.focus(), 30);
  }
  function closePalette() {
    overlay.classList.remove("open");
  }
  function togglePalette() {
    overlay.classList.contains("open") ? closePalette() : openPalette();
  }

  input.addEventListener("input", () => renderList(input.value));
  overlay.addEventListener("mousedown", (e) => {
    if (e.target === overlay) closePalette();
  });

  document.addEventListener("keydown", (e) => {
    const open = overlay.classList.contains("open");
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      togglePalette();
      return;
    }
    if (e.key === "/" && !open && !/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) {
      e.preventDefault();
      openPalette();
      return;
    }
    if (!open) return;
    if (e.key === "Escape") { e.preventDefault(); closePalette(); }
    else if (e.key === "ArrowDown") { e.preventDefault(); if (filtered.length) setActive((activeIndex + 1) % filtered.length); }
    else if (e.key === "ArrowUp") { e.preventDefault(); if (filtered.length) setActive((activeIndex - 1 + filtered.length) % filtered.length); }
    else if (e.key === "Enter") { e.preventDefault(); go(filtered[activeIndex]); }
  });

  // any element with data-cmdk opens the palette (e.g. the ⌘K nav button)
  $$("[data-cmdk]").forEach((el) => el.addEventListener("click", openPalette));

  /* ── Mobile menu (built from the desktop nav links) ───────────── */
  (function buildMobileMenu() {
    const nav = $("nav");
    if (!nav) return;
    const desktop = nav.querySelector(".md\\:flex");
    const links = desktop ? $$("a", desktop) : [];
    if (!links.length) return;

    const btn = document.createElement("button");
    btn.className = "menu-btn md:hidden";
    btn.setAttribute("aria-label", "Toggle menu");
    btn.setAttribute("aria-expanded", "false");
    btn.innerHTML = '<i class="fa-solid fa-bars text-lg"></i>';

    // place the button at the far right of the nav bar
    const bar = nav.querySelector(".flex.items-center.justify-between");
    if (bar) {
      btn.classList.add("ml-1");
      bar.appendChild(btn);
    }

    const panel = document.createElement("div");
    panel.className = "mobile-menu md:hidden px-8";
    panel.innerHTML = links
      .map((a) => '<a href="' + a.getAttribute("href") + '">' + a.textContent.trim() + "</a>")
      .join("");
    nav.appendChild(panel);

    btn.addEventListener("click", () => {
      const open = panel.classList.toggle("open");
      btn.setAttribute("aria-expanded", String(open));
      btn.innerHTML = open
        ? '<i class="fa-solid fa-xmark text-lg"></i>'
        : '<i class="fa-solid fa-bars text-lg"></i>';
    });
    $$("a", panel).forEach((a) =>
      a.addEventListener("click", () => {
        panel.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
        btn.innerHTML = '<i class="fa-solid fa-bars text-lg"></i>';
      })
    );
  })();

  /* ── Scroll-reveal ────────────────────────────────────────────── */
  (function reveal() {
    const targets = $$("section, .reveal");
    if (reduceMotion || !("IntersectionObserver" in window)) {
      targets.forEach((t) => t.classList.add("is-visible"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          if (en.isIntersecting) {
            en.target.classList.add("is-visible");
            io.unobserve(en.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: "0px 0px -8% 0px" }
    );
    targets.forEach((t) => {
      // already on screen at load → show immediately, no hide-then-reveal flicker
      if (t.getBoundingClientRect().top < window.innerHeight * 0.9) {
        t.classList.add("is-visible");
      } else {
        t.classList.add("reveal");
        io.observe(t);
      }
    });
  })();

  /* ── Scrollspy (active nav link) ──────────────────────────────── */
  (function scrollspy() {
    const navLinks = $$("nav a.nav-link").filter((a) => (a.getAttribute("href") || "").includes("#"));
    const map = new Map();
    navLinks.forEach((a) => {
      const id = (a.getAttribute("href") || "").split("#")[1];
      const sec = id && document.getElementById(id);
      if (sec) map.set(sec, a);
    });
    if (!map.size || !("IntersectionObserver" in window)) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((en) => {
          const a = map.get(en.target);
          if (!a) return;
          if (en.isIntersecting) {
            navLinks.forEach((l) => l.classList.remove("active"));
            a.classList.add("active");
          }
        });
      },
      { threshold: 0.5 }
    );
    map.forEach((_, sec) => io.observe(sec));
  })();

  /* ── Code copy buttons ────────────────────────────────────────── */
  $$(".prose pre").forEach((pre) => {
    const wrap = document.createElement("div");
    wrap.className = "code-wrap";
    pre.parentNode.insertBefore(wrap, pre);
    wrap.appendChild(pre);

    const btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.textContent = "Copy";
    wrap.appendChild(btn);

    btn.addEventListener("click", () => {
      const text = pre.innerText;
      const done = () => {
        btn.textContent = "Copied";
        btn.classList.add("copied");
        setTimeout(() => {
          btn.textContent = "Copy";
          btn.classList.remove("copied");
        }, 1600);
      };
      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(done).catch(fallbackCopy);
      } else {
        fallbackCopy();
      }
      function fallbackCopy() {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); done(); } catch (e) {}
        document.body.removeChild(ta);
      }
    });
  });

  /* ── Back to top ──────────────────────────────────────────────── */
  (function backToTop() {
    const btn = document.createElement("button");
    btn.className = "to-top";
    btn.setAttribute("aria-label", "Back to top");
    btn.innerHTML = '<i class="fa-solid fa-arrow-up"></i>';
    document.body.appendChild(btn);
    btn.addEventListener("click", () =>
      window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" })
    );
    let ticking = false;
    window.addEventListener("scroll", () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => {
        btn.classList.toggle("show", window.scrollY > 600);
        ticking = false;
      });
    });
  })();

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );
  }
})();
