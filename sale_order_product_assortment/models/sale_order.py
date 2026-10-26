# Copyright 2020 Tecnativa - Carlos Roca
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.fields import Domain


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
        partner_field = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_product_assortment.partner_field", "partner_id")
        )
        if partner_field not in self._fields:
            partner_field = "partner_id"
        for order in self:
            order.allowed_product_ids = False
            order.has_allowed_products = False
            partner = order[partner_field]
            product_domain = []
            if partner:
                assortments = partner.applied_assortment_ids.filtered(
                    lambda f: f.model_id == "product.product"
                )
                for ir_filter in assortments:
                    product_domain = Domain.AND(
                        [product_domain, ir_filter._get_eval_domain()]
                    )
                if product_domain:
                    order.allowed_product_ids = self.env["product.product"].search(
                        product_domain
                    )
                    order.has_allowed_products = True

    def _get_product_catalog_domain(self):
        domain = super()._get_product_catalog_domain()
        if self.has_allowed_products:
            domain = Domain.AND([domain, [("id", "in", self.allowed_product_ids.ids)]])
        return domain
