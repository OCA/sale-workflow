from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lot_id = fields.Many2one(
        "stock.lot",
        "Lot",
        copy=False,
        compute="_compute_lot_id",
        store=True,
        readonly=False,
    )

    def _prepare_procurement_values(self):
        vals = super()._prepare_procurement_values()
        if self.lot_id:
            vals["restrict_lot_id"] = self.lot_id.id
        return vals

    @api.depends("product_id", "order_id.warehouse_id")
    def _compute_lot_id(self):
        for sol in self:
            if sol.product_id != sol.lot_id.product_id:
                sol.lot_id = False
            elif sol.lot_id and sol.order_id.warehouse_id:
                quants = self.env["stock.quant"].search(
                    [
                        ("lot_id", "=", sol.lot_id.id),
                        (
                            "location_id",
                            "child_of",
                            sol.order_id.warehouse_id.view_location_id.id,
                        ),
                        ("quantity", ">", 0),
                    ],
                    limit=1,
                )
                if not quants:
                    sol.lot_id = False

    def action_split_lines_by_lot(self, lot_qty_dict):
        """
        Divides the sale order line into multiple lines according to
        the specified lots and quantities.
        lot_qty_dict is a dictionary {lot_id (int): qty (float)}
        """
        self.ensure_one()
        if not lot_qty_dict:
            return self

        # Evitar duplicaciones si se re-ejecuta el widget para el mismo producto.
        # Eliminamos otras líneas del mismo producto en esta misma orden.
        other_lines = self.order_id.order_line.filtered(
            lambda ln: ln.product_id == self.product_id and ln.id != self.id
        )
        if other_lines:
            other_lines.unlink()

        new_lines = self.env["sale.order.line"]
        is_first = True
        for lot_id, qty in lot_qty_dict.items():
            lot_id = int(lot_id)
            if qty <= 0:
                continue
            if is_first:
                self.lot_id = lot_id
                self.product_uom_qty = qty
                is_first = False
            else:
                new_line = self.copy(
                    {
                        "lot_id": lot_id,
                        "product_uom_qty": qty,
                        "order_id": self.order_id.id,
                    }
                )
                new_lines |= new_line

        # If the original line's quantity is now 0 (e.g., all selected lots had 0 qty),
        # we might want to unlink it, but usually the widget handles valid dicts.
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
            domain, ["lot_id"], ["quantity:sum"]
        )

        available = []
        for lot, qty in quants:
            if not lot:
                continue

            expiration_date = False
            if hasattr(lot, "expiration_date") and lot.expiration_date:
                expiration_date = lot.expiration_date.strftime("%Y-%m-%d")

            available.append(
                {
                    "id": lot.id,
                    "name": lot.name,
                    "qty": qty,
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
