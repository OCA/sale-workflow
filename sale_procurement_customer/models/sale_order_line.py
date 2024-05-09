# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    def _prepare_procurement_group_vals(self):
        """
        Adds also the customer to the procurement group values
        """
        res = super()._prepare_procurement_group_vals()
        res.update({"customer_id": self.order_id.partner_id.id})
        return res
