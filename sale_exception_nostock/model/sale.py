# -*- coding: utf-8 -*-
#
#
#    Author: Nicolas Bessi, Leonardo Pistone
#    Copyright 2013, 2014 Camptocamp SA
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
import datetime
from openerp import models, fields, api
from openerp.tools.translate import _


class SaleOrderLine(models.Model):

    """Adds two exception functions to be called by the sale_exceptions module.

    The first one will ensure that an order line can be delivered on the
    delivery date, if the related product is in MTS. Validation is done by
    using the shop related to the sales order line location and using the line
    delay.
    The second one will raise a sales exception if the current SO will break an
    order already placed in future

    """

    _inherit = "sale.order.line"

    @api.one
    def _compute_line_delivery_date(self):
        date_order = self.order_id.date_order
        date_order = fields.Date.from_string(date_order)
        # delay is a float, that is perfectly supported by timedelta
        return date_order + datetime.timedelta(days=self.delay)

    def _find_parent_locations(self):
        location = self.order_id.partner_shipping_id.property_stock_customer

        res = [location.id]
        while location.location_id:
            location = location.location_id
            res.append(location.id)
        return res

    @api.multi
    def _predict_rules(self):
        """Choose a rule without a procurement.

        This imitates what will be done when the order is validated, with the
        difference that here we do not have a procurement yet.

        """
        Rule = self.env['procurement.rule']
        Warehouse = self.env['stock.warehouse']

        order = self.order_id
        procurement_data = order._prepare_order_line_procurement(order, self)
        # normally this is the order's warehouse, but modules like
        # sale_sourced_by_line change this behaviour

        warehouse = Warehouse.browse(procurement_data['warehouse_id'])

        domain = [('location_id', 'in', self._find_parent_locations())]
        warehouse_route_ids = []
        if warehouse:
            domain += [
                '|',
                ('warehouse_id', '=', warehouse.id),
                ('warehouse_id', '=', False)
            ]
            warehouse_route_ids = [x.id for x in warehouse.route_ids]

        product_route_ids = [
            x.id
            for x in self.product_id.route_ids +
            self.product_id.categ_id.total_route_ids]
        procurement_route_ids = [x.id for x in self.route_id]
        res = Rule.search(
            domain + [('route_id', 'in', procurement_route_ids)],
            order='route_sequence, sequence'
        )

        if not res:
            res = Rule.search(
                domain + [('route_id', 'in', product_route_ids)],
                order='route_sequence, sequence'
            )
            if not res:
                res = warehouse_route_ids and Rule.search(
                    domain + [('route_id', 'in', warehouse_route_ids)],
                    order='route_sequence, sequence'
                ) or []
                if not res:
                    res = Rule.search(domain + [('route_id', '=', False)],
                                      order='sequence')
        return res

    @api.multi
    def _get_line_location(self):
        """ Get the source location from the predicted rule"""

        rules = self._predict_rules()

        if rules:
            return rules[0].location_src_id
        return False

    @api.multi
    def _is_make_to_stock(self):
        """Predict whether a make to stock rule will be chosen"""
        return self._predict_procure_method() == 'make_to_stock'

    @api.multi
    def _predict_procure_method(self):
        """Predict the procurement method that will be chosen"""
        rules = self._predict_rules()
        return rules[0].procure_method

    @api.multi
    def _should_skip_stock_checks(self):
        self.ensure_one()

        if (
            self.product_id and
            self.product_id.type == 'product' and
            self._is_make_to_stock() and
            self._get_line_location() and
            self._get_line_location().usage == 'internal'
        ):
            return False
        else:
            return True

    @api.multi
    def can_command_at_delivery_date(self):
        """Predicate that checks whether a SO line can be delivered at delivery
        date.

        The delivery date is computed using date of the order + line delay.
        The source location is predicted with a logic similar to the one that
        will be used for real.

        :return: True if line can be delivered on time

        """
        self.ensure_one()
        if self._should_skip_stock_checks():
            return True
        delivery_date = self._compute_line_delivery_date()[0]
        delivery_date = fields.Datetime.to_string(delivery_date)
        location = self._get_line_location()

        assert location, _("No rules specifies a location"
                           " for this sale order line")
        ctx = {
            'to_date': delivery_date,
            'compute_child': True,
            'location': location.id,
            }

        try:
            ctx['owner_id'] = self.stock_owner_id.id
        except AttributeError:
            # module sale_owner_stock_sourcing not installed, fine
            pass

        # Virtual qty is made on all childs of chosen location
        prod_for_virtual_qty = (self.product_id
                                .with_context(ctx)
                                .virtual_available)
        if prod_for_virtual_qty < self.product_uom_qty:
            return False
        return True

    @api.model
    def _get_states(self):
        return ('waiting', 'confirmed', 'assigned')

    @api.model
    def _get_affected_dates(self, location_id, product_id, delivery_date):
        """Determine future dates where virtual stock has to be checked.

        It will only look for stock move that pass by location_id.
        If your stock location have children or you have configured automated
        stock action
        they must pass by the location related to SO line, else the will be
        ignored

        :param location_id: location id to be checked
        :param product_id: product id te be checked

        :return: list of dates to be checked

        """
        cr = self._cr
        sql = ("SELECT date FROM stock_move"
               "  WHERE state IN %s"
               "   AND date > %s"
               "   AND product_id = %s"
               "   AND location_id = %s")
        cr.execute(sql, (self._get_states(),
                         delivery_date,
                         product_id,
                         location_id))
        return (row[0] for row in cr.fetchall())

    @api.multi
    def future_orders_are_affected(self):
        """Predicate function that is a naive workaround for the lack of stock
        reservation.

        This can be a performance killer, you should not use it
        if you have constantly a lot of running Orders

        :return: True if future order are affected by current command line
        """
        self.ensure_one()
        if self._should_skip_stock_checks():
            return False
        delivery_date = self._compute_line_delivery_date()[0]
        delivery_date = fields.Datetime.to_string(delivery_date)
        location = self._get_line_location()
        assert location, _("No rules specifies a location"
                           " for this sale order line")

        ctx = {
            'compute_child': True,
            'location_id': location.id,
            }

        try:
            ctx['owner_id'] = self.stock_owner_id.id
        except AttributeError:
            # module sale_owner_stock_sourcing not installed, fine
            pass

        # Virtual qty is made on all childs of chosen location
        dates = self._get_affected_dates(location.id, self.product_id.id,
                                         delivery_date)
        for aff_date in dates:
            ctx['to_date'] = aff_date
            prod_for_virtual_qty = (self.product_id
                                    .with_context(ctx)
                                    .virtual_available)
            if prod_for_virtual_qty < self.product_uom_qty:
                return True
        return False
