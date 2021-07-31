# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    rental_view_location_id = fields.Many2one(
        "stock.location",
        "Parent Rental",
        check_company=True,
        domain="[('usage', '=', 'view'), ('company_id', '=', company_id)]",
    )
    rental_in_location_id = fields.Many2one(
        "stock.location",
        "Rental In",
        check_company=True,
        domain="[('usage', '=', 'internal'), ('company_id', '=', company_id)]",
    )
    rental_out_location_id = fields.Many2one(
        "stock.location",
        "Rental Out",
        check_company=True,
        domain="[('usage', '=', 'internal'), ('company_id', '=', company_id)]",
    )
    rental_allowed = fields.Boolean("Rental Allowed")
    rental_route_id = fields.Many2one("stock.location.route", string="Rental Route")
    sell_rented_product_route_id = fields.Many2one(
        "stock.location.route", string="Sell Rented Product Route"
    )

    @api.onchange("rental_allowed")
    def _onchange_rental_allowed(self):
        if not self.rental_allowed:
            self.rental_view_location_id = False
            self.rental_in_location_id = False
            self.rental_out_location_id = False
            self.rental_route_id = False
            self.sell_rented_product_route_id = False

    def _get_rental_push_pull_rules(self):
        self.ensure_one()
        route_obj = self.env["stock.location.route"]
        try:
            rental_route = self.env.ref("sale_rental.route_warehouse0_rental")
        except Exception:
            rental_routes = route_obj.search([("name", "=", _("Rent"))])
            rental_route = rental_routes and rental_routes[0] or False
        if not rental_route:
            raise UserError(_("Can't find any generic 'Rent' route."))
        try:
            sell_rented_product_route = self.env.ref(
                "sale_rental.route_warehouse0_sell_rented_product"
            )
        except Exception:
            sell_rented_product_routes = route_obj.search(
                [("name", "=", _("Sell Rented Product"))]
            )
            sell_rented_product_route = (
                sell_rented_product_routes and sell_rented_product_routes[0] or False
            )
        if not sell_rented_product_route:
            raise UserError(_("Can't find any generic 'Sell Rented Product' route."))
        if not self.rental_in_location_id:
            raise UserError(
                _("The Rental Input stock location is not set on the " "warehouse %s")
                % self.name
            )
        if not self.rental_out_location_id:
            raise UserError(
                _("The Rental Output stock location is not set on the " "warehouse %s")
                % self.name
            )
        rental_pull_rule = {
            "name": self._format_rulename(
                self.rental_in_location_id, self.rental_out_location_id, ""
            ),
            "location_src_id": self.rental_in_location_id.id,
            "location_id": self.rental_out_location_id.id,
            "route_id": rental_route.id,
            "action": "pull",
            "picking_type_id": self.out_type_id.id,
            "warehouse_id": self.id,
            "company_id": self.company_id.id,
        }
        rental_push_rule = {
            "name": self._format_rulename(
                self.rental_out_location_id, self.rental_in_location_id, ""
            ),
            "location_src_id": self.rental_out_location_id.id,
            "location_id": self.rental_in_location_id.id,
            "route_id": rental_route.id,
            "action": "push",
            "picking_type_id": self.in_type_id.id,
            "warehouse_id": self.id,
            "company_id": self.company_id.id,
        }
        customer_loc = self.env.ref("stock.stock_location_customers")
        sell_rented_product_pull_rule = {
            "name": self._format_rulename(
                self.rental_out_location_id, customer_loc, ""
            ),
            "location_src_id": self.rental_out_location_id.id,
            "location_id": customer_loc.id,
            "route_id": sell_rented_product_route.id,
            "action": "pull",
            "picking_type_id": self.out_type_id.id,
            "warehouse_id": self.id,
            "company_id": self.company_id.id,
        }
        res = [
            rental_pull_rule,
            rental_push_rule,
            sell_rented_product_pull_rule,
        ]
        return res

    def _create_rental_locations(self):
        slo = self.env["stock.location"]
        for wh in self:
            # create stock locations
            if not wh.rental_view_location_id:
                view_loc = slo.with_context(lang="en_US").search(
                    [
                        ("name", "ilike", "Rental"),
                        ("location_id", "=", wh.view_location_id.id),
                        ("usage", "=", "view"),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
                if not view_loc:
                    view_loc = slo.with_context(lang="en_US").create(
                        {
                            "name": "Rental",
                            "location_id": wh.view_location_id.id,
                            "usage": "view",
                            "company_id": self.company_id.id,
                        }
                    )
                    slo.browse(view_loc.id).name = _("Rental")
                    logger.debug(
                        "New view rental stock location created ID %d", view_loc.id
                    )
                wh.rental_view_location_id = view_loc.id
            if not wh.rental_in_location_id:
                in_loc = slo.with_context(lang="en_US").search(
                    [
                        ("name", "ilike", "Rental In"),
                        ("location_id", "=", wh.rental_view_location_id.id),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
                if not in_loc:
                    in_loc = slo.with_context(lang="en_US").create(
                        {
                            "name": "Rental In",
                            "location_id": wh.rental_view_location_id.id,
                            "company_id": self.company_id.id,
                        }
                    )
                    slo.browse(in_loc.id).name = _("Rental In")
                    logger.debug(
                        "New in rental stock location created ID %d", in_loc.id
                    )
                wh.rental_in_location_id = in_loc.id
            if not wh.rental_out_location_id:
                out_loc = slo.with_context(lang="en_US").search(
                    [
                        ("name", "ilike", "Rental Out"),
                        ("location_id", "=", wh.rental_view_location_id.id),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
                if not out_loc:
                    out_loc = slo.with_context(lang="en_US").create(
                        {
                            "name": "Rental Out",
                            "location_id": wh.rental_view_location_id.id,
                            "company_id": self.company_id.id,
                        }
                    )
                    slo.browse(out_loc.id).name = _("Rental Out")
                    logger.debug(
                        "New out rental stock location created ID %d", out_loc.id
                    )
                wh.rental_out_location_id = out_loc.id

    def write(self, vals):
        if "rental_allowed" in vals:
            rental_route = self.env.ref("sale_rental.route_warehouse0_rental")
            sell_rented_route = self.env.ref(
                "sale_rental.route_warehouse0_sell_rented_product"
            )
            if vals.get("rental_allowed"):
                self._create_rental_locations()
                self.write(
                    {
                        "route_ids": [(4, rental_route.id)],
                        "rental_route_id": rental_route.id,
                        "sell_rented_product_route_id": sell_rented_route.id,
                    }
                )
                rental_rules = self.env["stock.rule"].search(
                    [
                        ("route_id", "in", [rental_route.id, sell_rented_route.id]),
                        ("active", "=", False),
                    ]
                )
                if rental_rules:
                    rental_rules.write({"active": True})
                else:
                    for rule_vals in self._get_rental_push_pull_rules():
                        self.env["stock.rule"].create(rule_vals)
            else:
                for wh in self:
                    rules_to_archive = self.env["stock.rule"].search(
                        [
                            (
                                "route_id",
                                "in",
                                (
                                    wh.rental_route_id.id,
                                    wh.sell_rented_product_route_id.id,
                                ),
                            ),
                            ("company_id", "=", wh.company_id.id),
                        ]
                    )
                    rules_to_archive.write({"active": False})
                    wh.write(
                        {
                            "route_ids": [(3, rental_route.id)],
                            "rental_route_id": False,
                            "sell_rented_product_route_id": False,
                        }
                    )
        return super().write(vals)
