# Copyright 2026 arielbarreiros96
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from ast import literal_eval

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.fields import Domain


class ProductLabelTrackingRule(models.Model):
    _name = "product.label.tracking.rule"
    _description = "Label Tracking Rule"
    _check_company_auto = True
    _order = "name, id"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company
    )
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        required=True,
        default=lambda self: self.env.user,
        domain="[('share', '=', False)]",
    )
    location_id = fields.Many2one(
        "stock.location",
        domain="[('usage', '=', 'internal')]",
        check_company=True,
        help="Only track products with stock on hand in this location "
        "or any of its children.",
    )
    include_non_storable = fields.Boolean(
        help="Track goods without stock tracking as if they were always "
        "present in the location.",
    )
    product_domain = fields.Char(
        default="[]",
        required=True,
        help="Products to track. Leave empty to track all goods.",
    )
    pricelist_id = fields.Many2one(
        "product.pricelist",
        check_company=True,
        help="Track the price of this pricelist. Leave empty to track the "
        "sales price of the product.",
    )
    interval_number = fields.Integer(string="Scan Every", default=1, required=True)
    interval_type = fields.Selection(
        [("hours", "Hours"), ("days", "Days"), ("weeks", "Weeks")],
        string="Scan Interval",
        default="days",
        required=True,
    )
    last_scan_date = fields.Datetime(readonly=True, copy=False)
    next_scan_date = fields.Datetime(
        compute="_compute_next_scan_date", store=True, copy=False
    )
    track_ids = fields.One2many("product.label.track", "rule_id")
    track_count = fields.Integer(compute="_compute_track_count")

    _interval_number_positive = models.Constraint(
        "CHECK(interval_number > 0)",
        "The scan interval must be positive.",
    )

    @api.depends("last_scan_date", "interval_number", "interval_type")
    def _compute_next_scan_date(self):
        for rule in self:
            rule.next_scan_date = rule.last_scan_date and (
                rule.last_scan_date
                + relativedelta(**{rule.interval_type: rule.interval_number})
            )

    def _compute_track_count(self):
        counts = dict(
            self.env["product.label.track"]._read_group(
                Domain("rule_id", "in", self.ids), ["rule_id"], ["__count"]
            )
        )
        for rule in self:
            rule.track_count = counts.get(rule, 0)

    def _get_stocked_product_ids(self):
        groups = self.env["stock.quant"]._read_group(
            Domain("location_id", "child_of", self.location_id.id)
            & Domain("product_id.is_storable", "=", True),
            ["product_id"],
            ["quantity:sum"],
        )
        return [product.id for product, quantity in groups if quantity > 0]

    def _get_product_domain(self):
        self.ensure_one()
        domain = (
            Domain("type", "=", "consu")
            & Domain("company_id", "in", [False, self.company_id.id])
            & Domain(literal_eval(self.product_domain or "[]"))
        )
        if self.location_id:
            located = Domain("id", "in", self._get_stocked_product_ids())
            if self.include_non_storable:
                located |= Domain("is_storable", "=", False)
            domain &= located
        return domain

    def _get_prices(self, products):
        self.ensure_one()
        if self.pricelist_id:
            return self.pricelist_id._get_products_price(products, 1.0)
        return {product.id: product.lst_price for product in products}

    def _get_currency(self):
        self.ensure_one()
        return self.pricelist_id.currency_id or self.company_id.currency_id

    def action_scan(self):
        for rule in self:
            rule.with_company(rule.company_id)._scan()
        return True

    def _scan(self):
        self.ensure_one()
        Track = self.env["product.label.track"]
        products = self.env["product.product"].search(self._get_product_domain())
        prices = self._get_prices(products)
        currency = self._get_currency()
        open_tracks, last_tracks, last_printed = {}, {}, {}
        for track in Track.search(
            Domain("rule_id", "=", self.id) & Domain("product_id", "in", products.ids)
        ):
            key = track.product_id.id
            if track.state in Track.OPEN_STATES:
                open_tracks[key] = track
                continue
            last_tracks.setdefault(key, track)
            if track.state == "printed":
                last_printed.setdefault(key, track)
        vals_list = []
        for product in products:
            price = prices[product.id]
            track = open_tracks.get(product.id)
            if track:
                if currency.compare_amounts(price, track.price):
                    track._update_price(price)
                continue
            last = last_tracks.get(product.id)
            if last and not currency.compare_amounts(price, last.price):
                continue
            vals = {"rule_id": self.id, "product_id": product.id, "price": price}
            if product.id in last_printed:
                vals["previous_price"] = last_printed[product.id].printed_price
            vals_list.append(vals)
        # Pending state changes must reach the database before inserting, or
        # the one-open-track index still sees the previous track as open.
        Track.flush_model(["state"])
        Track.create(vals_list)
        self.last_scan_date = fields.Datetime.now()

    @api.model
    def _cron_scan(self):
        rules = self.search(
            Domain("next_scan_date", "=", False)
            | Domain("next_scan_date", "<=", fields.Datetime.now())
        )
        rules.action_scan()

    def action_view_tracks(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "product_price_label_tracking.product_label_track_action"
        )
        action["domain"] = [("rule_id", "=", self.id)]
        action["context"] = {"search_default_new": 1, "search_default_updated": 1}
        return action
