# © 2021 Akretion (Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    business_provider_id = fields.Many2one(comodel_name="res.partner")
