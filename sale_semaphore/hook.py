# Copyright 2025 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(env):
    env.cr.execute(
        """
        ALTER TABLE sale_order_line
            ADD COLUMN IF NOT EXISTS semaphore VARCHAR DEFAULT '';
        """
    )
    env.cr.execute(
        """
        ALTER TABLE sale_order_line
            ADD COLUMN IF NOT EXISTS semaphore_active BOOLEAN DEFAULT FALSE;
        """
    )
