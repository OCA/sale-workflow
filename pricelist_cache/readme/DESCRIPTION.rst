Provides a cron task who caches prices for all products and all pricelists.
The goal is to be able to generate a whole catalog of prices and products for a given customer in a decent time.

Everyday, the cron task will trash the previous day's cache, and rebuild it from scratch.
It means that at any moment, the prices stored in the cache are those of the current day, and will not be recomputed before the next day.

However, new prices will be cached in the following cases:

* new product is created
* new pricelist is created
* new pricelist item is created
