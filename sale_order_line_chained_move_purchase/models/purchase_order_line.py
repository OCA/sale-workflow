# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    related_sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
    )

    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        """
        We append related_sale_line_id to purchase order line new values
        """
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )

        res["related_sale_line_id"] = values.get("related_sale_line_id")
        return res
