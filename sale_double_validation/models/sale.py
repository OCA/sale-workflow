# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _, api, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _setup_fields(self):
        super(SaleOrder, self)._setup_fields()
        selection = self._fields["state"].selection
        exists = False
        for _idx, (state, __) in enumerate(selection):
            if state == "to_approve":
                exists = True
        if not exists:
            selection.insert(0, ("to_approve", _("To Approve")))

    def is_amount_to_approve(self):
        self.ensure_one()
        currency = self.company_id.currency_id
        limit_amount = self.company_id.so_double_validation_amount
        limit_amount = currency._convert(
            limit_amount, self.currency_id, self.company_id, self.date_order.date
        )
        return (
            float_compare(
                limit_amount,
                self.amount_total,
                precision_rounding=self.currency_id.rounding,
            )
            <= 0
        )

    def is_to_approve(self):
        self.ensure_one()
        return (
            self.company_id.so_double_validation == "two_step"
            and self.is_amount_to_approve()
            and not self.user_has_groups("sales_team.group_sale_manager")
        )

    @api.model
    def create(self, vals):
        obj = super().create(vals)
        if obj.is_to_approve():
            obj.state = "to_approve"
        return obj

    def action_approve(self):
        self.write({"state": "draft"})
