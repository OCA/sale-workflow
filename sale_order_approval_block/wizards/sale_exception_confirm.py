# Copyright 2026 ForgeFlow, S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleExceptionConfirm(models.TransientModel):
    _inherit = "sale.exception.confirm"

    def action_confirm(self):
        self.ensure_one()
        if self.ignore and self.related_model_id.approval_block_id:
            self.related_model_id.button_release_approval_block()
        return super().action_confirm()
