// TiempoSesion.js — expira sesión tras 30 minutos de inactividad (sin UI)
(function () {
  const INACTIVITY_MS = 30 * 60 * 1000; // 30 min
  const SKEY = 'rostiseria_session';
  const now = Date.now();

  try {
    const sess = JSON.parse(localStorage.getItem(SKEY) || '{}');
    if (sess.lastActivity && (now - sess.lastActivity) > INACTIVITY_MS) {
      localStorage.removeItem('rostiseria_loggedUser');
      localStorage.removeItem(SKEY);
      alert('Tu sesión ha expirado por inactividad.');
    }
  } catch (e) {}

  const touch = () =>
    localStorage.setItem(SKEY, JSON.stringify({ lastActivity: Date.now() }));

  ['click', 'keydown', 'scroll', 'mousemove', 'touchstart'].forEach((ev) =>
    document.addEventListener(ev, touch, { passive: true })
  );

  touch();
})();
