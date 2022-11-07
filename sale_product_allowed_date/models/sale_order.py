# Copyright 2021 - 2022 Camptocamp SA
# @author: Damien Crier <damien.crier@camptocamp.com>
# @author: Julien Coux <julien.coux@camptocamp.com>
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commitment_date_end = fields.Datetime()

    def _get_allowed_product_ids(self, date):
        self.ensure_one()
        product_ids = []
        if date:
            config_lines = self.mapped("product_allowed_config_ids.line_ids").filtered(
                lambda l: l.is_sale_ok(date)
            )
            for config_line in config_lines:
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
            if sale.commitment_date:
                product_ids = sale._get_allowed_product_ids(sale.commitment_date)
                value = [(6, 0, product_ids)]
            sale.allowed_product_ids = value

    @api.onchange("commitment_date")
    def _onchange_commitment_date(self):
        res = super()._onchange_commitment_date()
        if self.commitment_date:
            self.commitment_date_end = self.commitment_date
        return res
