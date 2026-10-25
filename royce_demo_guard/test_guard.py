# Copyright (c) 2026, Royce Technologies LTD and Contributors
# See license.txt
from unittest.mock import MagicMock

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import now_datetime
from frappe.utils.data import sha256_hash
from frappe.utils.password import check_password
from frappe.utils.password import update_password as set_password

from royce_demo_guard.guard import DEMO_USER, update_password

PASSWORD = "Demo#Guard2026"
NEW_PASSWORD = "Changed#Guard2026xyz"
OTHER_USER = "demo-guard-other@example.com"


def ensure_user(email):
	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{"doctype": "User", "email": email, "first_name": "Guard Test", "send_welcome_email": 0}
		).insert(ignore_permissions=True)
	set_password(email, PASSWORD)


def issue_reset_key(email):
	key = frappe.generate_hash()
	frappe.db.set_value(
		"User",
		email,
		{"reset_password_key": sha256_hash(key), "last_reset_password_key_generated_on": now_datetime()},
	)
	return key


class TestDemoGuard(IntegrationTestCase):
	def setUp(self):
		ensure_user(DEMO_USER)
		ensure_user(OTHER_USER)
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_whitelisted_override_is_registered(self):
		overrides = frappe.get_hooks("override_whitelisted_methods")
		self.assertEqual(
			overrides["frappe.core.doctype.user.user.update_password"][-1],
			"royce_demo_guard.guard.update_password",
		)

	def test_user_form_password_change_blocked(self):
		doc = frappe.get_doc("User", DEMO_USER)
		doc.new_password = NEW_PASSWORD
		self.assertRaises(frappe.ValidationError, doc.save, ignore_permissions=True)

	def test_profile_edit_still_allowed(self):
		doc = frappe.get_doc("User", DEMO_USER)
		doc.phone = "0700000001"
		doc.save(ignore_permissions=True)
		self.assertEqual(frappe.db.get_value("User", DEMO_USER, "phone"), "0700000001")

	def test_update_password_page_blocked_for_demo(self):
		frappe.set_user(DEMO_USER)
		self.assertRaises(
			frappe.ValidationError, update_password, new_password=NEW_PASSWORD, old_password=PASSWORD
		)
		self.assertEqual(check_password(DEMO_USER, PASSWORD), DEMO_USER)

	def test_reset_link_blocked_for_demo(self):
		frappe.set_user("Guest")
		key = issue_reset_key(DEMO_USER)
		self.assertRaises(frappe.ValidationError, update_password, new_password=NEW_PASSWORD, key=key)
		self.assertEqual(check_password(DEMO_USER, PASSWORD), DEMO_USER)

	def test_other_users_reset_link_still_works(self):
		frappe.set_user("Guest")
		key = issue_reset_key(OTHER_USER)
		# Frappe's endpoint logs the user in at the end; tests have no web login manager.
		frappe.local.login_manager = MagicMock()
		update_password(new_password=NEW_PASSWORD, key=key)
		self.assertEqual(check_password(OTHER_USER, NEW_PASSWORD), OTHER_USER)
