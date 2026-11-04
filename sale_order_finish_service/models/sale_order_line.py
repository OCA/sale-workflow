# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools.sql import column_exists, create_column


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    finished_sale_order = fields.Boolean(
        related="order_id.finished_sale_order", store=True, copy=False
    )

    def _domain_sale_line_service(self, **kwargs):
        domain = super()._domain_sale_line_service(**kwargs)
        if kwargs.get("check_finished_sale_order", True):
            domain.append(("finished_sale_order", "=", False))
        return domain

    def _auto_init(self):
        """
        Create column to avoid computation by the ORM
        """
        if not column_exists(self.env.cr, "sale_order_line", "finished_sale_order"):
            create_column(self.env.cr, "sale_order_line", "finished_sale_order", "bool")
        return super()._auto_init()
