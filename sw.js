/* 每日简报 Service Worker
 * - 页面/manifest：网络优先，离线回退缓存（保证内容更新及时可见）
 * - data/*.json：网络优先，失败才回退缓存（每次都拿云端最新，缓存仅离线兜底）
 */
const VERSION = 'v2';
const SHELL = `shell-${VERSION}`;
const DATA = `data-${VERSION}`;
const SHELL_ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './apple-touch-icon.png',
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(SHELL).then((c) => c.addAll(SHELL_ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== SHELL && k !== DATA).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  // 数据文件：网络优先（缓存只在断网时兜底）
  if (url.pathname.includes('/data/')) {
    e.respondWith(
      fetch(req)
        .then((res) => {
          if (res.ok) {
            // 以不带 ?t= 的干净路径为键存/取，页面端带时间戳防 CDN 缓存
            caches.open(DATA).then((cache) => cache.put(url.pathname, res.clone()));
          }
          return res;
        })
        .catch(() => caches.match(url.pathname))
    );
    return;
  }

  // 页面与静态资源：网络优先，失败回退缓存
  e.respondWith(
    fetch(req)
      .then((res) => {
        const copy = res.clone();
        caches.open(SHELL).then((cache) => cache.put(req, copy));
        return res;
      })
      .catch(() =>
        caches.match(req, { ignoreSearch: true }).then((hit) => hit || caches.match('./index.html'))
      )
  );
});
