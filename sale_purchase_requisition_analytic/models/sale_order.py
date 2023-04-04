# Copyright 2023 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_create_purchase_requisition(self):
        res = super().action_create_purchase_requisition()
        res["context"]["default_analytic_account_id"] = self.analytic_account_id.id
        return res
