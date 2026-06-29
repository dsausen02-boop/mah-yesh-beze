const CACHE = "mah-yesh-beze-v2";
const ASSETS = [
  "/mah-yesh-beze/",
  "/mah-yesh-beze/index.html",
  "/mah-yesh-beze/torah.html",
  "/mah-yesh-beze/giyur.html",
  "/mah-yesh-beze/harav-ezra.jpg",
  "/mah-yesh-beze/icon-192.png",
  "/mah-yesh-beze/icon-512.png",
  "/mah-yesh-beze/manifest.json"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys =>
    Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
  ));
  self.clients.claim();
});

self.addEventListener("fetch", e => {
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request).catch(() => caches.match("/mah-yesh-beze/")))
  );
});
