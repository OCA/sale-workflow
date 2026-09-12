# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        # override to use partner_id.sale_priority as default priority if set
        for vals in vals_list:
            partner_id = vals.get("partner_id") or self.env.context.get(
                "default_partner_id"
            )
            partner = self.env["res.partner"].browse(partner_id)
            if partner.sale_priority:
                vals["priority"] = partner.sale_priority
        return super().create(vals_list)
