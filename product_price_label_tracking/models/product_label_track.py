# Copyright 2026 arielbarreiros96
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductLabelTrack(models.Model):
    _name = "product.label.track"
    _description = "Label Track"
    _rec_name = "product_id"
    _order = "id desc"

    OPEN_STATES = ("new", "updated")

    rule_id = fields.Many2one(
        "product.label.tracking.rule",
        required=True,
        readonly=True,
        index=True,
        ondelete="cascade",
    )
    product_id = fields.Many2one(
        "product.product",
        required=True,
        readonly=True,
        index=True,
        ondelete="cascade",
    )
    location_id = fields.Many2one(related="rule_id.location_id", store=True)
    pricelist_id = fields.Many2one(related="rule_id.pricelist_id", store=True)
    user_id = fields.Many2one(related="rule_id.user_id", store=True, index=True)
    company_id = fields.Many2one(related="rule_id.company_id", store=True)
    currency_id = fields.Many2one(
        "res.currency", compute="_compute_currency_id", store=True
    )
    price = fields.Monetary(readonly=True)
    previous_price = fields.Monetary(readonly=True)
    printed_price = fields.Monetary(readonly=True)
    state = fields.Selection(
        [
            ("new", "New"),
            ("updated", "Updated"),
            ("printed", "Printed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="new",
        required=True,
        readonly=True,
        index=True,
    )

    _printed_price_only_when_printed = models.Constraint(
        "CHECK(state = 'printed' OR printed_price = 0)",
        "Only printed tracks have a printed price.",
    )
    _one_open_track_per_rule_product = models.UniqueIndex(
        "(rule_id, product_id) WHERE state IN ('new', 'updated')",
        "A product can only have one pending track per rule.",
    )

    @api.depends("rule_id.pricelist_id.currency_id", "rule_id.company_id.currency_id")
    def _compute_currency_id(self):
        for track in self:
            track.currency_id = track.rule_id._get_currency()

    def _update_price(self, price):
        """Follow a new price on a pending track: back to the price on the
        shelf cancels it, anything else marks it as updated."""
        self.ensure_one()
        cancel = self.previous_price and not self.currency_id.compare_amounts(
            price, self.previous_price
        )
        self.write({"price": price, "state": "cancelled" if cancel else "updated"})

    def _check_state(self, states):
        wrong = self.filtered(lambda track: track.state not in states)
        if wrong:
            raise UserError(
                self.env._(
                    "This action is not allowed on the track of %(product)s "
                    "because of its status.",
                    product=wrong[0].product_id.display_name,
                )
            )

    def action_mark_printed(self):
        self._check_state(self.OPEN_STATES)
        for track in self:
            track.write({"state": "printed", "printed_price": track.price})
        return True

    def action_cancel(self):
        self._check_state(self.OPEN_STATES)
        self.state = "cancelled"
        return True

    def action_reset_to_new(self):
        self._check_state(("printed", "cancelled"))
        self.write({"state": "new", "printed_price": False})
        return True

    def action_print_labels(self):
        tracks = self.filtered(lambda track: track.state in self.OPEN_STATES)
        if not tracks:
            raise UserError(self.env._("Select at least one new or updated track."))
        if len(set(tracks.mapped(lambda track: track.pricelist_id.id))) > 1:
            raise UserError(
                self.env._(
                    "The selected tracks belong to different pricelists. "
                    "Group them by pricelist and print one group at a time."
                )
            )
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "product.action_open_label_layout"
        )
        action["context"] = {
            "default_label_track_ids": tracks.ids,
            "default_product_ids": tracks.product_id.ids,
            "default_pricelist_id": tracks.pricelist_id.id,
        }
        return action
