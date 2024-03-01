This offer a default behavior while confirming sale order to set the
**stock service level** to be use by `stock_service_level` (and
`stock_service_level_route`) modules.

This module add a computed field on sale order line that can be adapted to your needs.

This service level is used while calling the procurement method while confirming the sale order
and propagated to stock.move in order to apply rule or reservation rule on it.
