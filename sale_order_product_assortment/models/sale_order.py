# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    allowed_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Allowed Products",
        compute="_compute_product_assortment_ids",
    )
    has_allowed_products = fields.Boolean(compute="_compute_product_assortment_ids")

    @api.depends("partner_id", "partner_shipping_id", "partner_invoice_id")
    def _compute_product_assortment_ids(self):
        # If we don't initialize the fields we get an error with NewId
        IrFilters = self.env["ir.filters"]
        self.allowed_product_ids = self.env["product.product"]
        allowed_products = self.env["product.product"]
        not_allowed_products = self.env["product.product"]
        self.has_allowed_products = False
        partner_has_filter = False
        partner_field = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_product_assortment.partner_field", "partner_id")
        )
        if self[partner_field]:
            filters = IrFilters.browse()
            filters_partner_domain = self.env["ir.filters"].search(
                [("is_assortment", "=", True)]
            )
            for ir_filter in filters_partner_domain:
                if self[partner_field] & ir_filter.all_partner_ids:
                    filters |= ir_filter
                    allowed_products += self.env["product.product"].search(
                        ir_filter._get_eval_domain()
                    )
                    if ir_filter.apply_black_list_product_domain:
                        not_allowed_products += self.env["product.product"].search(
                            ir_filter._get_eval_black_list_domain()
                        )
                    partner_has_filter = True
            self.allowed_product_ids = allowed_products - not_allowed_products
            if self.allowed_product_ids or partner_has_filter:
                self.has_allowed_products = True
