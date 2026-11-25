To grant read-only access to the sales documents, select *Readonly* under the
*Sales* privilege in the user form (Settings / Users).

Holding the *Readonly* option grants read-only access to the sales documents on
the user, with no create, write or unlink right. Selecting another option of
the *Sales* privilege replaces it, as the privilege options are mutually
exclusive.

Users holding the group get:

* read access to quotations, sales orders, order lines and sales analysis;
* the *Quotations*, *Orders*, *Customers* and *Products* menus of the Sales
  application.

As the *Readonly* option is shared between the Sales applications, it also
grants read-only access to the documents of the other installed modules using
it (e.g. `crm_readonly` for the leads/opportunities).

Notes:

* The Sales root menu is only active when the `sale_management` application is
  installed (or any other module activating it).
* Action buttons on the sales orders (Confirm, Create Invoice, ...) are still
  displayed but raise an access error for users holding only this group.
