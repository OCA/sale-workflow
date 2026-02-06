# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _ensure_sale_order_linked(self, sol_ids):
        """Skip auto-confirmation when creating project manually."""
        if self.env.context.get("skip_auto_confirm_so"):
            return
        return super()._ensure_sale_order_linked(sol_ids)
