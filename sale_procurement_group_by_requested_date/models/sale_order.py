# -*- coding: utf-8 -*-
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
        req_datetime = fields.Datetime.from_string(line.requested_date)
        req_date = fields.Date.to_string(req_datetime)
        if line._get_procurement_group_key()[0] == 12:
            if line.requested_date:
                vals['name'] = '/'.join([vals['name'], req_date])
        return vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        values = super(SaleOrderLine, self).\
            _prepare_order_line_procurement(group_id=group_id)
        if self.requested_date:
            req_datetime = fields.Datetime.from_string(self.requested_date)
            req_date = fields.Date.to_string(req_datetime)
            values['date_planned'] = req_date
        return values

    @api.multi
    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups. The higher the priority number is the more
        preference the criteria has. E.g. sale_sourced_by_line has 10 priority,
        that is less priority than the requested date.
        """
        priority = 12
        key = super(SaleOrderLine, self)._get_procurement_group_key()
        # Check priority
        if key[0] >= priority:
            return key
        req_datetime = fields.Datetime.from_string(self.requested_date)
        req_date = fields.Date.to_string(req_datetime)
        if req_date:
            return (priority, str(req_date))
        return (priority, key)
