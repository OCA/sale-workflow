This module extends the functionality of sale coupon to allow
1) to create non cumulative program. This program will stop further computation of promotions.
By default all programs are applied.
2) Create program to apply pre-defined price lists. This is tricky as applying pricelist
to sale order may cause not revertible changes on product prices if you edit them manually or set a pricelist
to customer manually
3) Promotions applicable only for first sale order of the customer.
4) Promotions applicable for the first N orders of the customer.
5) Add the ability to reward a product even if it has not been ordered (free product).
