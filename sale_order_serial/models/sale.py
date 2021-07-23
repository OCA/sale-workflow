# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    line_serial_list = fields.Text(
        string="Serial List", related="order_line.serial_list"
    )

    def action_fill_serials(self):
        self.mapped("order_line").fill_serials()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    serial_list = fields.Text(string="Serial List", copy=False)
    serial_sequence_id = fields.Many2one("ir.sequence", string="Serial Sequence")

    @api.constrains("serial_list")
    def _constrain_serial_list(self):
        skip_existing_serials_check = self._context.get("skip_existing_serials_check")
        skip_existing_soline_check = self._context.get("skip_existing_soline_check")
        if skip_existing_serials_check and skip_existing_soline_check:
            return True

        serial_model = self.env["stock.production.lot"].sudo()
        sol_model = self.env["sale.order.line"].sudo()
        for line in self.filtered("serial_list"):
            serial_list = line.serial_list.strip("\n").split("\n")
            if not serial_list:
                continue
            if not skip_existing_serials_check:
                existing_serials = serial_model.search([("name", "in", serial_list)])
                if existing_serials:
                    raise ValidationError(
                        "Duplicate existing serial number ids: "
                        + str(existing_serials.ids)
                    )
            if not skip_existing_soline_check:
                for serial in serial_list:
                    potential_lines = sol_model.search(
                        [("serial_list", "like", serial), ("id", "!=", line.id)]
                    )
                    for pl in potential_lines:
                        potential_serial_list = pl.serial_list.split("\n")
                        if serial in potential_serial_list:
                            raise ValidationError(
                                "Sale Line ({}) has serial number: {}".format(
                                    pl.id, serial
                                )
                            )
        return True

    @api.model
    def create(self, values):
        record = super(SaleOrderLine, self).create(values)
        if not record.serial_sequence_id and record.product_id.tracking == "serial":
            # Take from product.
            serial_sequence_id = record.product_id.serial_sequence_id
            # Take from customer
            if record.order_id.partner_id.serial_sequence_id:
                serial_sequence_id = record.order_id.partner_id.serial_sequence_id
            # Take from attributes
            line_sequences = record.product_no_variant_attribute_value_ids.mapped(
                "product_attribute_value_id.serial_sequence_id"
            )
            if line_sequences:
                serial_sequence_id = line_sequences[0]

            if serial_sequence_id:
                record.serial_sequence_id = serial_sequence_id
        return record

    def fill_serials(self):
        for line in self.filtered(
            lambda l: l.product_id.tracking == "serial" and l.product_uom_qty > 0
        ):
            if line.serial_list and line.serial_list.strip():
                ordered_qty = line.product_uom_qty
                serial_list = [
                    x for x in line.serial_list.strip().split("\n") if x.strip()
                ]
                serial_qty = len(serial_list)
                if ordered_qty < serial_qty:
                    raise ValidationError(
                        "Ordered QTY is less than Serials.  Please resolve."
                    )
                if ordered_qty > serial_qty and line.serial_sequence_id:
                    serial_list += [
                        line.serial_sequence_id.next_by_id()
                        for _ in range(int(ordered_qty - serial_qty))
                    ]
                    line.write({"serial_list": "\n".join(serial_list)})
            elif line.serial_sequence_id:
                serial_list = [
                    line.serial_sequence_id.next_by_id()
                    for _ in range(int(line.product_uom_qty))
                ]
                line.write({"serial_list": "\n".join(serial_list)})
