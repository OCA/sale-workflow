# Copyright 2011 Akretion, Sodexis
# Copyright 2018 Akretion
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class SaleExceptionConfirm(models.TransientModel):
    _name = "sale.exception.confirm"
    _inherit = ["exception.rule.confirm"]
    _description = "Sale exception confirm wizard"

    related_model_id = fields.Many2one("sale.order", "Sale")

    def action_confirm(self):
        self.ensure_one()
        exceptions_blocking = self.exception_ids.filtered("is_blocking")
        if self.ignore and not exceptions_blocking:
            self.related_model_id.ignore_exception = True
        return super().action_confirm()
