This module extends `sale_pricelist_fixed_price_no_discount` and `sale_triple_discount`.

When a sale order line uses a fixed-price pricelist rule, the three discount
fields provided by `sale_triple_discount` are reset and made readonly. Backend
writes are validated to prevent triple discounts through imports, RPC calls, or
custom code.
