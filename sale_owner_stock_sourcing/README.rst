Sale Owner Stock Sourcing
=========================

This module allow you to choose for every sale order line the owner of the
stock that will be dispatched.  By choosing an owner, the generated deliveries
will then look for stock of the specified partner.  If no one is available,
then the picking will be in waiting availability until stocks of the proper
ownership are replenished.

Specifying an owner on a line, forces to use the stock of this owner.  Letting
the owner empty allows to use stock (quant) without owner.

Note: pickings and moves both have a owner field. Here we only propagate the
owner to moves. We have integration tests that check that this does end up with
the correct reservation of quants, even if two order lines have different
owners. If we decide instead to propagate the owner_id field of the picking as
well, we will have to split pickings accordingly in case a sale order has lines
with different owners. See the discussion on
https://github.com/odoo/odoo/pull/4548 for details.


Contributors
------------

* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Leonardo Pistone <leonardo.pistone@camptocamp.com>
