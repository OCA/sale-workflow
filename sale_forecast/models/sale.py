# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, exceptions, fields, models, _
import odoo.addons.decimal_precision as dp


class SaleForecast(models.Model):
    _name = 'sale.forecast'

    name = fields.Char(string='Name', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    forecast_lines = fields.One2many('sale.forecast.line',
                                     'forecast_id', string="Forecast Lines")

    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        if self.date_from >= self.date_to:
            raise exceptions.ValidationError(_('Error! Date to must be lower '
                                             'than date from.'))

    @api.multi
    def recalculate_actual_qty(self):
        for record in self.forecast_lines:
            record._compute_actual_qty()


class SaleForecastLine(models.Model):

    _name = 'sale.forecast.line'
    _order = 'forecast_id,product_id,qty,partner_id'

    @api.multi
    @api.depends('unit_price', 'qty')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.unit_price * record.qty

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.unit_price = self.product_id.list_price

    product_id = fields.Many2one('product.product', string='Product')
    product_category_id = fields.Many2one('product.category',
                                          string='Product Category')
    qty = fields.Float('Quantity', default=1,
                       digits=dp.get_precision('Product Unit of Measure'))
    unit_price = fields.Float('Unit Price',
                              digits=dp.get_precision('Product Price'))
    subtotal = fields.Float('Subtotal', compute=_compute_subtotal, store=True,
                            digits=dp.get_precision('Product Price'))
    partner_id = fields.Many2one("res.partner", string="Partner")
    commercial_id = fields.Many2one(comodel_name="res.users",
                                    related="partner_id.user_id",
                                    string="Commercial")
    currency_id = fields.Many2one(
        comodel_name="res.currency", string="Currency",
        related="partner_id.property_product_pricelist.currency_id")
    date_from = fields.Date(string="Date from", store=True,
                            related="forecast_id.date_from")
    date_to = fields.Date(string="Date to", related="forecast_id.date_to",
                          store=True)
    forecast_id = fields.Many2one('sale.forecast',
                                  string='Forecast',
                                  ondelete='cascade')
    date = fields.Date("Date")

    actual_qty = fields.Float(
        string='Actual Qty',
        compute='_compute_actual_qty',
        store=True)

    @api.multi
    @api.depends('forecast_id.forecast_lines')
    def _compute_actual_qty(self):
        sale_obj = self.env['sale.order.line']
        prod_obj = self.env['product.product']
        for record in self:
            domain = [
                ('invoice_status', '=', 'invoiced'),
                ('order_id.confirmation_date', '>=', record.date_from),
                ('order_id.confirmation_date', '<=', record.date_to)
            ]
            if record.product_id:
                domain += [('product_id', '=', record.product_id.id)]
                if record.partner_id:
                    domain += [
                        ('order_id.partner_id', '=', record.partner_id.id)]
                sale_ids = sale_obj.search(domain)
                record.actual_qty = sum(sale_ids.mapped('product_uom_qty'))

            elif record.product_category_id:
                product_ids = prod_obj.search([
                    ('categ_id', '=', record.product_category_id.id)])
                domain += [('product_id', 'in', product_ids.ids)]
                if record.partner_id:
                    domain += [
                        ('order_id.partner_id', '=', record.partner_id.id)]
                sale_ids = sale_obj.search(domain)
                record.actual_qty = sum(sale_ids.mapped('product_uom_qty'))
