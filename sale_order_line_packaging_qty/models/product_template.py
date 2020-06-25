# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sell_only_by_packaging = fields.Boolean(
        string="Only sell by packaging", default=False,
    )
