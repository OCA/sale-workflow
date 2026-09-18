from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _selection_product_tracking(self):
        return self.env["product.product"].fields_get(
            allfields=["tracking"],
        )["tracking"]["selection"]

    product_tracking = fields.Selection(
        selection=_selection_product_tracking,
        compute="_compute_product_tracking",
    )
    domain_lot_id = fields.Binary(compute="_compute_domain_lot_id")
    lot_id = fields.Many2one(
        "stock.lot",
        "Lot",
        domain="domain_lot_id",
        copy=False,
        compute="_compute_lot_id",
        inverse="_inverse_lot_id",
        store=True,
        readonly=False,
        precompute=True,
    )

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        if self.lot_id:
            vals["restrict_lot_id"] = self.lot_id.id
        return vals

    @api.depends("product_id")
    def _compute_product_tracking(self):
        for sol in self:
            sol.product_tracking = sol.product_id.tracking or sol.product_tracking

    def _get_lot_id_quant_domain_locations(self):
        """This method retrieves the location(s) that will later be used in
        _domain_lot_id_quant_domain(). It will be useful to extend this method if,
        for example, you want to search across different multi-warehouse
        locations.
        """
        self.ensure_one()
        return self.warehouse_id.lot_stock_id

    def _domain_lot_id_quant_domain(self):
        """This method defines the domain that will be used to obtain the appropriate
        stock.quant values and is useful for extending to other modules.
        """
        self.ensure_one()
        locations = self._get_lot_id_quant_domain_locations()
        return [
            ("product_id", "=", self.product_id.id),
            ("quantity", ">=", self.product_uom_qty),
            ("lot_id", "!=", False),
            ("location_id", "child_of", locations.ids),
        ]

    @api.depends("product_id", "product_uom_qty", "warehouse_id")
    def _compute_domain_lot_id(self):
        dp = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        for sol in self:
            domain = []
            if sol.product_id and sol.product_tracking != "none":
                # Only available lots should be displayed. In pickings, the
                # corresponding stock.quant record is selected directly, so we
                # use the same filters that are used.
                quants = self.env["stock.quant"].search(
                    sol._domain_lot_id_quant_domain()
                )
                available_quants = quants.filtered(
                    lambda x, qty=sol.product_uom_qty: float_compare(
                        x.available_quantity,
                        qty,
                        precision_digits=dp,
                    )
                    >= 0
                )
                available_lots = available_quants.mapped("lot_id")
                if (
                    sol.company_id.sale_order_lot_selection_exclude_pending_orders
                    and sol.product_tracking == "serial"
                ):
                    available_lots -= (
                        self.env["sale.order.line"]
                        .sudo()
                        .search(
                            [
                                ("state", "in", ("draft", "sent")),
                                ("lot_id", "!=", False),
                                ("product_uom_qty", ">", 0),
                                ("id", "!=", sol._origin.id or 0),
                            ]
                        )
                        .mapped("lot_id")
                    )
                domain = [("id", "in", available_lots.ids)]
            sol.domain_lot_id = domain

    @api.depends("product_id", "order_id.warehouse_id")
    def _compute_lot_id(self):
        lines_to_check = self.filtered(
            lambda sol: sol.lot_id
            and sol.product_id == sol.lot_id.product_id
            and sol.order_id.warehouse_id
        )
        (self - lines_to_check).lot_id = False

        if not lines_to_check:
            return

        warehouses = lines_to_check.mapped("order_id.warehouse_id")
        # Validity is scoped per (warehouse, lot) pair: a lot with stock in
        # one warehouse must not validate lines of another warehouse.
        valid_pairs = set()

        for wh in warehouses:
            wh_lines = lines_to_check.filtered(
                lambda line, w=wh: line.order_id.warehouse_id == w
            )
            lot_ids = wh_lines.mapped("lot_id").ids
            if not lot_ids:
                continue

            quants = self.env["stock.quant"].search_read(
                [
                    ("lot_id", "in", lot_ids),
                    ("location_id", "child_of", wh.view_location_id.id),
                    ("quantity", ">", 0),
                ],
                ["lot_id"],
            )
            valid_pairs.update((wh.id, q["lot_id"][0]) for q in quants)

        for sol in lines_to_check:
            if (sol.order_id.warehouse_id.id, sol.lot_id.id) not in valid_pairs:
                sol.lot_id = False

    def _inverse_lot_id(self):
        for item in self.filtered(
            lambda x: x.product_id and x.product_tracking != "none" and x.move_ids
        ):
            moves = item.move_ids.filtered(lambda x: x.restrict_lot_id)
            if any(move.state == "done" for move in moves):
                raise ValidationError(
                    self.env._(
                        "You can't modify the Lot/Serial number "
                        "because some stock move has already been done."
                    )
                )
            pending_moves = moves.filtered(lambda x: x.state != "cancel")
            if pending_moves:
                pending_moves._set_restrict_lot_id_from_sol(item.lot_id)

    def action_split_lines_by_lot(self, lot_qty_dict):
        """
        Divides the sale order line into multiple lines according to
        the specified lots and quantities.
        lot_qty_dict is a dictionary {lot_id (int): qty (float)}
        """
        self.ensure_one()
        if not lot_qty_dict:
            return self

        # We manage lines for the same product that either already have a lot
        # or are the current line being split. We avoid touching other lines
        # (e.g., added manually without a lot) to prevent data loss.
        lines_to_manage = self.order_id.order_line.filtered(
            lambda ln: ln.product_id == self.product_id
            and (ln.lot_id or ln.id == self.id)
        )

        # Sort lines to reuse `self` first, then others
        lines_list = [self] + [ln for ln in lines_to_manage if ln.id != self.id]

        new_lines = self.env["sale.order.line"]
        items = [(int(lot), qty) for lot, qty in lot_qty_dict.items() if qty > 0]

        for i, (lot_id, qty) in enumerate(items):
            if i < len(lines_list):
                # Reuse existing line
                lines_list[i].lot_id = lot_id
                lines_list[i].product_uom_qty = qty
                if i != 0:
                    new_lines |= lines_list[i]
            else:
                # Create a new line by copying `self`
                new_line = self.copy(
                    {
                        "lot_id": lot_id,
                        "product_uom_qty": qty,
                        "order_id": self.order_id.id,
                    }
                )
                new_lines |= new_line

        # Remove any leftover lines that are no longer needed
        leftover_lines = self.env["sale.order.line"]
        for ln in lines_list[len(items) :]:
            leftover_lines |= ln
        if leftover_lines:
            leftover_lines.unlink()

        return self | new_lines

    def get_available_lots_for_line(self):
        self.ensure_one()
        if not self.product_id or not self.product_id.is_storable:
            return []

        domain = [
            ("product_id", "=", self.product_id.id),
            ("quantity", ">", 0),
        ]
        if self.order_id.warehouse_id:
            domain.append(
                (
                    "location_id",
                    "child_of",
                    self.order_id.warehouse_id.view_location_id.id,
                )
            )

        quants = self.env["stock.quant"]._read_group(
            domain, ["lot_id"], ["quantity:sum", "reserved_quantity:sum"]
        )

        # Get pending unreserved quantities for these lots
        # Moves that are outgoing, not done/cancel, and restrict_lot_id is set
        move_domain = [
            ("product_id", "=", self.product_id.id),
            (
                "state",
                "in",
                ["confirmed", "waiting", "partially_available", "assigned"],
            ),
            ("restrict_lot_id", "!=", False),
        ]
        if self.order_id.warehouse_id:
            move_domain.append(
                (
                    "location_id",
                    "child_of",
                    self.order_id.warehouse_id.view_location_id.id,
                )
            )

        pending_moves = self.env["stock.move"]._read_group(
            move_domain, ["restrict_lot_id"], ["product_uom_qty:sum", "quantity:sum"]
        )
        pending_by_lot = {
            lot.id: max(0, uom_qty - res_qty)
            for lot, uom_qty, res_qty in pending_moves
            if lot
        }

        available = []
        for lot, qty, reserved in quants:
            if not lot:
                continue

            pending_unreserved = pending_by_lot.get(lot.id, 0.0)
            qty_available = qty - reserved - pending_unreserved

            if qty_available <= 0:
                continue

            expiration_date = False
            if hasattr(lot, "expiration_date") and lot.expiration_date:
                expiration_date = lot.expiration_date.strftime("%Y-%m-%d")

            available.append(
                {
                    "id": lot.id,
                    "name": lot.name,
                    "qty": qty_available,
                    "expiration_date": expiration_date,
                }
            )

        # Sort available lots: FEFO (First Expired First Out) then FIFO (by ID)
        def sort_key(lot_info):
            exp_date = lot_info["expiration_date"]
            if exp_date:
                return (0, exp_date, lot_info["id"])
            else:
                return (1, "", lot_info["id"])

        available.sort(key=sort_key)

        # Aggregate selected lots for this product across all lines in the same order
        selected = {}
        for line in self.order_id.order_line.filtered(
            lambda line: line.product_id == self.product_id and line.lot_id
        ):
            selected[line.lot_id.id] = (
                selected.get(line.lot_id.id, 0.0) + line.product_uom_qty
            )

        return {
            "available": available,
            "selected": selected,
        }
