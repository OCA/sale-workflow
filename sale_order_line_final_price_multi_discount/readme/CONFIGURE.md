In *Sales > Configuration > Settings > Pricing*, with *Discounts* enabled:

- **Final price discounts** sets what the final price does with the discounts
  of the line:
  - *Replace the discounts* (default): the distribution becomes the single
    discount that brings the unit price to the final price.
  - *Append to the pricelist discounts*: the discounts of the pricelist rule are
    kept (e.g. `40 + 5`) and one more discount is appended, the one that brings
    their result to the final price.
- **Salespeople Edit Prices and Discounts**: `sale_order_line_final_price`
  makes the unit price and the discounts read only for anyone who is not a
  *Sales Administrator*. Ticking this option lifts the lock for everybody.
