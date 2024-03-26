from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_delivered_untaxed = fields.Monetary(
        string="Delivered Untaxed Amount",
        store=True,
        readonly=True,
        compute="_compute_amount_delivered_all",
    )
    amount_delivered_tax = fields.Monetary(
        string="Delivered Taxes",
        store=True,
        readonly=True,
        compute="_compute_amount_delivered_all",
    )
    amount_delivered_total = fields.Monetary(
        string="Delivered Total",
        store=True,
        readonly=True,
        compute="_compute_amount_delivered_all",
    )

    amount_undelivered_untaxed = fields.Monetary(
        string="Undelivered Untaxed Amount",
        readonly=True,
        compute="_compute_amount_undelivered_all",
    )
    amount_undelivered_tax = fields.Monetary(
        string="Undelivered Taxes",
        readonly=True,
        compute="_compute_amount_undelivered_all",
    )
    amount_undelivered_total = fields.Monetary(
        string="Undelivered Total",
        readonly=True,
        compute="_compute_amount_undelivered_all",
    )

    display_delivered_value = fields.Boolean(
        string="Technical field specifying whether to display delivered value",
        readonly=True,
        compute="_compute_display_delivered_value",
    )

    @api.depends("order_line.price_delivered_total")
    def _compute_amount_delivered_all(self):
        """
        Compute the total delivered amounts of the SO.
        """
        for order in self:
            amount_delivered_untaxed = amount_delivered_tax = 0.0
            for line in order.order_line:
                amount_delivered_untaxed += line.price_delivered_subtotal
                amount_delivered_tax += line.price_delivered_tax

            order.update(
                {
                    "amount_delivered_untaxed": amount_delivered_untaxed,
                    "amount_delivered_tax": amount_delivered_tax,
                    "amount_delivered_total": amount_delivered_untaxed
                    + amount_delivered_tax,
                }
            )

    @api.depends("amount_delivered_total", "amount_total")
    def _compute_amount_undelivered_all(self):
        """
        Compute the total undelivered amounts of the SO.
        """
        for order in self:
            order.update(
                {
                    "amount_undelivered_untaxed": order.amount_untaxed
                    - order.amount_delivered_untaxed,
                    "amount_undelivered_tax": order.amount_tax
                    - order.amount_delivered_tax,
                    "amount_undelivered_total": order.amount_total
                    - order.amount_delivered_total,
                }
            )

    @api.depends("state", "order_line.qty_delivered")
    def _compute_display_delivered_value(self):
        for order in self:
            order.display_delivered_value = order.state in ["sale", "done"] and any(
                order.order_line.mapped("qty_delivered")
            )


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_delivered_subtotal = fields.Monetary(
        compute="_compute_amount_delivered",
        string="Subtotal delivered",
        readonly=True,
        store=True,
    )

    price_delivered_tax = fields.Monetary(
        compute="_compute_amount_delivered",
        string="Tax delivered",
        readonly=True,
        store=True,
    )

    price_delivered_total = fields.Monetary(
        compute="_compute_amount_delivered",
        string="Total delivered",
        readonly=True,
        store=True,
    )

    @api.depends("qty_delivered", "discount", "price_unit", "tax_id")
    def _compute_amount_delivered(self):
        """
        Compute the delivered amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(
                price,
                line.order_id.currency_id,
                line.qty_delivered,
                product=line.product_id,
                partner=line.order_id.partner_shipping_id,
            )
            line.update(
                {
                    "price_delivered_tax": sum(
                        t.get("amount", 0.0) for t in taxes.get("taxes", [])
                    ),
                    "price_delivered_total": taxes["total_included"],
                    "price_delivered_subtotal": taxes["total_excluded"],
                }
            )
