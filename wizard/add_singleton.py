from odoo import api, exceptions, fields, models

import logging
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

class AddSingleton(models.TransientModel):
    _name = 'hr.employee.singletonclocking'
    _description = 'Add or Delete a Singleton Clocking'

    clocking_to_add_or_delete = fields.Datetime(
        string="Timestamp",
        default=fields.Datetime.now)
    # checkin_or_checkout=fields.Selection([
    #     ('check_in', 'Check-In'),
    #     ('check_out', 'Check-Out'),
    #     ('not_defined', 'Not Defined')],
    #     string='Checkin or Checkout', 
    #     default="not_defined")
    # add_timestamp =fields.Boolean(
    #     string="true if add, false if delete", 
    #     default="True")    
    employee_id = fields.Many2one('hr.employee', string="Employee")
    source = fields.Char(   string="Source of the TimeStamp")


    @api.multi
    def button_add_clocking(self):
        self.ensure_one()
        # _logger.info( 'this is info:'+OKBLUE+ 'Button insert_timestamp works like a charm'+ENDC)
        # _logger.info(OKBLUE+"self.context is:  %s "+ENDC, self.env.context)
        # _logger.info(OKBLUE+"employee_id is:  %s "+ENDC, self.employee_id)
        # _logger.info(OKBLUE+"clocking_to_add_or_delete is:  %s "+ENDC,
        #                 self.clocking_to_add_or_delete)
        # _logger.info(OKBLUE+"checkin_or_checkout is:  %s "+ENDC, self.checkin_or_checkout)   
        # _logger.info(OKBLUE+"source is:  %s "+ENDC, self.source)
                                     
        # _logger.info(OKBLUE+"employee name is:  %s "+ENDC, self.employee_id.name)

        if not self.employee_id:
            raise exceptions.UserError(
                'Please select an Employee')

        if not self.clocking_to_add_or_delete:
            raise exceptions.UserError(
                'Please enter a time stamp.')

        attendanceModel = self.env['hr.attendance']

        result = attendanceModel.add_clocking(  self.employee_id,
                                                self.clocking_to_add_or_delete,
                                                from_RAS=False,
                                                source=self.source)

        if result != "all OK":
            raise exceptions.ValidationError(result)

        _logger.debug(OKBLUE+"result:  %s "+ENDC, result)
        return True


    # @api.multi
    # def button_delete_clocking(self):
    #     self.ensure_one()
    #     _logger.info( 'this is info:'+WARNING+ 'Button DELETE_timestamp works like a charm'+ENDC)
    #     _logger.debug( 'this is debug debug')
    #     _logger.debug(OKBLUE+"self.context is:  %s "+ENDC, self.env.context )
    #     _logger.debug(OKBLUE+"employee_id is:  %s "+ENDC, self.employee_id)

    
