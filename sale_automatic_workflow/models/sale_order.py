# Copyright 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>
# Copyright 2013 Camptocamp SA (author: Guewen Baconnier)
# Copyright 2016 Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    workflow_process_id = fields.Many2one(
        comodel_name="sale.workflow.process",
        string="Automatic Workflow",
        ondelete="restrict",
        copy=False,
    )
    all_qty_delivered = fields.Boolean(
        compute="_compute_all_qty_delivered",
        string="All quantities delivered",
        store=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        if "workflow_process_id" in fields:
            default_workflow = self.env["sale.workflow.process"].search(
                [("default", "=", True)], limit=1
            )
            if default_workflow:
                res["workflow_process_id"] = default_workflow.id
        return res

    # TODO: v15 -> make this module dependent on sale_delivery_state and
    # use the code in sale_automatic_workflow_delivery_state to replace this function
    @api.depends("order_line.qty_delivered", "order_line.product_uom_qty")
    def _compute_all_qty_delivered(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for order in self:
            order.all_qty_delivered = all(
                line.product_id.type not in ("product", "consu")
                or float_compare(
                    line.qty_delivered, line.product_uom_qty, precision_digits=precision
                )
                >= 0
                for line in order.order_line
            )

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        workflow = self.workflow_process_id
        if not workflow:
            return invoice_vals
        invoice_vals["workflow_process_id"] = workflow.id
        if workflow.invoice_date_is_order_date:
            invoice_vals["invoice_date"] = fields.Date.context_today(
                self, self.date_order
            )
        if workflow.property_journal_id:
            invoice_vals["journal_id"] = workflow.property_journal_id.id
        return invoice_vals

    @api.onchange("workflow_process_id")
    def _onchange_workflow_process_id(self):
        if not self.workflow_process_id:
            return
        workflow = self.workflow_process_id
        if workflow.picking_policy:
            self.picking_policy = workflow.picking_policy
        if workflow.team_id:
            self.team_id = workflow.team_id.id
        if workflow.warning:
            warning = {"title": _("Workflow Warning"), "message": workflow.warning}
            return {"warning": warning}

    def _create_invoices(self, grouped=False, final=False, date=None):
        for order in self:
            if not order.workflow_process_id.invoice_service_delivery:
                continue
            for line in order.order_line:
                if line.qty_delivered_method == "manual" and not line.qty_delivered:
                    line.write({"qty_delivered": line.product_uom_qty})
        return super()._create_invoices(grouped=grouped, final=final, date=date)

    def write(self, vals):
        if vals.get("state") == "sale" and vals.get("date_order"):
            sales_keep_order_date = self.filtered(
                lambda sale: sale.workflow_process_id.invoice_date_is_order_date
            )
            if sales_keep_order_date:
                new_vals = vals.copy()
                del new_vals["date_order"]
                res = super(SaleOrder, sales_keep_order_date).write(new_vals)
                res |= super(SaleOrder, self - sales_keep_order_date).write(vals)
                return res
        return super(SaleOrder, self).write(vals)

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super(SaleOrder, self).onchange_partner_id()
        if not self.workflow_process_id and self.partner_id.workflow_process_id:
            self.workflow_process_id = self.partner_id.workflow_process_id.id
        return res
