# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from odoo.tools.misc import format_date

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
            bo.original_uom_qty = sum(bo.mapped("line_ids.original_uom_qty"))
            bo.ordered_uom_qty = sum(bo.mapped("line_ids.ordered_uom_qty"))
            bo.invoiced_uom_qty = sum(bo.mapped("line_ids.invoiced_uom_qty"))
            bo.delivered_uom_qty = sum(bo.mapped("line_ids.delivered_uom_qty"))
            bo.remaining_uom_qty = sum(bo.mapped("line_ids.remaining_uom_qty"))

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
        action = self.env["ir.actions.act_window"]._for_xml_id("sale.action_orders")
        if len(sale_orders) > 0:
            action["domain"] = [("id", "in", sale_orders.ids)]
            action["context"] = [("id", "in", sale_orders.ids)]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def action_view_sale_blanket_order_line(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "sale_blanket_order.act_open_sale_blanket_order_lines_view_tree"
        )
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


class BlanketOrderLine(models.Model):
    _name = "sale.blanket.order.line"
    _description = "Blanket Order Line"
    _inherit = ["mail.thread", "mail.activity.mixin", "analytic.mixin"]

    @api.depends(
        "original_uom_qty",
        "price_unit",
        "taxes_id",
        "order_id.partner_id",
        "product_id",
        "currency_id",
    )
    def _compute_amount(self):
        for line in self:
            price = line.price_unit
            taxes = line.taxes_id.compute_all(
                price,
                line.currency_id,
                line.original_uom_qty,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )
            line.update(
                {
                    "price_tax": sum(
                        t.get("amount", 0.0) for t in taxes.get("taxes", [])
                    ),
                    "price_total": taxes["total_included"],
                    "price_subtotal": taxes["total_excluded"],
                }
            )

    name = fields.Char("Description", tracking=True)
    sequence = fields.Integer()
    order_id = fields.Many2one("sale.blanket.order", required=True, ondelete="cascade")
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        domain=[("sale_ok", "=", True)],
    )
    product_uom = fields.Many2one("uom.uom", string="Unit of Measure")
    price_unit = fields.Float(string="Price", digits="Product Price")
    taxes_id = fields.Many2many(
        "account.tax",
        string="Taxes",
        domain=["|", ("active", "=", False), ("active", "=", True)],
    )
    date_schedule = fields.Date(string="Scheduled Date")
    original_uom_qty = fields.Float(
        string="Original quantity", default=1, digits="Product Unit of Measure"
    )
    ordered_uom_qty = fields.Float(
        string="Ordered quantity", compute="_compute_quantities", store=True
    )
    invoiced_uom_qty = fields.Float(
        string="Invoiced quantity", compute="_compute_quantities", store=True
    )
    remaining_uom_qty = fields.Float(
        string="Remaining quantity", compute="_compute_quantities", store=True
    )
    remaining_qty = fields.Float(
        string="Remaining quantity in base UoM",
        compute="_compute_quantities",
        store=True,
    )
    delivered_uom_qty = fields.Float(
        string="Delivered quantity", compute="_compute_quantities", store=True
    )
    sale_lines = fields.One2many(
        "sale.order.line",
        "blanket_order_line",
        string="Sale order lines",
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        related="order_id.company_id", store=True, index=True, precompute=True
    )
    currency_id = fields.Many2one("res.currency", related="order_id.currency_id")
    partner_id = fields.Many2one(related="order_id.partner_id", string="Customer")
    user_id = fields.Many2one(related="order_id.user_id", string="Responsible")
    payment_term_id = fields.Many2one(
        related="order_id.payment_term_id", string="Payment Terms"
    )
    pricelist_id = fields.Many2one(related="order_id.pricelist_id", string="Pricelist")

    price_subtotal = fields.Monetary(
        compute="_compute_amount", string="Subtotal", store=True
    )
    price_total = fields.Monetary(compute="_compute_amount", string="Total", store=True)
    price_tax = fields.Float(compute="_compute_amount", string="Tax", store=True)
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )

    def name_get(self):
        result = []
        if self.env.context.get("from_sale_order"):
            for record in self:
                res = "[%s]" % record.order_id.name
                if record.date_schedule:
                    formatted_date = format_date(record.env, record.date_schedule)
                    res += " - {}: {}".format(_("Date Scheduled"), formatted_date)
                res += " ({}: {} {})".format(
                    _("remaining"),
                    record.remaining_uom_qty,
                    record.product_uom.name,
                )
                result.append((record.id, res))
            return result
        return super().name_get()

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
        :param obj product: object of current product record
        :param float qty: total quentity of product
        :param tuple price_and_rule: tuple(price, suitable_rule) coming
               from pricelist computation
        :param obj uom: unit of measure of current order line
        :param integer pricelist_id: pricelist id of sale order"""
        # Copied and adapted from the sale module
        PricelistItem = self.env["product.pricelist.item"]
        field_name = "lst_price"
        currency_id = None
        product_currency = None
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if pricelist_item.pricelist_id.discount_policy == "without_discount":
                while (
                    pricelist_item.base == "pricelist"
                    and pricelist_item.base_pricelist_id
                    and pricelist_item.base_pricelist_id.discount_policy
                    == "without_discount"
                ):
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(
                        uom=uom.id
                    )._get_product_price_rule(product, qty, uom)
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == "standard_price":
                field_name = "standard_price"
            if pricelist_item.base == "pricelist" and pricelist_item.base_pricelist_id:
                field_name = "price"
                product = product.with_context(
                    pricelist=pricelist_item.base_pricelist_id.id
                )
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        product_currency = (
            product_currency
            or (product.company_id and product.company_id.currency_id)
            or self.env.company.currency_id
        )
        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(
                    product_currency, currency_id
                )

        product_uom = product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id.id

    def _get_display_price(self, product):
        # Copied and adapted from the sale module
        self.ensure_one()
        pricelist = self.order_id.pricelist_id
        partner = self.order_id.partner_id
        if self.order_id.pricelist_id.discount_policy == "with_discount":
            return product.with_context(pricelist=pricelist.id).lst_price
        final_price, rule_id = pricelist._get_product_price_rule(
            self.product_id, self.original_uom_qty or 1.0, self.product_uom
        )
        context_partner = dict(
            self.env.context, partner_id=partner.id, date=fields.Date.today()
        )
        base_price, currency_id = self.with_context(
            **context_partner
        )._get_real_price_currency(
            self.product_id,
            rule_id,
            self.original_uom_qty,
            self.product_uom,
            pricelist.id,
        )
        if currency_id != pricelist.currency_id.id:
            currency = self.env["res.currency"].browse(currency_id)
            base_price = currency.with_context(**context_partner).compute(
                base_price, pricelist.currency_id
            )
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.onchange("product_id", "original_uom_qty")
    def onchange_product(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if self.product_id:
            name = self.product_id.name
            if not self.product_uom:
                self.product_uom = self.product_id.uom_id.id
            if self.order_id.partner_id and float_is_zero(
                self.price_unit, precision_digits=precision
            ):
                self.price_unit = self._get_display_price(self.product_id)
            if self.product_id.code:
                name = "[{}] {}".format(name, self.product_id.code)
            if self.product_id.description_sale:
                name += "\n" + self.product_id.description_sale
            self.name = name

            fpos = self.order_id.fiscal_position_id
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.company.id
                self.taxes_id = fpos.map_tax(
                    self.product_id.taxes_id.filtered(
                        lambda r: r.company_id.id == company_id
                    )
                )
            else:
                self.taxes_id = fpos.map_tax(self.product_id.taxes_id)

    @api.depends(
        "sale_lines.order_id.state",
        "sale_lines.blanket_order_line",
        "sale_lines.product_uom_qty",
        "sale_lines.product_uom",
        "sale_lines.qty_delivered",
        "sale_lines.qty_invoiced",
        "original_uom_qty",
        "product_uom",
    )
    def _compute_quantities(self):
        for line in self:
            sale_lines = line.sale_lines
            line.ordered_uom_qty = sum(
                sl.product_uom._compute_quantity(sl.product_uom_qty, line.product_uom)
                for sl in sale_lines
                if sl.order_id.state != "cancel" and sl.product_id == line.product_id
            )
            line.invoiced_uom_qty = sum(
                sl.product_uom._compute_quantity(sl.qty_invoiced, line.product_uom)
                for sl in sale_lines
                if sl.order_id.state != "cancel" and sl.product_id == line.product_id
            )
            line.delivered_uom_qty = sum(
                sl.product_uom._compute_quantity(sl.qty_delivered, line.product_uom)
                for sl in sale_lines
                if sl.order_id.state != "cancel" and sl.product_id == line.product_id
            )
            line.remaining_uom_qty = line.original_uom_qty - line.ordered_uom_qty
            line.remaining_qty = line.product_uom._compute_quantity(
                line.remaining_uom_qty, line.product_id.uom_id
            )

    def _validate(self):
        try:
            for line in self:
                assert (
                    not line.display_type and line.price_unit > 0.0
                ) or line.display_type, _("Price must be greater than zero")
                assert (
                    not line.display_type and line.original_uom_qty > 0.0
                ) or line.display_type, _("Quantity must be greater than zero")
        except AssertionError as e:
            raise UserError(e) from e

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get(
                "display_type", self.default_get(["display_type"])["display_type"]
            ):
                values.update(product_id=False, price_unit=0, product_uom=False)

        return super().create(vals_list)

    _sql_constraints = [
        (
            "accountable_required_fields",
            """
            CHECK(
                display_type IS NOT NULL OR (
                    product_id IS NOT NULL AND product_uom IS NOT NULL
                    )
            )
            """,
            "Missing required fields on accountable sale order line.",
        ),
        (
            "non_accountable_null_fields",
            """
            CHECK(
                display_type IS NULL OR (
                    product_id IS NULL AND price_unit = 0 AND product_uom IS NULL
                    )
            )
            """,
            "Forbidden values on non-accountable sale order line",
        ),
    ]

    def write(self, values):
        if "display_type" in values and self.filtered(
            lambda line: line.display_type != values.get("display_type")
        ):
            raise UserError(
                _(
                    """
                    You cannot change the type of a sale order line.
                    Instead you should delete the current line and create a new line
                    of the proper type.
                    """
                )
            )
        return super(BlanketOrderLine, self).write(values)
