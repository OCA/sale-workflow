# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class SaleOrderChangeAnalytic(models.TransientModel):
    """
    Tool used to change the analytic account set on a sale order
    """

    _name = "sale.order.change.analytic"
    _description = "Sale order change analytic account"

    sale_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale order",
        required=True,
        ondelete="cascade",
        # If the SO is not validated, the user can update analytic account
        # without this tool.
        domain=[("state", "=", "sale")],
        readonly=True,
    )
    current_analytic_account_id = fields.Many2one(
        # analytic_account_id is account.analytic.account
        related="sale_id.analytic_account_id",
        readonly=True,
        ondelete="cascade",
    )
    new_analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="New Analytic Account",
        required=True,
        ondelete="cascade",
    )

    @api.model
    def default_get(self, fields_list):
        """
        Inherit to auto fill the sale_id depending on the context
        :param fields_list: list of str
        :return: dict
        """
        result = super(SaleOrderChangeAnalytic, self).default_get(fields_list)
        ctx = self.env.context
        if ctx.get("active_model") == "sale.order" and ctx.get("active_id"):
            result.update({"sale_id": ctx.get("active_id")})
        return result

    def action_update(self):
        """
        Action to update the analytic account on target sale order
        :return: dict/action
        """
        self._action_update()
        return {}

    def _action_update(self):
        """
        Action to update the analytic account on target sale order
        :return: bool
        """
        self.ensure_one()
        self._action_update_invoices()
        self._action_update_sale_order()
        return True

    def _action_update_sale_order(self):
        """
        Action to update analytic account on target sale order.
        :return: bool
        """
        self.sale_id.write({"analytic_account_id": self.new_analytic_account_id.id})
        return True

    def _action_update_invoices(self):
        """
        Action to update analytic account on related journal entries
        (+ related objects)
        :return: bool
        """
        self.ensure_one()
        invoices = self.sale_id.invoice_ids
        invoice_lines = invoices.mapped("invoice_line_ids")
        # We have to load every invoices from invoice lines found
        # Then load every lines (even not related to sales) but related to
        # the original analytic account
        invoice_lines = invoice_lines.filtered(
            lambda l: l.analytic_account_id == self.current_analytic_account_id
        )
        invoice_lines.write({"analytic_account_id": self.new_analytic_account_id.id})
        return True
