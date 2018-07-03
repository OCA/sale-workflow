# coding: utf-8
#  @author Sébastien BEAU <sebastien.beau@akretion.com>
#  @author EBII MonsieurB <monsieurb@saaslys.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    generator_id = fields.Many2one(
        comodel_name='sale.generator', string="Generator")
    is_template = fields.Boolean()
