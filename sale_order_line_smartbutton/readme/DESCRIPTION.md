This module adds a smart button on the Sale Order form giving quick access
to a dedicated, searchable list of its order lines.

On large sale orders it can be hard to find a specific product line by
scrolling through the "Order Lines" notebook page. This module opens a
dedicated list/search view of the order's lines (excluding sections and
notes) so users can filter/search by product, customer or status, and
adapt prices, quantities, UoM, discount, etc. directly from that list.

Editability of the fields mimics the standard Sale Order form: fields are
readonly according to the same conditions used on ``sale.order.views``
(``product_updatable``, ``product_uom_readonly``, ``qty_invoiced``,
``is_downpayment``), and the whole line becomes readonly once its order is
cancelled or locked, matching the top-level
``readonly="state == 'cancel' or locked"`` gate applied to the order lines
on the sale order form itself. The ``sale.order.line`` model already
enforces this server-side when an order is locked, this module only makes
the view consistent with that behavior.
