* Seasonality has to be set by hand, but it would be nice to have it computed as well.
* An option for v13 could be merging the sales classification method with the module
  `product_abc_classification` that is based on delivered quantities and a more complex
  rule set design. In the moment of this PR, the module is still in development
  (https://github.com/OCA/product-attribute/pull/623) and even a divergent backport
  is beign made (https://github.com/OCA/product-attribute/pull/781).
  So this is a tinier and simpler approach with different metrics that can be merged
  into the logic of the more generic a broad `product_abc_classification`.
