# -*- coding: utf-8 -*-
# © 2016 Dreambits Technologies (http://www.dreambits.in)
# @author Karan Shah <admin@dreambits.in>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api
from openerp import models
import logging

_logger = logging.getLogger(__name__)


class CustomSaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def _action_procurement_create(self):
        result = {}

        for sale_order_line in self:

            proc_product_value = self.env['ir.config_parameter'].\
                get_param('procurement_product')
            proc_customer_value = self.env['ir.config_parameter'].\
                get_param('procurement_customer')

            # 0 = no stopping
            # 1 = stop blocklisted

            if proc_product_value != 0 or proc_customer_value != 0:
                _logger.info("something will be stopped on blacklisted")
                product_blacklist = customer_blacklist = False

                if proc_product_value != 0:
                    product_blacklist = sale_order_line.product_id.\
                        x_whitelist_blacklist

                if proc_customer_value != 0:
                    customer_blacklist = sale_order_line.order_partner_id.\
                        x_whitelist_blacklist

                stop_proc = False

                if proc_product_value == "1" and product_blacklist:
                    stop_proc = True

                if proc_customer_value == "1" and customer_blacklist:
                    stop_proc = True

                if not stop_proc or (
                    stop_proc and
                    sale_order_line.invoice_status == "invoiced" and
                    self.full_payment_done(sale_order_line)
                ):
                    result = self.getCreateProcurement()

            else:
                result = self.getCreateProcurement()

        return result

    def getCreateProcurement(self):
        return super(CustomSaleOrderLine, self)._action_procurement_create()

    @api.model
    def run_scheduler(self):
        search_condition = [('invoice_status', '=', 'invoiced')]
        sale_order_lines = self.search(search_condition)
        for sale_order_line in sale_order_lines:
            if len(sale_order_line.order_id.picking_ids) == 0 \
                    and self.full_payment_done(sale_order_line):
                sale_order_line._action_procurement_create()

        return None

    def full_payment_done(self, sale_order_line):
        all_invoice_status = [True
                              for invoice in
                              sale_order_line.order_id.invoice_ids
                              if invoice.state == "paid"]

        if all_invoice_status:
            all_paid = all(all_invoice_status)
            return all_paid
        elif len(sale_order_line.order_id.invoice_ids) > 0:
            return False
        else:
            return True
