# © 2016-2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID
from odoo.api import Environment


# DONE
def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    users = env['res.users'].search(
        ['|', ('active', '=', True), ('active', '=', False)])
    users.write({
        'groups_id': [(4, env.ref('product.group_stock_packaging').id)]})
