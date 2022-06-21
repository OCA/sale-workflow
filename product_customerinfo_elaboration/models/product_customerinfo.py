# Copyright 2022 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductCustomerInfo(models.Model):
    _inherit = "product.customerinfo"

    elaboration_id = fields.Many2one(comodel_name="product.elaboration")
    elaboration_note = fields.Char(
        string="Elaboration Note",
        store=True,
        compute="_compute_elaboration_note",
        readonly=False,
    )

    @api.depends("elaboration_id")
    def _compute_elaboration_note(self):
        for line in self:
            line.elaboration_note = line.elaboration_id.name
