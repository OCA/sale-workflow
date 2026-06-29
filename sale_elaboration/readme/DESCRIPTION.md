This module extends the functionality of sales orders to allow to set an
elaboration on lines that will add an extra order line with an
elaboration product linked to it when the delivery order is validated.

An **elaboration** is a process that needs to be done over the product,
usually on picking/handling phase. It doesn't modify too much the
product for needing an specific product, but it adds a surcharge on the
final price.

If the elaboration has a defined route, selecting the elaboration,
it is set on the order line, which will result in the generation of
multiple delivery notes depending on the established route.
