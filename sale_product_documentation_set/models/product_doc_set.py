# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductDocSet(models.Model):

    _inherit = "product.doc.set"

    usage = fields.Selection(selection_add=[("sale", "Sale Order")])
