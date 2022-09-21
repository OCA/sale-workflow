import time

from odoo import _, api, fields, models


class PlannedDownPayment(models.Model):
    _name = "planned.down.payment"
    _description = "Planned Down Payment"

    name = fields.Char(readonly=True)
    value = fields.Float("Advance Payment Value")
    payment_type = fields.Selection(
        selection=[("percentage", "Percentage"), ("fixed", "Fixed")],
        string="Advanced Payment Type",
        required=True,
        default="percentage",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("invoiced", "Invoiced"),
            ("canceled", "Canceled"),
        ],
        string="State",
        default="draft",
    )
    order_id = fields.Many2one("sale.order", required=True, readonly=True)
    date_invoice = fields.Datetime("Invoicing Date")
    # ('id', '=', self) - virtual One2many
    line_ids = fields.Many2many(
        "pdp.line", domain="[('order_id', '=', order_id),('pdp_id', '=', id)]"
    )
    total = fields.Float("Total", compute="_compute_all")
    # invoice_id = fields.Many2one('account.move', "Invoice", readonly=True)
    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
        compute="_compute_invoice_id",
        readonly=True,
        copy=False,
    )
    note = fields.Text()
    currency_id = fields.Many2one(related="order_id.currency_id")

    @api.model
    def default_get(self, fields_list):
        res = super(PlannedDownPayment, self).default_get(fields_list)
        res["date_invoice"] = fields.Datetime.now()
        return res

    @api.depends("order_id.order_line.invoice_lines")
    def _compute_invoice_id(self):
        for rec in self:
            invoices = self.env["account.move"].search([("pdp_id", "=", rec.id)])
            rec.invoice_id = invoices[:1]

    @api.depends("line_ids.total")
    def _compute_all(self):
        for rec in self:
            rec.total = sum(rec.line_ids.mapped("total"))

    @api.model
    def create(self, vals):
        res = super(PlannedDownPayment, self).create(vals)
        res.name = "DP/" + str(res.id)
        res.onchange_order_id()
        return res

    @api.onchange("order_id")
    def onchange_order_id(self):
        old_lines = self.env["pdp.line"].search(
            [("order_id", "=", self.order_id.id), ("pdp_id", "=", self._origin.id)]
        )
        for line in self.order_id.order_line.filtered(
            lambda x: x.product_uom_qty > 0 and x.is_downpayment is False
        ):
            if line.id not in old_lines.mapped("order_line_id.id"):
                self.env["pdp.line"].create(
                    {
                        "name": line.product_id.display_name,
                        "pdp_id": self._origin.id,
                        "order_id": self.order_id.id,
                        "order_line_id": line.id,
                        "qty": line.product_uom_qty,
                    }
                )

    @api.onchange("value", "payment_type")
    def onchange_value(self):
        for line in self.line_ids:
            if self.payment_type == "percentage":
                line.update({"subtotal": line.price_subtotal * self.value / 100})
            elif self.payment_type == "fixed":
                line.update({"subtotal": self.value})

    def action_add_all_lines(self):
        self.line_ids = [(5, 0, 0)]
        old_lines = self.env["pdp.line"].search(
            [("order_id", "=", self.order_id.id), ("pdp_id", "=", self._origin.id)]
        )
        self.line_ids = [(6, 0, old_lines.ids)]
        self.onchange_value()

    def action_remove_all_lines(self):
        self.line_ids = [(5, 0, 0)]

    def action_confirm(self):
        self.state = "confirmed"

    def action_invoice(self):
        self.state = "invoiced"
        product_id = self.get_dp_product()
        invoice_id = self.create_invoice(product_id)
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type"
        )
        action["domain"] = [("id", "in", invoice_id.ids)]
        action["view_mode"] = "form"
        action["res_id"] = invoice_id.id
        action["views"] = [(self.env.ref("account.view_move_form").id, "form")]
        return action

    def get_dp_product(self):
        product_id = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale.default_deposit_product_id")
        )
        product_id = self.env["product.product"].browse(int(product_id)).exists()
        if not product_id:
            sapi = self.env["sale.advance.payment.inv"].create({})
            vals = sapi._prepare_deposit_product()
            product_id = self.env["product.product"].create(vals)
            self.env["ir.config_parameter"].sudo().set_param(
                "sale.default_deposit_product_id", product_id.id
            )
        return product_id

    def create_dp_order_lines(self, product_id, dp_line):
        sale_line_obj = self.env["sale.order.line"]
        taxes = product_id.taxes_id.filtered(
            lambda r: not self.order_id.company_id
            or r.company_id == self.order_id.company_id
        )
        tax_ids = self.order_id.fiscal_position_id.map_tax(
            taxes, product_id, self.order_id.partner_shipping_id
        ).ids
        analytic_tag_ids = []
        for line in self.order_id.order_line:
            analytic_tag_ids = [
                (4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids
            ]

        so_line_values = self._prepare_so_line(
            self.order_id,
            product_id,
            analytic_tag_ids,
            tax_ids,
            dp_line,
        )
        so_line = sale_line_obj.create(so_line_values)
        return so_line

    def create_invoice(self, product_id):
        line_vals = []
        if len(self.line_ids) > 0:
            for dp_line in self.line_ids:
                so_line = self.create_dp_order_lines(product_id, dp_line)
                vals = {
                    "name": "%s - Down Payment" % dp_line.order_line_id.product_id.name,
                    "quantity": 1,
                    "product_id": product_id.id,
                    "price_unit": dp_line.amount * dp_line.order_line_id.qty_delivered,
                    "analytic_account_id": self.order_id.analytic_account_id.id,
                    "sale_line_ids": [(6, 0, so_line.ids)],
                }
                line_vals.append((0, 0, vals))
        invoice_id = self.env["account.move"].create(
            {
                "pdp_id": self.id,
                "move_type": "out_invoice",
                "ref": self.order_id.client_order_ref,
                "invoice_origin": self.order_id.name,
                "invoice_user_id": self.order_id.user_id.id,
                "narration": self.order_id.note,
                "partner_id": self.order_id.partner_invoice_id.id,
                "fiscal_position_id": (
                    self.order_id.fiscal_position_id
                    or self.order_id.fiscal_position_id.get_fiscal_position(
                        self.order_id.partner_id.id
                    )
                ).id,
                "partner_shipping_id": self.order_id.partner_shipping_id.id,
                "currency_id": self.order_id.pricelist_id.currency_id.id,
                "payment_reference": self.order_id.reference,
                "invoice_payment_term_id": self.order_id.payment_term_id.id,
                "partner_bank_id": self.order_id.company_id.partner_id.bank_ids[:1].id,
                "team_id": self.order_id.team_id.id,
                "campaign_id": self.order_id.campaign_id.id,
                "medium_id": self.order_id.medium_id.id,
                "source_id": self.order_id.source_id.id,
                "invoice_line_ids": line_vals,
            }
        )
        return invoice_id

    def _prepare_so_line(self, order, product_id, analytic_tag_ids, tax_ids, dp_line):
        so_values = {
            "name": "%s - Down Payment %s"
            % (
                dp_line.order_line_id.product_id.display_name,
                time.strftime("%d-%m-%Y"),
            ),
            "pdp_line_id": dp_line.id,
            "price_unit": dp_line.amount * dp_line.order_line_id.qty_delivered,
            "product_uom_qty": 0.0,
            "order_id": order.id,
            "discount": 0.0,
            "product_uom": product_id.uom_id.id,
            "product_id": product_id.id,
            "analytic_tag_ids": analytic_tag_ids,
            "tax_id": [(6, 0, tax_ids)],
            "is_downpayment": True,
            "sequence": order.order_line and order.order_line[-1].sequence + 1 or 10,
        }
        return so_values

    def action_show_invoice(self):
        return {
            "name": _("Invoice"),
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_id": self.invoice_id.id,
        }

    def action_cancel(self):
        self.state = "canceled"

    def action_reset_to_draft(self):
        self.state = "draft"

    def action_delete(self):
        self.unlink()


class PDPLine(models.Model):
    _name = "pdp.line"
    _description = "Planned Down Payment Line"

    name = fields.Char()
    order_id = fields.Many2one("sale.order")
    order_line_id = fields.Many2one("sale.order.line")
    price_unit = fields.Float(related="order_line_id.price_unit")
    currency_id = fields.Many2one(related="order_line_id.currency_id")
    price_subtotal = fields.Monetary(related="order_line_id.price_subtotal")
    order_line_dp_amount_invoiced = fields.Float(
        related="order_line_id.dp_amount_invoiced"
    )
    tax_id = fields.Many2many(related="order_line_id.tax_id")
    pdp_id = fields.Many2one("planned.down.payment")
    pdp_state = fields.Selection(related="pdp_id.state")
    qty = fields.Float("Quantity")
    amount = fields.Float(
        "DP per Unit", compute="_compute_all", store=True, readonly=True
    )
    subtotal = fields.Float("DP Subtotal")
    amount_tax = fields.Float("DP Tax")
    total = fields.Float("DP Total", compute="_compute_all", store=True)

    @api.depends("order_line_id", "qty", "subtotal", "amount_tax", "pdp_id.value")
    def _compute_all(self):
        for r in self:
            r.amount = r.subtotal / r.qty if r.qty else 0
            r.total = r.subtotal + r.amount_tax
