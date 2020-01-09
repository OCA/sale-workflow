# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    invoice_group_method_id = fields.Many2one(
        string='Default Invoice Group Method',
        comodel_name='sale.invoice.group.method'
    )

    def _get_invoice_group_method_id(self):
        if self.invoice_group_method_id:
            return self.invoice_group_method_id
        else:
            return self.commercial_partner_id.invoice_group_method_id
