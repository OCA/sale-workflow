# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_use_product_description_per_so_line = fields.Boolean(
        _("Show only the product description on the sales order lines"),
        implied_group="sale_order_line_description."
        "group_use_product_description_per_so_line",
        help=_("Allows you to use only product description on the sales order lines.")
    )
