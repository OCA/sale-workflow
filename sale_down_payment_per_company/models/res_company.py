# Copyright (C) 2020 - Today: GRAP (http://www.grap.coop)
# @author Quentin DUPONT (quentin.dupont@grap.coop)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    down_payment_product_id = fields.Many2one(
        string="Default Down Payment Product", comodel_name="product.product",
        help='Default product used for payment advances',
        domain="['&', ('company_id', '=', id), ('type', '=', 'service')]",
    )
