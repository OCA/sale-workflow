from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pdp_ids = fields.One2many("planned.down.payment", "order_id")
    pdp_total = fields.Float("DP Total", compute="_compute_pdp_total")

    def action_create_pdp(self):
        pdp_id = self.env["planned.down.payment"].create({"order_id": self.id})
        return {
            "name": _("Planned Down Payment"),
            "view_mode": "form",
            "views": [
                (self.env.ref("sale_product_advance_payment.pdp_view_form").id, "form")
            ],
            "res_model": "planned.down.payment",
            "res_id": pdp_id.id,
            "type": "ir.actions.act_window",
            "target": "current",
        }

    @api.depends("order_line.invoice_lines")
    def _get_invoiced(self):
        super(SaleOrder, self)._get_invoiced()
        self.pdp_ids._compute_invoice_id()

    def _compute_pdp_total(self):
        for rec in self:
            rec.pdp_total = sum(rec.pdp_ids.mapped("total"))

    def _get_invoiceable_lines(self, final=False):
        res = super(SaleOrder, self)._get_invoiceable_lines(final)
        new_res = self.env["sale.order.line"]
        # leave only invoiced PDP lines
        if (
            self.env.context.get("sapi_wizard_id")
            and self.env["sale.advance.payment.inv"]
            .browse(self.env.context.get("sapi_wizard_id"))
            .pdp_per_line
        ):
            dp_lines = res.filtered(lambda x: x.is_downpayment is True)
            product_lines = res.filtered(lambda x: x.is_downpayment is False)
            new_res += product_lines
            for dp_line in dp_lines:
                if dp_line.pdp_line_id.order_line_id.id in product_lines.ids:
                    new_res += dp_line
        return new_res or res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    dp_amount_invoiced = fields.Float("DP Invoiced", compute="_compute_pdp_values")
    dp_amount_remaining = fields.Float("DP Remaining", compute="_compute_pdp_values")
    pdp_line_id = fields.Many2one("pdp.line", string="PDP Line")

    def _compute_pdp_values(self):
        for rec in self:
            pdp_lies = self.env["pdp.line"].search(
                [("order_line_id", "=", rec.id), ("pdp_state", "=", "invoiced")]
            )
            rec.dp_amount_invoiced = sum(pdp_lies.mapped("total"))
            rec.dp_amount_remaining = rec.price_subtotal - rec.dp_amount_invoiced
