#! /usr/bin/env python3

""" For deployment on ix under CGI """

import site
site.addsitedir("/home/users/hhamm/public_html/htbin/cis322/proj2-ajax/env/lib
/python3.4/site-packages")

from wsgiref.handlers import CGIHandler
from app import app

CGIHandler().run(app)