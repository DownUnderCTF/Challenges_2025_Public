from flask import Blueprint, render_template, request, abort, session, url_for, redirect, flash
from .models import ScanResult, Company
from . import db
from urllib.parse import urlparse
from urllib.request import urlopen
import requests
import os
import logging
import re

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(message)s')
logger = logging.getLogger("flask_app.routes")

main = Blueprint('main', __name__)
BLACKLIST = ['file', 'gopher', 'dict']
AUTHENTICATION_KEY = os.environ.get('AUTHENTICATION_KEY')

def is_safe_url(url):
    scheme = urlparse(url).scheme
    if scheme in BLACKLIST:
        logger.warning(f"[!] Blocked by blacklist: scheme = {scheme}")
        flash("BAD URL: The URL scheme is not allowed.", "danger")
        return False
    return True

@main.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        logger.info(session)
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        url = request.form.get('url', '')
        if not url:
            logger.debug("[!] No URL provided.")
            return render_template("index.html", error="Please enter a URL.")

        if not is_safe_url(url):
            logger.warning(f"[!] Unsafe URL detected: {url}")
            return render_template("result.html", domain=url, result="Blocked by blacklist.")
        # TODO: Extract information from the domain, and check if they are with us.
        try:
            preview = urlopen(url).read().decode('utf-8', errors='ignore')
            # For now, just get the company name
            try:
                company_name = re.search(r'<title>(.*)</title>', preview).group(1) 
            except:
                company_name = "Company name not found"
            result = f"Website Responds with: <br><pre>{preview}</pre>"
            logger.debug(f"[+] Successfully fetched content from {preview}")
            company = Company(domain=url, name=company_name, description="No description provided.")
            db.session.add(company)
            db.session.commit()
        except Exception as e:
            result = f"Error: <code>{str(e)}</code>"

        scan = ScanResult(domain=url, result=result, user_id=session['user_id'])
        db.session.add(scan)
        db.session.commit()
        return render_template("result.html", domain=url, result=result, scan=scan)

    return render_template("index.html")

@main.route('/history')
def history():
    scans = ScanResult.query.filter_by(user_id=session['user_id']).order_by(ScanResult.timestamp.desc()).limit(10).all()
    return render_template("results.html", history=scans)

@main.route('/admin/', methods=['GET'])
def admin_index():
    """Admin dashboard to view all scan results."""
    logger.debug("[+] Admin index accessed.")
    return "Still under construction."

@main.route('/admin/stats', methods=['GET'])
def internal_stats():
    """Internal endpoint to fetch usage stats, provides limited accessibility for admins outside the network."""
    if 'user_id' not in session or session['user_id'] != 1:
        logger.warning("[!] Unauthorized access attempt to /admin/stats")
        abort(403)
    # result = requests.get("http://dev.rpc-service.ductf/stats", headers={"auth-key": AUTHENTICATION_KEY}).text
    return f"Still under construction."
