# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_order_line_procurement(self, cr, uid, order, line,
                                        group_id=False, context=None):
        values = super(SaleOrder, self)._prepare_order_line_procurement(
            cr, uid, order, line, group_id=group_id, context=context)
        if line.requested_date:
            req_datetime = fields.Datetime.from_string(line.requested_date)
            req_date = fields.Date.to_string(req_datetime)
            values['requested_date'] = req_date
        return values

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        vals = super(SaleOrder, self)._prepare_procurement_group_by_line(line)
        # for compatibility with sale_quotation_sourcing
        req_datetime = fields.Datetime.from_string(line.requested_date)
        req_date = fields.Date.to_string(req_datetime)
        if line._get_procurement_group_key()[0] == 9:
            if line.requested_date:
                vals['name'] = '/'.join([vals['name'], line.warehouse_id.name,
                                         req_date])
        return vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups. The higher the priority number is the more
        preference the criteria has. E.g. sale_sourced_by_line has 8 priority,
        that is less priority than the requested date.
        """
        priority = 9
        key = super(SaleOrderLine, self)._get_procurement_group_key()
        # Check priority
        if key[0] >= priority:
            return key
        req_datetime = fields.Datetime.from_string(self.requested_date)
        req_date = fields.Date.to_string(req_datetime)
        key = '/'.join([str(self.warehouse_id.id), req_date])
        return (priority, key)
