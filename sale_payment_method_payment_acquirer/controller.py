# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.website_sale.controllers.main import website_sale
from openerp import http
from openerp.http import request, route


class website_sale_customization(website_sale):

    # change the payment method if we choose the acquirer id from the website
    @http.route(['/shop/payment/transaction/<int:acquirer_id>'],
                type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id):

        res = super(website_sale_customization, self).\
            payment_transaction(acquirer_id)
        if acquirer_id:
            cr, uid, context, registry = \
                request.cr, request.uid, request.context, request.registry
            order = request.website.sale_get_order(context=context)
            order.onchange_payment_acquirer_id()
            order.onchange_payment_method_set_workflow()
        return res
