# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2024 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.exceptions import ValidationError


class SaleOrderLinePriceHistoryline(models.TransientModel):
    _name = "sale.order.line.price.history.line"
    _description = "Sale order line price history line"
    _order = "sale_order_date_order desc"

    history_id = fields.Many2one(
        comodel_name="sale.order.line.price.history",
    )
    target_sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        related="history_id.sale_order_line_id",
    )
    history_sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="history sale order line",
    )
    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
    )
    order_id = fields.Many2one(
        related="sale_order_line_id.order_id",
    )
    order_state = fields.Selection(
        related="order_id.state",
    )
    partner_id = fields.Many2one(
        related="sale_order_line_id.order_partner_id",
    )
    sale_order_date_order = fields.Datetime(
        related="sale_order_line_id.order_id.date_order",
    )
    product_uom_qty = fields.Float(
        related="sale_order_line_id.product_uom_qty",
    )
    price_unit = fields.Float(
        related="sale_order_line_id.price_unit",
    )
    discount = fields.Float(
        related="sale_order_line_id.discount",
    )

    def _prepare_set_price_history_vals(self):
        """Hook method to prepare the values to update the
        sales order line in context.

        This method is invoke by action_set_price method in this model.
        """
        self.ensure_one()
        return {"price_unit": self.price_unit, "discount": self.discount}

    def action_set_price(self):
        if self.history_sale_order_line_id and self.sale_order_line_id:
            self.history_sale_order_line_id.write(
                self._prepare_set_price_history_vals()
            )
        else:
            raise ValidationError(
                self.env._("Not found historical sale order line for this action!")
            )
