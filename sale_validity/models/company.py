# -*- coding: utf-8 -*-
# © 2014-2017 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    default_sale_order_validity_days = fields.Integer(
        string="Default Validity of Sale Orders",
        help="By default, the validity date of sale orders will be "
             "the date of the sale order plus the number of days defined "
             "in this field. If the value of this field is 0, the sale orders "
             "will not have a validity date by default.")

    _sql_constraints = [
        ('sale_order_validity_days_positive',
         'CHECK (default_sale_order_validity_days >= 0)',
         "The value of the field 'Default Validity Duration of Sale Orders' "
         "must be positive or 0."),
    ]
