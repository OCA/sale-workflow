# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


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
        self.has_allowed_products = False
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
                    self.allowed_product_ids += self.env["product.product"].search(
                        ir_filter._get_eval_domain()
                    )
            if self.allowed_product_ids:
                self.has_allowed_products = True

    @api.onchange("partner_id", "partner_shipping_id", "partner_invoice_id")
    def _onchange_partner_id(self):
        """
        Check if all the products in the order lines
        contains products that are allowed for the partner
        """
        for order in self:
            if order.has_allowed_products:
                product_ids = order.order_line.mapped("product_id")
                products_set = set(product_ids.ids)
                allowed_products_set = set(order.allowed_product_ids.ids)
                if not products_set <= allowed_products_set:
                    products_not_allowed_set = products_set - allowed_products_set
                    raise UserError(
                        _(
                            "This SO contains one or more products "
                            "that are not allowed for partner %s:\n- %s"
                        )
                        % (
                            order.partner_id.name,
                            "\n- ".join(
                                self.env["product.product"]
                                .browse(products_not_allowed_set)
                                .mapped("name")
                            ),
                        )
                    )
