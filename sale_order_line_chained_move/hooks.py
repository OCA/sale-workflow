# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def __fill_related(moves, line_id):
    for move in moves:
        move.related_sale_line_id = line_id
        if move.move_orig_ids:
            __fill_related(move.move_orig_ids, line_id)


def _fill_in_related_sale_line(env):
    """Update related_sale_line_id on recursive moves"""
    moves = env["stock.move"].search([("sale_line_id", "!=", False)])
    for move in moves:
        __fill_related(move.move_orig_ids, move.sale_line_id)


def post_init_hook(cr, registry):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _fill_in_related_sale_line(env)
