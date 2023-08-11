# Copyright 2023 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    related_so_sequence = fields.Char(
        string="SO Line Number",
        compute="_compute_related_so_sequence",
    )

    @api.depends("move_id.invoice_line_ids")
    def _compute_related_so_sequence(self):
        for rec in self:
            if len(rec.move_id.mapped("line_ids.sale_line_ids.order_id")) > 1:
                rec.related_so_sequence = "{}/{}".format(
                    rec.sale_line_ids.order_id.name,
                    rec.sale_line_ids.visible_sequence,
                )
            else:
                rec.related_so_sequence = str(rec.sale_line_ids.visible_sequence)
