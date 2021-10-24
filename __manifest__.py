# Copyright 2021 http://www.thingsintouch.com
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Things RAS3',
    'summary': "Connect Odoo with your RFID Attendance Terminal RAS3",       
    'description': """Manage your Attendances using a RFID Attendance Terminal RAS3.
        """,

    'version': '10.0.5.0.211027',
    'category': 'Things',
    'website': 'https://github.com/thingsintouch/things_ras3/tree/10.0',
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
        'views/hr_attendance_view.xml',
        'wizard/add_singleton.xml',
        'views/res_config_settings_views.xml',
    ],
}
