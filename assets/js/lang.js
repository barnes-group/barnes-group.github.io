/* Copyright (c) 2026 SPECTRIX. All rights reserved. */
/* Language dropdown: remember an explicit choice, keep the current section, close on outside click. */
document.addEventListener('click', function (e) {
  var a = e.target.closest && e.target.closest('.lang-switch [data-lang]');
  if (a) {
    try { localStorage.setItem('lang', a.getAttribute('data-lang')); } catch (err) {}
    if (location.hash) a.setAttribute('href', a.getAttribute('href').split('#')[0] + location.hash);
    return;
  }
  Array.prototype.forEach.call(document.querySelectorAll('.lang-switch[open]'), function (d) {
    if (!d.contains(e.target)) d.removeAttribute('open');
  });
});
document.addEventListener('keydown', function (e) {
  if (e.key !== 'Escape') return;
  Array.prototype.forEach.call(document.querySelectorAll('.lang-switch[open]'), function (d) {
    d.removeAttribute('open');
    d.querySelector('summary').focus();
  });
});
