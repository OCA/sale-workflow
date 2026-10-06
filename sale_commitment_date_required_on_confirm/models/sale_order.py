# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _commitment_date_required(self):
        self.ensure_one()
        return self.company_id.sale_commitment_date_required

    def _confirmation_error_message(self):
        message = super()._confirmation_error_message()
        if (
            not message
            and self._commitment_date_required()
            and not self.commitment_date
        ):
            return self.env._("You cannot confirm this order without a delivery date.")
        return message
