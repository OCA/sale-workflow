Negotiations happen on the price the customer ends up paying, but a quotation
where that figure has been typed straight into the unit price loses the only
thing that tells you a rebate ever happened: the price of the catalog. The line
then reads as if the product were worth what was agreed, the discount column
stays at zero, and there is no way to tell a well priced deal from a heavily
discounted one, neither on the printed quotation nor on any margin or discount
report.

Odoo already has the right place to record that gap. The unit price is what the
pricelist says the product is worth, and the discount is what was given away. So
the list price is worth keeping untouched, and the discount is worth keeping as
the only thing that moves.

The catch is that salespeople don't negotiate in percentages, and asking them to
work out that 45.00 out of 49.90 is a 9.82% discount is asking for typos and for
unit prices quietly edited down instead. This module closes that gap: the *Final
Price* field takes the agreed figure, and the discount is derived from it, so the
pricelist price stays on the line and the rebate is recorded as a rebate, without
anybody having to compute anything.

Locking the unit price and the discount for everyone but a *Sales Administrator*
is what keeps that invariant true. The two fields remain the record of what the
catalog said and what was conceded.