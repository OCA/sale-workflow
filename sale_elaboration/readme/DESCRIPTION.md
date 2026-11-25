This module extends the functionality of sales orders to allow to set an
elaboration on lines that will add an extra order line with an
elaboration product linked to it when the delivery order is validated.

An **elaboration** is a process that needs to be done over the product,
usually on picking/handling phase. It doesn't modify too much the
product for needing an specific product, but it adds a surcharge on the
final price.

If the elaborations have routes, selecting them sets all their routes
on the order line, which will result in the generation of multiple
delivery notes depending on the established routes. For each step,
procurement takes the first of those routes by sequence with a rule for
it, so the routes of several elaborations can complement each other.
