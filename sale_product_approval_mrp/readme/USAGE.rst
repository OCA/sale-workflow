* A User will not be able to manually add a product that is not in an approved state for manufacturing to the MO.
  If a product is moved to a state where the 'Approved to be Manufactured' is not set, then the manufacturing order will show an exception:
  Same for if a product is moved to a state where the 'Approved to be a Component on a Manufacturing Order' is not set, then the manufacturing order will show an exception
  In both of the above cases, if a user tries clicks either the 'Confirm' or 'Mark as Done' buttons, then a warning shows informing the user that there is an exception.

* For Work Orders on a Manufacturing Order which has an exception, if the user clicks either the 'Start' or 'Done' buttons, a warning shows information the user that there is an exception on the manufacturing order.

* For Bill of Materials, same logic applies as above so if a product that is on a BoM. If an existing product on a BoM is moved to a non-approved state then the BoM will show the exceptions.
  A User will not be able to manually add a product that is not in an approved state for manufacturing to the BoM.
