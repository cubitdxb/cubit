from odoo import fields, api, models, _


class CubitCompany(models.Model):
    _inherit = 'res.company'

    bank_ids = fields.One2many('res.partner.bank', 'company_id', string='Banks')
    bank_account_detail = fields.Html('Bank Account Details')
    notify_template_id = fields.Many2one('mail.template', string='Notify Email Template')
    overdue_msg_supplier = fields.Html('Supplier Overdue Message')
    overdue_msg = fields.Html('Customer Overdue Message')
    number_of_digits_to_match_from_end = fields.Integer('Number of Digits To Match From End')
    expired_template_id = fields.Many2one('mail.template', string='Expired Email Template')
    rml_footer = fields.Html('Report Footer')
    rml_ls_footer = fields.Html('Report LS Footer')
    cubit_id = fields.Integer('Cubit Id')
    proposal_header = fields.Binary(string='Proposal Banner')

    @api.depends('bank_ids')
    def bank_ids_mapping(self):
        for rec in self:
            rec.partner_id.bank_ids = rec.bank_ids.ids


class BankDetails(models.Model):
    _inherit = 'res.partner.bank'

    footer = fields.Boolean('Display On Reports')
    cubit_id = fields.Integer('Cubit Id')


class ResBank(models.Model):
    _inherit = 'res.bank'

    cubit_id = fields.Integer('Cubit Id')
    swift_code = fields.Char('Swift Code')


class ResUsers(models.Model):
    _inherit = 'res.users'

    cubit_id = fields.Integer('Cubit Id')

    @api.model
    def create(self, vals):
        vals['company_type'] = 'person'
        return super(ResUsers, self).create(vals)


class AccountAccountType(models.Model):
    _inherit = 'account.account.type'

    cubit_id = fields.Integer('Cubit Id')
    internal_group = fields.Selection(
        selection_add=[('none', '/')], ondelete={'none': 'cascade'}
    )


class AccountPaymentTermLine(models.Model):
    _inherit = 'account.payment.term.line'

    cubit_id = fields.Integer('Cubit Id')


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    cubit_id = fields.Integer('Cubit Id')


class AccountAccount(models.Model):
    _inherit = 'account.account'

    cubit_id = fields.Integer('Cubit Id')


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    cubit_id = fields.Integer('Cubit ID')


class AccountTaxInherit(models.Model):
    _inherit = 'account.tax'

    cubit_id = fields.Integer('Cubit ID')


class AccountAssetInherit(models.Model):
    _inherit = 'account.asset'

    cubit_id = fields.Integer('Cubit ID')


class AccountBankStatementInherit(models.Model):
    _inherit = 'account.bank.statement'

    cubit_id = fields.Integer('Cubit ID')


class AccountBankStatementLineInherit(models.Model):
    _inherit = 'account.bank.statement.line'

    cubit_id = fields.Integer('Cubit ID')


class AccountAnalyticInherit(models.Model):
    _inherit = 'account.analytic.account'

    cubit_id = fields.Integer('Cubit ID')
    use_tasks = fields.Boolean('Tasks')
    use_issues = fields.Boolean('Issues')
    manager_id = fields.Many2one('res.users', 'Account Manager')
    parent_id = fields.Many2one('account.analytic.account', 'Parent')
    date_start = fields.Date('Start Date')
    date = fields.Date('End Date')
    # type = fields.Selection([('')])


class AccountAnalyticLineInherit(models.Model):
    _inherit = 'account.analytic.line'

    cubit_id = fields.Integer('Cubit ID')



