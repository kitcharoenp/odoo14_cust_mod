# -*- coding: utf-8 -*-
# @author Kitcharoen Poolperm <kitcharoenp@gmail.com>
# @copyright Copyright (C) 2017
# @license http://opensource.org/licenses/gpl-3.0.html GNU Public License

from datetime import datetime

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError


class TelcoPurchaseAdvancePayment(models.TransientModel):
    _name = "telco.purchase.advance.payment"
    _description = "Purchase Advance Payment Invoice"

    @api.model
    def _count(self):
        return len(self._context.get('active_ids', []))

    # Deposit Product
    @api.model
    def _default_product_id(self):
        product_id = self.env[
            'ir.config_parameter'].sudo().get_param(
                'sale.default_deposit_product_id')
        return self.env['product.product'].browse(int(product_id)).exists()

    # Expense Account
    @api.model
    def _default_expense_account_id(self):
        return self._default_product_id()._get_product_accounts()['expense']

    # Vendor Taxes
    @api.model
    def _default_expense_taxes_id(self):
        return self._default_product_id().supplier_taxes_id

    @api.model
    def _default_currency_id(self):
        if self._context.get(
            'active_model') == 'purchase.order' and self._context.get(
                'active_id', False):
            purchase_order = self.env[
                'purchase.order'].browse(self._context.get(
                    'active_id'))
            return purchase_order.currency_id

    advance_payment_method = fields.Selection([
        ('delivered', 'Regular invoice'),
        ('percentage', 'Down payment (percentage)'),
        ('fixed', 'Down payment (fixed amount)')
        ],
        string='Create Bill',
        default='delivered',
        required=True,
        help="A standard bill is issued with all the order lines ready \
        for billing, according to their billing policy (based on ordered \
        or delivered quantity).")
    product_id = fields.Many2one(
        'product.product',
        string='Down Payment Product',
        domain=[('type', '=', 'service')],
        default=_default_product_id)

    # TODO: add `deduct_down_payments` and `has_down_payments` field

    count = fields.Integer(
        default=_count,
        string='Order Count')
    amount = fields.Float(
        string='Down Payment Amount',
        digits='Account',
        help="The percentage of amount to be billed in advance, \
            taxes excluded.")
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=_default_currency_id)
    fixed_amount = fields.Monetary(
        'Down Payment Amount (Fixed)',
        help="The fixed amount to be   in advance, taxes excluded.")
    expense_account_id = fields.Many2one(
        "account.account",
        string="Expense Account",
        domain=[('deprecated', '=', False)],
        help="Account used for deposits",
        default=_default_expense_account_id)
    expense_taxes_id = fields.Many2many(
        "account.tax",
        string="Vendor Taxes",
        help="Taxes used for deposits",
        default=_default_expense_taxes_id)

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.advance_payment_method == 'percentage':
            amount = self.default_get(['amount']).get('amount')
            return {'value': {'amount': amount}}
        return {}

    # This function is not on odoo10
    def _prepare_invoice_values(self, order, name, amount, po_line):
        invoice_vals = {
            # TODO: see `_prepare_invoice(self)` in purchase`
            'ref': order.partner_ref or '',  # can addition other ref
            'move_type': 'in_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            # 'payment_reference': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,

            # TODO: add addition field

            'invoice_line_ids': [(0, 0, {
                'name': name,
                'price_unit': amount,
                'quantity': 1.0,
                'purchase_line_id': po_line.id,
                'product_id': self.product_id.id,
                'product_uom_id': po_line.product_uom.id,
                'tax_ids': [(6, 0, po_line.tax_id.ids)],
                'analytic_tag_ids': [(6, 0, po_line.analytic_tag_ids.ids)],
                'analytic_account_id': order.analytic_account_id.id or False,
            })],
        }

        return invoice_vals

    def _create_invoice(self, order, po_line, amount):
        if (self.advance_payment_method == 'percentage'
                and self.amount <= 0.00) or (
                self.advance_payment_method == 'fixed'
                and self.fixed_amount <= 0.00):
            raise UserError(_(
                'The value of the down payment amount must be positive.'))

        amount, name = self._get_advance_details(order)

        invoice_vals = self._prepare_invoice_values(
            order, name, amount, po_line)

        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id

        invoice = self.env['account.move'].sudo().create(
            invoice_vals).with_user(self.env.uid)
        invoice.message_post_with_view(
            'mail.message_origin_link',
            values={'self': invoice, 'origin': order},
            subtype_id=self.env.ref('mail.mt_note').id)
        return invoice

    def _get_advance_details(self, order):
        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Down payment of %s%%") % (self.amount)
        else:
            amount = self.fixed_amount
            name = _('Down payment (Fixed): %s') % (self.fixed_amount)
        del context

        return amount, name

    def _prepare_po_line(self, order, analytic_tag_ids, tax_ids, amount, name):
        context = {'lang': order.partner_id.lang}
        po_line_values = {
            # 'name': _('Down Payment: %s') % (time.strftime('%m %Y'),),
            'name': name,
            'price_unit': amount,
            'product_uom_qty': 0.0,
            'order_id': order.id,
            'product_uom': self.product_id.uom_id.id,
            'product_id': self.product_id.id,
            'analytic_tag_ids': analytic_tag_ids,
            'tax_id': [(6, 0, tax_ids)],
            # 'is_downpayment': True,
            'sequence': order.order_line and order.order_line[
                -1].sequence + 1 or 10,
            'date_planned': datetime.today().strftime(
                DEFAULT_SERVER_DATETIME_FORMAT),
        }
        del context
        return po_line_values

    def create_invoices(self):
        purchase_orders = self.env['purchase.order'].browse(
            self._context.get('active_ids', []))

        # TODO:  `deduct_down_payments is missing, create its` and validate
        # '_create_invoices' in `sale` module

        if self.advance_payment_method == 'delivered':
            purchase_orders._create_invoices(final=self.deduct_down_payments)
        else:
            # Create default deposit product in sale config if necessary
            if not self.product_id:
                vals = self._prepare_expense_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env[
                    'ir.config_parameter'].sudo().set_param(
                        'sale.default_deposit_product_id', self.product_id.id)

            purchase_line_obj = self.env['purchase.order.line']

            for order in purchase_orders:
                amount, name = self._get_advance_details(order)

                if self.product_id.type != 'service':
                    raise UserError(_("The product used to bill \
                    a down payment should be of type 'Service'. \
                    Please use another product or update this product."))

                # evaluate tax_ids for po_line
                taxes = self.product_id.taxes_id.filtered(
                    lambda r: not order.company_id or
                    r.company_id == order.company_id)

                # need in `_prepare_so_line`
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [
                        (4, analytic_tag.id,
                            None) for analytic_tag in line.analytic_tag_ids]

                # need in `_prepare_so_line`
                tax_ids = order.fiscal_position_id.map_tax(
                    taxes,
                    self.product_id,
                    # Maybe need to fix sale is `partner_shipping_id`
                    order.partner_id).ids

                po_line_values = self._prepare_po_line(
                    order, analytic_tag_ids, tax_ids, amount, name)
                po_line = purchase_line_obj.create(po_line_values)
                self._create_invoice(order, po_line, amount)
                # end else

        if self._context.get('open_invoices', False):
            return purchase_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}

    def _prepare_expense_product(self):
        return {
            'name': 'Down payment',
            'type': 'service',
            # fix invoice_policy on sale
            # 'invoice_policy': 'order',
            'property_account_expense_id': self.expense_account_id.id,
            'supplier_taxes_id': [(6, 0, self.expense_taxes_id.ids)],
        }
