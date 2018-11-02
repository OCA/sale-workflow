import werkzeug
from odoo import http
from odoo.http import request


class SaleQuote(http.Controller):

    @http.route(
        ["/quote/substitute_line/<int:line_id>/<int:order_id>/<token>"],
        type='http',
        auth="public",
        website=True
        )
    def substitute_line(self, line_id, order_id, token, **post):
        Order = request.env['sale.order'].sudo().browse(int(order_id))
        if token != Order.access_token:
            return request.render('website.404')
        if Order.state not in ('draft', 'sent'):
            return False
        LineSub = request.env['sale.order.substitute'].sudo().browse(
            int(line_id))
        LineSub.button_substitute_product()
        return werkzeug.utils.redirect(
            "/quote/%s/%s#quote_header_2" % (Order.id, token))
