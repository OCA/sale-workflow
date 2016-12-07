# -*- coding: utf-8 -*-
# © 2016 Dreambits Technologies (http://www.dreambits.in)
# @author Karan Shah <admin@dreambits.in>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api
from openerp import models
from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)


class CustomSaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _action_procurement_create(self):
        result = {}
        for sale_order_line in self:
            # checking the settings values and see which conditions are
            # needed to be checked

            proc_product_value = self.env['ir.config_parameter'].get_param('procurement_product')
            proc_customer_value = self.env['ir.config_parameter'].get_param('procurement_customer')

            # 0 = no stopping
            # 1 = stop blocklisted
            # 2 = allow only whitelisted

            if proc_product_value!=0 or proc_customer_value!=0:
                product_blacklist = customer_blacklist = False

                if proc_product_value!=0:
                    #lets get the product info and see if they are blacklisted or whitelisted
                    product_blacklist = sale_order_line.product_id.x_whitelist_blacklist

                if proc_customer_value!=0:
                    #lets get the product info and see if they are blacklisted or whitelisted
                    customer_blacklist = sale_order_line.order_partner_id.x_whitelist_blacklist

                # lets find if full payment for the sale order line is done or
                # not.
                # If all payment is done then call the method to create
                # procurements
                # Else we return empty dict
                stop_proc = False

                _logger.info(proc_product_value=="1" and product_blacklist)
                if proc_product_value=="1" and product_blacklist:
                    _logger.info("product is blackilist")
                    stop_proc = True

                _logger.info(proc_customer_value=="1" and customer_blacklist)
                if proc_customer_value=="1" and customer_blacklist:
                    _logger.info("customer is blackilist")
                    stop_proc = True


                _logger.info("For so ")
                _logger.info(sale_order_line.order_id.name)
                _logger.info(proc_product_value=="1")
                _logger.info(product_blacklist==True)
                _logger.info(proc_customer_value=="1")
                _logger.info(customer_blacklist==True)
                _logger.info(stop_proc)


                if not stop_proc or (stop_proc and sale_order_line.invoice_status=="invoiced" and self.full_payment_done(sale_order_line)):
                    result = super(CustomSaleOrderLine, self)\
                            ._action_procurement_create()

        return result

    @api.model
    def run_scheduler(self):
        search_condition = [('invoice_status', '=', 'invoiced')]
        sale_order_lines = self.search(search_condition)
        for sale_order_line in sale_order_lines:
            if len(sale_order_line.order_id.picking_ids) == 0 \
                    and self.full_payment_done(sale_order_line):
                _logger.info("setting for")
                _logger.info(sale_order_line)
                sale_order_line._action_procurement_create()

        return None

    def full_payment_done(self,sale_order_line):
        all_invoice_status = [True for invoice in
            sale_order_line.order_id.invoice_ids if invoice.state == "paid"]
        # There may be order lines for which invoice
        # might not have been generated yet
        if all_invoice_status:
            all_paid = all(all_invoice_status)
            return all_paid
        elif len(sale_order_line.order_id.invoice_ids)>0:
            return False
        else:
            return True
