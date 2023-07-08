// This is the service worker with the Cache-first network

const CACHE = "pwabuilder-precache";
const precacheFiles = [
  "/",
  "/static/css/bootstrap.min.css",
  "/static/js/bootstrap.min.js",

];

self.addEventListener("install", function (event) {
  console.log("[PWA Builder] Install Event processing");
  console.log("[PWA Builder] Skip waiting on install");
  self.skipWaiting();

  event.waitUntil(
    caches.open(CACHE).then(function (cache) {
      console.log("[PWA Builder] Caching pages during install");
      return cache.addAll(precacheFiles);
    })
  );
});

self.addEventListener("fetch", function (event) {
  console.log("[PWA Service Worker] Fetch event detected, now serving the cached assets");
  event.respondWith(
    caches.match(event.request).then(function (cacheResponse) {
      return (
        cacheResponse ||
        fetch(event.request).then(function (networkResponse) {
          caches.open(CACHE).then(function (cache) {
            cache.put(event.request, networkResponse.clone());
          });
          return networkResponse;
        })
      );
    })
  );
});


function serviceworker() {
    console.log("Registering service worker");;
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/service_worker.js').then(function(registration) {
            console.log('Service Worker is registered', registration);
        }, function(err) {
            console.log('Service Worker registration failed: ', err);
        });
        });
    }
};


serviceworker();