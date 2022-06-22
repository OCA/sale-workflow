Create a new sale order and add discounts in any of the three discount
fields given.

For multiplicative discounts they go in order of precedence so discount 2 will
be calculated over discount 1 and discount 3 over the result of discount 2. For
example, let's divide by two on every discount:

Unit price: 600.00 ->

  - Disc. 1 = 50% -> Amount = 300.00
  - Disc. 2 = 50% -> Amount = 150.00
  - Disc. 3 = 50% -> Amount = 75.00

For additive discounts they will be summed first and then applied. For
example, let's have a three 20% discounts:

Unit price: 600.00 ->

  - Disc. 1, 2, 3 = 20% + 20% + 20% -> 60%
  - Disc. final = 60% -> Amount = 240.00


You can also use negative values to make a charge instead of a discount:

Unit price: 600.00 ->

  - Disc. 1 = 50% -> Amount = 300.00
  - Disc. 2 = -5% -> Amount = 315.00

Module allows defining additional discount fields and applying them with
other by adding them to the `_discount_fields` method.
