# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    skip_sale_delivery_state = fields.Boolean(
        string="Skip Delivery State",
        compute="_compute_skip_sale_delivery_state",
        store=True,
        readonly=False,
    )

    @api.depends("company_id", "product_id")
    def _compute_skip_sale_delivery_state(self):
        for line in self:
            skip_sale_delivery_state = False
            if (
                line.product_id
                and line.product_id.type == "service"
                and line.company_id.skip_service_sale_delivery_state
            ):
                skip_sale_delivery_state = True
            line.skip_sale_delivery_state = skip_sale_delivery_state
