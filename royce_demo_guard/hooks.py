app_name = "royce_demo_guard"
app_title = "Demo Guard"
app_publisher = "Royce Technologies LTD"
app_description = "Protects the shared public demo tenant's login. Installed on the demo site only."
app_email = "developer@roycetechnologies.co.ke"
app_license = "mit"

# Not shown on the Apps screen -- this exists purely to carry one hook, nothing
# for a demo visitor to click into.
add_to_apps_screen = []

# Document Events
# ---------------

doc_events = {
	"User": {
		"before_validate": "royce_demo_guard.guard.block_demo_password_change",
	}
}
