# Copyright (C) 2023 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLineTag(models.Model):
    _name = "sale.order.line.tag"
    _description = "Sales Order Line Tag Model"

    name = fields.Char(required=True)
