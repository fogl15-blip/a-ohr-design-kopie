// A&Ohr – Neuauflage: Menü am Handy, Karten und Video erst nach Klick laden.
(function () {
  'use strict';

  // --- Menü (Handy/Tablet) ---
  var knopf = document.querySelector('.menueknopf');
  var menue = document.getElementById('mobilmenue');
  if (knopf && menue) {
    var text = knopf.querySelector('.menueknopf__text');
    var setze = function (offen) {
      knopf.setAttribute('aria-expanded', String(offen));
      menue.hidden = !offen;
      if (text) text.textContent = offen ? 'Schließen' : 'Menü';
    };
    knopf.addEventListener('click', function () { setze(menue.hidden); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menue.hidden) { setze(false); knopf.focus(); }
    });
    var breit = window.matchMedia('(min-width: 1025px)');
    var beiBreite = function () { if (breit.matches) setze(false); };
    if (breit.addEventListener) breit.addEventListener('change', beiBreite);
    else if (breit.addListener) breit.addListener(beiBreite);
  }

  // --- Google Maps und YouTube erst nach Klick (keine Verbindung ohne Zustimmung) ---
  document.querySelectorAll('iframe[data-src]').forEach(function (frame) {
    var video = frame.dataset.src.indexOf('youtube') !== -1;
    var box = document.createElement('div');
    box.className = 'einbettung' + (video ? ' einbettung--video' : '');
    var hinweis = document.createElement('p');
    hinweis.textContent = (video ? 'Das Video wird von YouTube geladen.' : 'Die Karte wird von Google Maps geladen.') +
      ' Dabei werden Daten wie Ihre IP-Adresse an Google übertragen.';
    var los = document.createElement('button');
    los.type = 'button';
    los.className = 'knopf ' + (video ? 'knopf--hell' : 'knopf--kontur');
    los.textContent = video ? 'Video abspielen' : 'Karte anzeigen';
    box.appendChild(hinweis);
    box.appendChild(los);
    frame.hidden = true;
    frame.parentNode.insertBefore(box, frame);
    los.addEventListener('click', function () {
      frame.src = frame.dataset.src;
      frame.hidden = false;
      box.remove();
      frame.focus();
    });
  });
})();
