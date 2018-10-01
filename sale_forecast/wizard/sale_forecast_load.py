# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class SaleForecastLoad(models.TransientModel):

    _name = 'sale.forecast.load'

    def _get_default_forecast(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        forecast = False
        if model == 'sale.forecast':
            forecast = record.id
        return forecast

    def _get_default_date_from(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        date_from = False
        if model == 'sale.forecast':
            reg_date = record.date_from
            cur_year = fields.Date.from_string(reg_date).year
            date_from = fields.Date.from_string(reg_date).replace(
                year=cur_year-1)
        return date_from

    def _get_default_date_to(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        date_to = False
        if model == 'sale.forecast':
            reg_date = record.date_to
            cur_year = fields.Date.from_string(reg_date).year
            date_to = fields.Date.from_string(reg_date).replace(
                year=cur_year-1)
        return date_to

    partner_id = fields.Many2one("res.partner", string="Partner")
    date_from = fields.Date(string="Date from", default=_get_default_date_from)
    date_to = fields.Date(string="Date to", default=_get_default_date_to)
    forecast_id = fields.Many2one("sale.forecast", "Forecast",
                                  default=_get_default_forecast)
    product_categ_id = fields.Many2one("product.category", string="Category")
    product_tmpl_id = fields.Many2one("product.template", string="Template")
    product_id = fields.Many2one("product.product", string="Product")
    factor = fields.Float(string="Factor", default=1)

    @api.multi
    def match_sales_forecast(self, sales, factor):
        self.ensure_one()
        res = {}
        for sale in sales:
            product = sale.product_id.id
            partner = sale.order_id.partner_id.id
            # cumulative
            if partner not in res:
                res[partner] = {}
            if product not in res[partner]:
                res[partner][product] = {'qty': 0.0, 'amount': 0.0}
            product_dict = res[partner][product]
            sum_qty = product_dict['qty'] + sale.product_uom_qty * factor
            sum_subtotal = (product_dict['amount'] +
                            sale.price_subtotal)
            product_dict['qty'] = sum_qty
            product_dict['amount'] = sum_subtotal
        return res

    @api.multi
    def get_sale_forecast_lists(self, forecast):
        sale_line_obj = self.env['sale.order.line']
        sale_obj = self.env['sale.order']
        product_obj = self.env['product.product']
        self.ensure_one()
        sale_domain = [('date_order', '>=', self.date_from),
                       ('date_order', '<=', self.date_to),
                       ('state', 'in', ['sale', 'done'])]
        if self.partner_id:
            sale_domain += [('partner_id', '=', self.partner_id.id)]
        sales = sale_obj.search(sale_domain)
        sale_line_domain = [('order_id', 'in', sales.ids)]
        if self.product_id:
            sale_line_domain += [('product_id', '=', self.product_id.id)]
        elif self.product_categ_id:
            products = product_obj.search([('categ_id', '=',
                                            self.product_categ_id.id)])
            sale_line_domain += [('product_id', 'in', products.ids)]
        sale_lines = sale_line_obj.search(sale_line_domain)
        return sale_lines

    @api.multi
    def load_sales(self):
        self.ensure_one()
        forecast_line_obj = self.env['sale.forecast.line']
        forecast = self.forecast_id
        sale_lines = self.get_sale_forecast_lists(forecast)
        result = self.match_sales_forecast(sale_lines, self.factor)
        for partner in result.keys():
            for product in result[partner].keys():
                prod_vals = result[partner][product]
                line = forecast_line_obj.search(
                    [
                        ('forecast_id', '=', self.forecast_id.id),
                        ('partner_id', '=', partner),
                        ('product_id', '=', product)
                    ])
                unit_price = prod_vals['amount'] / prod_vals['qty']
                if line:
                    line.unit_price = (line.unit_price * line.qty + unit_price
                                       * prod_vals['qty']) / (line.qty +
                                                              prod_vals['qty'])

                    line.qty += prod_vals['qty']
                else:
                    forecast_line_vals = {'product_id': product,
                                          'forecast_id': self.forecast_id.id,
                                          'partner_id': partner,
                                          'qty': prod_vals['qty'],
                                          'unit_price': unit_price
                                          }
                    forecast_line_obj.create(forecast_line_vals)
        return True


class SelfSaleForecastLoad(models.TransientModel):
    _name = 'self.sale.forecast.load'
    _description = 'Load sale forecast from existing sale forecast'

    def _get_default_forecast(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        forecast = False
        if model == 'sale.forecast':
            forecast = record.id
        return forecast

    forecast_id = fields.Many2one(
        comodel_name='sale.forecast',
        string='Sale Forecast',
        default=_get_default_forecast)

    forecast_sales = fields.Many2one(
        comodel_name='sale.forecast',
        string='Sale Forecast')

    @api.multi
    def button_confirm(self):
        for line in self.forecast_sales.forecast_lines:
            forecast_line_obj = self.env['sale.forecast.line']
            line_dest = forecast_line_obj.search(
                [
                    ('forecast_id', '=', self.forecast_id.id),
                    ('partner_id', '=', line.partner_id.id),
                    ('product_id', '=', line.product_id.id)
                ])
            if line_dest:
                line_dest.unit_price = (line_dest.unit_price * line_dest.qty
                                        + line.unit_price * line.qty) / (
                                            line_dest.qty + line.qty)

                line_dest.qty += line.qty
            else:
                self.forecast_id.write({'forecast_lines': [(0, 0, {
                    'product_id': line.product_id.id,
                    'product_category_id': line.product_category_id.id,
                    'unit_price': line.unit_price,
                    'qty': line.qty,
                    'subtotal': line.subtotal,
                    'partner_id': line.partner_id.id,
                    })],
                })
