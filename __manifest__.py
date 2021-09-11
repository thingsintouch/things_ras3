# Copyright 2021 http://www.thingsintouch.com
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Things RAS3',
    'summary': "Connect Odoo with your RFID Attendance Terminal RAS3",       
    'description': """Manage your Attendances using a RFID Attendance Terminal RAS3.
        """,

    'version': '11.0.5.0.210910',
    'category': 'Things',
    'website': 'https://github.com/thingsintouch/things_attendance/tree/12.0',
    'author': 'thingsintouch.com',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'hr_attendance_rfid',
        'things_gateway',
    ],
    'data': [
        'views/hr_employee_view.xml',
        'wizard/add_singleton.xml',
        'views/res_config_settings_views.xml',
    ],
}
