# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        # for compatibility with sale_quotation_sourcing
        vals = super(SaleOrder, self)._prepare_procurement_group_by_line(line)
        req_datetime = fields.Datetime.from_string(line.requested_date)
        req_date = fields.Date.to_string(req_datetime)
        if line._get_procurement_group_key()[0] == 14:
            if line.requested_date and line.warehouse_id:
                vals['name'] = '/'.join([vals['name'], line.warehouse_id.name,
                                         req_date])
        return vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups. The higher the priority number is the more
        preference the criteria has. E.g. sale_sourced_by_line has 10 priority,
        that is less priority than the requested date.
        """
        priority = 14
        key = super(SaleOrderLine, self)._get_procurement_group_key()
        # Check priority
        if key[0] >= priority:
            return key
        req_datetime = fields.Datetime.from_string(self.requested_date)
        req_date = fields.Date.to_string(req_datetime)
        if self.warehouse_id and not req_date:
            return (priority, self.warehouse_id.id)
        if req_date and not self.warehouse_id:
            return (priority, str(req_date))
        if self.warehouse_id and req_date:
            key = '/'.join([str(self.warehouse_id.id), req_date])
        return (priority, key)
