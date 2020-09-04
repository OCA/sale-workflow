# Copyright 2020 Akretion Renato Lima <renato.lima@akretion.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    bom_id = fields.Many2one(
        comodel_name='mrp.bom',
        string='BOM',
        domain="[('product_tmpl_id.product_variant_ids', '=', product_id),"
               "'|', ('product_id', '=', product_id), "
               "('product_id', '=', False)]",
    )
