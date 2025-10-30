import frappe
import json
import pymysql
from frappe.utils import nowdate, getdate
from datetime import date
from bench_manager.bench_manager.utils import verify_whitelisted_call, run_command
from bench_manager.bench_manager.doctype.bench_settings.bench_settings import sync_sites
from frappe.desk.page.setup_wizard.setup_wizard import setup_complete
from frappe.utils.password import update_password
from frappe.permissions import AUTOMATIC_ROLES
import uuid

def unique_key():
    return f"{frappe.utils.now_datetime().isoformat()}-{uuid.uuid4().hex[:8]}"

@frappe.whitelist()
def create_site_from_hd_ticket(ticket, email, plan, full_name, site_name):

    if not all([ticket, email, plan, full_name, site_name]):
        frappe.throw("All fields are required to create a site.")

    sccc_settings = frappe.get_single("SCCC Setting")

    if not sccc_settings.mysql_password:
        frappe.throw("Please provide MySQL Password in SCCC Setting.")

    mysql_password = sccc_settings.mysql_password

    try:
        job = frappe.enqueue(
            "sccc.api.provision_site",
            full_name=full_name,
            email=email,
            site_name=site_name,
            modules=plan,
            onboarding_doc=ticket,
            mysql_password=mysql_password,
            timeout=3600,
            queue="long",
        )

        if job:
            job_id = getattr(job, "id", job)
            frappe.msgprint(
                f"Site creation has started in the background.<br>"
                f"You can track the job here: <a href='/app/rq-job/{job_id}' target='_blank'>RQ Job</a>"
            )

        return {"status": "success", "message": "Site creation started.", "job_id": job_id}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Create Site from HD Ticket Failed")
        frappe.throw(f"Failed to start site creation job: {str(e)}")



@frappe.whitelist()
def provision_site(full_name, email, site_name, modules, onboarding_doc, mysql_password):
	try:
		verify_password(site_name, mysql_password)
		job_id = create_site(
            site_name=site_name,
            mysql_password=mysql_password,
            admin_password="12345",
            key=unique_key(),
            full_name=full_name,
            email=email,
            onboarding_doc=onboarding_doc,
            a_async=True,
        )

		if job_id:
			frappe.msgprint("Site created")
	except Exception:
		raise


@frappe.whitelist()
def verify_password(site_name, mysql_password):
	verify_whitelisted_call()
	for host in (frappe.conf.db_host or "localhost", "127.0.0.1"):
		try:
			db = pymysql.connect(host=host, user="root", passwd=mysql_password)
			db.close()
			return "console"
		except Exception:
			continue
	frappe.throw("MySQL password is incorrect")
	return "console"


@frappe.whitelist()
def create_site(site_name, mysql_password, admin_password, key, full_name, email, onboarding_doc, a_async=True):
    verify_whitelisted_call()
    commands = [
        f"bench new-site --mariadb-root-password {mysql_password} --admin-password {admin_password} --no-mariadb-socket {site_name}"
    ]
    try:
        with open("apps.txt", "r") as f:
            app_list = f.read()
    except Exception:
        app_list = ""
    if "erpnext" not in app_list:
        commands.append("bench get-app erpnext")
    if "zatca_erpgulf" not in app_list:
        commands.append("bench get-app https://github.com/ERPGulf/zatca_erpgulf.git")
    commands.append(f"bench --site {site_name} install-app erpnext")
    commands.append(f"bench --site {site_name} set-maintenance-mode off")
    commands.append(f"bench --site {site_name} migrate")
    job = frappe.enqueue(
        "sccc.api.job_site_creation",
        commands=commands,
        doctype="Bench Settings",
        key=unique_key(),
        site_name=site_name,
        onboarding_doc=onboarding_doc,
        full_name=full_name,
        email=email,
        is_async=a_async,
        timeout=3600,
        queue="long",
    )
    if job:
        return getattr(job, "id", job)
    return None


def job_site_creation(commands, doctype, key, site_name, onboarding_doc, full_name, email, *args, **kwargs):
	try:
		run_command(commands=commands, doctype=doctype, key=unique_key())
		sync_sites()
		site = frappe.get_doc("Site", site_name)
		site.customer_onboarding = onboarding_doc
		site.save()
		frappe.db.commit()

		kwargs_json = json.dumps({
			"full_name": full_name,
			"email": email,
			"password": "12345"
		})

		commands_to_run = [
			f"bench --site {site_name} install-app sccc_theme",
			f"bench --site {site_name} migrate",
			f"bench --site {site_name} execute sccc.api.run_setup_wizard --kwargs '{kwargs_json}'",
			f"bench --site {site_name} execute sccc.api.create_or_update_user --kwargs '{kwargs_json}'"
		]

		for cmd in commands_to_run:
			run_command(commands=[cmd], doctype=doctype, key=unique_key())

	except Exception:
		raise

@frappe.whitelist()
def run_setup_wizard(full_name, email):
	fy_start, fy_end = get_fiscal_year_dates()
	args = {
		"currency": "SAR",
		"country": "Saudi Arabia",
		"timezone": "Asia/Riyadh",
		"language": "English",
		"company_name": full_name,
		"company_abbr": "".join([p[0] for p in full_name.split()]).upper(),
		"chart_of_accounts": "Standard",
		"fy_start_date": fy_start,
		"fy_end_date": fy_end,
		"setup_demo": 0
	}
	setup_complete(args)


def get_fiscal_year_dates():
	today = getdate(nowdate())
	year = today.year
	if today.month < 4:
		fy_start = date(year - 1, 4, 1).isoformat()
		fy_end = date(year, 3, 31).isoformat()
	else:
		fy_start = date(year, 4, 1).isoformat()
		fy_end = date(year + 1, 3, 31).isoformat()
	return fy_start, fy_end


def _update_master_site(onboarding_doc, values: dict):
	master_site = frappe.local.site
	frappe.init(master_site)
	frappe.connect()
	frappe.db.commit()

@frappe.whitelist()
def create_or_update_user(args):  # nosemgrep
	email = args.get("email")
	if not email:
		return

	first_name, last_name = args.get("full_name", ""), ""
	if " " in first_name:
		first_name, last_name = first_name.split(" ", 1)

	if user := frappe.db.get_value("User", email, ["first_name", "last_name"], as_dict=True):
		if user.first_name != first_name or user.last_name != last_name:
			(
				frappe.qb.update("User")
				.set("first_name", first_name)
				.set("last_name", last_name)
				.set("full_name", args.get("full_name"))
			).run()
	else:
		_mute_emails, frappe.flags.mute_emails = frappe.flags.mute_emails, True

		user = frappe.new_doc("User")
		user.update(
			{
				"email": email,
				"first_name": first_name,
				"last_name": last_name,
			}
		)
		user.append_roles(*_get_default_roles())
		user.append_roles("System Manager")
		user.flags.no_welcome_mail = True
		user.insert()

		frappe.flags.mute_emails = _mute_emails

	if args.get("password"):
		update_password(email, args.get("password"))


def _get_default_roles() -> set[str]:
	skip_roles = {
		"Administrator",
		"Customer",
		"Supplier",
		"Partner",
		"Employee",
	}.union(AUTOMATIC_ROLES)
	return set(frappe.get_all("Role", pluck="name")) - skip_roles