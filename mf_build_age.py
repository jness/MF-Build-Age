#!/usr/bin/env python 
import sys
from smtplib import SMTP
import argparse
from socket import error
from connection import get_connection
from monkeyfarm.interface import MFAPIKeyRequestHandler, MFInterface
from datetime import datetime, timedelta

class MF:

    # Current date using datetime
    now = datetime.now().date()

    def connect(self):
        '''Connects to Monkey Farm'''
        config = get_connection(con_name='default')
        if config:
            rh = MFAPIKeyRequestHandler(config['url'])
            rh.auth(config['user'], config['api_key'])
            hub = MFInterface(request_handler=rh)
            return hub
        else:
            print 'It does not appear you have a ~/.mf.conf'
            sys.exit()

    def tag(self, tagname):
        '''Get all builds in a tag'''
        request = hub.tag.get_one(tagname, 'ius')
        builds = request['data']['tag']['builds']
        return builds

    def build(self, builds):
        package = {}
        for build in builds:
            package[build] = hub.build.get_one(build, 'ius')
        return package

    def packages(self, packages):
        '''Extract all the needed informatoin from package'''
        pkginfo = {}
        for package in packages:
            # Turn the Pkg's date in to a datetime()
            date = packages[package]['data']['build']['update_date']
            date = date.split()[0]
            date = date.split('-')
            date = datetime(int(date[0]), int(date[1]), int(date[2])).date()

            # Link MF Calls to local vars
            package = packages[package]['data']['build']['label']
            owner = packages[package]['data']['build']['user_label']
            status = packages[package]['data']['build']['status_label']
            update_date = packages[package]['data']['build']['update_date']
            release = packages[package]['data']['build']['releases']
            tag = packages[package]['data']['build']['tags']

            # Create dictionary space for package
            try:
                pkginfo[owner][package] = {}
            except KeyError:
                pkginfo[owner] = {}
                pkginfo[owner][package] = {}

            # Create a new Dictionary with our information
            pkginfo[owner][package]['owner'] = owner
            pkginfo[owner][package]['status'] = status
            pkginfo[owner][package]['update_date'] = update_date
            pkginfo[owner][package]['release'] = release
            pkginfo[owner][package]['tag'] = tag
            pkginfo[owner][package]['date'] = date
        return pkginfo


    def getemail(self, userlabel):
        request = hub.user.get_one(userlabel)
        email = request['data']['user']['email']
        return email

# Check input
parser = argparse.ArgumentParser()
parser.add_argument('--email', action='store_true',
        dest='email', default=None, help='Send emails to package maintainers')
args = parser.parse_args()

# Link to our MF Class and do the dirty work
mf = MF()
now = mf.now
hub = mf.connect()
builds = mf.tag('testing')

# get data for all packages
packages = mf.build(builds)
pkginfo = mf.packages(packages)

# Packages Age
for owner in pkginfo:
    
    # Create our Email structure
    fromaddr = 'ius-community@lists.launchpad.net'
    toaddr = mf.getemail(owner)
    subject = '[MonkeyFarm] Builds in testing for 2 weeks or more'

    header = 'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n' % (
                                fromaddr, toaddr, subject
                                )

    body = ''

    for package in pkginfo[owner]:

        delta = (now - pkginfo[owner][package]['date'])
        days = delta.days

        # Only packages 14 days or older
        if delta >= timedelta(days = 14):

            body = body + 'Build: %s\nDate: %s\nStatus: %s\nReleases: %s\nTags: %s\nAge: %s\r\n\r\n' % (
                            package, 
                            pkginfo[owner][package]['update_date'], 
                            pkginfo[owner][package]['status'], 
                            ', '.join(pkginfo[owner][package]['release']), 
                            ', '.join(pkginfo[owner][package]['tag']), 
                            days
                             )

    msg = header + body

    # To email or not to email..
    if args.email:
        # Try to connect to local SMTP and send email
        try:
            server = SMTP('localhost')
            server.set_debuglevel(0)

        except error:
            print 'Unable to connect to SMTP Server, quitting...\n'
            sys.exit()

        else:
            server.sendmail(fromaddr, toaddr, msg)
            server.quit()
            print 'Email for sent to', toaddr
    else:
        print '='*35
        print msg


