from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount1 = fields.Float(
        compute="_compute_discount1", store=True, readonly=False, precompute=True
    )
    discount2 = fields.Float(
        compute="_compute_discount1", store=True, readonly=False, precompute=True
    )
    discount3 = fields.Float(
        compute="_compute_discount1", store=True, readonly=False, precompute=True
    )
    _set_general_discount_in_compute_discount = False

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_discount1(self):
        res = super()._compute_discount1()
        pricelist_discount = self._get_discount_field_position("pricelist_discount")
        general_discount = self._get_discount_field_position("general_discount")
        for line in self:
            if pricelist_discount:
                line.update({pricelist_discount: line._get_pricelist_discount()})
            if general_discount:
                line.update({general_discount: line.order_id.general_discount})
        return res

    def _get_pricelist_discount(self):
        if not self.product_id or self.display_type:
            return 0.0
        if not (
            self.order_id.pricelist_id
            and self.order_id.pricelist_id.discount_policy == "without_discount"
        ):
            return 0.0
        if not self.pricelist_item_id:
            return 0.0
        self = self.with_company(self.company_id)
        pricelist_price = self._get_pricelist_price()
        base_price = self._get_pricelist_price_before_discount()
        if base_price != 0:
            discount = (base_price - pricelist_price) / base_price * 100
            if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                return discount
        return 0.0

    def _get_discount_field_position(self, field_name):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "sale_order_general_discount_triple.{}".format(field_name), "discount1"
            )
        )
