Fill in *Final Price* on a sale order line: the discount distribution is worked
out at once and the aggregated discount follows. A final price of 80.00 over a
unit price of 100.00 gives `[20]`, or `[10, 11.11]` when the pricelist rule
already grants 10% and the *append* policy is active.

The discount is rounded to the *Discount* decimal precision, so the final price
then shows the closest figure the line can really reach: 333.33 over 1,000.00
gives `[66.67]`, that is 333.30.

Modules built on top can:

- change the rounding direction of the discount
  (`_get_price_final_discount_rounding_method`);
- take out of the final price the amounts they fold into the line discount
  (`_get_price_final_reach`);
- reuse `_set_discount_to_reach` to aim the line at any other price.
