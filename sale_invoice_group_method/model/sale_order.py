# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import json

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoice_group_method_id = fields.Many2one(
        string="Invoice Group Method", comodel_name="sale.invoice.group.method"
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if self.partner_id.invoice_group_method_id:
            self.update(
                {
                    "invoice_group_method_id": self.partner_id.invoice_group_method_id.id,
                }
            )
        return

    @api.model
    def _get_invoice_group_key(self, order):
        res = super(SaleOrder, self)._get_invoice_group_key(order)
        invoice_group_method_fields = order.invoice_group_method_id.criteria_fields_ids
        for method_fields in invoice_group_method_fields:
            value = order[method_fields.name]
            if method_fields.ttype in ("many2one", "one2many", "many2many"):
                value = tuple(value.ids)
            res += (value,)
        res += (order.payment_term_id.id,)
        return res

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res["invoice_group_method_key"] = self._get_invoice_group_method_key()
        return res

    def _get_invoice_group_method_key(self):
        self.ensure_one()
        if not self.invoice_group_method_id:
            return json.dumps([False, self.id], default=str)
        key = [self.invoice_group_method_id.id]
        for field in self.invoice_group_method_id.criteria_fields_ids:
            value = self[field.name]
            if field.ttype in ("many2one", "one2many", "many2many"):
                value = tuple(value.ids)
            key.append(value)
        key.append(self.payment_term_id.id)
        return json.dumps(key, default=str)

    def _get_invoice_grouping_keys(self):
        keys = super()._get_invoice_grouping_keys()
        return keys + ["invoice_group_method_key"]
