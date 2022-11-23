from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_fully_delivered = fields.Boolean(
        compute="_compute_is_fully_delivered", store=True, index=True
    )
    # Same as invoice_status, but excluding invoices in draft
    invoice_status_validated = fields.Selection(
        [
            ("no", "Nothing to Invoice"),
            ("to invoice", "Can be Invoiced"),
            ("invoiced", "Fully Invoiced"),
        ],
        string="Posted Invoice Status",
        compute="_compute_invoice_status_validated",
        store=True,
        readonly=True,
        copy=False,
        default="no",
    )

    @api.depends("order_line.qty_delivered")
    def _compute_is_fully_delivered(self):
        for sale in self:
            if all(
                line.product_uom_qty <= line.qty_delivered
                for line in sale.order_line.filtered(
                    lambda l: l._include_in_fully_delivered_compute()
                )
            ):
                sale.is_fully_delivered = True
            else:
                sale.is_fully_delivered = False

    @api.depends("invoice_status")
    def _compute_invoice_status_validated(self):
        # Same as invoice status, execpt it is not invoiced unless there is no invoice
        # in draft
        for order in self:
            if order.invoice_status in ("no", "to invoice"):
                order.invoice_status_validated = order.invoice_status
            elif order.invoice_status in ("no", "upselling"):
                order.invoice_status_validated = "no"
            else:
                if not any(inv.state == "draft" for inv in order.invoice_ids):
                    order.invoice_status_validated = order.invoice_status
                else:
                    order.invoice_status_validated = "to invoice"
