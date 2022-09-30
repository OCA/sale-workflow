# Copyright 2020 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        vals = super(SaleOrder, self)._prepare_procurement_group_by_line(
            line)
        if line._get_procurement_group_key()[0] == 16 and line.dest_address_id:
            name_extension = line.dest_address_id.name or \
                line.dest_address_id.contact_address
            vals['name'] = '/'.join([vals['name'], name_extension])
        return vals
