# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2020 Tecnativa - Pedro M. Baeza

from datetime import datetime, timedelta

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Type",
        compute="_compute_sale_type_id",
        store=True,
        readonly=False,
        states={
            "sale": [("readonly", True)],
            "done": [("readonly", True)],
            "cancel": [("readonly", True)],
        },
        default=lambda so: so._default_type_id(),
        ondelete="restrict",
        copy=True,
        check_company=True,
    )

    @api.model
    def _default_type_id(self):
        return self.env["sale.order.type"].search(
            [("company_id", "in", [self.env.company.id, False])], limit=1
        )

    @api.model
    def _default_sequence_id(self):
        """We get the sequence in same way the core next_by_code method does so we can
        get the proper default sequence"""
        force_company = self.company_id.id or self.env.company.id
        return self.env["ir.sequence"].search(
            [
                ("code", "=", "sale.order"),
                "|",
                ("company_id", "=", force_company),
                ("company_id", "=", False),
            ],
            order="company_id",
            limit=1,
        )

    @api.depends("partner_id", "company_id")
    @api.depends_context("partner_id", "company_id", "company")
    def _compute_sale_type_id(self):
        for record in self:
            if not record.partner_id:
                record.type_id = self.env["sale.order.type"].search(
                    [("company_id", "in", [self.env.company.id, False])], limit=1
                )
            else:
                sale_type = (
                    record.partner_id.with_company(record.company_id).sale_type
                    or record.partner_id.commercial_partner_id.with_company(
                        record.company_id
                    ).sale_type
                )
                if sale_type:
                    record.type_id = sale_type

    @api.onchange("type_id")
    def onchange_type_id(self):
        # TODO: To be changed to computed stored readonly=False if possible in v14?
        vals = {}
        for order in self:
            order_type = order.type_id
            # Order values
            vals = {}
            if order_type.warehouse_id:
                vals.update({"warehouse_id": order_type.warehouse_id})
            if order_type.picking_policy:
                vals.update({"picking_policy": order_type.picking_policy})
            if order_type.payment_term_id:
                vals.update({"payment_term_id": order_type.payment_term_id})
            if order_type.pricelist_id:
                vals.update({"pricelist_id": order_type.pricelist_id})
            if order_type.incoterm_id:
                vals.update({"incoterm": order_type.incoterm_id})
            if order_type.analytic_account_id:
                vals.update({"analytic_account_id": order_type.analytic_account_id})
            if order_type.quotation_validity_days:
                vals.update(
                    {
                        "validity_date": fields.Date.to_string(
                            datetime.now()
                            + timedelta(order_type.quotation_validity_days)
                        )
                    }
                )
            if vals:
                order.update(vals)
            # Order line values
            line_vals = {}
            line_vals.update({"route_id": order_type.route_id.id})
            order.order_line.update(line_vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New") and vals.get("type_id"):
                sale_type = self.env["sale.order.type"].browse(vals["type_id"])
                if sale_type.sequence_id:
                    vals["name"] = sale_type.sequence_id.next_by_id(
                        sequence_date=vals.get("date_order")
                    )
        return super().create(vals_list)

    def write(self, vals):
        """A sale type could have a different order sequence, so we could
        need to change it accordingly"""
        default_sequence = self._default_sequence_id()
        if vals.get("type_id"):
            sale_type = self.env["sale.order.type"].browse(vals["type_id"])
            if sale_type.sequence_id:
                for record in self:
                    # An order with a type without sequence would get the default one.
                    # We want to avoid changing the order reference when the new
                    # sequence has the same default sequence.
                    ignore_default_sequence = (
                        not record.type_id.sequence_id
                        and sale_type.sequence_id == default_sequence
                    )
                    if (
                        record.state in {"draft", "sent"}
                        and record.type_id.sequence_id != sale_type.sequence_id
                        and not ignore_default_sequence
                    ):
                        new_vals = vals.copy()
                        new_vals["name"] = sale_type.sequence_id.next_by_id(
                            sequence_date=vals.get("date_order")
                        )
                        super(SaleOrder, record).write(new_vals)
                    else:
                        super(SaleOrder, record).write(vals)
                return True
        return super().write(vals)

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.type_id.journal_id:
            res["journal_id"] = self.type_id.journal_id.id
        if self.type_id:
            res["sale_type_id"] = self.type_id.id
        return res
