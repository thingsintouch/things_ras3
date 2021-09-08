# Copyright 2017 Comunitea Servicios Tecnológicos S.L.
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging
import time
import json
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

class HrEmployee(models.Model):

    _inherit = "hr.employee"

    @api.multi
    def register_attendance_with_external_timestamp(self, timestamp = None):
        """ allows to register attendance with external timestamp
        """
        if len(self) > 1:
            raise exceptions.UserError(_('Cannot perform check in or check out on multiple employees.'))

        if not timestamp:
            timestamp = fields.Datetime.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            print("in attendance_action_change_sync - got timestamp as an input from outside the method (call)", timestamp)

        print("in attendance_action_change_sync - timestamp ", timestamp)

        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'check_in': timestamp,
            }
            print("in attendance_action_change_sync - when checked_out - self", self)
            print("in attendance_action_change_sync - when checked_out - self.attendance_state ", self.attendance_state)
            return self.env['hr.attendance'].create(vals)
        else:
            attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
            if attendance:
                print("in attendance_action_change_sync - when checked_in - self", self)
                print("in attendance_action_change_sync - when checked_in - self.attendance_state ", self.attendance_state)
                attendance.check_out = timestamp
            else:
                raise exceptions.UserError(_('Cannot perform check out on %(empl_name)s, could not find corresponding check in. '
                    'Your attendances have probably been modified manually by human resources.') % {'empl_name': self.name, })
            return attendance

    @api.model
    def registerAttendanceWithExternalTimestamp(self, card_code, timestamp = None ):
        """ Register the attendance of the employee.
        :returns: dictionary
            'rfid_card_code': char
            'employee_name': char
            'employee_id': int
            'error_message': char
            'logged': boolean
            'action': check_in/check_out
        """
        #timestamp= None

        res = {
            'rfid_card_code': card_code,
            'employee_name': '',
            'employee_id': False,
            'error_message': '',
            'logged': False,
            'action': 'FALSE',
        }
        employee = self.search([('rfid_card_code', '=', card_code)], limit=1)
        if not timestamp:
            timestamp = fields.Datetime.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            print("in register_attendance - got timestamp as an input from outside the method (call)", timestamp)
        print("in register_attendance - timestamp: ", timestamp)
        print("in register_attendance - fields.Datetime.to_datetime(time.strftime())", fields.Datetime.to_datetime(time.strftime("%Y-%m-%d %H:%M:%S")))
        if employee:
            res['employee_name'] = employee.name
            res['employee_id'] = employee.id
        else:
            msg = _("No employee found with card %s") % card_code
            #_logger.warning(msg)
            res['error_message'] = msg
            return res
        try:
            attendance = employee.register_attendance_with_external_timestamp(timestamp)
            print("in register_attendance - attendance: ", attendance)
            if attendance:
                msg = _('Attendance recorded for employee %s') % employee.name
                #_logger.debug(msg)
                res['logged'] = True
                if attendance.check_out:
                    res['action'] = 'check_out'
                else:
                    res['action'] = 'check_in'
                print("in register_attendance - res: ", res)
                return res
            else:
                msg = _('No attendance was recorded for '
                        'employee %s') % employee.name
                #_logger.error(msg)
                res['error_message'] = msg
                return res
        except Exception as e:
            res['error_message'] = e
            _logger.error(e)
        return res

    @api.model
    def registerMultipleAsyncAttendances(self, attendancesToDispatch):
        """ Register the attendance of the employee.
        :returns: string
        "All OK"
        "Something went wrong"
        """
        response = "All OK"
        for attendance in attendancesToDispatch:
            res = self.registerAttendanceWithExternalTimestamp(attendance[0], attendance[1])
            if res['action']==attendance[2]:
                print("wonderful, there is concordance database and async checkinORcheckout")
            else:
                print("Oh! no concordance database and async checkinORcheckout")
                response = "Something went wrong"

        return response

    @api.model
    def get_attendance_information_of_all_employees(self, number_of_days=60):
        """Returns a dictionary/json file with this indices:
                employees:      all data of employees indexed with employee.id
                rfid_card_code: contains employee.id
           Input:
            number_of_days: only the attendance records from
                the last number_of_days are passed 
        """
        def is_attendance_to_be_sent(attendance):

            def is_attendance_in_the_future():
                return attendance.check_in > fields.Datetime.now()

            def is_attendance_too_old():
                cutting_date = attendance.check_in.fromtimestamp(time.time()-(number_of_days*24*60*60))
                return attendance.check_in < cutting_date

            if is_attendance_in_the_future():
                return False
            if is_attendance_too_old():
                return False
            return True

        def get_attendances_to_be_sent(employee):
            attendances = self.env['hr.attendance'].search(
                [('employee_id', '=', employee.id),
                ])
            attendances_to_be_sent = {}
            for attendance in attendances:
                if is_attendance_to_be_sent(attendance):
                    #the index is "check_in" to allow easy ordering
                    attendances_to_be_sent[str(attendance.check_in)] = {
                            "id": attendance.id,
                            "check_out": str(attendance.check_out),
                            "worked_hours": float(attendance.worked_hours),                        
                            }
            return attendances_to_be_sent

        # answer to employee query attendance from RAS2
        answer = {  'employees': {} ,
                    'rfid_codes_to_ids': {},
                    'ids_with_no_rfid_codes': [] }

        all_employees = self.env['hr.employee'].search([])

        for employee in all_employees:

            answer['employees'][employee.id]= {
                'name': employee.name ,
                'attendances': get_attendances_to_be_sent(employee),
                'rfid_card_code': employee.rfid_card_code,
                }

            if employee.rfid_card_code:
                answer['rfid_codes_to_ids'][employee.rfid_card_code]= {
                'id': employee.id ,
                }
            else:
                answer['ids_with_no_rfid_codes'].append(employee.id)

        #json_attendance_information_of_all_employees = json.dumps(answer, indent = 4)
        json_attendance_information_of_all_employees = json.dumps(answer)    
        print(json_attendance_information_of_all_employees)

        return json_attendance_information_of_all_employees

    @api.model
    def get_rfid_codes_with_names(self):
        """Returns a dictionary/json file with this index:
                rfid_card_code: contains name of the employee
        """
        # answer to employee query attendance from RAS2
        answer = {  'rfid_codes_to_names': {} }

        all_employees = self.env['hr.employee'].search([])

        for employee in all_employees:

            if employee.rfid_card_code:
                answer['rfid_codes_to_names'][employee.rfid_card_code] = employee.name

        # json_rfid_codes_with_names = json.dumps(answer)    
        # _logger.debug(f'json_rfid_codes_with_names {json_rfid_codes_with_names} ')
        #_logger.debug(f'answer get_rfid_codes_with_names {answer} ')

        return answer

