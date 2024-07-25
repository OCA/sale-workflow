from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    discount1 = fields.Float(compute="_compute_discount1", store=True, readonly=False)
    discount2 = fields.Float(compute="_compute_discount2", store=True, readonly=False)
    discount3 = fields.Float(compute="_compute_discount3", store=True, readonly=False)

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_discount1(self):
        pricelist_discount = self._get_discount_field_position("pricelist_discount")
        general_discount = self._get_discount_field_position("general_discount")
        if "discount1" not in [pricelist_discount, general_discount]:
            self.update({"discount1": 0.0})
            return
        for line in self:
            if pricelist_discount == "discount1":
                line.update({"discount1": line._get_pricelist_discount()})
            elif general_discount == "discount1":
                line.update({"discount1": line.order_id.general_discount})
        return

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_discount2(self):
        pricelist_discount = self._get_discount_field_position("pricelist_discount")
        general_discount = self._get_discount_field_position("general_discount")
        if "discount2" not in [pricelist_discount, general_discount]:
            self.update({"discount2": 0.0})
            return
        for line in self:
            if pricelist_discount == "discount2":
                line.update({"discount2": line._get_pricelist_discount()})
            elif general_discount == "discount2":
                line.update({"discount2": line.order_id.general_discount})

    @api.depends("product_id", "product_uom", "product_uom_qty")
    def _compute_discount3(self):
        pricelist_discount = self._get_discount_field_position("pricelist_discount")
        general_discount = self._get_discount_field_position("general_discount")
        if "discount3" not in [pricelist_discount, general_discount]:
            self.update({"discount3": 0.0})
            return
        for line in self:
            if pricelist_discount == "discount3":
                line.update({"discount3": line._get_pricelist_discount()})
            elif general_discount == "discount3":
                line.update({"discount3": line.order_id.general_discount})

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
