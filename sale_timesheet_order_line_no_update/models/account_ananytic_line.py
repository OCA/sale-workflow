from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.depends(
        "task_id.sale_line_id",
        "project_id.sale_line_id",
        "employee_id",
        "project_id.allow_billable",
    )
    def _compute_so_line(self):
        # Skip this method to keep same so_line after it was changed
        pass
