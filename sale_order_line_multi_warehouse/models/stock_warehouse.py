# Copyright 2024 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    alternative_warehouse_ids = fields.Many2many(
        string="Alternative Warehouses",
        comodel_name="stock.warehouse",
        domain="[('id', '!=', id)]",
        relation="alternative_warehouse",
        column1="warehouse_id",
        column2="alternative_warehouse_id",
    )
