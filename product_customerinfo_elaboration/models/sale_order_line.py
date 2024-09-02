# Copyright 2022 Tecnativa - Carlos Roca
# Copyright 2023 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    elaboration_ids = fields.Many2many(
        comodel_name="product.elaboration",
        compute="_compute_elaboration_ids",
        store=True,
        readonly=False,
        string="Elaborations",
    )

    @api.depends("product_id")
    def _compute_elaboration_ids(self):
        for line in self:
            customer_info = line._get_product_customer_info()
            if customer_info:
                line.elaboration_ids = customer_info.elaboration_ids

    def _get_product_customer_info(self):
        customerinfo = self.product_id.customer_ids.filtered(
            lambda pc: pc.elaboration_ids and pc.name == self.order_id.partner_id
        )[:1]
        if not customerinfo:
            customerinfo = self.product_id.customer_ids.filtered(
                lambda pc: pc.elaboration_ids
                and pc.name == self.order_id.partner_id.commercial_partner_id
            )[:1]
        return customerinfo

    @api.onchange("elaboration_ids")
    def onchange_elaboration_ids(self):
        res = super().onchange_elaboration_ids()
        for line in self:
            customer_info = line._get_product_customer_info()
            if (
                customer_info
                and line.elaboration_ids
                and (
                    # Comparing with ids because comparison with newId doesn't work
                    line.elaboration_ids.ids == customer_info.elaboration_ids.ids
                    or not line.elaboration_ids
                )
            ):
                line.elaboration_note = customer_info.elaboration_note
        return res
