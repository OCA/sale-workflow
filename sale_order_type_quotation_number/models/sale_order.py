# Copyright 2023 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    applied_quotation_seq_id = fields.Many2one(
        comodel_name="ir.sequence", readonly=True
    )
    recompute_quotation_seq = fields.Boolean(
        compute="_compute_recompute_quotation_seq",
        store=True,
    )

    @api.model
    def create(self, vals):
        orders = super(
            SaleOrder, self.with_context(type_id=vals.get("type_id"))
        ).create(vals)
        for order in orders.filtered(lambda a: a.quotation_seq_used):
            order.applied_quotation_seq_id = order.get_quotation_seq_id()
        return orders

    @api.depends("type_id", "type_id.quotation_sequence_id", "state")
    def _compute_recompute_quotation_seq(self):
        for sel in self:
            res = False
            if (
                sel.state in ["draft", "sent"]
                and sel.type_id.quotation_sequence_id
                and sel.type_id.quotation_sequence_id != sel.applied_quotation_seq_id
            ):
                res = True
            sel.recompute_quotation_seq = res

    def action_recompute_quotation_seq(self):
        for sel in self.filtered(
            lambda a: a.state in ["draft", "sent"] and a.recompute_quotation_seq
        ):
            sel.write(
                {
                    "name": sel.type_id.quotation_sequence_id.next_by_id(),
                    "applied_quotation_seq_id": sel.type_id.quotation_sequence_id.id,
                }
            )

    def get_quotation_seq_id(self):
        self.ensure_one()
        seq_id = False
        if not self.company_id.keep_name_so:
            seq_id = self.type_id.quotation_sequence_id or self.env[
                "ir.sequence"
            ].search([("code", "=", "sale.quotation")], limit=1)
        return seq_id

    @api.model
    def get_quotation_seq(self):
        seq = ""
        type_id = False
        if self.env.context.get("type_id"):
            type_id = self.env["sale.order.type"].browse(
                self.env.context.get("type_id")
            )
        if type_id and type_id.quotation_sequence_id:
            seq = type_id.quotation_sequence_id.next_by_id()
        else:
            seq = super().get_quotation_seq()
        return seq

    def get_sale_order_seq(self):
        if self.type_id and self.type_id.sequence_id:
            seq = self.type_id.sequence_id.next_by_id()
        else:
            seq = super().get_sale_order_seq()
        return seq
