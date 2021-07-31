# Copyright 2014-2021 Akretion (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare
from dateutil.relativedelta import relativedelta
import logging


logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_cancel(self):
        """
        When the user cancels a rental extension, Odoo writes the initial
        end date on the return picking
        """
        res = super().action_cancel()
        for order in self:
            for line in order.order_line.filtered(
                    lambda l: l.rental_type == 'rental_extension' and
                    l.extension_rental_id):
                initial_end_date = line.extension_rental_id.end_date
                line.extension_rental_id.in_move_id.write({
                    'date': initial_end_date,
                    })
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    rental = fields.Boolean(string='Rental', default=False)
    can_sell_rental = fields.Boolean(string='Can Sell from Rental')
    rental_type = fields.Selection([
        ('new_rental', 'New Rental'),
        ('rental_extension', 'Rental Extension')], string='Rental Type',
        readonly=True, states={'draft': [('readonly', False)]})
    extension_rental_id = fields.Many2one(
        'sale.rental', string='Rental to Extend', check_company=True,
        readonly=True, states={'draft': [('readonly', False)]})
    rental_qty = fields.Float(
        string='Rental Quantity',
        digits='Product Unit of Measure',
        readonly=True, states={'draft': [('readonly', False)]},
        help="Indicate the number of items that will be rented.")
    sell_rental_id = fields.Many2one(
        'sale.rental', string='Rental to Sell', check_company=True,
        readonly=True, states={'draft': [('readonly', False)]})

    _sql_constraints = [(
        'rental_qty_positive',
        'CHECK(rental_qty >= 0)',
        'The rental quantity must be positive or null.'
        )]

    @api.constrains(
        'rental_type', 'extension_rental_id', 'start_date', 'end_date',
        'rental_qty', 'product_uom_qty', 'product_id')
    def _check_sale_line_rental(self):
        for line in self:
            if line.rental_type == 'rental_extension':
                if not line.extension_rental_id:
                    raise ValidationError(_(
                        "Missing 'Rental to Extend' on the sale order line "
                        "with rental service %s") % line.product_id.display_name)

                if line.rental_qty != line.extension_rental_id.rental_qty:
                    raise ValidationError(_(
                        "On the sale order line with rental service %s, "
                        "you are trying to extend a rental with a rental "
                        "quantity (%s) that is different from the quantity "
                        "of the original rental (%s). This is not supported.")
                        % (
                        line.product_id.display_name,
                        line.rental_qty,
                        line.extension_rental_id.rental_qty))
            if line.rental_type in ('new_rental', 'rental_extension'):
                if not line.product_id.rented_product_id:
                    raise ValidationError(_(
                        "On the 'new rental' sale order line with product "
                        "'%s', we should have a rental service product !")
                        % line.product_id.display_name)
                if line.product_uom_qty !=\
                        line.rental_qty * line.number_of_days:
                    raise ValidationError(_(
                        "On the sale order line with product '%s' "
                        "the Product Quantity (%s) should be the "
                        "number of days (%s) "
                        "multiplied by the Rental Quantity (%s).") % (
                        line.product_id.display_name, line.product_uom_qty,
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
                        line.product_id.display_name,
                        line.product_uom_qty,
                        line.sell_rental_id.rental_qty))

    def _prepare_rental(self):
        self.ensure_one()
        return {'start_order_line_id': self.id}

    def _prepare_new_rental_procurement_values(self, group=False):
        vals = {
            'company_id': self.order_id.company_id,
            'group_id': group,
            'sale_line_id': self.id,
            'date_planned': self.start_date,
            'route_ids': self.route_id or self.order_id.warehouse_id.rental_route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'partner_id': self.order_id.partner_shipping_id.id,
            }
        return vals

    def _run_rental_procurement(self, vals):
        self.ensure_one()
        procurements = [self.env['procurement.group'].Procurement(
            self.product_id.rented_product_id,
            self.rental_qty,
            self.product_id.rented_product_id.uom_id,
            self.order_id.warehouse_id.rental_out_location_id,
            self.name,
            self.order_id.name,
            self.order_id.company_id,
            vals)]
        self.env['procurement.group'].run(procurements)

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        errors = []
        for line in self:
            if (
                    line.rental_type == 'new_rental' and
                    line.product_id.rented_product_id):
                group = line.order_id.procurement_group_id
                if not group:
                    group = self.env['procurement.group'].create({
                        'name': line.order_id.name,
                        'move_type': line.order_id.picking_policy,
                        'sale_id': line.order_id.id,
                        'partner_id': line.order_id.partner_shipping_id.id,
                    })
                    line.order_id.procurement_group_id = group

                vals = line._prepare_new_rental_procurement_values(group)
                try:
                    line._run_rental_procurement(vals)
                except UserError as error:
                    errors.append(error.name)

                self.env['sale.rental'].create(line._prepare_rental())

            elif (
                    line.rental_type == 'rental_extension' and
                    line.product_id.rented_product_id and
                    line.extension_rental_id and
                    line.extension_rental_id.in_move_id):
                end_datetime = fields.Datetime.to_datetime(
                    line.end_date)
                line.extension_rental_id.in_move_id.write({
                    'date': end_datetime,
                    })
            elif line.sell_rental_id:
                if line.sell_rental_id.out_move_id.state != 'done':
                    raise UserError(_(
                        'Cannot sell the rental %s because it has '
                        'not been delivered')
                        % line.sell_rental_id.display_name)
                line.sell_rental_id.in_move_id._action_cancel()

        if errors:
            raise UserError('\n'.join(errors))

        # call super() at the end, to make procurement_jit work
        res = super()._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
        return res

    def _prepare_procurement_values(self, group_id=False):
        """
            Overriding this function to changethe route
            on selling rental product
        """
        vals = super()._prepare_procurement_values(group_id=group_id)
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
                    % self.extension_rental_id.rental_product_id.display_name)
            initial_end_date = self.extension_rental_id.end_date
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
