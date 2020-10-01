# Copyright Komit <http://komit-consulting.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    check_stock_on_sale = fields.Selection(
        selection=[('skip', 'Skip the check'),
                   ('not_skip', 'Do not skip the check'),
                   ('defer', 'Defer to the setting on the category')],
        company_dependent=True,
        help="'Skip the check' will disable warning 'Not enough inventory' "
             "when there isn't enough product in stock!\n"
             "'Do not skip the check' won't disable warning 'Not enough "
             "inventory' when there isn't enough product in stock!\n"
             "'Defer to the setting on the category' will use the "
             "setting from the Internal Category",
        string="Check Stock on Sale",
        default="defer",
    )

    @api.multi
    def _check_stock_on_sale(self):
        self.ensure_one()
        if self.check_stock_on_sale == 'skip':
            return False
        elif self.check_stock_on_sale == 'defer':
            return self.categ_id.check_stock_on_sale
        else:
            return True
