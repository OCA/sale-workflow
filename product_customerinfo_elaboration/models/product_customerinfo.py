# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductCustomerInfo(models.Model):
    _inherit = "product.customerinfo"

    elaboration_ids = fields.Many2many(comodel_name="product.elaboration")
    elaboration_note = fields.Char(
        store=True,
        compute="_compute_elaboration_note",
        readonly=False,
    )

    @api.depends("elaboration_ids")
    def _compute_elaboration_note(self):
        for line in self:
            line.elaboration_note = ", ".join(line.elaboration_ids.mapped("name"))
