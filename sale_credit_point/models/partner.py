# Copyright 2018-2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    credit_point = fields.Monetary(
        string="Points Attribution",
        currency_field="credit_point_currency_id",
        readonly=True,
        default=0,
    )
    yearly_point_increase = fields.Monetary(
        string="Yearly points increase",
        currency_field="credit_point_currency_id",
        readonly=True,
        compute="_compute_yearly_point_increase",
    )
    credit_history_ids = fields.One2many(
        comodel_name="credit.point.history",
        inverse_name="partner_id",
    )
    credit_point_currency_id = fields.Many2one(
        comodel_name="res.currency",
        default=lambda self: self._default_credit_point_currency_id(),
    )

    def _default_credit_point_currency_id(self):
        curr = self.env.ref(
            "sale_credit_point.res_currency_pt", raise_if_not_found=False
        )
        return curr.id if curr else None

    def credit_point_bypass_check(self):
        group = "sale_credit_point.group_manage_credit_point"
        return self.user_has_groups(group) or self.env.context.get("skip_credit_check")

    @api.constrains("credit_point")
    def _check_credit_point(self):
        for partner in self:
            if partner.credit_point < 0 and not partner.credit_point_bypass_check():
                raise exceptions.ValidationError(
                    _("You can't set a credit point lower than 0")
                )

    def action_update_credit_point(self):
        """Open update credit point wizard."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "wiz.manage.credit.point",
            "src_model": "res.partner",
            "view_mode": "form",
            "target": "new",
            "context": {"default_partner_ids": self.ids},
        }

    def _credit_point_update(self, amount, comment=""):
        self.credit_point = amount
        if comment:
            msg = _("Credit updated to {points}. Reason: {comment}")
            self.message_post(
                body=msg.format(points=self.credit_point, comment=comment)
            )

    def credit_point_replace(self, amount, comment=""):
        self._credit_point_update(amount, comment=comment)

    def credit_point_increase(self, amount, comment=""):
        self._credit_point_update(self.credit_point + amount, comment=comment)

    def credit_point_decrease(self, amount, comment=""):
        self._credit_point_update(self.credit_point - amount, comment=comment)

    def update_history(self, amount, operation, comment):
        history_model = self.env["credit.point.history"]
        vals = {
            "partner_id": self.id,
            "operation": operation,
            "amount": amount,
            "comment": comment,
        }
        return history_model.create(vals)

    def _compute_yearly_point_increase(self):
        self.env.cr.execute(
            """select partner_id, sum(amount) from credit_point_history
            where operation='increase' and partner_id in %s
            and date_part('year', create_date)=date_part('year', CURRENT_DATE)
            group by partner_id""",
            (tuple(self.ids),),
        )
        amounts = dict(self.env.cr.fetchall())
        for record in self:
            record.yearly_point_increase = amounts.get(record.id, 0)
