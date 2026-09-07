# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.http import request, route

from odoo.addons.product.controllers.catalog import ProductCatalogController


class SaleProductCatalogController(ProductCatalogController):
    @route("/product/catalog/sale/open_order_line", auth="user", type="json")
    def product_catalog_open_order_line(self, order_id, product_id, **kwargs):
        """Open sale order line on a given order for a given product.

        :param int order_id: The order id.
        :param int product_id: The product, as a `product.product` id.
        :return: The id of the open sale order line.
        :rtype: int
        """
        order = request.env["sale.order"].browse(order_id)
        return order.with_company(order.company_id)._get_catalog_order_line(
            product_id,
            **kwargs,
        )

    @route("/product/catalog/sale/exclude_from_last_sales", auth="user", type="json")
    def product_catalog_exclude_from_last_sales(self, order_id, product_id, **kwargs):
        """Exclude a product from the catalog *Last sales* origin.

        The exclusion is stored for the partner the order matches its sale
        history against, so the product is no longer offered by that origin for
        any order of the same partner.

        :param int order_id: The order id.
        :param int product_id: The product, as a `product.product` id.
        :return: The id of the exclusion record.
        :rtype: int
        """
        order = request.env["sale.order"].browse(order_id)
        return order.with_company(order.company_id)._add_catalog_last_sales_exclusion(
            product_id
        )

    @route("/product/catalog/sale/get_order_line_data", auth="user", type="json")
    def product_catalog_get_order_line_data(self, order_line_ids, **kwargs):
        """Open sale order line on a given order for a given product.

        :param list order_line_ids: The order lines to update the record.
        :return: The data of the record that is being updated.
        :rtype: dict
        """
        order_lines = request.env["sale.order.line"].browse(order_line_ids)
        res = order_lines._get_product_catalog_lines_data(**kwargs)
        if order_lines:
            res["productType"] = order_lines[0].product_id.type
        return res

    @route("/product/catalog/sale/update_line_qty", auth="user", type="json")
    def product_catalog_update_line_qty(self, line_id, quantity, **kwargs):
        """Update the quantity of a specific sale order line.

        When quantity is 0 and the order is in draft/sent state, the line is
        unlinked. Returns the updated discounted price (or pricelist price if
        the line was deleted).

        :param int line_id: The sale order line id to update.
        :param float quantity: The new quantity.
        :return: The unit price after the update.
        :rtype: float
        """
        line = request.env["sale.order.line"].browse(line_id)
        order = line.order_id.with_company(line.company_id)
        request.update_context(catalog_skip_tracking=True)
        if quantity == 0 and order.state in ["draft", "sent"]:
            price_unit = order.pricelist_id._get_product_price(
                product=line.product_id,
                quantity=1.0,
                currency=order.currency_id,
                date=order.date_order,
            )
            line.unlink()
            return price_unit
        line.product_uom_qty = quantity
        return line._get_discounted_price()
