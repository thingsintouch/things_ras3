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
    _name = 'thingsintouch.attendance.addsingleton'
    _description = 'Add a Singleton Attendance'

    def _default_employee(self):
        OKBLUE = '\033[94m'
        ENDC = '\033[0m'
        print(OKBLUE+"default employee ", self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1), ENDC)
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    clocking_to_add_or_delete = fields.Datetime(
        string="clocking to Add or Delete",
        default=fields.Datetime.now)
    add_timestamp =fields.Boolean(
        string="true if add, false if delete", 
        default="True")    
    employee_id = fields.Many2one('hr.employee', string="Employee")

    # checkout_ids = fields.Many2many(
    #     'library.checkout',
    #     string='Checkouts')
    # message_subject = fields.Char()
    # message_body = fields.Html()

    # @api.model
    # def default_get(self, field_names):
    #     defaults = super().default_get(field_names)
    #     checkout_ids = self.env.context.get('active_ids')
    #     defaults['checkout_ids'] = checkout_ids
    #     return defaults

    @api.multi
    def button_add_clocking(self):
        _logger.info( 'this is info:'+OKBLUE+ 'Button insert_timestamp works like a charm'+ENDC)
        attendanceModel = self.env['hr.attendance']
        _logger.debug(
            OKBLUE+"self.employee_id is:  %s "+ENDC, 
            self.employee_id )         

        # _logger.debug( 'this is debug debug')
        # _logger.debug(
        #     OKBLUE+"dir(self.env) is:  %s "+ENDC, 
        #     dir(self.env) ) 
        # _logger.debug(
        #     OKBLUE+"dir(self.env.ref) is:  %s "+ENDC, 
        #     dir(self.env.ref))
        # _logger.debug(
        #     OKBLUE+"dir(self.env.ref('hr.employee')) is:  %s "+ENDC, 
        #     dir(self.env.ref('hr.employee')))        
        # _logger.debug(
        #     OKBLUE+"self.env['hr.employee'] is:  %s "+ENDC,
        #     self.env['hr.employee'] )
        # _logger.debug(
        #     OKBLUE+"self.env.context is:  %s "+ENDC,
        #     self.env.context )

    @api.multi
    def button_delete_clocking(self):
        _logger.info( 'this is info:'+WARNING+ 'Button DELETE_timestamp works like a charm'+ENDC)
        _logger.debug( 'this is debug debug')
        _logger.debug(OKBLUE+"self.context is:  %s "+ENDC, self.env.context ) 

    #     import pudb; pu.db
    #     self.ensure_one()

    #     if not self.checkout_ids:
    #         raise exceptions.UserError(
    #             'Select at least one Checkout to send messages to.')
    #     if not self.message_body:
    #         raise exceptions.UserError(
    #             'Write a message body to send.')

    #     for checkout in self.checkout_ids:
    #         checkout.message_post(
    #             body=self.message_body,
    #             subject=self.message_subject,
    #             subtype='mail.mt_comment',
    #         )
    #         _logger.debug(
    #             'Message on %d to followers: %s',
    #             checkout.id,
    #             checkout.message_follower_ids)

    #     _logger.info(
    #         'Posted %d messages to Checkouts: %s',
    #         len(self.checkout_ids),
    #         self.checkout_ids.ids,
    #     )
    #     return True