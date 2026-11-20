# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrderLinePriceHistory(models.TransientModel):
    _name = "sale.order.line.price.history"
    _description = "Sale order line price history"

    @api.model
    def _default_partner_id(self):
        line_id = self.env.context.get("active_id")
        return self.env["sale.order.line"].browse(line_id).order_partner_id.id

    @api.model
    def _default_product_id(self):
        line_id = self.env.context.get("active_id")
        return self.env["sale.order.line"].browse(line_id).product_id.id

    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Sale order line",
        default=lambda self: self.env.context.get("active_id"),
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        default=lambda self: self._default_product_id(),
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        default=lambda self: self._default_partner_id(),
    )
    line_ids = fields.One2many(
        comodel_name="sale.order.line.price.history.line",
        inverse_name="history_id",
        string="History lines",
        readonly=True,
    )
    include_quotations = fields.Boolean(
        help="Include quotations lines in the sale history",
    )
    include_commercial_partner = fields.Boolean(
        string="Include commercial entity",
        default=True,
        help="Include commercial entity and its contacts in the sale history",
    )

    @api.onchange("partner_id", "include_quotations", "include_commercial_partner")
    def _onchange_partner_id(self):
        self.line_ids = False
        states = ["sale", "done"]
        if self.include_quotations:
            states += ["draft", "sent"]
        domain = [
            ("product_id", "=", self.product_id.id),
            ("state", "in", states),
        ]
        if self.partner_id:
            if self.include_commercial_partner:
                domain += [
                    (
                        "order_partner_id",
                        "child_of",
                        self.partner_id.commercial_partner_id.ids,
                    )
                ]
            else:
                domain += [("order_partner_id", "child_of", self.partner_id.ids)]

        vals = []
        sol_limit = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_int("sale_order_line_price_history.order_line_limit", default=20)
        )
        order_lines = self.env["sale.order.line"].search(domain, limit=sol_limit)
        order_lines -= self.sale_order_line_id
        for order_line in order_lines:
            vals.append(
                (
                    0,
                    False,
                    {
                        "sale_order_line_id": order_line.id,
                        "history_sale_order_line_id": self.sale_order_line_id.id,
                        "history_id": self.id,
                    },
                )
            )
        self.line_ids = vals
