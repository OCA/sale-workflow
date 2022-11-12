# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_signature = fields.Binary(string="Customer acceptance", attachment=True)
