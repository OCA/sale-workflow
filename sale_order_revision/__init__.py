# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from . import models


def populate_unrevisioned_name(cr, registry):
    cr.execute('UPDATE sale_order '
               'SET unrevisioned_name = name '
               'WHERE unrevisioned_name is NULL')
