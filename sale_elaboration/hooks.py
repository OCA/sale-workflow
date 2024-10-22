# Copyright 2022 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def pre_init_hook(env):
    """Create computed columns if not exists when the module is instelled"""
    env.cr.execute(
        """
        ALTER TABLE sale_order_line
        ADD COLUMN IF NOT EXISTS is_elaboration BOOLEAN;
    """
    )
    env.cr.execute(
        """
        ALTER TABLE sale_order_line ADD COLUMN IF NOT EXISTS elaboration_note VARCHAR;
    """
    )
