From this change https://github.com/odoo/odoo/pull/243987 , `price_unit` in sale order
lines has a minimum display digits instead of a rounding in screen as it used to be.
This is for compatibility issues with Peppol.

For the cases this isn't needed, the new behavior is quite anoying, as prices computed
from the pricelists or currency conversion often throw quite a bunch of decimals
(e.g.: 10.000023), which is ok for accuracy sake but is terrible for ux.
