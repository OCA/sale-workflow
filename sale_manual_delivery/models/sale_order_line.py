# -*- coding: utf-8 -*-
# Copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _action_procurement_create(self):
        for line in self:
            if (line.order_id.manual_delivery and
                    line.product_id.type != 'service'):
                return self.env['procurement.order'].browse()
            else:
                return super(SaleOrderLine, self)._action_procurement_create()

    @api.multi
    def _action_manual_delivery_create(self, product_qty, date_planned,
                                          carrier):

        new_procs = self.env['procurement.order']  # Empty recordset
        for line in self:
            # if line.state != 'sale' or not
                # line.product_id._need_procurement():
            #     continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty

            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group()
                line.order_id.procurement_group_id = self.env[
                    "procurement.group"].create(vals)

            vals = line._prepare_order_line_procurement(
                group_id=line.order_id.procurement_group_id.id)
            vals['date_planned'] = date_planned  # line added
            vals['product_qty'] = product_qty  # line added
            vals['carrier_id'] = carrier.id  # line added
            new_proc = self.env["procurement.order"].create(vals)
            new_proc.message_post_with_view('mail.message_origin_link',
                                            values={'self': new_proc,
                                                    'origin': line.order_id},
                                            subtype_id=self.env.ref(
                                                'mail.mt_note').id)
            new_procs += new_proc
        new_procs.run()
        return new_procs
