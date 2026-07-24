# Copyright 2026 OBS Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # The restriction "own-set" flags became independent stored booleans in this
    # version and the effective restriction now re-inherits from the parent
    # unless that flag is set. Repair databases that carried stale/pinned
    # restriction modes (see the model method for the full policy).
    env["product.product"]._repair_restrict_inheritance()
