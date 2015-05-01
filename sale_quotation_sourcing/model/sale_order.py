# -*- coding: utf-8 -*-
#
#    Author: Alexandre Fayolle, Leonardo Pistone, Yannick Vaucher
#    Copyright 2014-2015 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_button_confirm(self):
        """before triggering the workflow, if some lines need sourcing, run the
        sourcing wizard, otherwise, propagate the call and do the confirmation
        of the SO.
        """
        self.ensure_one()
        order = self[0]
        lines_to_source = []
        for line in order.order_line:
            if line.needs_sourcing():
                lines_to_source.append(line)
        if lines_to_source:
            wizard = self._create_sourcing_wizard(lines_to_source)
            return {'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_model': 'sale.order.sourcing',
                    'res_id': wizard.id,
                    'target': 'new',
                    }
        else:
            return super(SaleOrder, self).action_button_confirm()

    @api.model
    def _prepare_procurement_group_by_line(self, line):
        vals = super(SaleOrder, self)._prepare_procurement_group_by_line(line)
        # for compatibility with sale_quotation_sourcing
        if line._get_procurement_group_key()[0] == 16:
            if line.sourced_by:
                vals['name'] += '/' + line.sourced_by.order_id.name
        return vals

    @api.model
    def _create_sourcing_wizard(self, lines_to_source):
        line_values = []
        for line in lines_to_source:
            line_values.append((0, 0, {'so_line_id': line.id}))
        values = {'sale_id': self[0].id,
                  'line_ids': line_values,
                  }
        return self.env['sale.order.sourcing'].create(values)

    @api.multi
    def has_consistent_routes(self):
        self.ensure_one()
        return all((line.has_consistent_route() for line in self.order_line))


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    manually_sourced = fields.Boolean('Manually Sourced')
    sourced_by = fields.Many2one(
        'purchase.order.line', copy=False,
        domain="[('product_id', '=', product_id),"
               " ('order_id.state', 'in', ['draft', 'confirmed'])]")

    @api.multi
    def has_consistent_route(self):
        self.ensure_one()
        if self.route_id and self.sourced_by:
            selected_route = self.route_id
            self.set_route_form_so()
            return selected_route == self.route_id
        else:
            return True

    @api.multi
    def needs_sourcing(self):
        return any(line.manually_sourced and not line.sourced_by
                   for line in self)

    @api.model
    def _get_po_location_usage(self, purchase_order_line):
        """Retrieve the destination location usage of a PO
        from a PO line

        :param purchase_order_line: record of `purchase.order.line` Model
        :type purchase_order_line: :py:class:`openerp.models.Model`
        :return: PO location usage
        :rtype: str

        """
        return purchase_order_line.order_id.location_id.usage

    @api.model
    def _find_route_from_usage(self, usage):
        """Return the routes to assing on SO lines
        based on a location usage.

        If no match return None.

        At the moment this method returns the standard dropshipping and MTO
        routes. This method will work in many cases, but we could improve it to
        find dropshipping-like and MTO-like routes that have been configured
        afterwards.

        See onchange_dest_address_in in the module purchase_delivery_address
        for a similar situation.

        :param usage: stock.location Model usage
        :type usage: str

        :return: a record of `stock.location.route`
        :rtype: :py:class:`openerp.models.Model` or None
        """
        if usage == 'customer':
            return self.env.ref('stock_dropshipping.route_drop_shipping')
        elif usage == 'internal':
            return self.env.ref('stock.route_warehouse0_mto')
        else:
            return None

    @api.one
    @api.onchange('sourced_by')
    @api.constrains('sourced_by')
    def set_route_form_so(self):
        """Set route on SO line based on fields sourced_by.

        Wee look for the PO related
        to current SO line by the sourced_by fields.

        If the PO has a destination location with usage
        "customer" we apply the dropshipping route to current SO line.

        If the PO has a destination location with usage
        "internal" we apply the make to order route to current SO line.

        As there is no trigger decorator that works on
        non computed fields we use constrains decorator instead.
        """
        if not self.sourced_by:
            return
        usage = self._get_po_location_usage(self.sourced_by)
        route = self._find_route_from_usage(usage)
        if route:
            self.route_id = route

    @api.multi
    def _get_procurement_group_key(self):
        """ Return a key with priority to be used to regroup lines in multiple
        procurement groups

        """
        priority = 16
        key = super(SaleOrderLine, self)._get_procurement_group_key()
        # Check priority
        if key[0] < priority:
            if self.sourced_by:
                return (priority, self.sourced_by.order_id.id)
        return key
