# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    sale_warn_msg = fields.Text(compute="_compute_sale_warn_msg")

    @api.depends(
        "state", "partner_id.sale_warn", "partner_id.commercial_partner_id.sale_warn"
    )
    def _compute_sale_warn_msg(self):
        for rec in self:
            if rec.state not in ["draft", "sent"]:
                rec.sale_warn_msg = False
                continue
            p = rec.partner_id.commercial_partner_id
            sale_warn_msg = ""
            separator = ""
            if p.sale_warn == "warning":
                separator = "\n"
                sale_warn_msg += p.sale_warn_msg
            if p != rec.partner_id and rec.partner_id.sale_warn == "warning":
                sale_warn_msg += separator + rec.partner_id.sale_warn_msg
            rec.sale_warn_msg = False if sale_warn_msg == "" else sale_warn_msg
