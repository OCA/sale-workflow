# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class BaseSubstateType(models.Model):
    _inherit = "base.substate.type"

    model = fields.Selection(
        selection_add=[("sale.order", "Sale order")], ondelete={"sale.order": "cascade"}
    )


class SaleOrder(models.Model):
    _inherit = ["sale.order", "base.substate.mixin"]
    _name = "sale.order"

    has_base_substate = fields.Boolean(compute="_compute_has_base_substate")

    def _compute_has_base_substate(self):
        for rec in self:
            rec.has_base_substate = bool(self.env["base.substate"].search_count([]))
