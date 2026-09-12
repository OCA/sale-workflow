from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount1 = fields.Float(compute="_compute_discount1", store=True, readonly=False)
    discount2 = fields.Float(
        compute="_compute_discount2", store=True, readonly=False, precompute=True
    )
    discount3 = fields.Float(
        compute="_compute_discount3", store=True, readonly=False, precompute=True
    )

    @api.depends(
        "product_id",
        "product_uom_id",
        "product_uom_qty",
        "order_id.general_discount",
        "display_type",
    )
    def _compute_discount1(self):
        pricelist_discount = self._get_discount_field_position("pricelist_discount")
        general_discount = self._get_discount_field_position("general_discount")
        for line in self:
            if line._check_is_reward_line() or line.display_type:
                line.discount1 = 0.0
                continue
            val = 0.0
            if pricelist_discount == "discount1":
                val = line._get_pricelist_discount()
            elif (
                general_discount == "discount1"
                and line.product_id
                and not line.product_id.bypass_general_discount
            ):
                val = line.order_id.general_discount
            line.discount1 = val

    @api.depends(
        "product_id",
        "product_uom_id",
        "product_uom_qty",
        "order_id.general_discount",
        "display_type",
    )
    def _compute_discount2(self):
        pricelist_discount = self._get_discount_field_position("pricelist_discount")
        general_discount = self._get_discount_field_position("general_discount")
        for line in self:
            if line._check_is_reward_line() or line.display_type:
                line.discount2 = 0.0
                continue
            val = 0.0
            if pricelist_discount == "discount2":
                val = line._get_pricelist_discount()
            elif (
                general_discount == "discount2"
                and line.product_id
                and not line.product_id.bypass_general_discount
            ):
                val = line.order_id.general_discount
            line.discount2 = val

    @api.depends(
        "product_id",
        "product_uom_id",
        "product_uom_qty",
        "order_id.general_discount",
        "display_type",
    )
    def _compute_discount3(self):
        pricelist_discount = self._get_discount_field_position("pricelist_discount")
        general_discount = self._get_discount_field_position("general_discount")
        for line in self:
            if line._check_is_reward_line() or line.display_type:
                line.discount3 = 0.0
                continue
            val = 0.0
            if pricelist_discount == "discount3":
                val = line._get_pricelist_discount()
            elif (
                general_discount == "discount3"
                and line.product_id
                and not line.product_id.bypass_general_discount
            ):
                val = line.order_id.general_discount
            line.discount3 = val

    def _check_is_reward_line(self):
        self.ensure_one()
        if "is_reward_line" not in self._fields:
            return False
        return self.is_reward_line

    def _get_pricelist_discount(self):
        if not self.product_id or self.display_type:
            return 0.0
        if not (self.pricelist_item_id and self.pricelist_item_id._show_discount()):
            return 0.0
        self = self.with_company(self.company_id)
        pricelist_price = self._get_pricelist_price()
        base_price = self._get_pricelist_price_before_discount()
        if base_price != 0:
            discount = ((base_price - pricelist_price) / base_price) * 100
            if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                return discount
        return 0.0

    def _get_discount_field_position(self, field_name):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(f"sale_order_general_discount_triple.{field_name}", "discount1")
        )
