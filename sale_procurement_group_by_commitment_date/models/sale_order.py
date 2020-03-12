# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        vals = super(SaleOrder, self)._prepare_procurement_group_by_line(line)
        # for compatibility with sale_quotation_sourcing
        com_datetime = line.commitment_date
        com_date = fields.Date.to_string(com_datetime)
        if line._get_procurement_group_key()[0] == 12:
            if line.commitment_date:
                vals['name'] = '/'.join([vals['name'], com_date])
        return vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        values = super(SaleOrderLine, self).\
            _prepare_order_line_procurement(group_id=group_id)
        if self.commitment_date:
            com_datetime = self.commitment_date
            com_date = fields.Date.to_string(com_datetime)
            values['date_planned'] = com_date
        return values

    @api.multi
    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups. The higher the priority number is the more
        preference the criteria has.
        """
        priority = 12
        key = super(SaleOrderLine, self)._get_procurement_group_key()
        # Check priority
        if key[0] >= priority:
            return key
        com_datetime = self.commitment_date
        com_date = fields.Date.to_string(com_datetime)
        if com_date:
            return (priority, com_date)
        return (priority, key)
