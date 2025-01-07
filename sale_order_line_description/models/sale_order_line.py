# Copyright 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _compute_name(self):
        res = super()._compute_name()
        for line in self:
            if not line.product_id:
                continue
            if (
                line.user_has_groups(
                    "sale_order_line_description."
                    "group_use_product_description_per_so_line"
                )
                and line.product_id.description_sale
            ):
                product = line.product_id
                partner = line.order_id.partner_id
                if partner:
                    product = product.with_context(lang=partner.lang)
                line.name = product.description_sale
        return res
