# Copyright 2021 Tecnativa - Carlos Dauden
# Copyright 2021 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ast import literal_eval

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    missing_tracking_count = fields.Integer(compute="_compute_missing_tracking_count")

    def _compute_missing_tracking_count(self):
        groups = (
            self.env["sale.missing.tracking"]
            .sudo()
            .read_group(
                domain=[("order_id", "in", self.ids)],
                fields=["order_id"],
                groupby=["order_id"],
            )
        )
        groups_dic = {g["order_id"][0]: g["order_id_count"] for g in groups}
        for sale_order in self:
            sale_order.missing_tracking_count = groups_dic.get(sale_order.id, 0)

    def _get_missing_exception_product_ids(self):
        self.ensure_one()
        groups = (
            self.env["sale.missing.tracking.exception"]
            .sudo()
            .read_group(
                domain=[
                    ("partner_id", "=", self.partner_id.id),
                    ("state", "=", "approved"),
                    ("product_id.sale_missing_tracking", "=", True),
                ],
                # Don't works "product_ids:array_agg(distinct(product_id))"
                fields=["product_ids:array_agg(product_id)"],
                groupby=[],
            )
        )
        return groups[0]["product_ids"] or []

    def _get_missing_product_ids(self, now):
        SaleOrderLine = self.env["sale.order.line"]
        # Get habitual products
        order_ids = self.search(
            [
                ("company_id", "=", self.company_id.id),
                ("state", "in", ("sale", "done")),
                ("partner_id", "=", self.partner_id.id),
                (
                    "date_order",
                    ">=",
                    now - relativedelta(days=self.company_id.sale_missing_days_from),
                ),
                (
                    "date_order",
                    "<=",
                    now - relativedelta(days=self.company_id.sale_missing_days_to),
                ),
            ]
        ).ids
        # Improve performance because "normal domain" search all orders < date_x and
        # all orders > date_y and add those huge lists to domain (from 2400ms to 270ms)
        groups = SaleOrderLine.sudo().read_group(
            domain=[
                ("product_id.sale_missing_tracking", "=", True),
                ("order_id", "in", order_ids),
            ],
            fields=["product_ids:array_agg(product_id)"],
            groupby=[],
        )
        habitual_product_set = set(groups[0]["product_ids"] or [])
        # Remove exceptions
        exception_product_set = set(self._get_missing_exception_product_ids())
        missing_product_set = habitual_product_set - exception_product_set
        # Get and remove already sold products
        groups = SaleOrderLine.sudo().read_group(
            domain=[
                ("company_id", "=", self.company_id.id),
                ("order_partner_id", "=", self.partner_id.id),
                "|",
                ("order_id", "=", self.id),
                ("state", "in", ("sale", "done")),
                ("product_id", "in", tuple(habitual_product_set)),
                ("product_uom_qty", ">", 0.0),
                (
                    "order_id.date_order",
                    ">",
                    now - relativedelta(days=self.company_id.sale_missing_days_to),
                ),
            ],
            fields=["product_ids:array_agg(product_id)"],
            groupby=[],
        )
        sold_product_set = set(groups[0]["product_ids"] or [])
        missing_product_set -= sold_product_set
        ICP = self.env["ir.config_parameter"].sudo()
        relativedelta_params = ICP.get_param(
            "sale_missing_tracking.already_notified_relativedelta_params",
        )
        if missing_product_set and relativedelta_params:
            relativedelta_params = literal_eval(relativedelta_params)
            already_notified = self.env["sale.missing.tracking"].read_group(
                domain=[
                    ("product_id", "in", list(missing_product_set)),
                    ("user_id", "=", self.user_id.id),
                    ("partner_id", "=", self.partner_id.id),
                    (
                        "date_order",
                        ">",
                        fields.Datetime.now() + relativedelta(**relativedelta_params),
                    ),
                ],
                fields=["product_ids:array_agg(product_id)"],
                groupby=[],
            )
            missing_product_set -= set(already_notified[0]["product_ids"] or [])
        return list(missing_product_set)

    def _get_missing_products(self):
        self.ensure_one()
        now = fields.Datetime.now()
        missing_product_ids = self._get_missing_product_ids(now)
        groups = (
            self.env["sale.order.line"]
            .sudo()
            .read_group(
                domain=[
                    ("company_id", "=", self.company_id.id),
                    ("order_partner_id", "=", self.partner_id.id),
                    ("state", "in", ("sale", "done")),
                    ("product_id", "in", missing_product_ids),
                    (
                        "order_id.date_order",
                        ">=",
                        now
                        - relativedelta(
                            months=self.company_id.sale_missing_months_consumption
                        ),
                    ),
                ],
                fields=["product_id", "price_subtotal"],
                groupby=["product_id"],
            )
        )
        missing_product_dict = {}
        minimal_consumption = self.company_id.sale_missing_minimal_consumption
        for group in groups:
            if group["price_subtotal"] >= minimal_consumption:
                missing_product_dict[group["product_id"][0]] = group["price_subtotal"]
        return missing_product_dict

    def _create_missing_cart_tracking(self):
        missing_product_dict = self._get_missing_products()
        vals_list = []
        for product_id, consumption in missing_product_dict.items():
            vals_list.append(
                {
                    "order_id": self.id,
                    "product_id": product_id,
                    "consumption": consumption,
                }
            )
        missing_tracking = self.env["sale.missing.tracking"].sudo().create(vals_list)
        return missing_tracking

    @api.model
    def _action_missing_tracking(self, missing_trackings):
        wiz = self.env["sale.missing.tracking.wiz"].create(
            {"missing_tracking_ids": [(6, 0, missing_trackings.ids)]}
        )
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale_missing_tracking.action_sale_missing_tracking_wiz"
        )
        action["view_mode"] = "form"
        action["res_id"] = wiz.id
        action["flags"] = {
            "withControlPanel": False,
        }
        action["context"] = {"form_view_initial_mode": "edit"}
        action["target"] = "new"
        return action

    def recover_missing_tracking(self):
        for order in self:
            product_ids = []
            for line in order.order_line:
                if line.product_uom_qty > 0.0 and line.product_id.sale_missing_tracking:
                    product_ids.append(line.product_id.id)
            to_recover_trackings = self.env["sale.missing.tracking"].search(
                [
                    ("partner_id", "=", order.partner_id.id),
                    ("product_id", "in", product_ids),
                    ("state", "in", ["draft", "request", "refused"]),
                    (
                        "date_order",
                        "<=",
                        order.date_order
                        + relativedelta(days=self.company_id.sale_missing_days_to),
                    ),
                ]
            )
            to_recover_trackings.write({"state": "recovered"})

    def action_confirm(self):
        if not self.env.context.get("bypass_missing_cart_tracking"):
            SaleMissingTracking = self.env["sale.missing.tracking"]
            missing_trackings = SaleMissingTracking.browse()
            # Remove old tracking linked to this order
            SaleMissingTracking.sudo().search([("order_id", "in", self.ids)]).unlink()
            for order in self:
                if not order.partner_id.sale_missing_tracking:
                    continue
                order.recover_missing_tracking()
                missing_trackings += self._create_missing_cart_tracking()
            if missing_trackings:
                return self._action_missing_tracking(missing_trackings)
        res = super().action_confirm()
        return res

    def action_pending_missing_tracking_reason(self):
        missing_trackings = self.env["sale.missing.tracking"].search(
            [("reason_id", "=", False)]
        )
        return self._action_missing_tracking(missing_trackings)

    def action_open_missing_tracking(self):
        missing_trackings = self.env["sale.missing.tracking"].search(
            [("order_id", "in", self.ids)]
        )
        return self._action_missing_tracking(missing_trackings)

    def action_cancel(self):
        """Remove missing tracking linked"""
        res = super().action_cancel()
        trackings = self.env["sale.missing.tracking"].search(
            [("order_id", "in", self.ids)]
        )
        trackings.state = "cancel"
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.product_id and line.order_id.state == "sale":
                trackings = self.env["sale.missing.tracking"].search(
                    [
                        ("order_id", "=", line.order_id.id),
                        ("product_id", "=", line.product_id.id),
                    ]
                )
                trackings.state = "recovered"
        return lines
