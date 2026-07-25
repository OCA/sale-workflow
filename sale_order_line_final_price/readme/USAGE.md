On any sale order line, fill in *Final Price* with the unit price agreed with
the customer. The discount is computed right away, keeping the unit price given
by the pricelist: a final price of 750.00 over 1,000.00 gives a 25% discount.
Editing the unit price or the discount refreshes the final price instead.

A line whose pricelist price is zero is the exception. No discount can ever lift
that price up to the agreed figure, and there is no catalog price worth keeping
either, so the final price is written straight into the unit price and the
discount stays at zero.

The discount is the only figure that moves, so the final price can only be
reached as close as the *Discount* decimal precision allows. When the requested
figure is out of reach, the line settles for the closest one, and the final price
shown is always what the line is really worth: asking for 333.33 over 1,000.00
gives a 66.67% discount, which is 333.30.

That leftover can also stay out of sight on the final price and still show up on
the amount of the line: 30.75 with the -78.86% needed to reach 55.00 is 54.99945
per unit, so 10 units amount to 549.99 instead of 550.00. Raising the decimal
precision of *Discount* narrows the gap.
