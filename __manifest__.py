# Copyright 2017 Comunitea Servicios Tecnológicos S.L.
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# Copyright 2021 http://www.thingsintouch.com
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Things RAS3',
    'summary': "Connect Odoo with your RFID Attendance Terminal RAS3",       
    'description': """Manage your Attendances using a RFID Attendance Terminal RAS3.
        """,

    'version': '13.0.5.0.211118',
    'category': 'Things',
    'website': 'https://github.com/thingsintouch/things_ras3/tree/13.0',
    'author': 'Comunitea,'
              'Eficent,'
              'Odoo Community Association (OCA)'
              'thingsintouch.com',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'hr_attendance_rfid',
        'things_gateway',
    ],
    'data': [
        'security/things_ras3_security.xml',
        'security/ir.model.access.csv',
        #'views/hr_employee_view.xml',
        'views/hr_attendance_view.xml',
        'wizard/add_singleton.xml',
        'views/res_config_settings_views.xml',
    ],
}
