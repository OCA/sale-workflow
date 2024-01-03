# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

from odoo.addons.sale.models.sale_order import READONLY_FIELD_STATES


class BlanketOrder(models.Model):
    _name = "sale.blanket.order"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Blanket Order"
    _check_company_auto = True

    @api.model
    def _default_note(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account.use_invoice_terms")
            and self.env.company.invoice_terms
            or ""
        )

    @api.depends("line_ids.price_total")
    def _compute_amount_all(self):
        for order in self.filtered("currency_id"):
            amount_untaxed = amount_tax = 0.0
            for line in order.line_ids:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update(
                {
                    "amount_untaxed": order.currency_id.round(amount_untaxed),
                    "amount_tax": order.currency_id.round(amount_tax),
                    "amount_total": amount_untaxed + amount_tax,
                }
            )

    name = fields.Char(default="Draft", readonly=True, copy=False)
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        states=READONLY_FIELD_STATES,
    )
    line_ids = fields.One2many(
        "sale.blanket.order.line", "order_id", string="Order lines", copy=True
    )
    line_count = fields.Integer(
        string="Sale Blanket Order Line count",
        compute="_compute_line_count",
        readonly=True,
    )
    product_id = fields.Many2one(
        "product.product",
        related="line_ids.product_id",
        string="Product",
    )
    pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Pricelist",
        required=True,
        states=READONLY_FIELD_STATES,
    )
    currency_id = fields.Many2one("res.currency", related="pricelist_id.currency_id")
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        copy=False,
        check_company=True,
        states=READONLY_FIELD_STATES,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    payment_term_id = fields.Many2one(
        "account.payment.term",
        string="Payment Terms",
        states=READONLY_FIELD_STATES,
    )
    confirmed = fields.Boolean(copy=False)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("open", "Open"),
            ("done", "Done"),
            ("expired", "Expired"),
        ],
        compute="_compute_state",
        store=True,
        copy=False,
    )
    validity_date = fields.Date(
        states=READONLY_FIELD_STATES,
    )
    client_order_ref = fields.Char(
        string="Customer Reference",
        copy=False,
        states=READONLY_FIELD_STATES,
    )
    note = fields.Text(default=_default_note, states=READONLY_FIELD_STATES)
    user_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        states=READONLY_FIELD_STATES,
    )
    team_id = fields.Many2one(
        "crm.team",
        string="Sales Team",
        change_default=True,
        default=lambda self: self.env["crm.team"]._get_default_team_id(),
        states=READONLY_FIELD_STATES,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    sale_count = fields.Integer(compute="_compute_sale_count")

    fiscal_position_id = fields.Many2one(
        "account.fiscal.position", string="Fiscal Position"
    )

    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        store=True,
        readonly=True,
        compute="_compute_amount_all",
        tracking=True,
    )
    amount_tax = fields.Monetary(
        string="Taxes", store=True, readonly=True, compute="_compute_amount_all"
    )
    amount_total = fields.Monetary(
        string="Total", store=True, readonly=True, compute="_compute_amount_all"
    )

    # Fields use to filter in tree view
    original_uom_qty = fields.Float(
        string="Original quantity",
        compute="_compute_uom_qty",
        search="_search_original_uom_qty",
        default=0.0,
    )
    ordered_uom_qty = fields.Float(
        string="Ordered quantity",
        compute="_compute_uom_qty",
        search="_search_ordered_uom_qty",
        default=0.0,
    )
    invoiced_uom_qty = fields.Float(
        string="Invoiced quantity",
        compute="_compute_uom_qty",
        search="_search_invoiced_uom_qty",
        default=0.0,
    )
    remaining_uom_qty = fields.Float(
        string="Remaining quantity",
        compute="_compute_uom_qty",
        search="_search_remaining_uom_qty",
        default=0.0,
    )
    delivered_uom_qty = fields.Float(
        string="Delivered quantity",
        compute="_compute_uom_qty",
        search="_search_delivered_uom_qty",
        default=0.0,
    )

    route_id = fields.Many2one(
        "stock.route",
        string="Route",
        domain=[("sale_selectable", "=", True)],
        ondelete="restrict",
        check_company=True,
    )

    def _get_sale_orders(self):
        return self.mapped("line_ids.sale_lines.order_id")

    @api.depends("line_ids")
    def _compute_line_count(self):
        self.line_count = len(self.mapped("line_ids"))

    def _compute_sale_count(self):
        for blanket_order in self:
            blanket_order.sale_count = len(blanket_order._get_sale_orders())

    @api.depends(
        "line_ids.remaining_uom_qty",
        "validity_date",
        "confirmed",
    )
    def _compute_state(self):
        today = fields.Date.today()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for order in self:
            if not order.confirmed:
                order.state = "draft"
            elif order.validity_date <= today:
                order.state = "expired"
            elif float_is_zero(
                sum(
                    order.line_ids.filtered(lambda l: not l.display_type).mapped(
                        "remaining_uom_qty"
                    )
                ),
                precision_digits=precision,
            ):
                order.state = "done"
            else:
                order.state = "open"

    def _compute_uom_qty(self):
        for bo in self:
            bo.original_uom_qty = sum(bo.mapped("order_id.original_uom_qty"))
            bo.ordered_uom_qty = sum(bo.mapped("order_id.ordered_uom_qty"))
            bo.invoiced_uom_qty = sum(bo.mapped("order_id.invoiced_uom_qty"))
            bo.delivered_uom_qty = sum(bo.mapped("order_id.delivered_uom_qty"))
            bo.remaining_uom_qty = sum(bo.mapped("order_id.remaining_uom_qty"))

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment term
        - Fiscal position
        """
        if not self.partner_id:
            self.payment_term_id = False
            self.fiscal_position_id = False
            return

        values = {
            "pricelist_id": (
                self.partner_id.property_product_pricelist
                and self.partner_id.property_product_pricelist.id
                or False
            ),
            "payment_term_id": (
                self.partner_id.property_payment_term_id
                and self.partner_id.property_payment_term_id.id
                or False
            ),
            "fiscal_position_id": self.env["account.fiscal.position"]
            .with_context(company_id=self.company_id.id)
            ._get_fiscal_position(self.partner_id),
        }

        if self.partner_id.user_id:
            values["user_id"] = self.partner_id.user_id.id
        if self.partner_id.team_id:
            values["team_id"] = self.partner_id.team_id.id
        self.update(values)

    def unlink(self):
        for order in self:
            if order.state not in ("draft", "expired") or order._check_active_orders():
                raise UserError(
                    _(
                        "You can not delete an open blanket or "
                        "with active sale orders! "
                        "Try to cancel it before."
                    )
                )
        return super().unlink()

    def _validate(self):
        try:
            today = fields.Date.today()
            for order in self:
                assert order.validity_date, _("Validity date is mandatory")
                assert order.validity_date > today, _(
                    "Validity date must be in the future"
                )
                assert order.partner_id, _("Partner is mandatory")
                assert len(order.line_ids) > 0, _("Must have some lines")
                order.line_ids._validate()
        except AssertionError as e:
            raise UserError(e) from e

    def set_to_draft(self):
        for order in self:
            order.write({"state": "draft", "confirmed": False})
        return True

    def action_confirm(self):
        self._validate()
        for order in self:
            sequence_obj = self.env["ir.sequence"]
            if order.company_id:
                sequence_obj = sequence_obj.with_company(order.company_id.id)
            name = sequence_obj.next_by_code("sale.blanket.order")
            order.write({"confirmed": True, "name": name})
        return True

    def _check_active_orders(self):
        for order in self.filtered("sale_count"):
            for so in order._get_sale_orders():
                if so.state not in ("cancel"):
                    return True
        return False

    def action_cancel(self):
        for order in self:
            if order._check_active_orders():
                raise UserError(
                    _(
                        "You can not delete a blanket order with opened "
                        "sale orders! "
                        "Try to cancel them before."
                    )
                )
            order.write({"state": "expired"})
        return True

    def action_view_sale_orders(self):
        sale_orders = self._get_sale_orders()
        action = self.env.ref("sale.action_orders").read()[0]
        if len(sale_orders) > 0:
            action["domain"] = [("id", "in", sale_orders.ids)]
            action["context"] = [("id", "in", sale_orders.ids)]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def action_view_sale_blanket_order_line(self):
        action = self.env.ref(
            "sale_blanket_order.act_open_sale_blanket_order_lines_view_tree"
        ).read()[0]
        lines = self.mapped("line_ids")
        if len(lines) > 0:
            action["domain"] = [("id", "in", lines.ids)]
        return action

    @api.model
    def expire_orders(self):
        today = fields.Date.today()
        expired_orders = self.search(
            [("state", "=", "open"), ("validity_date", "<=", today)]
        )
        expired_orders.modified(["validity_date"])
        expired_orders.flush_recordset()

    @api.model
    def _search_original_uom_qty(self, operator, value):
        bo_line_obj = self.env["sale.blanket.order.line"]
        res = []
        bo_lines = bo_line_obj.search([("original_uom_qty", operator, value)])
        order_ids = bo_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_ordered_uom_qty(self, operator, value):
        bo_line_obj = self.env["sale.blanket.order.line"]
        res = []
        bo_lines = bo_line_obj.search([("ordered_uom_qty", operator, value)])
        order_ids = bo_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_invoiced_uom_qty(self, operator, value):
        bo_line_obj = self.env["sale.blanket.order.line"]
        res = []
        bo_lines = bo_line_obj.search([("invoiced_uom_qty", operator, value)])
        order_ids = bo_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_delivered_uom_qty(self, operator, value):
        bo_line_obj = self.env["sale.blanket.order.line"]
        res = []
        bo_lines = bo_line_obj.search([("delivered_uom_qty", operator, value)])
        order_ids = bo_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res

    @api.model
    def _search_remaining_uom_qty(self, operator, value):
        bo_line_obj = self.env["sale.blanket.order.line"]
        res = []
        bo_lines = bo_line_obj.search([("remaining_uom_qty", operator, value)])
        order_ids = bo_lines.mapped("order_id")
        res.append(("id", "in", order_ids.ids))
        return res
