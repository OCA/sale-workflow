# Copyright 2019 Akretion
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# Copyright 2024 CorporateHub
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "sale.product.restricted.qty.mixin"]

    _sale_restricted_qty_parent_field = "categ_id"
