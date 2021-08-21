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
from odoo import fields
from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
_logger = logging.getLogger(__name__)

howManyDaysAllowedToChange = 60     # this is the period in which changes are allowed
defaultClockingSource = "fff"       # fff is Odoo Standard Clocking Source
maxAllowedWorkingHours = 12         # max number of hours allowed between Check-In and Check-Out

class attendanceHelpers():

    def __init__(self,  attendanceModel,
                        employee_id, 
                        timestamp, 
                        checkin_or_checkout, 
                        source):

        self.attendanceModel = attendanceModel
        self.employee_id = employee_id
        self.timestamp = timestamp
        self.timestamp_dt = datetime.strptime(timestamp, DATETIME_FORMAT)
        self.checkin_or_checkout = checkin_or_checkout
        self.source = source or defaultClockingSource# in which device RAS2 (for example) was the clocking issued
        self.howManyDaysAllowedToChange = howManyDaysAllowedToChange
        self.warningMessage = None
        self.defaultClockingSource = defaultClockingSource
        self.maxAllowedWorkingHours = maxAllowedWorkingHours

        self.logging_at_the_beginning()
        if self.are_input_parameters_valid():
            self.getPreviousClocking()
            self.setCheckInOrCheckOut()
            if self.checkin_or_checkout == "check_in":
                self.register_CheckIn_creating_a_new_Attendance_Record(self.timestamp, self.source)
            else:
                self.register_CheckOut_in_existing_Attendance_Record()

    def logging_at_the_beginning(self):
        _logger.info(OKBLUE+'this is in hr_attendance---- info:'+ENDC)
        _logger.debug(OKBLUE+"self is:  %s "+ENDC, self )
        #_logger.debug(OKBLUE+"self.env.context is:  %s "+ENDC, self.env.context )
        _logger.debug(OKBLUE+"employee_id is:  %s "+ENDC, self.employee_id)
        _logger.debug(OKBLUE+"employee name is:  %s "+ENDC, self.employee_id.name)
        _logger.debug(OKBLUE+"checkin_or_checkout is:  %s "+ENDC, self.checkin_or_checkout)
        _logger.debug(OKBLUE+"clocking_to_add_or_delete is:  %s "+ENDC, self.timestamp)
        
    def is_timestamp_in_the_future(self):
        return self.timestamp > fields.Datetime.now()

    def is_timestamp_too_old(self):
        NOW = datetime.now()
        self.cutting_date_dt = NOW - relativedelta(days=self.howManyDaysAllowedToChange)

        #self.cutting_date = datetime.strptime(datetime.now().strftime(DATETIME_FORMAT), '%Y-%m-%d') - relativedelta(days=self.howManyDaysAllowedToChange)
        
        # self.cutting_date = self.timestamp.fromtimestamp(
        #                     time.time()-(self.howManyDaysAllowedToChange*24*60*60))

        return self.timestamp_dt < self.cutting_date_dt

    def is_timestamp_already_registered(self, type_of_check):
        if type_of_check not in ("check_in", "check_out"):
            type_of_check = "check_in"
        return self.attendanceModel.search([ ('employee_id', '=', self.employee_id.id),
                                        ( type_of_check, '=', self.timestamp),
                                    ],
                                    order='check_in desc', 
                                    limit=1)

    def is_clocking_source_not_valid(self):
        # TODO: Check if the Source is a Valid Clocking Source
        if self.source == "ffe": # killme, only for test function
            return True
        return False

    def is_checkin_or_checkout_variable_not_valid(self):
        return self.checkin_or_checkout not in ["check_in", "check_out", "not_defined"]

    def are_input_parameters_valid(self):

        if self.is_checkin_or_checkout_variable_not_valid():
            self.warningMessage =  "Could not add the clocking.\n"+ \
                    "Please specify Check-In or Check-Out Input in a valid format." 
            return False           

        if self.is_clocking_source_not_valid():
            self.warningMessage =  "Could not add the clocking.\n"+ \
                    "Timestamp Source is not valid."
            return False

        if self.is_timestamp_in_the_future():
            self.warningMessage =  "Could not add the clocking.\n"+ \
                    "Timestamp is in the future."
            return False

        if self.is_timestamp_too_old():
            self.warningMessage =  "Could not add the clocking.\n"+ \
                    "Timestamp is more than "+ str(self.howManyDaysAllowedToChange) + " days in the past.\n"+ \
                    "You can change the limit of days in the past in the Settings if you like."
            return False

        if self.is_timestamp_already_registered("check_in"):
            self.warningMessage =  "Could not add the clocking.\n"+ \
                    " Timestamp is already registered as a check-in"
            return False
        
        if self.is_timestamp_already_registered("check_out"):
            self.warningMessage =  "Could not add the clocking.\n"+ \
                    " Timestamp is already registered as a check-out"
            return False

        return True     

    def getPreviousClocking(self):
        self.previousCheckIn = self.attendanceModel.search([ ('employee_id', '=', self.employee_id.id),
                                        ( "check_in", '<', self.timestamp),
                                    ],
                                    order='check_in desc', 
                                    limit=1)
        self.previousCheckOut = self.attendanceModel.search([ ('employee_id', '=', self.employee_id.id),
                                        ( "check_out", '<', self.timestamp),
                                    ],
                                    order='check_in desc', 
                                    limit=1)
        _logger.debug(OKCYAN+"self.previousCheckIn.check_in is:  %s "+ENDC, self.previousCheckIn.check_in)
        _logger.debug(OKCYAN+"self.previousCheckOut.check_out is:  %s "+ENDC, self.previousCheckOut.check_out)

