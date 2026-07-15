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

  /* Related articles under each post — topic-matched, not random.
     Scores every other post by shared meaningful words in title/category/
     excerpt (palette posts suggest palette posts, tips suggest tips);
     category match weighs extra. Renders like the homepage journal cards. */
  var STOP = {};
  ('a,an,the,and,or,for,your,you,to,of,in,on,with,without,how,what,why,when,that,this,' +
   'junk,journal,journals,journaling,page,pages,printable,printables,ideas,idea,vintage,' +
   'more,make,making,should,never,every,some,from,into,about').split(',').forEach(function (w) { STOP[w] = 1; });
  function keywords(p) {
    return String((p.title || '') + ' ' + (p.category || '') + ' ' + (p.excerpt || ''))
      .toLowerCase().replace(/[^a-z0-9\s-]/g, ' ').split(/[\s-]+/)
      .filter(function (w) { return w.length > 3 && !STOP[w]; });
  }
  function relatedArticles() {
    var m = location.pathname.match(/\/blog\/([a-z0-9-]+?)(?:\.html)?$/);
    var article = document.querySelector('article');
    if (!m || !article) return;
    fetch('/blog/index.json?t=' + Date.now())
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var all = d.posts || [];
        var me = null, rest = [];
        all.forEach(function (p) { (p.slug === m[1] ? (me = p) : rest.push(p)); });
        if (!me || !rest.length) return;
        var mine = {};
        keywords(me).forEach(function (w) { mine[w] = 1; });
        rest.forEach(function (p) {
          var s = 0, seen = {};
          keywords(p).forEach(function (w) { if (mine[w] && !seen[w]) { s += 1; seen[w] = 1; } });
          if (p.category && me.category && p.category === me.category) s += 3;
          p._score = s;
        });
        rest.sort(function (a, b) { return (b._score - a._score) || String(b.date || '').localeCompare(String(a.date || '')); });
        var picks = rest.slice(0, 9);
        var sec = document.createElement('section');
        sec.className = 'section related-posts';
        sec.innerHTML =
          '<div class="section-head"><h2>More from the <em>journal</em></h2>' +
          '<a href="/blog.html" class="more">All posts →</a></div>' +
          '<div class="post-carousel">' +
          '<button class="carousel-arrow carousel-prev" aria-label="Previous articles" hidden>&#8592;</button>' +
          '<div class="post-grid">' + picks.map(function (p) {
            var thumb = p.thumb
              ? '<img class="post-thumb-img" src="/' + esc(String(p.thumb).replace(/^\//, '')) + '" alt="' + esc(p.title) + '" loading="lazy">'
              : '<div class="post-thumb t' + (1 + Math.floor(Math.random() * 3)) + '"></div>';
            return '<a href="/blog/' + esc(p.slug) + '.html" class="post-card">' + thumb +
              '<div class="post-cat">' + esc(p.category || '') + '</div>' +
              '<h3>' + esc(p.title) + '</h3>' +
              '<p>' + esc(p.excerpt || '') + '</p>' +
              '<div class="post-meta">' + esc(p.dateDisplay || p.date || '') + (p.readTime ? ' · ' + esc(p.readTime) : '') + '</div></a>';
          }).join('') + '</div>' +
          '<button class="carousel-arrow carousel-next" aria-label="More articles" hidden>&#8594;</button>' +
          '</div>';
        article.parentNode.insertBefore(sec, article.nextSibling);
        wireCarousel(sec);
      })
      .catch(function () {});
  }

  /* Same arrow behaviour as the homepage journal row: → pages forward one
     screenful of cards, ← only appears once you've moved. */
  function wireCarousel(sec) {
    var track = sec.querySelector('.post-carousel .post-grid');
    var prev = sec.querySelector('.carousel-prev');
    var next = sec.querySelector('.carousel-next');
    if (!track || !prev || !next) return;
    function update() {
      var maxScroll = track.scrollWidth - track.clientWidth - 4;
      prev.hidden = track.scrollLeft <= 4;
      next.hidden = track.scrollLeft >= maxScroll;
    }
    prev.onclick = function () { track.scrollBy({ left: -track.clientWidth, behavior: 'smooth' }); };
    next.onclick = function () { track.scrollBy({ left: track.clientWidth, behavior: 'smooth' }); };
    track.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    update();
  }

  /* Shop pitch under each article — moved here from the homepage hero
     (2026-07-14). Injected right after the article, before the shop strip. */
  function articlePromo() {
    var article = document.querySelector('article');
    if (!article || !document.querySelector('.post-body')) return;
    var sec = document.createElement('section');
    sec.className = 'hero-compact article-promo';
    sec.innerHTML =
      '<div class="hero-eyebrow">Instant-download printables</div>' +
      '<h2>Vintage digital papers for your <em>next beautiful page.</em></h2>' +
      '<p class="hero-compact-sub">Printable junk journal, art journal &amp; scrapbook kits — instant digital download.</p>' +
      '<a href="https://www.etsy.com/shop/sentimentalica" class="hero-cta" target="_blank" rel="noopener">Shop all designs on Etsy →</a>';
    article.parentNode.insertBefore(sec, article.nextSibling);
  }

  /* Shop strip — auto-injected "Newest in the shop" before the footer on
     every page that loads post.js (posts, blog listing). Skipped on pages
     that already have their own grid (homepage #etsy-grid) or opt out with
     <body data-no-shop-strip>. Mobile-friendly: reuses .product-grid CSS. */
  function shopStrip() {
    if (document.getElementById('etsy-grid')) return;
    if (document.body.hasAttribute('data-no-shop-strip')) return;
    var footer = document.querySelector('footer');
    if (!footer) return;
    var sec = document.createElement('section');
    sec.className = 'section shop-strip';
    sec.innerHTML =
      '<div class="section-head"><h2>Newest in the <em>shop</em></h2>' +
      '<a href="https://www.etsy.com/shop/sentimentalica" class="more" target="_blank" rel="noopener">View all on Etsy →</a></div>' +
      '<div class="product-grid post-products shop-strip-grid" aria-busy="true"></div>';
    footer.parentNode.insertBefore(sec, footer);
    var grid = sec.querySelector('.shop-strip-grid');
    fetch(FEED + '?limit=3')
      .then(function (r) { return r.json(); })
      .then(function (d) {
        var items = (d.listings || []).slice(0, 3);
        if (!items.length) { sec.remove(); return; }
        grid.innerHTML = items.map(cardHtml).join('');
        grid.removeAttribute('aria-busy');
        wireVideoHover(grid);
      })
      .catch(function () { sec.remove(); });
  }

  /* Admin affordance — if Ksenia is logged in (localStorage 'sp' from /admin/),
     every post page gets a floating "Edit" pill that opens this post in the
     editor. Invisible to normal visitors. */
  var ADMIN_API = 'https://sentimentalica-admin-api.teter-album.workers.dev';
  function adminEditPill() {
    if (!localStorage.getItem('sp')) return;
    var m = location.pathname.match(/\/blog\/([a-z0-9-]+?)(?:\.html)?$/);
    if (!m) return;
    var slug = m[1];
    var bar = document.createElement('div');
    bar.className = 'admin-pill-bar';
    var edit = document.createElement('a');
    edit.className = 'admin-edit-pill';
    edit.href = '/admin/?edit=' + slug;
    edit.textContent = '✎ Edit';
    var del = document.createElement('button');
    del.className = 'admin-edit-pill admin-delete-pill';
    del.textContent = 'Delete';
    del.onclick = function () {
      if (!confirm('Delete this post from the site? This cannot be undone.')) return;
      del.textContent = 'Deleting…'; del.disabled = true;
      fetch(ADMIN_API + '/delete-post', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password: localStorage.getItem('sp'), slug: slug })
      }).then(function (r) { return r.json(); }).then(function (d) {
        if (!d.ok) throw new Error(d.error || 'failed');
        alert('Deleted. The live page disappears in ~1 minute.');
        location.href = '/blog.html';
      }).catch(function (e) {
        alert('Could not delete: ' + e.message);
        del.textContent = 'Delete'; del.disabled = false;
      });
    };
    bar.appendChild(edit); bar.appendChild(del);
    document.body.appendChild(bar);

    // Same actions inline: right under the post title AND at the end of
    // the article — wherever the admin happens to be while reading.
    function actionRow() {
      var row = document.createElement('div');
      row.className = 'post-admin-row';
      var e2 = edit.cloneNode(true);
      var d2 = del.cloneNode(true);
      d2.onclick = del.onclick;
      row.appendChild(e2); row.appendChild(d2);
      return row;
    }
    var hero = document.querySelector('.post-hero');
    if (hero) hero.appendChild(actionRow());
    var bodyEl = document.querySelector('.post-body');
    if (bodyEl) bodyEl.parentNode.insertBefore(actionRow(), bodyEl.nextSibling);
  }

  /* Hero image — if the post has a thumbnail in blog/index.json and no hero
     yet, show it big under the title (works on all posts, old and new). */
  function heroImage() {
    var m = location.pathname.match(/\/blog\/([a-z0-9-]+?)(?:\.html)?$/);
    if (!m || document.querySelector('.post-hero-img')) return;
    var header = document.querySelector('.post-hero');
    if (!header) return;
    fetch('/blog/index.json').then(function (r) { return r.json(); })
      .then(function (d) {
        var p = (d.posts || []).find(function (x) { return x.slug === m[1]; });
        if (!p || !p.thumb) return;
        // No duplicates: if the thumb image already appears in the article
        // body, don't inject it again as a hero (Ksenia 2026-07-06).
        var thumbFile = p.thumb.split('/').pop();
        var dupe = Array.prototype.some.call(
          document.querySelectorAll('.post-body img'),
          function (im) { return im.src.indexOf(thumbFile) !== -1; });
        if (dupe) return;
        var img = document.createElement('img');
        img.className = 'post-hero-img';
        img.src = '/' + p.thumb.replace(/^\//, '');
        img.alt = p.title || '';
        header.parentNode.insertBefore(img, header.nextSibling);
        linkImagesToListing(); // wrap the just-inserted hero too (idempotent)
      }).catch(function () {});
  }

  /* RULE (Ksenia 2026-07-06): every image in an article links to the
     article's Etsy listing. Listing id = first id of the article's product
     embed. Applies to hero + body images; product-card images already link. */
  function linkImagesToListing() {
    var emb = document.querySelector('.etsy-products[data-ids]');
    if (!emb) return;
    var id = (emb.getAttribute('data-ids') || '').split(',')[0].trim();
    if (!id) return;
    var url = 'https://www.etsy.com/listing/' + id;
    var SHOP = 'https://www.etsy.com/shop/sentimentalica';
    var imgs = document.querySelectorAll('.post-body img, .post-hero-img');
    imgs.forEach(function (img) {
      if (img.closest('a') || img.closest('.etsy-products')) return;
      // Neutral mood scenes (no product in frame) -> the whole shop;
      // anything showing the product -> its listing.
      var neutral = img.getAttribute('data-link') === 'shop' ||
        (/\/gen[13]\.jpg/.test(img.src) && img.getAttribute('data-link') !== 'listing');
      var a = document.createElement('a');
      a.href = neutral ? SHOP : url; a.target = '_blank'; a.rel = 'noopener';
      a.className = 'post-img-link';
      a.title = neutral ? 'Visit the Sentimentalica shop on Etsy' : 'See this collection on Etsy';
      img.parentNode.insertBefore(a, img);
      a.appendChild(img);
    });
  }

  /* Kit carousel controls: arrows + Instagram-style dots (Ksenia 2026-07-06) */
  function enhanceCarousels() {
    document.querySelectorAll('.kit-carousel').forEach(function (car) {
      if (car.dataset.enhanced) return;
      car.dataset.enhanced = '1';
      var wrap = document.createElement('div');
      wrap.className = 'kit-carousel-wrap';
      car.parentNode.insertBefore(wrap, car);
      wrap.appendChild(car);
      var slides = car.querySelectorAll('img');
      var prev = document.createElement('button');
      var next = document.createElement('button');
      prev.className = 'car-arrow car-prev'; prev.innerHTML = '&#10094;';
      next.className = 'car-arrow car-next'; next.innerHTML = '&#10095;';
      prev.setAttribute('aria-label', 'previous'); next.setAttribute('aria-label', 'next');
      var dots = document.createElement('div');
      dots.className = 'car-dots';
      slides.forEach(function (_, i) {
        var d = document.createElement('span');
        d.className = 'car-dot' + (i === 0 ? ' on' : '');
        d.onclick = function () { go(i); };
        dots.appendChild(d);
      });
      wrap.appendChild(prev); wrap.appendChild(next); wrap.appendChild(dots);
      function idx() {
        var w = slides[0] ? slides[0].offsetWidth + 14 : 1;
        return Math.min(slides.length - 1, Math.max(0, Math.round(car.scrollLeft / w)));
      }
      function go(i) {
        i = Math.min(slides.length - 1, Math.max(0, i));
        var w = slides[0] ? slides[0].offsetWidth + 14 : 0;
        car.scrollTo({ left: i * w, behavior: 'smooth' });
      }
      prev.onclick = function () { go(idx() - 1); };
      next.onclick = function () { go(idx() + 1); };
      car.addEventListener('scroll', function () {
        var i = idx();
        dots.querySelectorAll('.car-dot').forEach(function (d, k) {
          d.classList.toggle('on', k === i);
        });
      }, { passive: true });
    });
  }

  function init() {
    enhanceCarousels();
    document.querySelectorAll('.etsy-products[data-ids]').forEach(hydrate);
    linkImagesToListing();
    articlePromo();
    relatedArticles();
    shopStrip();
    adminEditPill();
    heroImage();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
