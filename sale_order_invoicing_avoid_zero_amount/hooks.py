# Copyright 2026 Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def post_init_hook(env):
    """Refresh the already stored invoice status of the pending orders."""
    orders = env["sale.order"].search([("invoice_status", "=", "to invoice")])
    env.add_to_compute(orders._fields["invoice_status"], orders)
