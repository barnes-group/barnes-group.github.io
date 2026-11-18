/* Copyright (c) 2026 SPECTRIX. All rights reserved. */
/* Remember an explicit language choice and keep the current section when switching. */
document.addEventListener('click', function (e) {
  var a = e.target.closest && e.target.closest('.lang-switch [data-lang]');
  if (!a) return;
  try { localStorage.setItem('lang', a.getAttribute('data-lang')); } catch (err) {}
  if (location.hash) a.setAttribute('href', a.getAttribute('href').split('#')[0] + location.hash);
});
