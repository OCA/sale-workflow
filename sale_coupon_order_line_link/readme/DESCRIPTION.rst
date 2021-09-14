This module adds a link in the sale order line to the program used in a discount, so
it can be easily tracked afterwards. Also eases the implementation of coupon modules
that don't necessarily use the discount product as product for the discount line.

It also links the reward lines to:
  - The order lines that generated them, so we can follow which order lines produced
    which discounts.
  - The order lines over which the reward is applied:

    - In a discount promo: the cheapest product, specific products or the whole order.
    - In a product promo: the product lines over which the reward is discounted.
