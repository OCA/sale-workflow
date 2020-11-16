This module provides Tiered Pricing features.
It extends pricelists to use them for tiered pricing, e.g:

- starting from 0, sell for 10€
- starting from 100, sell for 8€
- starting from 200, sell for 7€

In tiered pricing, somebody buying 250 units would pay `100*10 + 200*8 + 50*7`.
In other words the unit price is equivalent to the weighted average of tiers.
