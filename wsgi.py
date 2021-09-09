import sys
import site

site.addsitedir('/home/cisateducation/public_html/creativecoin.net/venv/lib/python3.6/site-packages')

sys.path.insert(0, '/home/cisateducation/public_html/creativecoin.net')

from creativecoin import app as application

if __name__ == "__main__":
    application.run()