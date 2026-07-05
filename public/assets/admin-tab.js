/* Admin nav tab — visible ONLY to the logged-in admin (localStorage 'sp'
   is set by /admin/ login and cleared by Log out). Injected into the main
   site nav on every page, so the admin can jump back to the dashboard from
   anywhere without keeping a separate tab open. */
(function () {
  if (!localStorage.getItem('sp')) return;
  var ul = document.querySelector('.site-nav ul');
  if (!ul || ul.querySelector('.nav-admin')) return;
  var li = document.createElement('li');
  li.className = 'nav-admin';
  var a = document.createElement('a');
  a.href = '/admin/';
  a.textContent = '⚙ Admin';
  a.style.cssText = 'background:#163087;color:#fff;border-radius:999px;padding:.35rem .9rem;';
  li.appendChild(a);
  ul.appendChild(li);
})();
