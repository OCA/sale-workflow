# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.model
    def _get_can_amend_and_reprocure_depends(self):
        res = super()._get_can_amend_and_reprocure_depends()
        res.append("chained_purchase_line_ids.state")
        return res

    def _compute_can_amend_and_reprocure(self):
        """
        Filter here the lines that can be reprocured
        Don't take into account confirmed or done purchase lines
        """
        super()._compute_can_amend_and_reprocure()
        lines_with_purchase = self.filtered("chained_purchase_line_ids")
        lines_cannot_reprocure = lines_with_purchase.filtered(
            lambda line: any(
                purchase_line.state not in ("draft", "cancel")
                for purchase_line in line.chained_purchase_line_ids
            )
        )
        lines_cannot_reprocure.update({"can_amend_and_reprocure": False})

    def _get_purchase_line_amendment(self):
        return self.chained_purchase_line_ids.filtered(lambda l: l.state == "draft")

    def _amend_and_reprocure(self):
        """
        Get purchase lines that can be amended
        """
        purchase_line = self._get_purchase_line_amendment()
        purchase_line.unlink()
        super()._amend_and_reprocure()
