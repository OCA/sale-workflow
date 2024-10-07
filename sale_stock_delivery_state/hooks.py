# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    sales = env["sale.order"].search([])
    sales._compute_oca_delivery_status()
