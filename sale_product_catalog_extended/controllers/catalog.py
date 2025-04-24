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

    @route("/product/catalog/sale/get_order_line_data", auth="user", type="json")
    def product_catalog_get_order_line_data(self, order_line_ids, **kwargs):
        """Open sale order line on a given order for a given product.

        :param list order_line_ids: The order lines to update the record.
        :return: The data of the record that is being updated.
        :rtype: dict
        """
        order_lines = request.env["sale.order.line"].browse(order_line_ids)
        return order_lines._get_product_catalog_lines_data(**kwargs)
