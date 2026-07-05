/*
 * Sentimentalica — blog post enhancements.
 *
 * Inline Etsy product cards: any element in a post like
 *   <div class="etsy-products" data-ids="4480338966,4480315829"></div>
 * hydrates into live product cards (image, title, hover-video) identical to
 * the homepage grid, fetched from the etsy-feed worker. Listing IDs come
 * from the Etsy listing URL or the pipeline's tracker.
 */
(function () {
  var FEED = 'https://sentimentalica-etsy-feed.teter-album.workers.dev/';

  function esc(s) {
    return String(s || '').replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function cardHtml(l) {
    var img = l.image && l.image.src
      ? '<img src="' + esc(l.image.src) + '" alt="' + esc(l.image.alt) + '" loading="lazy">'
      : '<div class="product-img-placeholder"></div>';
    var video = l.video && l.video.src
      ? '<video class="product-video" muted loop playsinline preload="none" src="' +
        esc(l.video.src) + '"' +
        (l.video.poster ? ' poster="' + esc(l.video.poster) + '"' : '') + '></video>'
      : '';
    return (
      '<a class="product-card' + (video ? ' has-video' : '') + '" href="' + esc(l.url) +
      '" target="_blank" rel="noopener">' +
      '<div class="product-img">' + img + video +
      '<span class="product-badge">Shop on Etsy →</span></div>' +
      '<h3 class="product-title">' + esc(l.title) + '</h3>' +
      '<span class="product-link">Get it on Etsy →</span></a>'
    );
  }

  function wireVideoHover(grid) {
    grid.querySelectorAll('.product-card.has-video').forEach(function (card) {
      var video = card.querySelector('.product-video');
      if (!video) return;
      var playing = false;
      card.addEventListener('mouseenter', function () {
        if (playing) return;
        playing = true;
        card.classList.add('playing');
        var p = video.play();
        if (p) p.catch(function () {});
      });
      card.addEventListener('mouseleave', function () {
        playing = false;
        card.classList.remove('playing');
        video.pause();
        try { video.currentTime = 0; } catch (e) {}
      });
    });
  }

  function hydrate(el) {
    var ids = (el.getAttribute('data-ids') || '').trim();
    if (!ids) return;
    fetch(FEED + '?ids=' + encodeURIComponent(ids))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var items = d.listings || [];
        if (!items.length) { el.remove(); return; } // sold out / delisted — vanish quietly
        el.classList.add('product-grid', 'post-products');
        el.innerHTML = items.map(cardHtml).join('');
        el.removeAttribute('aria-busy');
        wireVideoHover(el);
      })
      .catch(function () { el.remove(); });
  }

  function init() {
    document.querySelectorAll('.etsy-products[data-ids]').forEach(hydrate);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
