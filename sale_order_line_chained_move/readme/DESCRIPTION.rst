This module defines a technical field to store the related sale order line
on stock move level in order to get all chained moves on sale order line side.

In case the stock move contains multiple lines of the same product, Odoo's
default behaviour is to merge those lines into the same one.

With this module, there is the option of preserving one move for each
sale order line, which enables correct tracing of each move back to its source.

Each stock rule can define how the moves it creates should behave.
If at least one move in the chain of moves is set to preserve one move
per sale order line, all moves in the chain will act accordingly.
