# Copyright 2021 - 2022 Camptocamp SA
# @author: Damien Crier <damien.crier@camptocamp.com>
# @author: Julien Coux <julien.coux@camptocamp.com>
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    product_allowed_config_ids = fields.Many2many(
        string="Product seasonal configuration",
        comodel_name="product.allowed.list",
        default=lambda self: self._default_product_allowed_config_id(),
    )
    allowed_product_ids = fields.Many2many(
        string="Allowed products",
        comodel_name="product.product",
        column1="sale_id",
        column2="product_id",
        compute="_compute_allowed_product_ids",
    )

    def _default_product_allowed_config_id(self):
        return self.env.user.company_id.default_product_allowed_config_id.ids

    def _get_allowed_product_ids(self):
        self.ensure_one()
        product_ids = []
        for config_line in self.mapped("product_allowed_config_ids.line_ids"):
            if config_line.product_id:
                product_ids.append(config_line.product_id.id)
            else:
                product_ids.extend(
                    config_line.product_template_id.product_variant_ids.ids
                )
        return product_ids

    @api.depends("commitment_date", "product_allowed_config_ids.line_ids")
    def _compute_allowed_product_ids(self):
        for sale in self:
            value = [(5, 0)]
            product_ids = sale._get_allowed_product_ids()
            value = [(6, 0, product_ids)]
            sale.allowed_product_ids = value

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        if self.partner_id:
            self._update_product_allowed_config(self.partner_id)
        return res

    def _update_product_allowed_config(self, partner):
        commercial_partner = partner.commercial_partner_id
        # config
        config = (
            partner.product_allowed_list_ids
            or commercial_partner.product_allowed_list_ids
        )
        self.product_allowed_config_ids = (
            config.ids or self._default_product_allowed_config_id()
        )
