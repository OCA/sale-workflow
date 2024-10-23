# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("source_id"):
                partner = self.env["res.partner"].browse(vals["partner_id"])
                if partner.utm_source_id:
                    vals["source_id"] = partner.utm_source_id.id
        return super().create(vals_list)
