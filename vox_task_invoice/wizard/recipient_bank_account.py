# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
# from odoo.exceptions import UserError


class UpdateReceipientBank(models.TransientModel):
    _name = 'update.recipient.bank'

    partner_bank_id = fields.Many2one('res.partner.bank', string="Recipient Bank Account",
                                      readonly=False, store=True, tracking=True)
    #                                   compute='_compute_partner_bank_id',
    #                                   domain="[('id', 'in', available_partner_bank_ids)]")
    #                                   # check_company=True)
    #
    # bank_partner_id = fields.Many2one('res.partner', help='Technical field to get the domain on the bank', compute='_compute_bank_partner_id')

    # @api.depends('commercial_partner_id')
    # def _compute_bank_partner_id(self):
    #     for move in self:
    #         if move.is_inbound():
    #             move.bank_partner_id = move.company_id.partner_id
    #         else:
    #             move.bank_partner_id = move.commercial_partner_id


    move_id = fields.Many2one(
        'account.move', string='Invoice', readonly=True)


    @api.model
    def _prepare_default_get(self, order):
        default = {
            'move_id': order.id,
            'partner_bank_id': order.partner_bank_id.id,

        }
        return default

    @api.model
    def default_get(self, fields):
        res = super(UpdateReceipientBank, self).default_get(fields)
        assert self._context.get('active_model') == 'account.move', \
            'active_model should be account.move'
        order = self.env['account.move'].browse(self._context.get('active_id'))
        default = self._prepare_default_get(order)
        res.update(default)
        return res

    def _prepare_update_so(self):
        self.ensure_one()
        return {
            'partner_bank_id': self.partner_bank_id.id,
        }

    def action_post(self):
        self.ensure_one()
        self.move_id.action_post()
        vals = self._prepare_update_so()
        self.move_id.write(vals)
        return True


