The discount is the only room the final price has to move in, so the decimal
precision of *Discount* is what says how exact the final price can be. With the
two decimals Odoo ships with, the leftover of the rounding is at most
`unit price * 0.005 / 100` per unit, which stays under a cent on a single unit
but adds up with the quantity: 10 units of a line priced at 30.75 amount to
549.99 instead of the 550.00 asked for.

Raising the decimal precision of *Discount* (*Settings > Technical > Decimal
Accuracy*) to 5 or 6 digits drops that leftover below the cent for any sensible
price and quantity, and the amounts of the line then add up to the final price.

Bear in mind that this precision rules every discount of the database, and that
discounts with that many decimals will be printed as such unless the report is
told otherwise.
