
This module add the possibility to handle mutual events on sale.order.lines
As it's not possible to silence field changes, a change to price_unit will
trigger a change to visible_discount and a change to visible_discount will
trigger a change to price_unit.

For that reason, a pair of temp field has been added to the sale.order.line
to store some "interleaving" values. Thoses values can be reset instead of
calculating them twice.

FIXME: ./models/sale.py
-----------------------

Instead of using fields on the model, it might be possible to add the values
to the context. If the context is reused for the multiple on change events.
It might be possible to track value changes from there.

If that is true, we can then remove the dummy_search and both temp fields
temp_price and temp_discount.
