# Copyright 2017 Tecnativa - Sergio Teruel
# Copyright 2017 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends(
        "state", "order_line.invoice_status", "order_line.task_ids.invoiceable"
    )
    def _get_invoiced(self):
        super()._get_invoiced()
        for order in self.filtered(lambda o: o.invoice_status != "no"):
            if not all(
                t.invoiceable
                for t in order.mapped("order_line.task_ids")
                if t.invoicing_finished_task
            ):
                order.update({"invoice_status": "no"})


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    task_ids = fields.One2many(
        comodel_name="project.task", inverse_name="sale_line_id", string="Tasks",
    )

    @api.depends(
        "qty_invoiced",
        "qty_delivered",
        "product_uom_qty",
        "order_id.state",
        "task_ids.invoiceable",
    )
    def _get_to_invoice_qty(self):
        lines = self.filtered(
            lambda x: (
                x.product_id.type == "service"
                and x.product_id.invoicing_finished_task
                and x.product_id.service_tracking
                in ["task_global_project", "task_in_project"]
                and not all(x.task_ids.mapped("invoiceable"))
            )
        )
        if lines:
            lines.update({"qty_to_invoice": 0.0})
        super(SaleOrderLine, self - lines)._get_to_invoice_qty()

    def _timesheet_compute_delivered_quantity_domain(self):
        vals = super()._timesheet_compute_delivered_quantity_domain()
        vals = (
            ["|", ("amount", "<=", 0.0)]
            + vals
            + [
                # don't update the qty on sale order lines which are not
                # with a product invoiced on ordered qty +
                # invoice_finished task = True
                "|",
                ("so_line.product_id.invoice_policy", "=", "delivery"),
                ("so_line.product_id.invoicing_finished_task", "=", False),
            ]
        )
        return vals
