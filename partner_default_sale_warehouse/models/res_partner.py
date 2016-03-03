# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L. <contact@eficent.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_warehouse_id = fields.Many2one('stock.warehouse',
                                        'Delivery Warehouse',
                                        help="Default warehouse proposed in "
                                             "sales orders.")
