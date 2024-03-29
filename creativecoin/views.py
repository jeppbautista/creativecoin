from flask import Blueprint, redirect, render_template, render_template_string, request, url_for
from flask_login import current_user

main = Blueprint('main', __name__)

from creativecoin import app
from creativecoin.email import EmailSender
from creativecoin.forms import Contact
from creativecoin.helper.utils import crawl_usd, crawl_grain

env = app.config['ENV']


def subdomain(rule='/', subdomain=''):
    if app.config['ENV'] == "production":
        return dict(rule=rule, subdomain=subdomain)
    else:
        if rule == "/":
            rule = ""
        return dict(rule=rule + '/' + subdomain, subdomain='')


@app.route('/', subdomain='', strict_slashes=False)
def index():
    return render_template('landing/index.html', current_user=current_user)
    # return render_template('index/index.html')


@app.route('/prices')
def prices():
    return render_template('landing/privacy.html')


@app.route('/privacy-policy')
def privacy():
    return render_template('landing/privacy.html')


@app.route('/terms-and-conditions')
def terms():
    return render_template('landing/terms.html')


@app.route('/disclaimer')
def disclaimer():
    return render_template('landing/disclaimer.html')


@app.route('/system')
def system():
    return render_template('system/index.html')


@app.route("/Z2V0LXVzZA")
def usd():
    usd = crawl_usd()
    return str(usd)


@app.route("/Z2V0LWdyYWlu")
def grain():
    grain = crawl_grain()
    return str(grain)


@app.route(rule='/cdn', strict_slashes=False)
def cdn():
    return "CDN"


@app.route(rule='/my', strict_slashes=False)
def my():
    return "My"


@app.route(rule='/news', strict_slashes=False)
def news():
    return "News"


@app.route(rule="/get-in-touch", strict_slashes=False)
def contact_us():
    contactform = Contact()
    return render_template("contact-us.html", contactform=contactform)


@app.route(rule="/contact", strict_slashes=False, methods=["GET", "POST"])
def contact():
    app.logger.error("INFO - /contact")
    contact = Contact(request.form)

    mail = EmailSender()
    mail.sender = "contact-form@creativecoin.net"
    params = {
        "$email": contact.email.data,
        "$name": contact.name.data,
        "$message": contact.message.data
    }

    body = mail.prepare_body(params, path="contact.html")
    if not mail.send_mail(app.config["ADMIN_MAIL"], "Contact Form", body):
        app.logger.error("ERROR - sending email failed")
        return redirect(url_for("contact_us"))
    return redirect(url_for("contact_us"))


@app.route(rule='/test', strict_slashes=False, methods=["GET", "POST"])
def test():
    import pyqrcode
    # x = os.path.join(os.getcwd(), "creativecoin\\static")
    big_code = pyqrcode.create('0987654321', error='L', version=27, mode='binary')
    big_code.png('code.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xcc])
    return str("FOO")


@app.errorhandler(503)
def internal_error(e):
    return render_template("error/503.html")


@app.errorhandler(500)
def internal_error2(e):
    return render_template("error/500.html")


@app.errorhandler(404)
def not_found(e):
    print(request.path)
    return render_template("error/404.html")


@app.errorhandler(400)
def bad_request(e):
    return render_template("error/400.html")


# 0 */6 * * * /usr/bin/curl --silent -XGET https://creativecoin.net/Z2V0LXVzZA &> /dev/null
# 0 */6 * * * /usr/bin/curl --silent -XGET https://creativecoin.net/Z2V0LWdyYWlu &> /dev/null
# 59 23 * * * /usr/bin/curl --silent -XGET https://creativecoin.net/c3RhcnRtaW5pbmc &> /dev/null
