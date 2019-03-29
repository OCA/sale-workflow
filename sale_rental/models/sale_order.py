# Copyright 2014-2016 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,\
    DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
import odoo.addons.decimal_precision as dp
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
                    # Check availability of picking moves
                    # and changing picking status also
                    line.move_ids._action_assign()
                elif line.rental_type == 'rental_extension':
                    if not line.extension_rental_id or\
                            not line.extension_rental_id.in_move_id:
                        continue
                    line.extension_rental_id.in_move_id.date_expected =\
                        line.end_date
                    line.extension_rental_id.in_move_id.date = line.end_date
                elif line.sell_rental_id:
                    if line.sell_rental_id.out_move_id.state != 'done':
                        raise UserError(_(
                            'Cannot sell the rental %s because it has '
                            'not been delivered')
                            % line.sell_rental_id.display_name)
                    line.sell_rental_id.sell_move_id._action_assign()
                    line.sell_rental_id.in_move_id._action_cancel()
        return res

    @api.multi
    def action_cancel(self):
        """
            In case cancelling a SO which sells rental product.
            Picking in should be created manually
        """
        res = super(SaleOrder, self).action_cancel()
        for order in self:
            for line in order.order_line:
                if line.rental_type == 'new_rental':
                    sale_rental = self.env['sale.rental'].search(
                        [('start_order_line_id', '=', line.id)], limit=1)
                    sale_rental.out_move_id._action_cancel()
                    sale_rental.in_move_id._action_cancel()
                elif line.rental_type == 'rental_extension':
                    line.extension_rental_id.in_move_id.date_expected = \
                        line.extension_rental_id.end_date
                    line.extension_rental_id.in_move_id.date = \
                        line.extension_rental_id.end_date
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rental = fields.Boolean(string='Rental')
    can_sell_rental = fields.Boolean(string='Can Sell from Rental')
    rental_type = fields.Selection([
        ('new_rental', 'New Rental'),
        ('rental_extension', 'Rental Extension')], 'Rental Type',
        readonly=True, states={'draft': [('readonly', False)]})
    extension_rental_id = fields.Many2one(
        'sale.rental', string='Rental to Extend')
    rental_qty = fields.Float(
        string='Rental Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        help="Indicate the number of items that will be rented.")
    sell_rental_id = fields.Many2one(
        'sale.rental', string='Rental to Sell')

    @api.constrains(
        'rental_type', 'extension_rental_id', 'start_date', 'end_date',
        'rental_qty', 'product_uom_qty', 'product_id')
    def _check_sale_line_rental(self):
        for line in self:
            if line.rental_type == 'rental_extension':
                if not line.extension_rental_id:
                    raise ValidationError(_(
                        "Missing 'Rental to Extend' on the sale order line "
                        "with rental service %s") % line.product_id.name)

                if line.rental_qty != line.extension_rental_id.rental_qty:
                    raise ValidationError(_(
                        "On the sale order line with rental service %s, "
                        "you are trying to extend a rental with a rental "
                        "quantity (%s) that is different from the quantity "
                        "of the original rental (%s). This is not supported.")
                        % (
                        line.product_id.name,
                        line.rental_qty,
                        line.extension_rental_id.rental_qty))
            if line.rental_type in ('new_rental', 'rental_extension'):
                if not line.product_id.rented_product_id:
                    raise ValidationError(_(
                        "On the 'new rental' sale order line with product "
                        "'%s', we should have a rental service product !") % (
                        line.product_id.name))
                if line.product_uom_qty !=\
                        line.rental_qty * line.number_of_days:
                    raise ValidationError(_(
                        "On the sale order line with product '%s' "
                        "the Product Quantity (%s) should be the "
                        "number of days (%s) "
                        "multiplied by the Rental Quantity (%s).") % (
                        line.product_id.name, line.product_uom_qty,
                        line.number_of_days, line.rental_qty))
                # the module sale_start_end_dates checks that, when we have
                # must_have_dates, we have start + end dates
            elif line.sell_rental_id:
                if line.product_uom_qty != line.sell_rental_id.rental_qty:
                    raise ValidationError(_(
                        "On the sale order line with product %s "
                        "you are trying to sell a rented product with a "
                        "quantity (%s) that is different from the rented "
                        "quantity (%s). This is not supported.") % (
                        line.product_id.name,
                        line.product_uom_qty,
                        line.sell_rental_id.rental_qty))

    @api.multi
    def _prepare_rental(self):
        self.ensure_one()
        return {'start_order_line_id': self.id}

    @api.multi
    def _get_rental_date_planned(self):
        self.ensure_one()
        start_date = datetime.strptime(
            self.start_date, DEFAULT_SERVER_DATE_FORMAT)
        return start_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.multi
    def _action_launch_procurement_rule(self):
        res = super(SaleOrderLine, self)._action_launch_procurement_rule()
        errors = []
        for line in self:
            if not line.product_id.rented_product_id or\
                    line.rental_type == 'rental_extension':
                continue

            procurement_group = line.order_id.procurement_group_id
            if not procurement_group:
                procurement_group = self.env['procurement.group'].create({
                    'name': line.order_id.name,
                    'move_type': line.order_id.picking_policy,
                    'sale_id': line.order_id.id,
                    'partner_id': line.order_id.partner_shipping_id.id,
                })
                line.order_id.procurement_group_id = procurement_group

            if line.rental_type == 'new_rental':
                vals = {
                    'company_id': line.order_id.company_id,
                    'group_id': procurement_group,
                    'sale_line_id': line.id,
                    'date_planned': line._get_rental_date_planned(),
                    'route_ids': line.order_id.warehouse_id.rental_route_id,
                    'warehouse_id': line.order_id.warehouse_id or False,
                    'partner_dest_id': line.order_id.partner_shipping_id
                }
            try:
                self.env['procurement.group'].run(
                    line.product_id.rented_product_id, line.rental_qty,
                    line.product_id.rented_product_id.uom_id,
                    line.order_id.warehouse_id.rental_out_location_id,
                    line.name, line.order_id.name, vals)
            except UserError as error:
                errors.append(error.name)
        if errors:
            raise UserError('\n'.join(errors))
        return res

    @api.multi
    def _prepare_procurement_values(self, group_id=False):
        """
            Overriding this function to changethe route
            on selling rental product
        """
        vals = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
        if self.sell_rental_id:
            vals.update({
                'route_ids':
                    self.order_id.warehouse_id.sell_rented_product_route_id})
        return vals

    @api.onchange('product_id', 'rental_qty')
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
                    rented_product_ctx = \
                        self.with_context(
                            location=rental_in_location.id
                        ).product_id.rented_product_id
                    in_location_available_qty =\
                        rented_product_ctx.qty_available -\
                        rented_product_ctx.outgoing_qty
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
        if self.product_id and\
                self.rental_type == 'rental_extension' and\
                self.extension_rental_id:
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
