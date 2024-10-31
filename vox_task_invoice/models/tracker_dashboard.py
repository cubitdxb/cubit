# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResCompany(models.Model):
    _inherit = "res.company"


    @api.model
    def action_open_check_tracker_onboarding(self):
        """ Called by the 'check tracker' button of the setup bar."""

        company = self.env.company
        # company.sudo().set_onboarding_step_done('account_setup_taxes_state')
        view_id_list = self.env.ref('vox_task_invoice.view_cheque_tracker_tree').id
        view_id_form = self.env.ref('vox_task_invoice.check_tracker_form2').id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Check Tracker'),
            'res_model': 'check.tracker',
            'target': 'current',
            'views': [[view_id_list, 'list'], [view_id_form, 'form']],
            # 'context': {'search_default_sale': True, 'search_default_purchase': True, 'active_test': False},
        }