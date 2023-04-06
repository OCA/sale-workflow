# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import groupby


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.constrains("line_ids")
    def _check_split_lines(self):
        lines = self.line_ids.filtered("discount_split_by_sale_line_id")
        if lines:
            groups = groupby(lines, key=type(lines)._get_split_line_group_key)
            if groups and any(len(recs) != 2 for key, recs in groups):
                raise ValidationError(
                    _(
                        "The lines you have created/deleted/modified are"
                        " linked some other ones in the Sale Order.\n"
                        "Please create/delete/modify both lines."
                    )
                )

    @api.model
    def _move_autocomplete_invoice_lines_create(self, vals_list):
        return super()._move_autocomplete_invoice_lines_create(
            [self._update_vals_with_discount_lines(v) for v in vals_list]
        )

    @api.model
    def _update_vals_with_discount_lines(self, move_vals: dict) -> dict:
        invoice_line_vals = move_vals.get("invoice_line_ids")
        if not invoice_line_vals:
            return move_vals

        # We're creating a new invoice: at this point, ``invoice_line_ids``
        # should be an iterable of
        #   (fields.Command.CREATE, virtual_ID or False-ish, {line values})
        # triplets, because lines too should be created anew. If it's not ,
        # then there must be something wrong at the root of this process.
        if any(cmd[0] != fields.Command.CREATE for cmd in invoice_line_vals):
            raise ValueError("Unexpected invoice line values: %s" % invoice_line_vals)

        inv_line_vals = []
        for __, __, line_vals in move_vals["invoice_line_ids"]:
            discount_line_vals = {}
            sale_line_id = line_vals.get("discount_split_by_sale_line_id")
            if sale_line_id:
                sol = self.env["sale.order.line"].browse(sale_line_id)
                discount_line_vals = line_vals.copy()
                line_vals = self._update_line_vals_from_discounted_sale_line(
                    line_vals, sol
                )
                discount_line_vals = (
                    self._update_discount_line_vals_from_discounted_sale_line(
                        discount_line_vals, sol
                    )
                )
            inv_line_vals.append((0, 0, line_vals))
            if discount_line_vals:
                inv_line_vals.append((0, 0, discount_line_vals))
        move_vals.update({"invoice_line_ids": inv_line_vals})
        return move_vals

    @api.model
    def _update_line_vals_from_discounted_sale_line(
        self, line_vals: dict, sale_line: models.Model
    ) -> dict:
        return dict(
            line_vals,
            price_unit=sale_line.origin_price_unit,
            is_split_line=True,
        )

    @api.model
    def _update_discount_line_vals_from_discounted_sale_line(
        self, discount_line_vals: dict, sale_line: models.Model
    ) -> dict:
        product_id = discount_line_vals["product_id"]
        product = self.env["product.product"].browse(product_id)
        account = product.product_tmpl_id.get_product_accounts()["discount"]
        return dict(
            discount_line_vals,
            account_id=account.id,
            price_unit=sale_line.price_unit - sale_line.origin_price_unit,
            name=_("Discount on %s") % discount_line_vals["name"],
            is_split_line=True,
            is_split_discount_line=True,
        )
