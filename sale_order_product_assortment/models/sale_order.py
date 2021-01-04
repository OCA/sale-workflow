# Copyright 2020 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    whitelist_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Whitelisted Products",
        compute="_compute_product_assortment_ids",
    )
    blacklist_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Blacklisted Products",
        compute="_compute_product_assortment_ids",
    )
    has_whitelist = fields.Boolean(compute="_compute_product_assortment_ids")
    has_blacklist = fields.Boolean(compute="_compute_product_assortment_ids")

    @api.depends("partner_id")
    def _compute_product_assortment_ids(self):
        # If we don't initialize the fields we get an error with NewId
        self.whitelist_product_ids = self.env["product.product"]
        self.blacklist_product_ids = self.env["product.product"]
        self.has_whitelist = False
        self.has_blacklist = False
        if self.partner_id:
            filters = self.env["ir.filters"].search(
                [
                    (
                        "partner_ids",
                        "in",
                        (self.partner_id + self.partner_id.commercial_partner_id).ids,
                    ),
                ]
            )
            whitelist_products = set()
            blacklist_products = set()
            for fil in filters:
                whitelist_products = whitelist_products.union(
                    fil.whitelist_product_ids.ids
                )
                blacklist_products = blacklist_products.union(
                    fil.blacklist_product_ids.ids
                )
            if whitelist_products:
                self.has_whitelist = True
            if blacklist_products:
                self.has_blacklist = True
            self.whitelist_product_ids = self.whitelist_product_ids.browse(
                whitelist_products
            )
            self.blacklist_product_ids = self.blacklist_product_ids.browse(
                blacklist_products
            )
