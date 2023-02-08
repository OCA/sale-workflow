# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import api, fields, models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        for move in self:
            if move.picking_id:
                # Write dummy variable so that the state of the
                #  picking will be updated.
                move.picking_id.dummy_int_to_trigger_state_update = (
                    move.picking_id.dummy_int_to_trigger_state_update + 1
                ) % 2
                if (
                    self._context.get("payment_check", True)
                    and move.picking_id.is_on_hold()
                ):
                    # Do not assign picking because it is on hold
                    return False
        return super(StockMove, self)._action_assign()

    def _search_picking_for_assignation(self):
        self.ensure_one()
        picking = self.env["stock.picking"].search(
            [
                ("group_id", "=", self.group_id.id),
                ("location_id", "=", self.location_id.id),
                ("location_dest_id", "=", self.location_dest_id.id),
                ("picking_type_id", "=", self.picking_type_id.id),
                ("printed", "=", False),
                (
                    "state",
                    "in",
                    [
                        "draft",
                        "confirmed",
                        "waiting",
                        "partially_available",
                        "assigned",
                        "hold",
                    ],
                ),
            ],
            limit=1,
        )
        return picking


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends(
        "move_type",
        "dummy_int_to_trigger_state_update",
        "immediate_transfer",
        "move_lines.state",
        "move_lines.picking_id",
    )
    def _compute_state(self):
        """State of a picking depends on the state of its related stock.move
        - Draft: only used for "planned pickings"
        - Waiting: if the picking is not ready to be sent so if
          - (a) no quantity could be reserved at all or if
          - (b) some quantities could be reserved and the shipping policy is
          "deliver all at once"
        - Waiting another move: if the picking is waiting for another move
        - Ready: if the picking is ready to be sent so if:
          - (a) all quantities are reserved or if
          - (b) some quantities could be reserved and the shipping policy is
          "as soon as possible"
        - Done: if the picking is done.
        - Cancelled: if the picking is cancelled
        """
        # self.ensure_one()
        picking_moves_state_map = defaultdict(dict)
        picking_move_lines = defaultdict(set)
        for move in self.env["stock.move"].search([("picking_id", "in", self.ids)]):
            picking_id = move.picking_id
            move_state = move.state
            picking_moves_state_map[picking_id.id].update(
                {
                    "any_draft": picking_moves_state_map[picking_id.id].get(
                        "any_draft", False
                    )
                    or move_state == "draft",
                    "all_cancel": picking_moves_state_map[picking_id.id].get(
                        "all_cancel", True
                    )
                    and move_state == "cancel",
                    "all_cancel_done": picking_moves_state_map[picking_id.id].get(
                        "all_cancel_done", True
                    )
                    and move_state in ("cancel", "done"),
                }
            )
            picking_move_lines[picking_id.id].add(move.id)
        for picking in self:
            picking_id = (picking.ids and picking.ids[0]) or picking.id
            if not picking_moves_state_map[picking_id]:
                picking.state = "draft"
            elif picking_moves_state_map[picking_id]["any_draft"]:
                picking.state = "draft"
            elif picking_moves_state_map[picking_id]["all_cancel"]:
                picking.state = "cancel"
            elif picking_moves_state_map[picking_id]["all_cancel_done"]:
                picking.state = "done"
            else:
                states = ["confirmed", "assigned", "partially_available"]
                relevant_move_state = (
                    self.env["stock.move"]
                    .browse(picking_move_lines[picking_id])
                    ._get_relevant_state_among_moves()
                )
                if relevant_move_state in states and picking.is_on_hold():
                    picking.state = "hold"
                elif picking.immediate_transfer and relevant_move_state not in (
                    "draft",
                    "cancel",
                    "done",
                ):
                    picking.state = "assigned"
                elif relevant_move_state == "partially_available":
                    picking.state = "assigned"
                else:
                    picking.state = relevant_move_state

    dummy_int_to_trigger_state_update = fields.Integer(
        string="Dummy Integer (to trigger update of state field)"
    )

    state = fields.Selection(
        selection_add=[("hold", "Waiting For Payment"), ("assigned",)],
        ondelete={"hold": "set confirmed"},
    )

    @api.depends("immediate_transfer", "state")
    def _compute_show_check_availability(self):
        for picking in self:
            if picking.immediate_transfer or picking.state not in (
                "confirmed",
                "waiting",
                "assigned",
                "hold",
            ):
                picking.show_check_availability = False
                continue
            picking.show_check_availability = any(
                move.state in ("waiting", "confirmed", "partially_available")
                and float_compare(
                    move.product_uom_qty,
                    0,
                    precision_rounding=move.product_uom.rounding,
                )
                for move in picking.move_lines
            )

    @api.depends("state")
    def _compute_show_validate(self):
        states = ("draft", "waiting", "confirmed", "assigned", "hold")
        for picking in self:
            if self._context.get("planned_picking") and picking.state == "draft":
                picking.show_validate = False
            elif picking.state not in states or not picking.is_locked:
                picking.show_validate = False
            else:
                picking.show_validate = True

    def is_on_hold(self):
        """Returns True if picking should be held because the
        corresponding order has not been paid yet."""
        self.ensure_one()
        # Skip checking of the payment
        if not self._context.get("payment_check", True):
            return False
        if (
            self.sale_id
            and self.sale_id.hold_picking_until_payment
            and not self.sale_id.invoice_status == "invoiced"
        ):
            return True
        return False

    def action_assign_unpaid(self):
        self.with_context(payment_check=False).action_assign()
        self.write({"state": "assigned"})
