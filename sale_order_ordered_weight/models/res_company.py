# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    display_line_weight_on_sale_report = fields.Boolean(default=False)

    display_order_weight_on_sale_report = fields.Boolean(default=True)
