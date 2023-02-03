# Copyright 2020 Tecnativa - Carlos Roca
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json

from odoo import api, fields, models
from odoo.osv.expression import AND


class SaleOrder(models.Model):
    _inherit = "sale.order"

    has_allowed_products = fields.Boolean(compute="_compute_allowed_product_domain")
    allowed_product_domain = fields.Char(compute="_compute_allowed_product_domain")

    @api.depends("partner_id", "partner_shipping_id", "partner_invoice_id")
    def _compute_allowed_product_domain(self):
        partner_field = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("sale_order_product_assortment.partner_field", "partner_id")
        )
        filters_partner_domain = self.env["ir.filters"].search(
            [("is_assortment", "=", True)]
        )
        for rec in self:
            rec.allowed_product_domain = json.dumps([(1, "=", 1)])
            rec.has_allowed_products = False

            domains = []
            for ir_filter in filters_partner_domain.filtered(
                lambda f, partner=rec[partner_field]: partner.id
                in f.all_partner_ids.ids
            ):
                domains.append(ir_filter._get_eval_domain())
            if domains:
                rec.has_allowed_products = True
                rec.allowed_product_domain = json.dumps(AND(domains))
