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
  var spyMap = { overview: 'overview', how: 'how', features: 'features', device: 'device', contact: 'contact' };
  if ('IntersectionObserver' in window) {
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var target = spyMap[en.target.id];
        $$('#nav a').forEach(function (a) { a.classList.toggle('active', a.getAttribute('href') === '#' + target); });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(spyMap).forEach(function (id) { var el = document.getElementById(id); if (el) spy.observe(el); });

    var seen = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('in');
        seen.unobserve(en.target);
        $$('[data-count]', en.target).forEach(countUp);
      });
    }, { threshold: 0.15 });
    $$('.reveal').forEach(function (el) { seen.observe(el); });
  } else {
    $$('.reveal').forEach(function (el) { el.classList.add('in'); });
  }

  function countUp(el) {
    if (reduced) return;
    var end = parseFloat(el.getAttribute('data-count'));
    var start = null;
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / 1100, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = String(Math.round(end * eased));
      if (p < 1) requestAnimationFrame(step);
    }
    el.textContent = '0';
    requestAnimationFrame(step);
  }

  /* Feature tabs -------------------------------------------------------- */
  function activate(tab, focus, scroll) {
    var list = tab.closest('[role="tablist"]');
    $$('[role="tab"]', list).forEach(function (t) {
      var on = t === tab;
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      document.getElementById(t.getAttribute('aria-controls')).hidden = !on;
    });
    if (focus) tab.focus();
    tab.scrollIntoView({ block: 'nearest', inline: 'center' });
    if (scroll) {
      var top = list.getBoundingClientRect().top + window.scrollY - parseInt(getComputedStyle(doc).getPropertyValue('--header-h'), 10);
      if (window.scrollY > top + 4) window.scrollTo({ top: top, behavior: reduced ? 'auto' : 'smooth' });
    }
  }
  $$('[role="tablist"]').forEach(function (list) {
    var tabs = $$('[role="tab"]', list);
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { activate(t, false, true); });
      t.addEventListener('keydown', function (e) {
        var n = null;
        if (e.key === 'ArrowRight') n = tabs[(i + 1) % tabs.length];
        else if (e.key === 'ArrowLeft') n = tabs[(i - 1 + tabs.length) % tabs.length];
        else if (e.key === 'Home') n = tabs[0];
        else if (e.key === 'End') n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); activate(n, true, true); }
      });
    });
  });
  function openFromHash() {
    var id = location.hash.slice(1);
    var t = id && document.getElementById('tab-' + id);
    if (t) { activate(t, false, false); document.getElementById(id).scrollIntoView(); }
  }
  window.addEventListener('hashchange', openFromHash);
  openFromHash();

  /* Lightbox ------------------------------------------------------------ */
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
    var container = el.closest('.feature-visual, .hero-visual') || el.parentNode;
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
