=========================================================================
Odoo Modules needed to operate the RFID Attendance System - RAS2 Terminal
=========================================================================

This module extends the functionality of HR Attendance in order to allow
the logging of employee attendances using an RFID based employee
attendance system.

**Table of contents**

.. contents::
   :local:

Configuration
=============

To use this module, you need to use an external system that calls the method
'register_attendance' of the model 'hr.employee' passing as parameter the
code of the RFID card.

Developers of a compatible RFID based employee attendance system should
be familiar with the outputs of this method and implement proper calls and
management of responses.

It is advisory to create an exclusive user to perform this task. As
user doesn't need several access, it is just essential to perform the check
in/out, a group has been created. Add your attendance device user to
RFID Attendance group.

Usage
=====

#. The HR employee responsible to set up new employees should go to
   'Attendances -> Manage Attendances -> Employees' and register the
   RFID card code of each of your employees. You can use an USB plugged
   RFID reader connected to your computer for this purpose.
#. The employee should put his/her card to the RFID based employee
   attendance system. It is expected that the system will provide some form
   of output of the registration event.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/thingsintouch/attendance/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.
Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* thingsintouch.com

Contributors
~~~~~~~~~~~~

* Luis Burrel <luis.burrel@thingsintouch.com>

Maintainers
~~~~~~~~~~~

This module is maintained by thingsintouch.

