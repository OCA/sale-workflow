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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if self.is_using_quotation_number(vals):
                company_id = vals.get("company_id", self.env.company.id)
                sequence = self.with_company(company_id).get_quotation_seq()
                vals.update({"name": sequence or "/", "quotation_seq_used": True})
        return super().create(vals_list)

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
        return super().copy(default)

    @api.model
    def get_quotation_seq(self):
        return self.env["ir.sequence"].next_by_code("sale.quotation")

    def get_sale_order_seq(self):
        self.ensure_one()
        return self.env["ir.sequence"].next_by_code("sale.order")

    def action_confirm(self):
        sequence = self.env["ir.sequence"].search(
            [("code", "=", "sale.quotation")], limit=1
        )
        for order in self:
            if not self.quotation_seq_used:
                continue
            if order.state not in ("draft", "sent") or order.company_id.keep_name_so:
                continue
            if order.origin and order.origin != "":
                quo = order.origin + ", " + order.name
            else:
                quo = order.name
            sequence = order.with_company(order.company_id.id).get_sale_order_seq()
            order.write({"origin": quo, "name": sequence, "quotation_seq_used": False})
        return super().action_confirm()
