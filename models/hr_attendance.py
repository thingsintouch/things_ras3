# Copyright 2021 thingsintouch.com
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

import logging
import time
import json
from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)
from . import helpers as h


class HrAttendance(models.Model):

    _inherit = "hr.attendance"


    check_in_source = fields.Char( string="Source of the Check-In TimeStamp", 
                                    default=h.defaultClockingSource, 
                                    required=True)
    check_out_source = fields.Char( string="Source of the Check-Out TimeStamp", 
                                    default=h.defaultClockingSource,
                                    required=True)
    check_in_with_RAS = fields.Boolean( string="Used an RFID Attendance Terminal to check-in?",
                                        default=False,
                                        required=True)
    check_out_with_RAS = fields.Boolean( string="Used an RFID Attendance Terminal to check-out?",
                                        default=False,
                                        required=True)

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we can have :
                * "open" attendance records (without check_out)
            But we must have:
                * no overlapping time slices with previous employee records
        """
        for attendance in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('check_in', '<=', attendance.check_in),
                ('id', '!=', attendance.id),
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > attendance.check_in:
                raise exceptions.ValidationError(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                    'empl_name': attendance.employee_id.name,
                    'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance.check_in))),
                })


    @api.multi
    def add_clocking(   self,
                        employee_id,
                        timestamp, 
                        from_RAS=False, 
                        source=h.defaultClockingSource):
        # _logger.info(OKBLUE+"self.context is:  %s "+ENDC, self.env.context)
        # _logger.info(OKBLUE+"employee_id is:  %s "+ENDC, employee_id)
        # _logger.info(OKBLUE+"clocking_to_add_or_delete is:  %s "+ENDC,
        #                 timestamp)
        # _logger.info(OKBLUE+"checkin_or_checkout is:  %s "+ENDC, checkin_or_checkout)   
        # _logger.info(OKBLUE+"source is:  %s "+ENDC, source)     
        helper = h.attendanceHelpers(self.env['hr.attendance'],
                                    employee_id.id, 
                                    timestamp, 
                                    from_RAS, 
                                    source)

        if helper.warningMessage: return helper.warningMessage

        
        return "all OK"
        #return "Could not add the clocking."


    # @api.multi
    # def delete_clocking(self):
    #     _logger.info( 'this is info:'+WARNING+ 'Button DELETE_timestamp works like a charm'+ENDC)
    #     _logger.debug( 'this is debug debug')
    #     _logger.debug(OKBLUE+"self.context is:  %s "+ENDC, self.env.context ) 
