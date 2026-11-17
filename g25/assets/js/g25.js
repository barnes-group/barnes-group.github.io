/* Copyright (c) 2026 SPECTRIX. All rights reserved. */
(function () {
  'use strict';

  var doc = document.documentElement;
  var reduced = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* Theme -------------------------------------------------------------- */
  var themeBtn = $('.theme-btn');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var next = doc.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      doc.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }

  /* Header, mobile menu ----------------------------------------------- */
  var header = $('.site-header');
  var onScroll = function () { header.classList.toggle('scrolled', window.scrollY > 8); };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  var menuBtn = $('.menu-btn');
  var nav = $('#nav');
  function setMenu(open) {
    nav.classList.toggle('open', open);
    menuBtn.setAttribute('aria-expanded', String(open));
  }
  menuBtn.addEventListener('click', function () { setMenu(!nav.classList.contains('open')); });
  $$('#nav a').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });

  /* Scroll spy ---------------------------------------------------------- */
  var spyMap = { news: 'news', overview: 'overview', how: 'overview', signature: 'signature', highlights: 'highlights', explore: 'explore', contact: 'contact' };
  if ('IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var target = spyMap[en.target.id];
        $$('#nav a').forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#' + target); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(spyMap).forEach(function (id) { var el = document.getElementById(id); if (el) spy.observe(el); });

    /* Reveal + curve drawing + counters --------------------------------- */
    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('in');
        seen.unobserve(en.target);
        $$('[data-count]', en.target).forEach(countUp);
      });
    }, { threshold: 0.15 });
    $$('.reveal, .curve').forEach(function (el) { seen.observe(el); });
  } else {
    $$('.reveal, .curve').forEach(function (el) { el.classList.add('in'); });
  }

  function countUp(el) {
    if (reduced) return;
    var end = parseFloat(el.getAttribute('data-count'));
    var dec = parseInt(el.getAttribute('data-dec') || '0', 10);
    var start = null;
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / 1100, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = (end * eased).toFixed(dec);
      if (p < 1) requestAnimationFrame(step);
    }
    el.textContent = (0).toFixed(dec);
    requestAnimationFrame(step);
  }

  /* Hero rotator -------------------------------------------------------- */
  var rot = $('#hero-rotator');
  if (rot && !reduced) {
    var slides = $$('img', rot);
    var idx = 0;
    setInterval(function () {
      if (document.hidden) return;
      slides[idx].classList.remove('on');
      idx = (idx + 1) % slides.length;
      slides[idx].classList.add('on');
    }, 4800);
  } else if (rot) {
    $$('img', rot)[0].classList.add('on');
  }

  /* Remote operation scenarios ----------------------------------------- */
  var scenarios = [
    { panel: 'dashboard_zones_reaching_target', tablet: 'dashboard_line_chart', browser: 'alarms',
      alt: { dashboard_zones_reaching_target: 'Dashboard with zone tiles heating to target', dashboard_line_chart: 'Line chart of zone temperatures', alarms: 'Alarms screen with no active alarms' },
      text: 'The operator works at the panel, the shift supervisor follows the temperature trend on a tablet and the control room keeps an eye on alarms.' },
    { panel: 'dashboard_all_zones_on', tablet: 'mold_doctor_tda_completed', browser: 'report_view',
      alt: { dashboard_all_zones_on: 'Dashboard with all zones up to temperature', mold_doctor_tda_completed: 'Thermodynamic analysis results', report_view: 'Analysis report' },
      text: 'The process engineer runs a thermodynamic analysis from a tablet and reviews the report on a laptop, while the panel keeps showing the dashboard.' },
    { panel: 'dashboard_table', tablet: 'tools_and_diagnostics_service', browser: 'activity_log',
      alt: { dashboard_table: 'Table view with per-zone values', tools_and_diagnostics_service: 'Service page with system status', activity_log: 'Activity log of user actions' },
      text: 'Maintenance checks system status on a tablet next to the cabinet and reviews the activity log from the office.' }
  ];
  var stage = $('#remote-stage');
  var caption = $('#stage-caption');
  function showScenario(i) {
    var s = scenarios[i];
    ['panel', 'tablet', 'browser'].forEach(function (slot) {
      var img = $('img[data-slot="' + slot + '"]', stage);
      var name = s[slot];
      var base = 'assets/img/screens/' + name;
      var pre = new Image();
      pre.onload = function () {
        img.style.opacity = '0';
        setTimeout(function () {
          img.src = base + '-sm.webp';
          img.srcset = base + '-sm.webp 540w, ' + base + '.webp 1080w';
          img.alt = s.alt[name];
          img.style.opacity = '1';
        }, reduced ? 0 : 280);
      };
      pre.src = base + '-sm.webp';
    });
    caption.textContent = s.text;
    $$('.pill[data-scenario]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-scenario') === String(i))); });
  }
  if (stage) {
    caption.textContent = scenarios[0].text;
    $$('.pill[data-scenario]').forEach(function (b) {
      b.addEventListener('click', function () { showScenario(parseInt(b.getAttribute('data-scenario'), 10)); });
    });
  }

  /* Explorer tabs -------------------------------------------------------- */
  var tabs = $$('[role="tab"]');
  function activate(tab, focus) {
    tabs.forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      var panel = document.getElementById(t.getAttribute('aria-controls'));
      panel.hidden = !on;
      panel.classList.toggle('active', on);
    });
    if (focus) tab.focus();
  }
  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () { activate(t, false); });
    t.addEventListener('keydown', function (e) {
      var n = null;
      if (e.key === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
      else if (e.key === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
      else if (e.key === 'Home') n = tabs[0];
      else if (e.key === 'End') n = tabs[tabs.length - 1];
      if (n) { e.preventDefault(); activate(n, true); }
    });
  });
  $$('[data-open-tab]').forEach(function (a) {
    a.addEventListener('click', function () {
      var t = document.getElementById('tab-' + a.getAttribute('data-open-tab'));
      if (t) activate(t, false);
    });
  });

  /* Lightbox ---------------------------------------------------------------- */
  var lb = $('#lightbox');
  var lbImg = $('.lb-stage img', lb);
  var lbCap = $('.lb-cap', lb);
  var group = [];
  var pos = 0;
  function show(i) {
    pos = (i + group.length) % group.length;
    var el = group[pos];
    lbImg.src = el.getAttribute('data-full');
    lbImg.alt = el.alt;
    lbCap.textContent = el.getAttribute('data-caption') + (group.length > 1 ? '  ·  ' + (pos + 1) + ' / ' + group.length : '');
  }
  function open(el) {
    var container = el.closest('.gallery, .pair, .trio, .single, .card-media') || el.parentNode;
    group = $$('.zoomable', container);
    show(group.indexOf(el));
    var multi = group.length > 1;
    $('.lb-prev', lb).hidden = !multi;
    $('.lb-next', lb).hidden = !multi;
    if (!lb.open) lb.showModal();
  }
  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('.zoomable');
    if (el) open(el);
  });
  document.addEventListener('keydown', function (e) {
    var el = document.activeElement;
    if (el && el.classList && el.classList.contains('zoomable') && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); open(el); }
    if (!lb.open) return;
    if (e.key === 'Escape') lb.close();
    if (e.key === 'ArrowRight') show(pos + 1);
    if (e.key === 'ArrowLeft') show(pos - 1);
  });
  $('.lb-prev', lb).addEventListener('click', function () { show(pos - 1); });
  $('.lb-next', lb).addEventListener('click', function () { show(pos + 1); });
  $('.lb-close', lb).addEventListener('click', function () { lb.close(); });
  lb.addEventListener('click', function (e) { if (e.target === lb || e.target.classList.contains('lb') || e.target.classList.contains('lb-stage')) lb.close(); });
})();
