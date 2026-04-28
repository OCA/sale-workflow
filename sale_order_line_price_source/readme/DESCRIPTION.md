This module tracks from where each sale order line unit price comes
from.

It extends `sale.order.line` with: - `price_source` (`pricelist`,
`product`, `manual`) - `price_source_pricelist_item_id` (the applied
`product.pricelist.item` when source is `pricelist`)

Price source is computed from core pricing behavior, including
manual-price detection based on `technical_price_unit` versus
`price_unit`.
