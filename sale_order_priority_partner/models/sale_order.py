# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        # use partner_id.sale_priority as default priority if not explicitly provided
        for vals in vals_list:
            if "priority" not in vals:
                partner_id = vals.get("partner_id") or self.env.context.get(
                    "default_partner_id"
                )
                if partner_id:
                    partner = self.env["res.partner"].browse(partner_id)
                    priority = (
                        partner.sale_priority
                        or partner.commercial_partner_id.sale_priority
                    )
                    if priority:
                        vals["priority"] = priority
        return super().create(vals_list)

    @api.onchange("partner_id")
    def _onchange_partner_id_sale_priority(self):
        priority = (
            self.partner_id.sale_priority
            or self.partner_id.commercial_partner_id.sale_priority
        )
        if priority:
            self.order_line.priority = priority
            self.priority = priority
