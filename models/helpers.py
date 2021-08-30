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
defaultClockingSource = "internal"       # fff is Odoo Standard Clocking Source
maxAllowedWorkingHours = 12         # max number of hours allowed between Check-In and Check-Out

class attendanceHelpers():

    def __init__(self,  attendanceModel,
                        employee_id, 
                        timestamp, 
                        #checkin_or_checkout, 
                        source):

        self.attendanceModel = attendanceModel
        self.employee_id = employee_id
        self.timestamp = timestamp
        self.timestamp_dt = datetime.strptime(timestamp, DATETIME_FORMAT)
        #self.checkin_or_checkout = checkin_or_checkout
        self.source = source or defaultClockingSource # in which device RAS2 (for example) was the clocking issued
        self.howManyDaysAllowedToChange = howManyDaysAllowedToChange
        self.warningMessage = None
        self.defaultClockingSource = defaultClockingSource
        self.maxAllowedWorkingHours = maxAllowedWorkingHours

        #self.logging_at_the_beginning()
        if self.are_input_parameters_valid():
            while self.timestamp is not None:
                self.registerClocking()

    def logging_at_the_beginning(self):
        # _logger.info(OKBLUE+'this is in hr_attendance---- info:'+ENDC)
        # _logger.debug(OKBLUE+"self is:  %s "+ENDC, self )
        # #_logger.debug(OKBLUE+"self.env.context is:  %s "+ENDC, self.env.context )
        # _logger.debug(OKBLUE+"employee_id is:  %s "+ENDC, self.employee_id)
        # #_logger.debug(OKBLUE+"employee name is:  %s "+ENDC, self.employee_id.name)
        # _logger.debug(OKBLUE+"checkin_or_checkout is:  %s "+ENDC, self.checkin_or_checkout)
        # _logger.debug(OKBLUE+"clocking_to_add_or_delete is:  %s "+ENDC, self.timestamp)
        pass
        
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
        return self.attendanceModel.sudo().search([ ('employee_id', '=', self.employee_id),
                                        ( type_of_check, '=', self.timestamp),
                                    ],
                                    order='check_in desc', 
                                    limit=1)

    def is_clocking_source_not_valid(self):
        # TODO: Check if the Source is a Valid Clocking Source
        # if self.source == "ffe": # killme, only for test function
        #     return True
        return False

    # def is_checkin_or_checkout_variable_not_valid(self):
    #     return self.checkin_or_checkout not in ["check_in", "check_out", "not_defined"]

    def are_input_parameters_valid(self):

        # if self.is_checkin_or_checkout_variable_not_valid():
        #     self.warningMessage =  "Could not add the clocking.\n"+ \
        #             "Please specify Check-In or Check-Out Input in a valid format." 
        #     return False           

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

    def get_adjacent_clockings(self):
        self.attendances_check_in_sorted = self.attendanceModel.sudo().search([ ('employee_id', '=', self.employee_id),
                                ('check_in', '!=', False),
                                    ]).sorted(key=lambda r: r.check_in)
        if self.attendances_check_in_sorted:
            if self.timestamp < self.attendances_check_in_sorted[0].check_in:
                self.PCI = False
                self.NCI = self.attendances_check_in_sorted[0]
            else:                              
                self.PCI = self.attendances_check_in_sorted[0]
                self.NCI = False
                for r in self.attendances_check_in_sorted:
                    if r.check_in and r.check_in > self.timestamp:
                        self.NCI = r
                    else:
                        self.PCI = r
                    if self.NCI: break
        else:
            self.PCI = False
            self.NCI = False

        self.attendances_check_out_sorted = self.attendanceModel.sudo().search([ ('employee_id', '=', self.employee_id),
                                ('check_out', '!=', False),
                                    ]).sorted(key=lambda r: r.check_out)
        if self.attendances_check_out_sorted:
            if self.timestamp < self.attendances_check_out_sorted[0].check_out:
                self.PCO = False
                self.NCO = self.attendances_check_out_sorted[0]
            else:                              
                self.PCO = self.attendances_check_out_sorted[0]
                self.NCO = False
                for r in self.attendances_check_out_sorted:
                    if r.check_out and r.check_out > self.timestamp:
                        self.NCO = r
                    else:
                        self.PCO = r
                    if self.NCO: break
        else:
            self.PCO = False
            self.NCO = False

        # _logger.debug(f"self.attendances_sorted  {self.attendances_sorted} ")
        self.previousCheckIn_AttendanceRecord = self.PCI
        self.previousCheckOut_AttendanceRecord = self.PCO
        self.nextCheckIn_AttendanceRecord = self.NCI
        self.nextCheckOut_AttendanceRecord = self.NCO

        if self.PCI:    self.PCI_exists = True
        else:           self.PCI_exists = False

        if self.PCO:    self.PCO_exists = True
        else:           self.PCO_exists = False

        if self.NCI:    self.NCI_exists = True
        else:           self.NCI_exists = False

        if self.NCO:    self.NCO_exists = True
        else:           self.NCO_exists = False

        # _logger.debug(OKCYAN+"############################################ "+ENDC)
        # _logger.debug(OKCYAN+"PCI exists:  %s "+ENDC, self.PCI_exists)
        # _logger.debug(OKCYAN+"self.previousCheckIn_AttendanceRecord is:  %s "+ENDC, self.PCI.check_in)
        # _logger.debug(OKCYAN+"self.previousCheckOut_AttendanceRecord is:  %s "+ENDC, self.PCO.check_out)
        # _logger.debug(OKCYAN+"self.nextCheckIn_AttendanceRecord is:  %s "+ENDC, self.NCI.check_in)
        # _logger.debug(OKCYAN+"self.nextCheckOut_AttendanceRecord is:  %s "+ENDC, self.NCO.check_out)        
        # # _logger.debug(OKCYAN+"self.previousCheckIn.check_in is:  %s "+ENDC, self.previousCheckIn.check_in)
        # # _logger.debug(OKCYAN+"self.previousCheckOut.check_out is:  %s "+ENDC, self.previousCheckOut.check_out)
        # _logger.debug(OKCYAN+"############################################ "+ENDC)

    def prepare_exit_register_clocking_process(self):
        self.timestamp = None
        self.source = None

    def could_register_using_only_PCI_and_PCO(self):
        if self.PCI_exists and not self.PCO_exists:
            if self.register_new_Timestamp_in_existing_PCI_Attendance_Record_as_CheckOut():
                return True
        if self.PCI_exists and self.PCO_exists:
            if self.PCI.check_in > self.PCO.check_out:
                if self.register_new_Timestamp_in_existing_PCI_Attendance_Record_as_CheckOut():
                    return True
        return False

    def register_new_Timestamp_in_existing_PCI_Attendance_Record_as_CheckOut(self):
        def check_out_of_PCI_has_to_be_relocated_in_next_iteration():
            self.temp_timestamp         = self.PCI.check_out
            self.temp_source            = self.PCI.check_out_source
            self.PCI.check_out          = self.timestamp
            self.PCI.check_out_source   = self.source
            self.timestamp              = self.temp_timestamp
            self.source                 = self.temp_source
        def insert_checkout():
            self.PCI.check_out          = self.timestamp
            self.PCI.check_out_source   = self.source
            self.prepare_exit_register_clocking_process()             
 
        if  self.maxAllowedWorkingHoursNotReached(self.timestamp, self.PCI.check_in):
            #_logger.debug(OKCYAN+"self.PCI.check_out: "+ENDC, self.PCI.check_out)
            if self.PCI.check_out:
                check_out_of_PCI_has_to_be_relocated_in_next_iteration()
            else:
                insert_checkout()             
            return True
        return False

    def register_new_Timestamp_in_existing_NCI_Attendance_Record_as_CheckIn(self):

        def move_new_timestamp_to_CI_and_old_CI_to_CO():
            self.temp_timestamp         = self.NCI.check_in
            self.temp_source            = self.NCI.check_in_source
            self.NCI.check_in           = self.timestamp
            self.NCI.check_in_source    = self.source
            self.NCI.check_out          = self.temp_timestamp
            self.NCI.check_out_source   = self.temp_source

        def move_check_in_of_NCI_to_the_check_out():
            _logger.debug(OKCYAN+"in move_check_in_of_NCI_to_the_check_out()"+ENDC)
            if self.NCI.check_out:
                self.to_relocate__timestamp = self.NCI.check_out
                self.to_relocate__source    =  self.NCI.check_out_source
                move_new_timestamp_to_CI_and_old_CI_to_CO()
                self.timestamp              = self.to_relocate__timestamp
                self.source                 = self.to_relocate__source                 
            else:
                move_new_timestamp_to_CI_and_old_CI_to_CO()    
                self.prepare_exit_register_clocking_process()

        _logger.debug(f"self.NCI.check_in: {self.NCI.check_in}-  self.timestamp: {self.timestamp}")
        if  self.maxAllowedWorkingHoursNotReached(self.NCI.check_in, self.timestamp):
            move_check_in_of_NCI_to_the_check_out()
            return True
        return False

    def register_new_Timestamp_in_existing_NCO_Attendance_Record_as_CheckIn(self):
        def register_timestamp_as_check_in_in_existing_NCO():
            self.NCO.check_in           = self.timestamp
            self.NCO.check_in_source    = self.source
            self.prepare_exit_register_clocking_process()             
 
        if  self.maxAllowedWorkingHoursNotReached(self.NCO.check_out, self.timestamp):
            register_timestamp_as_check_in_in_existing_NCO()
            return True
        return False

    def register_CheckIn_creating_a_new_Attendance_Record(self):
        vals = {
                'employee_id': self.employee_id,
                'check_in': self.timestamp,
                'check_in_source': self.source
            }
        newAttendance = self.attendanceModel.sudo().create(vals)
        self.prepare_exit_register_clocking_process()

    def register_new_Timestamp_in_existing_attendance_record_with_NCI_AND_NCO(self):
        def register_and_NCI_NCO_check_out_has_to_be_relocated_in_next_iteration():
            self.temp_timestamp         = self.NCI.check_out
            self.temp_source            = self.NCI.check_out_source
            self.NCI.check_out          = self.timestamp
            self.NCI.check_out_source   = self.source
            self.timestamp              = self.temp_timestamp
            self.source                 = self.temp_source             
 
        if  self.maxAllowedWorkingHoursNotReached(self.timestamp, self.NCI.check_in):
            register_and_NCI_NCO_check_out_has_to_be_relocated_in_next_iteration()             
            return True
        return False


    def could_register_using_NCI_and_NCO(self):
        if self.NCI_exists and not self.NCO_exists:
            if self.register_new_Timestamp_in_existing_NCI_Attendance_Record_as_CheckIn():
                return True
        if not self.NCI_exists and self.NCO_exists:
            if self.register_new_Timestamp_in_existing_NCO_Attendance_Record_as_CheckIn():
                return True
        if self.NCI_exists and self.NCO_exists:
            if self.NCI.check_in > self.NCO.check_out:
                if self.register_new_Timestamp_in_existing_NCO_Attendance_Record_as_CheckIn():
                    return True
            if self.NCI.check_in < self.NCO.check_out:
                if self.register_new_Timestamp_in_existing_NCI_Attendance_Record_as_CheckIn():
                    return True
            if self.NCI == self.NCO: # doesn't need to check because it is the only possibility left
                if self.register_new_Timestamp_in_existing_attendance_record_with_NCI_AND_NCO():
                    return True
        return False

    def registerClocking(self):
        self.get_adjacent_clockings() # PCI PCO NCI NCO

        if self.could_register_using_only_PCI_and_PCO():
            return

        if self.could_register_using_NCI_and_NCO():
            return
        
        self.register_CheckIn_creating_a_new_Attendance_Record()
        return

    def maxAllowedWorkingHoursNotReached(self, timestamp_1, timestamp_2):
        if not timestamp_1 or not timestamp_2:
            return True
        timestamp_1_dt = datetime.strptime(timestamp_1, DATETIME_FORMAT)
        timestamp_2_dt = datetime.strptime(timestamp_2, DATETIME_FORMAT)
        differenceInHours = abs(timestamp_1_dt - timestamp_2_dt).total_seconds()/3600
        _logger.debug(OKCYAN+"delta is:  %s "+ENDC, differenceInHours)
        return  (differenceInHours < self.maxAllowedWorkingHours)


    def nextClockingIsASingleton(self, timestamp):
        self.nextCheckIn = self.attendanceModel.sudo().search([ ('employee_id', '=', self.employee_id),
                                        ( "check_in", '>', timestamp),
                                    ],
                                      order='check_in asc', 
                                    limit=1)     
        return (self.nextCheckIn and not self.nextCheckIn.check_out)


    def list_all_attendances(self):
        listOfAllAttendances = self.attendanceModel.sudo().search([])
        for attendance in listOfAllAttendances:
            _logger.debug(OKCYAN+"+++++++ attendance is:  %s "+ENDC, attendance) 