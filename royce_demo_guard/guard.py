# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

"""Protects the shared public demo login from a visitor changing its password
and locking out everyone after them.

No site check here on purpose -- this app's isolation comes from where it's
installed (only demo.royceerp.com), not from a runtime string comparison.
Keeping the demo guard out of kenyan_accountant/royce_payroll_ke/royce_talk
means it structurally cannot run against a real customer's site, even if this
code has a bug -- it simply won't be present in their installed-apps list.

Must hook before_validate, not before_save: frappe.core.doctype.user.user.User
.validate() stashes new_password into a private attribute and clears the field
to "" before before_save ever fires. A before_save version of this was tried
first, confirmed broken via a real password-change attempt going through
uncaught, and reverted.

The /update-password page (frappe.core.doctype.user.user.update_password)
writes the password straight to __Auth and never saves the User document, so
before_validate never sees it. The demo password is public, so a visitor could
change it there with the "old password" form; update_password below wraps that
endpoint (override_whitelisted_methods) and refuses it for this account.

Only blocks a password *change* on the one named account -- normal profile
edits (phone number, etc.) on that same account still work, and this has no
effect on any other user, including other users on this same site.
"""

import frappe
from frappe.core.doctype.user import user as frappe_user
from frappe.utils.data import sha256_hash

DEMO_USER = "demo@royceerp.com"


def block_demo_password_change(doc, method=None):
	if doc.name != DEMO_USER:
		return
	if doc.get("new_password"):
		_refuse()


@frappe.whitelist(allow_guest=True, methods=["POST"])
def update_password(
	new_password: str, logout_all_sessions: int = 0, key: str | None = None, old_password: str | None = None
):
	if key:
		target = frappe.db.get_value("User", {"reset_password_key": sha256_hash(key)}, "name")
	else:
		target = frappe.session.user
	if target == DEMO_USER:
		_refuse()
	return frappe_user.update_password(
		new_password, logout_all_sessions=logout_all_sessions, key=key, old_password=old_password
	)


def _refuse():
	frappe.throw(
		"This is a shared public demo login. For security, its password can't be "
		"changed here. Contact Royce ERP if you'd like your own trial account."
	)
