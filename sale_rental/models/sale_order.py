# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from openerp.tools import float_compare
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
import logging

logger = logging.getLogger(__name__)
# TODO : block if we sell a rented product already sold => state


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            for line in order.order_line:
                if line.rental_type == 'new_rental':
                    self.env['sale.rental'].create(line._prepare_rental())
                elif line.rental_type == 'rental_extension':
                    line.extension_rental_id.in_move_id.date_expected =\
                        line.end_date
                    line.extension_rental_id.in_move_id.date = line.end_date
                elif line.sell_rental_id:
                    if line.sell_rental_id.out_move_id.state != 'done':
                        raise UserError(_(
                            'Cannot sell the rental %s because it has '
                            'not been delivered')
                            % line.sell_rental_id.display_name)
                    line.sell_rental_id.in_move_id.action_cancel()
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rental = fields.Boolean(string='Rental')
    can_sell_rental = fields.Boolean(string='Can Sell from Rental')
    rental_type = fields.Selection([
        ('new_rental', 'New Rental'),
        ('rental_extension', 'Rental Extension'),
        ], 'Rental Type',
        readonly=True, states={'draft': [('readonly', False)]})
    extension_rental_id = fields.Many2one(
        'sale.rental', string='Rental to Extend')
    rental_qty = fields.Float(
        string='Rental Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Indicate the number of items that will be rented.")
    sell_rental_id = fields.Many2one(
        'sale.rental', string='Rental to Sell')

    @api.one
    @api.constrains(
        'rental_type', 'extension_rental_id', 'start_date', 'end_date',
        'rental_qty', 'product_uom_qty', 'product_id', 'must_have_dates')
    def _check_sale_line_rental(self):
        if self.rental_type == 'rental_extension':
            if not self.extension_rental_id:
                raise ValidationError(_(
                    "Missing 'Rental to Extend' on the sale order line with "
                    "rental service %s")
                    % self.product_id.name)
            if self.rental_qty != self.extension_rental_id.rental_qty:
                raise ValidationError(_(
                    "On the sale order line with rental service %s, "
                    "you are trying to extend a rental with a rental "
                    "quantity (%s) that is different from the quantity "
                    "of the original rental (%s). This is not supported.") % (
                    self.product_id.name,
                    self.rental_qty,
                    self.extension_rental_id.rental_qty))
        if self.rental_type in ('new_rental', 'rental_extension'):
            if not self.product_id.rented_product_id:
                raise ValidationError(_(
                    "On the 'new rental' sale order line with product '%s', "
                    "we should have a rental service product !") % (
                    self.product_id.name))
            if self.product_uom_qty != self.rental_qty * self.number_of_days:
                raise ValidationError(_(
                    "On the sale order line with product '%s' "
                    "the Product Quantity (%s) should be the "
                    "number of days (%s) "
                    "multiplied by the Rental Quantity (%s).") % (
                    self.product_id.name, self.product_uom_qty,
                    self.number_of_days, self.rental_qty))
            # TODO: If we confirm self.must_have_dates in a related field
            # we can remove this check
            if not self.must_have_dates:
                raise ValidationError(_(
                    "On the rental sale order line with product %s "
                    "the must have dates option should be enabled")
                    % self.product_id.name)
                # the module sale_start_end_dates checks that, when we have
                # must_have_dates, we have start + end dates
        elif self.sell_rental_id:
            if self.product_uom_qty != self.sell_rental_id.rental_qty:
                raise ValidationError(_(
                    "On the sale order line with product %s "
                    "you are trying to sell a rented product with a "
                    "quantity (%s) that is different from the rented "
                    "quantity (%s). This is not supported.") % (
                    self.product_id.name,
                    self.product_uom_qty,
                    self.sell_rental_id.rental_qty))

    @api.multi
    def _prepare_rental(self):
        self.ensure_one()
        return {'start_order_line_id': self.id}

    @api.multi
    def _get_rental_date_planned(self):
        self.ensure_one()
        return self.start_date

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        res = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id)
        if (
                self.product_id.rented_product_id and
                self.rental_type == 'new_rental'):
            res.update({
                'product_id': self.product_id.rented_product_id.id,
                'product_qty': self.rental_qty,
                'product_uom': self.product_id.rented_product_id.uom_id.id,
                'location_id':
                self.order_id.warehouse_id.rental_out_location_id.id,
                'route_ids':
                [(6, 0, [self.order_id.warehouse_id.rental_route_id.id])],
                'date_planned': self._get_rental_date_planned(),
                })
        elif self.sell_rental_id:
            res['route_ids'] = [(6, 0, [
                self.order_id.warehouse_id.sell_rented_product_route_id.id])]
        return res

    @api.onchange('product_id')
    def rental_product_id_change(self):
        res = {}
        if self.product_id:
            if self.product_id.rented_product_id:
                self.rental = True
                self.can_sell_rental = False
                self.sell_rental_id = False
                if not self.rental_type:
                    self.rental_type = 'new_rental'
                elif (
                        self.rental_type == 'new_rental' and
                        self.rental_qty and self.order_id.warehouse_id):
                    product_uom = self.product_id.rented_product_id.uom_id
                    warehouse = self.order_id.warehouse_id
                    rental_in_location = warehouse.rental_in_location_id
                    rented_product_ctx = self.with_context(
                        location=rental_in_location.id).product_id.\
                        rented_product_id
                    in_location_available_qty = rented_product_ctx.\
                        qty_available - rented_product_ctx.outgoing_qty
                    compare_qty = float_compare(
                        in_location_available_qty, self.rental_qty,
                        precision_rounding=product_uom.rounding)
                    if compare_qty == -1:
                        res['warning'] = {
                            'title': _("Not enough stock !"),
                            'message': _(
                                "You want to rent %.2f %s but you only "
                                "have %.2f %s currently available on the "
                                "stock location '%s' ! Make sure that you "
                                "get some units back in the mean time or "
                                "re-supply the stock location '%s'.") % (
                                self.rental_qty,
                                product_uom.name,
                                in_location_available_qty,
                                product_uom.name,
                                rental_in_location.name,
                                rental_in_location.name)
                            }
            elif self.product_id.rental_service_ids:
                self.can_sell_rental = True
                self.rental = False
                self.rental_type = False
                self.rental_qty = 0
                self.extension_rental_id = False
            else:
                self.rental_type = False
                self.rental = False
                self.rental_qty = 0
                self.extension_rental_id = False
                self.can_sell_rental = False
                self.sell_rental_id = False
        else:
            self.rental_type = False
            self.rental = False
            self.rental_qty = 0
            self.extension_rental_id = False
            self.can_sell_rental = False
            self.sell_rental_id = False
        return res

    @api.onchange('extension_rental_id')
    def extension_rental_id_change(self):
        if (
                self.product_id and
                self.rental_type == 'rental_extension' and
                self.extension_rental_id):
            if self.extension_rental_id.rental_product_id != self.product_id:
                raise UserError(_(
                    "The Rental Service of the Rental Extension you just "
                    "selected is '%s' and it's not the same as the "
                    "Product currently selected in this Sale Order Line.")
                    % self.extension_rental_id.rental_product_id.name)
            initial_end_date = fields.Date.from_string(
                self.extension_rental_id.end_date)
            self.start_date = initial_end_date + relativedelta(days=1)
            self.rental_qty = self.extension_rental_id.rental_qty

    @api.onchange('sell_rental_id')
    def sell_rental_id_change(self):
        if self.sell_rental_id:
            self.product_uom_qty = self.sell_rental_id.rental_qty

    @api.onchange('rental_qty', 'number_of_days', 'product_id')
    def rental_qty_number_of_days_change(self):
        if self.product_id.rented_product_id:
            qty = self.rental_qty * self.number_of_days
            self.product_uom_qty = qty

    @api.onchange('rental_type')
    def rental_type_change(self):
        if self.rental_type == 'new_rental':
            self.extension_rental_id = False
