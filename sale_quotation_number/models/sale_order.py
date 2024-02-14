# © 2010-2012 Andy Lu <andy.lu@elico-corp.com> (Elico Corp)
# © 2013 Agile Business Group sagl (<http://www.agilebg.com>)
# © 2017 valentin vinagre  <valentin.vinagre@qubiq.es> (QubiQ)
# © 2020 Manuel Regidor  <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    quotation_seq_used = fields.Boolean(
        string="Quotation Sequence Used", default=False, copy=False, readonly=True
    )

    @api.model
    def create(self, vals):
        if self.is_using_quotation_number(vals):
            sequence = self.get_quotation_seq()
            vals.update({"name": sequence or "/", "quotation_seq_used": True})
        return super(SaleOrder, self).create(vals)

    @api.model
    def is_using_quotation_number(self, vals):
        company = False
        if "company_id" in vals:
            company = self.env["res.company"].browse(vals.get("company_id"))
        else:
            company = self.env.company
        return not company.keep_name_so

    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if self.origin and self.origin != "":
            default["origin"] = self.origin + ", " + self.name
        else:
            default["origin"] = self.name
        return super(SaleOrder, self).copy(default)

    @api.model
    def get_quotation_seq(self):
        return self.env["ir.sequence"].next_by_code("sale.quotation")

    def get_sale_order_seq(self):
        self.ensure_one()
        return self.env["ir.sequence"].next_by_code("sale.order")

    def _action_confirm(self):
        for order in self:
            if not (
                order.state == "sale"
                and order.quotation_seq_used
                and not order.company_id.keep_name_so
            ):
                continue
            quo = ""
            if order.origin and order.origin != "":
                quo = order.origin + ", " + order.name
            else:
                quo = order.name
            sequence = order.get_sale_order_seq()
            order.write({"origin": quo, "name": sequence, "quotation_seq_used": False})
        return super()._action_confirm()