## new stuff
        self.previousTimestamp = False
        if not self.previousCheckOut.check_out and not self.previousCheckIn.check_in:
            self.previousClockingType = "check_out"
            return
        if not self.previousCheckOut.check_out and self.previousCheckIn.check_in:
            self.previousClockingType = "check_in"
            self.previousTimestamp = self.previousCheckIn.check_in
            return
        if self.previousCheckOut.check_out and not self.previousCheckIn.check_in:
            self.previousClockingType = "check_out"
            self.previousTimestamp = self.previousCheckOut.check_out
            return
## end of new stuff
 
        if self.previousCheckIn.check_in > self.previousCheckOut.check_out:
            self.previousClockingType = "check_in"
            self.previousTimestamp = self.previousCheckIn.check_in
        else:
            self.previousClockingType = "check_out"
            self.previousTimestamp =  self.previousCheckOut.check_out

    def maxAllowedWorkingHoursNotReached(self, timestamp_1, timestamp_2):
        if not timestamp_1 or not timestamp_2:
            return True
        timestamp_1_dt = datetime.strptime(timestamp_1, DATETIME_FORMAT)
        timestamp_2_dt = datetime.strptime(timestamp_2, DATETIME_FORMAT)
        differenceInHours = abs(timestamp_1_dt - timestamp_2_dt).total_seconds()/3600
        _logger.debug(OKCYAN+"delta is:  %s "+ENDC, differenceInHours)
        return  (differenceInHours < self.maxAllowedWorkingHours)

    def setCheckInOrCheckOut(self):
        if self.checkin_or_checkout == "not_defined":
            if self.previousClockingType == "check_in"  \
               and self.maxAllowedWorkingHoursNotReached(self.timestamp, self.previousTimestamp):
                self.checkin_or_checkout = "check_out"
            else:
                self.checkin_or_checkout = "check_in"
        _logger.debug(OKCYAN+"checkin_or_checkout is:  %s "+ENDC, self.checkin_or_checkout)

    def nextClockingIsASingleton(self, timestamp):
        self.nextCheckIn = self.attendanceModel.search([ ('employee_id', '=', self.employee_id.id),
                                        ( "check_in", '>', timestamp),
                                    ],
                                      order='check_in asc', 
                                    limit=1)     
        return (self.nextCheckIn and not self.nextCheckIn.check_out)

    def make_existing_NextCheckIn_a_CheckOut_of_the_same_Record(self, newAttendance):
            temp = self.nextCheckIn.check_in
            tempSource = self.nextCheckIn.check_in_source

            self.nextCheckIn.unlink()

            newAttendance.check_out = temp
            newAttendance.check_out_source = tempSource

    def register_CheckIn_creating_a_new_Attendance_Record(self, timestamp, source):
        vals = {
                'employee_id': self.employee_id.id,
                'check_in': timestamp,
                'check_in_source': source
            }

        newAttendance = self.attendanceModel.create(vals)

        if self.nextClockingIsASingleton(timestamp) and  \
                self.maxAllowedWorkingHoursNotReached(timestamp, self.nextCheckIn.check_in):
            self.make_existing_NextCheckIn_a_CheckOut_of_the_same_Record(newAttendance)

    def register_new_Timestamp_in_existing_previous_Attendance_Record_as_CheckOut(self):
        self.previousCheckIn.check_out = self.timestamp
        self.previousCheckIn.check_out_source = self.source

    def register_new_Timestamp_as_CheckOut_and_move_existing_CheckOut_to_a_new_CheckIn(self):
        timestamp = self.previousCheckIn.check_out
        source = self.previousCheckIn.check_out_source

        self.register_new_Timestamp_in_existing_previous_Attendance_Record_as_CheckOut()

        self.register_CheckIn_creating_a_new_Attendance_Record(timestamp, source)

    def register_CheckOut_in_existing_Attendance_Record(self):
        if self.previousCheckIn.check_out:
            self.register_new_Timestamp_as_CheckOut_and_move_existing_CheckOut_to_a_new_CheckIn()
        else:
            self.register_new_Timestamp_in_existing_previous_Attendance_Record_as_CheckOut()

    def list_all_attendances(self):
        listOfAllAttendances = self.attendanceModel.search([])
        for attendance in listOfAllAttendances:
            _logger.debug(OKCYAN+"+++++++ attendance is:  %s "+ENDC, attendance) 