const CACHE = "mah-yesh-beze-v3";
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
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Network-first: always try to get the freshest page when online.
// Falls back to cache only when offline (or the network request fails).
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(
    fetch(e.request)
      .then(networkResponse => {
        const copy = networkResponse.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
        return networkResponse;
      })
      .catch(() =>
        caches.match(e.request).then(cached => cached || caches.match("/mah-yesh-beze/"))
      )
  );
});
