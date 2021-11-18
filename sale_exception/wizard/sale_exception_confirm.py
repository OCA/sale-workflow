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

    def action_confirm_ignore_exc(self):
        self.ensure_one()
        self.related_model_id.ignore_exception = True
        self.related_model_id.action_confirm()
        return super().action_confirm()
