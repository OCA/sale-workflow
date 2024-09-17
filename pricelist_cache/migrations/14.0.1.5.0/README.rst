As it causes problems in other module's tests when creating pricelist items,
drop the base automation record in favor of a hook in `product.pricelist.cache.create()`.
