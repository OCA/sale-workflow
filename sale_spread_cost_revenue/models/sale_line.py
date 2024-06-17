# Copyright 2024 Ecosoft (<https://ecosoft.co.th>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    spread_id = fields.Many2one("account.spread", string="Spread Board", copy=False)
    spread_check = fields.Selection(
        [
            ("linked", "Linked"),
            ("unlinked", "Unlinked"),
            ("unavailable", "Unavailable"),
        ],
        compute="_compute_spread_check",
    )

    @api.depends("spread_id", "order_id.state")
    def _compute_spread_check(self):
        for line in self:
            if line.spread_id:
                line.spread_check = "linked"
            elif line.order_id.state == "draft":
                line.spread_check = "unlinked"
            else:
                line.spread_check = "unavailable"

    def spread_details(self):
        """Button on the sale lines tree view of the sales order
        form to show the spread form view."""
        if not self:
            # In case the widget clicked before the creation of the line
            return

        if self.spread_id:
            return {
                "name": _("Spread Details"),
                "view_mode": "form",
                "res_model": "account.spread",
                "type": "ir.actions.act_window",
                "target": "current",
                "readonly": False,
                "res_id": self.spread_id.id,
            }

        # In case no spread board is linked to the sale line
        # open the wizard to link them
        ctx = dict(
            self.env.context,
            default_sale_line_id=self.id,
            default_company_id=self.order_id.company_id.id,
            allow_spread_planning=self.order_id.company_id.allow_spread_planning,
        )
        return {
            "name": _("Link Sales Line with Spread Board"),
            "view_mode": "form",
            "res_model": "account.spread.sale.line.link.wizard",
            "type": "ir.actions.act_window",
            "target": "new",
            "context": ctx,
        }

    def create_auto_spread(self):
        """Create auto spread table for each sale line, when needed"""

        def _filter_line(aline, sline):
            """Find matching template auto line with sale line"""
            if aline.product_id and sline.product_id != aline.product_id:
                return False
            return True

        # Skip create new template when create move on spread lines
        if self.env.context.get("skip_create_template"):
            return

        for line in self:
            if line.spread_check == "linked":
                continue
            spread_type = "sale"
            spread_auto = self.env["account.spread.template.auto"].search(
                [
                    ("template_id.auto_spread", "=", True),
                    ("template_id.spread_type", "=", spread_type),
                ]
            )
            matched = spread_auto.filtered(lambda a, s=line: _filter_line(a, s))
            template = matched.mapped("template_id")
            if not template:
                continue
            elif len(template) > 1:
                raise UserError(
                    _(
                        "Too many auto spread templates (%(len_template)s) matched with the "
                        "sale line, %(line_name)s"
                    )
                    % {"len_template": len(template), "line_name": line.display_name}
                )
            # Found auto spread template for this invoice line, create it
            wizard = self.env["account.spread.sale.line.link.wizard"].new(
                {
                    "sale_line_id": line.id,
                    "company_id": line.company_id.id,
                    "spread_action_type": "template",
                    "template_id": template.id,
                }
            )
            wizard.confirm()

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        # Creating invoice from sales order, ensure same spread account
        if self.spread_id:
            res["spread_on_sale"] = True
            res["spread_id"] = self.spread_id.id
            res["account_id"] = self.spread_id.debit_account_id.id
        return res
