# ----------------------------------------------------------------------------
#
# Charm: A Python-based client for LiveJournal and other blogging services.
#
# Version 1.9.1
# January 11th, 2009
# Copyright (C) 2001 - 2009  Lydia Leong (evilhat@livejournal.com)
#
# Usage: charm --help
#
# (Don't invoke this module directly. It's meant to be imported.)
#
# Written for Python 2.5, but should work with other versions as well.
#
# ----------------------------------------------------------------------------
# GNU General Public License v2
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# ----------------------------------------------------------------------------

import sys
import os
import os.path
import string
import getopt
import time
import locale
import stat
import md5
import urllib
import calendar

try:
    import feedparser
    import httplib
    import base64
    import datetime
    import sha
    atom_ok = 1
except:
    atom_ok = 0

try:
    import xmms.control
except:
    pass

# ----------------------------------------------------------------------------
# Constants.
# ----------------------------------------------------------------------------

__version__ = "1.9.1"
__doc__ = "Charm, a Python-based client for cross-platform blogging."
__author__ = "evilhat@livejournal.com"

Client_Name = "python-Charm"

Client_URL = "http://ljcharm.sourceforge.net/"

barline = "------------------------------------------------------------------------------"

Charm_Header = "\n--------------[ Charm " + __version__ + ", a Cross-Platform Blogging Client ]--------------\n"

Social_Bookmarks = {
    "addthis" : """<a href="http://www.addthis.com/bookmark.php?url=%s&title=%s" title="Bookmark and Share" target="_blank"><img src="http://s9.addthis.com/button1-share.gif" width="125" height="16" border="0" alt="Bookmark and Share" /></a>""",
    "addthis_js" : """<script type="text/javascript"><!--
addthis_pub = '%s';
// --></script><a onclick="return addthis_sendto()" onmouseover="return addthis_open(this, '', '%s', '%s')" onmouseout="addthis_close()" href="http://www.addthis.com/bookmark.php"><img src="http://s7.addthis.com/static/btn/lg-share-en.gif" border="0" alt="Bookmark and Share" width="125" height="16" /></a><script src="http://s7.addthis.com/js/152/addthis_widget.js" type="text/javascript"></script>""" }

# A '1' indicates that the option's normal value is reversed.

Bool_Opts = { "archive" : 0, "archive_edits" : 0, "archive_overwrite" : 0,
	      "archive_subdirs" : 0, "show_permissions" : 0, "nocache" : 0,
	      "nologin" : 0, "autoformat" : 1, "comments" : 1,
	      "noemail" : 0, "backdate" : 0, "edit_times" : 0,
              "autodetect" : 0, "debug" : 0 }

Bool_Map = { "archive" : "archive",
	     "archive_edits" : "archive_edits",
	     "archive_overwrite" : "archive_overwrite",
	     "archive_subdirs" : "archive_subdirs",
	     "show_permissions" : "showperms",
	     "nocache" : "nocache", "nologin" : "nologin",
	     "autoformat" : "prop_opt_preformatted",
	     "comments" : "prop_opt_nocomments",
	     "noemail" : "prop_opt_noemail",
	     "backdate" : "prop_opt_backdated",
	     "edit_times" : "edit_times",
             "autodetect" : "autodetect",
             "debug" : "debug" }

Other_Opts = { "archive_dir" : 1, "draft_dir" : 1, "organize" : 1,
	       "editor" : 0, "pager" : 0, "spellchecker" : 0,
	       "user" : 1, "password" : 1, "hpassword" : 1,
	       "login" : 1, "hlogin" : 1,
               "atomblog" : 1, "hatomblog" : 1, "metaweb" : 1,
               "default_user" : 0, "social" : 1, "socialuser" : 1,
               "groupheader" : 1, "commpic" : 1, "tagpic" : 1,
	       "security" : 1, "journal" : 1, "url" : 0,
               "checkgroups" : 1, "checkdelay" : 1,
               "default_filter" : 0, "default_template" : 0 }

Basic_MetaData = [ "year", "mon", "day", "hour", "min", "event", "unfiltered",
		   "subject", "usejournal", "poster",
		   "security", "allowmask",
		   "prop_current_mood", "prop_current_moodid",
		   "prop_picture_keyword", "prop_current_music",
		   "prop_opt_preformatted",
		   "prop_opt_backdated", "prop_opt_screening",
		   "prop_opt_nocomments", "prop_opt_noemail",
                   "prop_taglist", "prop_keywords", "excerpt" ]

Conf_MetaData = [ "prop_opt_preformatted", "prop_opt_nocomments",
		  "prop_opt_noemail", "prop_opt_backdated",
                  "prop_opt_screening", "security", "allowmask" ]

# ----------------------------------------------------------------------------
# Color data.
# ----------------------------------------------------------------------------

Colors = [ ("Red, Darkest", "#5B0101"), ("Red, Dark", "#9E0000"),
           ("Red", "#FF0000"), ("Red, Light", "#FF8B8B"),
           ("Red, Pink", "#FFCBCB"), ("Brown, Dark", "#330000"),
           ("Brown", "#993300"), ("Brown, Tan", "#CC9966"),
           ("Orange, Brown", "#BC5D00"), ("Orange, Bright", "#FF6600"),
           ("Orange", "#FFB22B"), ("Orange, Light", "#FFE2A3"),
           ("Olive", "#696A0A"), ("Yellow, Dark", "#B0B200"),
           ("Yellow", "#FFFF00"), ("Yellow, Light", "#FEFFBB"),
           ("Green, Pine", "#002400"), ("Green, Dark", "#015B01"),
           ("Green", "#019501"), ("Green, Bright", "#00FF00"),
           ("Green, Light", "#B3FFB3"), ("Green, Mint", "#00EEC4"),
           ("Green, Aqua", "#88FEE9"), ("Blue, Steel", "#066D98"),
           ("Blue, Ocean", "#019997"), ("Blue, Sky", "#00FFFF"),
           ("Blue, Light Sky", "#BBFFFE"), ("Blue, Midnight", "#00025C"),
           ("Blue, Navy", "#01059D"), ("Blue, Bright", "#0000FF"),
           ("Blue, Medium", "#6569FF"), ("Blue, Light", "#ADB1FF"),
           ("Blue, Powder", "#E3E5FF"), ("Violet, Dark", "#8E01D7"),
           ("Violet", "#CA65FF"), ("Violet, Light", "#EFCFFF"),
           ("Purple, Wine", "#520155"), ("Purple", "#A501A7"),
           ("Purple, Fuchsia", "#FF00FF"), ("Purple, Pink", "#F999FF"),
           ("Pink, Ice", "#FCDDFF"), ("Black", "#000000"),
           ("Gray, Dark", "#676767"), ("Gray, Light", "#C0C0C0"),
           ("White", "#FFFFFF") ]

# ----------------------------------------------------------------------------
# Miscellaneous functions.
# ----------------------------------------------------------------------------

def client_info():
    "Print client information."

    print barline
    print """
Client ID: %s/%s

This cross-platform blogging client (for LiveJournal, the MetaWebLog API,
the Movable Type API, and the Atom API) was written by Lydia Leong.
Copyright 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008.
Terms of the GNU Public License apply.
The author can be reached at evilhat@livejournal.com
""" % (Client_Name, __version__)
    print barline


def sane_raw_input(prompt = "Action: "):
    "Handles EOF more gracefully."

    try:
	res = raw_input(prompt)
    except EOFError:
	res = ""
    return res


def dump_dict(this_dict):
    "Dump contents of a dictionary."

    try:
        for k in this_dict.keys():
            print "%s = %s" % (k, this_dict[k])
    except:
        try:
            for d in this_dict:
                dump_dict(d)
        except:
            print "Error dumping dictionary."
            print this_dict


def errmsg():
    "Return an error message."

    s = sys.exc_info()[1]
    if s is None:
        return "unknown error"
    return str(s)


def parse_bool(instr):
    "Parse a boolean string, return 0 or 1, or -1 on error."

    if instr in ("yes", "y", "true", "t", "on", "1"):
	return 1
    elif instr in ("no", "n", "false", "f", "off", "0"):
	return 0
    else:
	return -1


def create_dir(dname, derr):
    "Create a directory if it doesn't exist."

    if not os.path.exists(dname):
	try:
	    os.mkdir(dname)
	except OSError:
	    print "Error creating '%s' directory %s: %s" % (derr, dname, errmsg())
	    return 0
	try:
	    os.chmod(dname, 0700)
	except OSError:
	    pass			# just ignore
    return 1


def column_table(list, n_cols):
    "Print a list, numbered, in a certain number of columns."

    l_len = len(list)
    width = (78 / n_cols) - n_cols
    if l_len > 99:
	width = width - 2
    elif l_len > 9:
	width = width - 1

    i = 1
    for k in list:
	if i % n_cols == 0:		# last item in column
	    print "%-4s %s" % (str(i) + ".", k[:width])
	else:
	    print "%-4s %s " % (str(i) + ".",
			      string.ljust(k[:width], width)),
	i = i + 1
    if (i % n_cols) != 1:			# just went past last item
	print

        
def color_table():
    "Print a color table."

    column_table( [ k for (k, v) in Colors ], 3)


def color_input(prompt):
    "Display and obtain color information."

    while 1:
        color_table()
        print
        colname = sane_raw_input(prompt)
        print
        try:
            n = int(colname)
        except ValueError:
            n = 0
        if n < 1 or n > len(Colors):
            print "That is not a valid color."
            print
        else:
            return Colors[n - 1][1] 
        

def md5digest(sstr):
    "md5digest hex digestify a string."

    # -- Newer versions of python have hexdigest() built into the md5
    #    module. We provide an alternative, for earlier versions.

    try:
	hexd = md5.hexdigest(sstr)
    except AttributeError:
	digest = md5.new(sstr).digest()
        hexd = string.join(map(lambda c: "%s%s" % (string.hexdigits[ord(c) / 16], string.hexdigits[ord(c) % 16]), digest), "")

    return hexd


def get_nonce(tstamp):
    "Create a nonce."

    sstr = sha.new("%s:%s" % (tstamp, Client_Name)).hexdigest() 
    return "%s %s" % (tstamp, sstr)


def commalist(list):
    "Create a comma-separated list string, out of a list of strings."

    return string.join(list, ", ")


def truncstr_more(str, len, more_str = " [...more]"):
    "Truncate a string to a specified length."

    return string.replace(string.replace(str[:len], "\r", " "),
			  "\n", " ") + more_str


def append_htblock(orig, new):
    "Append a paragraph to an existing HTML text body. Return string."

    if orig[-2:] == "\n\n":
	tstr = orig
	orig = orig[:-2]
    elif orig[-1] == "\n":
        tstr = "%s\n" % (orig)
	orig = orig[:-1]
    else:
	tstr = orig + "\n\n"

    if orig[-3:] == "<P>" or orig[-3:] == "<p>":
        return "%s%s\n<P>\n" % (tstr, new)
    elif orig[-4:] == "</P>" or orig[-4:] == "</p>":
        return "%s<P>%s\n</P>\n" % (tstr, new)
    else:
        return "%s<P>\n\n%s\n" % (tstr, new)


def get_home_dir():
    "Get user's home directory."
    
    try:
        return os.environ['HOME']
    except KeyError:
        return "/tmp"


# ----------------------------------------------------------------------------
# Dealing with Unicode.
# ----------------------------------------------------------------------------

def utf8(s):
    "UTF-8 encode a string, if supported."

    loc = locale.getdefaultlocale()
    if loc[1] == "UTF8":
        return s
    else:
        try:
            return unicode(s, "iso-8859-1").encode("UTF-8")
        except:
            return s


def utf8_urlencode(data):
    "Equivalent of urllib.urlencode(), but handles Unicode data."

    out = []

    for (k, v) in data.items():

        # -- x-www-form-urlencoded requires normalization of newlines to \r\n
        #    Lack of list comprehensions in older versions prevent us from
        #    just writing:
        #    v = "\r\n".join( [ x.replace("\n", "\r\n")
        #                       for x in v.split("\r\n") ] )

        elems = []
        for x in string.split(v, "\r\n"):
            elems.append(string.replace(x, "\n", "\r\n"))
        v = string.join(elems, "\r\n")

        # -- Split on spaces and rejoin with pluses, and recreate each
        #    segment by leaving unreserved characters alone and UTF-8 and
        #    percent-encoding the others.
        #    Concise expression:
        #    v = '+'.join( [ ''.join( [ octet in unreserved and octet or
        #                               u'%%%02X' % ord(octet) for octet
        #                               in word.encode('utf-8')] )
        #                       for word in v.split(' ') ] )

        words = string.split(v, " ")
        enc = []
        for w in words:
            res = []
            for c in w:
                if c not in urllib.always_safe:
                    c = u'%%%02X' % ord(c)
                res.append(c)
            enc.append(string.join(res, ""))
        v = string.join(enc, "+")

        out.append("%s=%s" % (k, v.encode("us-ascii")))

    return string.join(out, "&")
   

# ----------------------------------------------------------------------------
# Override the URL opener object so we can set cookies.
# ----------------------------------------------------------------------------

class CustomURLopener(urllib.FancyURLopener):
    def __init__(self, *args):
	apply(urllib.FancyURLopener.__init__, (self,) + args)


# ----------------------------------------------------------------------------

class BloggerData:
    """Storage for Atom and MetaWeb data. Charm's code really needs general
       refactoring for LJ versus Atom at some point in the future, since
       this is a kludge."""

    def __init__(self):

        self.Q = None                   # feedparsed query response
        self.Blogs = {}
        self.Current = {}
        self.PostTime = ""
        self.Categories = []

# ----------------------------------------------------------------------------
# Object to cache data returned from server across invocations of client.
# ----------------------------------------------------------------------------

class LJ_Cache:
    "Server data cache."

    def __init__(self):
	"Initialize."

	self.Moods = {}
	self.Mood_Count = 0
	self.Journals = []
	self.PicKws = []
	self.Friends = {}
	self.FriendSorter = {}
        self.FriendNums = {}
        self.FriendPublic = []
	self.Irrelevant = []
        self.Tags = []
        self.LastSync = ""

    def load_cache(self, fname, username):
	"Load cache file."

	try:
	    f = open(fname, 'r')
	except IOError:
	    return			# just ignore
	line = f.readline()
	while line != "":
            line = string.rstrip(line)  # zap newline, trailing whitespace
	    if line == "":
		pass
	    else:
		inpair = string.split(line, '=', 1)
		ustr = "%s " % (username)
		ulen = len(ustr)
		if inpair[0][:5] == "mood_":
		    self.Moods[inpair[0][5:]] = inpair[1]
		elif inpair[0][:ulen] == ustr:
		    # -- Read only the data associated with our username.
		    if inpair[0][ulen:] == "pic":
			self.PicKws.append(inpair[1])
		    elif inpair[0][ulen:] == "journal":
			self.Journals.append(inpair[1])
                    elif inpair[0][ulen:] == "tag":
                        self.Tags.append(inpair[1])
		    elif inpair[0][ulen:][:3] == "fg_":
			self.Friends[inpair[0][ulen:][3:]] = inpair[1]
		    elif inpair[0][ulen:][:4] == "ofg_":
			self.FriendSorter[inpair[0][ulen:][4:]] = inpair[1]
                    elif inpair[0][ulen:] == "lastsync":
                        self.LastSync = inpair[1]
		else:
		    # -- Must still save data from other usernames.
		    self.Irrelevant.append(line)
	    line = f.readline()
	f.close()

	self.Mood_Count = 0
	for k in self.Moods.keys():
	    n = int(self.Moods[k])
	    if n > self.Mood_Count:
		self.Mood_Count = n 


    def save_cache(self, username):
	"Save cache file."

	if self.Mood_Count < 1:
	    return

        user_home_dir = get_home_dir()
	fname = "%s/.charmcache" % (user_home_dir)
	cfile = open(fname, 'w')
        if self.LastSync != "":
            cfile.write("%s lastsync=%s\n" % (username, self.LastSync))
	for k in self.Moods.keys():
	    cfile.write("mood_%s=%s\n" % (k, self.Moods[k]))
	for k in self.PicKws:
	    cfile.write("%s pic=%s\n" % (username, k))
	for k in self.Journals:
	    cfile.write("%s journal=%s\n" % (username, k))
	for k in self.Tags:
	    cfile.write("%s tag=%s\n" % (username, k))
	for k in self.Friends.keys():
	    cfile.write("%s fg_%s=%s\n" % (username, k, self.Friends[k]))
	for k in self.FriendSorter.keys():
	    cfile.write("%s ofg_%s=%s\n" % (username, k, self.FriendSorter[k]))
	for k in self.Irrelevant:
	    cfile.write("%s\n" % (k))
	cfile.close()


    def load_moods_from_net(self, net_dict):
	"Given a dictionary containing network output, load moods."

	# -- Indexed by name. The data contents are the IDs.

	try:
	    max_moods = int(net_dict["mood_count"])
	    if max_moods != 0:
		for n in range(1, max_moods + 1):
		    try:
			idstr = net_dict["mood_%d_id" % (n)]
			self.Moods[net_dict["mood_%d_name" % (n)]] = idstr
			idn = int(idstr)
			if idn > self.Mood_Count:
			    self.Mood_Count = idn
		    except KeyError:
			pass
	except KeyError:
	    pass


    def load_journals_from_net(self, net_dict):
	"Given a dictionary containing network output, load journals."

	# -- Indexed by NAME, not number. 

	self.Journals = []

	try:
	    max_journs = int(net_dict["access_count"])
	    if max_journs != 0:
		for n in range(1, max_journs + 1):
		    try:
			self.Journals.append(net_dict["access_%d" % (n)])
		    except KeyError:
			pass
	except KeyError:
	    pass


    def load_tags_from_net(self, net_dict):
	"Given a dictionary containing network output, load tags."

        tags = []
        try:
            max_tags = int(net_dict["tag_count"])
            if max_tags != 0:
                for n in range(1, max_tags + 1):
                    try:
                        tags.append(net_dict["tag_%d_name" % (n)])
                    except KeyError:
                        pass
            self.Tags = tags
        except KeyError:
            pass
                           

    def load_pickws_from_net(self, net_dict):
	"Given a dictionary containing network output, load picture keywords."

	self.PicKws = []

	try:
	    max_pk = int(net_dict["pickw_count"])
	    if max_pk != 0:
		for n in range(1, max_pk + 1):
		    try:
			self.PicKws.append(net_dict["pickw_%d" % (n)])
		    except KeyError:
			pass
	except KeyError:
	    pass


    def load_frgrps_from_net(self, net_dict):
	"Given a dictionary containing network output, load friend groups."

	# -- Process friend groups. Indexed by name. Store bitmask (the
	#    friend group number corresponds to the bit to turn on).

	self.Friends = {}
	self.FriendSorter = {}
        self.FriendNums = {}
        self.FriendPublic = []

	try:
	    max_frgrps = int(net_dict["frgrp_maxnum"])
	    if max_frgrps != 0:
		for n in range(1, max_frgrps + 1):
		    try:
			frgrpname = net_dict["frgrp_%d_name" % (n)]
			self.Friends[frgrpname] = str(pow(2, n))
                        self.FriendNums[frgrpname] = n
			try:
			    sortord = int(net_dict["frgrp_%d_sortorder" % (n)])
			except KeyError:
			    sortord = 50
			self.FriendSorter[frgrpname] = sortord
                        if net_dict.has_key("frgrp_%d_public" % (n)):
                            self.FriendPublic.append(frgrpname)
		    except KeyError:
			pass
	except KeyError:
	    pass

# ----------------------------------------------------------------------------
# The do-it-all object.
# ----------------------------------------------------------------------------

class Jabber:
    "The do-everything object." 

    def __init__(self):
	"Set initial configuration parameters."

	self.FastServer = 0

	self.Params = { "clientversion" : Client_Name + "/" + __version__,
			"url" : "http://www.livejournal.com/interface/flat",
			"archive" : "1", "organize" : "month",
			"archive_edits" : "1", "archive_overwrite" : "0",
			"archive_subdirs" : "0", "showperms" : "0",
                        "getmoods" : "0", "getpickws" : "1", "blogapi" : "lj" }

	self.Save_Meta = { }

	# -- Figure out what type of line endings we (hopefully) have,
	#    based on our system type.

	if os.name == "posix":
	    le = "unix"
	elif os.name in ("nt", "dos", "os2", "ce"):
	    le = "pc"
	elif os.name == "mac":
	    le = "mac"
	else:
	    le = "unix"			# something mysterious. pray.
	self.Params["lineendings"] = le

	# -- Look for our important directories.

        user_home_dir = get_home_dir()
	self.Params["draft_dir"] = "%s/.ljdrafts" % (user_home_dir) 
	self.Params["archive_dir"] = "%s/.ljarchive" % (user_home_dir)

	# -- Find what editor we'd like to use.

	try:
	    self.Params["editor"] = os.environ['VISUAL']
	except KeyError:
	    try:
		self.Params["editor"] = os.environ['EDITOR']
	    except KeyError:
		self.Params["editor"] = "vi"

	# -- Initialize miscellaneous other stuff.

	self.Cache = LJ_Cache()

	self.NonRecurs = []
	self.Logins = {}
        self.Sites = {}

	self.Sent = ""
	self.Got = {}
	self.LoggedIn = 0
	self.GottenFriends = 0
        self.GottenTags = 0
        self.Blogger = None

	self.Mood = ""

	self.Entries = []
	self.Entry = {}
	self.GroupHeaders = {}
	self.CommPics = {}
        self.TagPics = {}
        self.SocialUsers = {}

        self.Buddies = {}

	self.CheckDelay = 0
	self.CheckGroups = []

    # -----
    # Helpful routines.
    # -----

    def getval(self, pname, dstr = "(none)" ):
	"Return parameter with name pname, or dstr if it doesn't exist."

	if self.Params.has_key(pname):
	    return self.Params[pname]
	else:
	    return dstr


    def del_param(self, pname):
	"Delete parameter, if it exists."

	try:
	    del self.Params[pname]
	except KeyError:
	    pass


    def dump_debug_info(self):
	"Print the debugging info we need most often."

	print
	print "--------------------------[ Dumping Debugging Info ]--------------------------"
	print
	print "Params:"
	dump_dict(self.Params)
	print
	print "Journals:"
	for k in self.Cache.Journals:
	    print k
	print
	print "Friends:"
	dump_dict(self.Cache.Friends)
	print
	print "Picture keywords:"
	for k in self.Cache.PicKws:
	    print k
	print
#	print "Moods:"
#	dump_dict(self.Cache.Moods)
#	print
	print "Sent:"
	print self.Sent
	print
	print "Got:"
	dump_dict(self.Got)
	print barline
	print


    def format_time(self, d = None):
	"Return the current post time as a string."

	if d is None:
	    d = self.Params

	return "%s-%s-%s %s:%s" % (d["year"], d["mon"], d["day"],
				   d["hour"], d["min"])


    def populate_time(self, timetuple):
	"Populate the time parameters with a time."

	self.Params["year"] = time.strftime("%Y", timetuple)
	self.Params["mon"] = time.strftime("%m", timetuple)
	self.Params["day"] = time.strftime("%d", timetuple)
	self.Params["hour"] = time.strftime("%H", timetuple)
	self.Params["min"] = time.strftime("%M", timetuple)


    def save_conf_meta(self):
        "Save off conf options we'll want to preserve across operations."

        for k in Conf_MetaData:
            try:
                self.Save_Meta[k] = self.Params[k]
            except KeyError:
                pass
            

    def copy_net_data(self, pstr, klist):
	"Copy from network data, with a prefix string."

	for k in klist:
	    try:
		self.Params[k] = self.Got[pstr + k]
	    except KeyError:
		pass

    def blog_login_config(self, pval, is_hashed):
        "Process Atom API login options."

        inpair = string.split(pval, ' ', 3)

        if len(inpair) == 4:
            self.Sites[inpair[0]] = (inpair[2], inpair[3])
        elif len(inpair) == 3:
            try:
                (proto, rstr) = inpair[2].split(":")
                rstr = rstr[2:]         # get rid of //
                (site, baseuri) = rstr.split("/", 1)
                if proto == "https": 
                    self.Sites[inpair[0]] = (site, "/%s" % (baseuri), 1)
                else:
                    self.Sites[inpair[0]] = (site, "/%s" % (baseuri), 0)
            except:
                self.Sites[inpair[0]] = ("www.blogger.com", "/atom/", 1)
        else:
            self.Sites[inpair[0]] = ("www.blogger.com", "/atom/", 1)

        if self.Sites[inpair[0]][2] == 1:  # basic auth over SSL
            if is_hashed == 0:
                self.Logins[inpair[0]] = base64.encodestring("%s:%s" % (inpair[0], inpair[1]))[:-1]
            else:
                self.Logins[inpair[0]] = inpair[1]
        else:                           # WSSE, no SSL
            if is_hashed == 1:
                print "Warning, Charm needs a cleartext password for WSSE non-SSL authentication."
            self.Logins[inpair[0]] = inpair[1]
            

    def set_special_opt(self, pname, pval):
	"Set a special option that requires pre-processing."

	if pname == "user":
	    # -- Ignore this, because the user is going to get complained
	    #    at when we get to the password option, and we shouldn't
	    #    do that twice.
	    pass

	elif pname in ("password", "hpassword"):
	    print """\
The options user, password, and hpassword are deprecated. Please use
one of the following:
    login = username password
    hlogin = username MD5hexpassword
    atomblog = username password
    hatomblog = username base64password
in your .charmrc file instead."""

	elif pname in ("draft_dir", "archive_dir"):
	    self.Params[pname] = os.path.expanduser(pval)

	elif pname == "organize":
	    if pval in ("none", "year", "month"):
		self.Params[pname] = pval
	    else:
		print "Warning: invalid value for option %s" % (pname)

	elif pname == "login":
	    inpair = string.split(pval, ' ', 2)
	    try:
		self.Logins[inpair[0]] = md5digest(inpair[1])
                if len(inpair) == 3:
                    self.Sites[inpair[0]] = "http://%s/interface/flat" % (inpair[2])
	    except IndexError:
		print "Warning: malformed value for login option."

	elif pname == "hlogin":
	    inpair = string.split(pval, ' ', 2)
	    try:
		self.Logins[inpair[0]] = inpair[1]
                if len(inpair) == 3:
                    self.Sites[inpair[0]] = "http://%s/interface/flat" % (inpair[2])
	    except IndexError:
		print "Warning: malformed value for hlogin option."

	elif pname == "atomblog" or pname == "hatomblog":
            if atom_ok == 1:
                try:
                    if pname == "atomblog":
                        self.blog_login_config(pval, 0)
                    else:
                        self.blog_login_config(pval, 1)
                except IndexError:
                    print "Warning: malformed value for %s option." % (pname)
            else:
                print "Warning: no support for Atom API blogging."

        elif pname == "metaweb":
            inpair = string.split(pval, ' ', 2)
            if len(inpair) != 3:
                print "Warning: malformed value for metaweb option."
            else:
                self.Logins[inpair[0]] = inpair[1]
                self.Sites[inpair[0]] = (inpair[2], "IGNORE-APPKEY")

        elif pname == "socialuser":
            inpair = string.split(pval, ',', 1)
            try:
                self.SocialUsers[inpair[0]] = inpair[1]
            except IndexError:
                print "Warning: malformed value for socialuser option."

        elif pname == "groupheader":
	    inpair = string.split(pval, ',', 1)
	    try:
		self.GroupHeaders[inpair[0]] = inpair[1]
	    except IndexError:
		print "Warning: malformed value for groupheader option."

	elif pname == "commpic":
	    inpair = string.split(pval, ',', 1)
	    try:
		self.CommPics[inpair[0]] = inpair[1]
	    except IndexError:
		print "Warning: malformed value for commpic option."

	elif pname == "tagpic":
	    inpair = string.split(pval, ',', 1)
	    try:
		self.TagPics[inpair[0]] = inpair[1]
	    except IndexError:
		print "Warning: malformed value for tagpic option."
                
	elif pname == "security":
	    # -- We have to do this later, after we log in, so we can
	    #    get group names.
	    if pval != "":
		self.Params["security"] = pval

	elif pname == "journal":
	    # -- No error-checking.
	    self.Params["usejournal"] = string.lower(pval)

	elif pname == "checkgroups":
	    self.CheckGroups = map(lambda x: string.lower(x),
				   string.split(pval, ','))

	elif pname == "checkdelay":
	    try:
		n = int(pval) * 60
		if n <= 0:
		    print "Warning: bad value for checkdelay option, ignoring."
		else:
		    self.CheckDelay = n
	    except ValueError:
		print "Warning: malformed value for checkdelay option."

        elif pname == "social":
            if Social_Bookmarks.has_key(pval.lower()):
                self.Params["social"] = pval.lower()
            else:
                print "Warning: invalid social bookmarks service option."
                
	else:
	    # Huh. Unimplemented. Do default.
	    self.Params[pname] = pval


    def read_rcfile(self, rcfile=".charmrc"):
	"Read in config info from an rc file of key=value pairs."

	if rcfile in self.NonRecurs:
            print "Attempt to recursively read rcfile %s, skipped." % (rcfile)
	    return
	self.NonRecurs.append(rcfile)

	try:
	    f = open(rcfile, 'r')
	except IOError:
	    if self.NonRecurs == [ rcfile ]:
		print "Unable to open rcfile '%s': %s. Exiting." % (rcfile, errmsg())
		sys.exit(1)
	    else:
                print "Unable to open rcfile '%s': %s. Skipped." % (rcfile, errmsg())
		return

	line = f.readline()
	while line != "":
            line = string.rstrip(line)
	    if line == "":
		pass
	    elif line[0] == "#":	# comment line, discard
		pass
	    elif line[:8] == "include ":
		self.read_rcfile(os.path.expanduser(line[8:]))
	    else:
		inpair = string.split(line, '=', 1)
		if len(inpair) < 2:
		    print "Warning: invalid line, %s" % (line)
		else:
		    pname = string.lower(string.strip(inpair[0]))
		    pval = string.strip(inpair[1])
		    try:
			# -- Here is our song and dance to deal with boolean
			#    options, since we want nice short option names for
			#    users, rather than the big long non-intuitive
			#    names used by the protocol. Map the names, check
			#    for reversal, and, if we now have a 1, set it.

			preal = Bool_Map[pname]
			pnum = parse_bool(pval)
			if pnum == -1:
			    print "Warning: invalid value for boolean option %s" % (pname)
			else:
			    if Bool_Opts[pname] == 1:
				if pnum == 0:
				    pnum = 1
				else:
				    pnum = 0
			    if pnum == 1:
				self.Params[preal] = str(pnum)
			    else:
				if self.Params.has_key(preal):
				    del self.Params[preal]
		    except KeyError:
			try:
			    if Other_Opts[pname] == 0:
				self.Params[pname] = pval
			    else:
				self.set_special_opt(pname, pval)
			except KeyError:
			    print "Warning: invalid option name %s" % (pname)
	    line = f.readline()
	f.close()


    def autodetect_music(self):
        "Set and return the title of auto-detected music, if we can manage it."

        music = ""
        try:
            if self.Params.has_key("autodetect") and xmms.control.is_running(0) and xmms.control.is_playing(0):
                music = string.strip(xmms.control.get_playlist_title(xmms.control.get_playlist_pos(0), 0))
        except:
            pass

        if music != "":
            self.Params["prop_current_music"] = music
            self.Params["autodetect"] = 1
            return music
        else:
            return "(none)"


    def sort_friendgroups(self):
	"Return friend group list in sorted order, by sort priority."

	# -- Python versions before 2.0 don't have list comprehensions,
	#    or we'd replace the maps/lambdas with:
	# items = [ (v, k) for k, v in self.Cache.FriendSorter.items() ]
	# olist = [ k for v, k in items ]

	items = map(lambda x: (x[1], x[0]), self.Cache.FriendSorter.items())
        items.sort()
	olist = map(lambda x: x[1], items)
	return olist


    def make_draft_file(self, timestr):
	"Set up for a draft file."

	# -- If we don't have a drafts directory, make one.

	ddir = self.Params["draft_dir"]
	ok = create_dir(ddir, "drafts")
	if ok == 0:
	    return 0

	# -- Drafts are named after timestamps.

	dfile = "%s/draft_%s" % (ddir, timestr)
	self.Params["draft_file"] = dfile
	return 1


    # -----
    # Draft file and meta-data utilities.
    # -----

    def clear_metadata(self):
	"Clear out metadata."

	for k in Basic_MetaData:
	    try:
		del self.Params[k]
	    except KeyError:
		pass
	self.Mood = ""
        try:
            self.Blogger.PostTime = ""
            del self.Blogger.Current["edit"]
        except:
            pass


    def reset_metadata(self):
	"Restore metadata to defaults."

	self.clear_metadata()
	for k in Conf_MetaData:
	    try:
		self.Params[k] = self.Save_Meta[k]
	    except KeyError:
		pass


    def save_metadata(self, timestr):
	"Save metadata."

	# -- Our base directory is the base directory of our drafts file,
	#    if we have one. Otherwise it's our drafts directory.

	try:
	    mfname = "%s/.meta_%s" % \
		     (os.path.dirname(self.Params["draft_file"]), timestr)
	except KeyError:
	    mfname = "%s/.meta_%s" % (self.Params["draft_dir"], timestr)

	try:
	    mfile = open(mfname, 'w')
	    for k in Basic_MetaData:
		try:
		    mfile.write("%s=%s\n" % (k, self.Params[k]))
		except KeyError:
		    pass
	    mfile.close()
	except IOError:
	    pass			# whoops. oh well.


    def save_session(self, noisy = 0):
	"Save a session."

	# -- Important note. If we're operating in noisy mode, and
	#    the user chooses not to save, wipe out the draft file.

	try:
	    dfile = self.Params["draft_file"]
	    if dfile != "":
		dbase = os.path.basename(dfile)
		ddir = os.path.dirname(dfile)
		timestr = string.join((string.split(dbase, '_'))[-2:], '_')

		if noisy == 1:
                    res = sane_raw_input("Do you want to save the current session (Y/N)? ")
		    print
		    res = string.lower(string.strip(res))

		    # -- Err on the side of caution. If we get malformed
		    #    input we'd rather save than not.

		    if res in ("n", "no"):
			mfname = "%s/.meta_%s" % (ddir, timestr)
			try:
			    os.unlink(dfile)
			except OSError:
			    pass
			os.unlink(mfname)
			return

		    print "Saving current session. You can resume it with:\n\t%s -r" % (sys.argv[0]),
		    if ddir == self.Params["draft_dir"]:
			print dbase
		    else:
			print dfile

		self.save_metadata(timestr)
		print
	except KeyError:
	    pass


    def clear_session(self, dfile = ""):
	"Delete old files and clear out meta-data."

	if dfile == "":
	    dfile = self.Params["draft_file"]

	dbase = os.path.basename(dfile)
	ddir = os.path.dirname(dfile)
	timestr = string.join((string.split(dbase, '_'))[-2:], '_')
	mfname = "%s/.meta_%s" % (ddir, timestr)
	try:
	    os.unlink(dfile)
	except OSError:
	    pass
	os.unlink(mfname)
	self.reset_metadata()

	for k in [ "draft_file", "event", "itemid" ]:
	    try:
		del self.Params[k]
	    except KeyError:
		pass


    def read_event(self, f):
	"Read a file into the event parameter."

	body = []
	line = f.readline()
	while line != "":
	    body.append(line)
	    line = f.readline()
	self.Params["event"] = string.join(body, "")


    def slurp_draft(self, optype):
	"Read a draft file into the event parameter."

	# -- First, we need a non-empty draft file that we can read.

	try:
	    dfile = self.Params["draft_file"]
	except KeyError:
	    print "%s attempt cancelled: No current draft." % (optype)
	    return 0

	if os.access(dfile, os.F_OK | os.R_OK) == 0:
	    print "%s attempt cancelled: Cannot read the current draft file." % (optype)
	    return 0

	if (os.stat(dfile))[stat.ST_SIZE] == 0:
	    print "%s attempt cancelled: Draft file is empty." % (optype)
	    return 0

	try:
	    f = open(dfile, 'r')
	except IOError:
	    print "%s attempt cancelled, error reading draft file: %s." % (optype, errmsg())
	    return 0

	# -- Read the draft file into a really big buffer.

	self.read_event(f)
	f.close()
	return 1


    # -----
    # Web operation handlers.
    # -----

    def web_encode(self, mode, has_utf, klist, blist = []):
	"Encode a list of parameters into a URL string."

        pdict = { "mode": mode, "ver" : utf8(str(has_utf)) }

	for k in klist:
	    try:
		if self.Params[k] != "":
		    pdict[k] = utf8(self.Params[k])
	    except KeyError:
		pass			# if we don't have it, just ignore it

	# -- For these keys, force encoding even if blank.

	for k in blist:
	    try:
		pdict[k] = utf8(self.Params[k])
	    except KeyError:
		pdict[k] = ""

        if has_utf:
            s = utf8_urlencode(pdict)
        else:
            s = urllib.urlencode(pdict)
            
	return s


    def parse_return(self, optype):
	"Parse server-returned success code."

	try:
	    succ_code = self.Got["success"]
	    if succ_code == "FAIL":
		try:
                    self.show("%s failed: %s" % (optype, self.Got["errmsg"]))
		except KeyError:
		    self.show("%s failed, no error message specified." % (optype))
		return 0
	except KeyError:
	    self.show("%s failed, server error. Try again later." % (optype))
	    return 0
	return 1


    def raw_client_op(self):
	"Client operation: Send request, read response."

	# -- urllib doesn't play nice with cookies. Kludge for fast server.

	tmp = CustomURLopener()
	if self.FastServer == 1:
	    tmp.addheader('Cookie', 'ljfastserver=1')
	urllib._urlopener = tmp

	# - Get it, parse it, save it.

	try:
	    netobj = urllib.urlopen(self.Params["url"], self.Sent)
	except:
	    print "\nNetwork error (%s). Try again later.\n" % (errmsg())
	    self.Got = {}
	    return

	self.Got = {}
	str = ""
	line = netobj.readline()
	while line != "":
	    line = line[:-1]		# discard newline
	    if str == "":
		str = line
	    else:
		self.Got[str] = line
		str = ""
	    line = netobj.readline()


    def client_op(self, mode, klist, blist = []):
        """Client operation: Obtain a challenge string, if possible. Use
           this to authenticate the full operation, sending data and
           reading the response."""

        # -- Not all python versions support Unicode. For those that
        #    don't, we use the protocol version 0.

        try:
            a = unicode("a")
            ver = 1
        except:
            ver = 0

        self.Sent = self.web_encode("getchallenge", ver, [ "user" ])
        self.raw_client_op()
        ok = self.parse_return("Challenge authentication")
        if ok == 0:
            # Fall back on auth in the clear.
            self.del_param("auth_method")
            self.del_param("auth_challenge")
            self.del_param("auth_response")
            self.Sent = self.web_encode(mode, ver,
                                        klist + [ "user", "hpassword" ], blist)
        else:
            self.Params["auth_method"] = "challenge"
            self.Params["auth_challenge"] = self.Got["challenge"]
            self.Params["auth_response"] = md5digest("%s%s" % (self.Got["challenge"], self.Params["hpassword"]))
            self.Sent = self.web_encode(mode, ver,
                                        klist + [ "user", "auth_method",
                                                  "auth_challenge",
                                                  "auth_response" ], blist)
        self.raw_client_op()


    def cli_xmlrpc(self, meth, send_dict = {}):
        "XML-RPC transaction."

        try:
            import xmlrpclib
        except ImportError:
            self.Got["success"] = "FAIL"
            self.Got["errmsg"] = "Your Python installation lacks the required xmlrpclib module."
            return

        # -- Fix up the flat URL into an XML-RPC one.

        raw_url_elems = self.Params["url"].split("/")
        url = "%s/xmlrpc" % ("/".join(raw_url_elems[:-1]))

        server = xmlrpclib.ServerProxy(url)
        data = {}

        # -- Try challenge/auth first. Fall back to clear if it fails.

        try:
            self.Got = server.LJ.XMLRPC.getchallenge()
            data["auth_method"] = "challenge"
            data["auth_challenge"] = self.Got["challenge"]
            data["auth_response"] = md5digest("%s%s" % (self.Got["challenge"], self.Params["hpassword"]))
        except:
            data["hpassword"] = self.Params["hpassword"]

        data["username"] = self.Params["user"]
        data["ver"] = "1"
        for (k, v) in send_dict.items():
            data[k] = v

        # -- Send the commands.
        
        try:
            if meth == "editfriends":
                self.Got = server.LJ.XMLRPC.editfriends(data)
            elif meth == "getfriends":
                self.Got = server.LJ.XMLRPC.getfriends(data)                
            else:
                self.Got = server.LJ.XMLRPC.consolecommand(data)
            self.Got["success"] = "OK"
        except xmlrpclib.Error, faultobj:
            self.Got["errmsg"] = faultobj.faultString
            self.Got["success"] = "FAIL"
        except:
            print "\nNetwork error. Try again later.\n"
            self.Got = {}


    def show(self, msg):
	"Show a word-wrapped message in an output window."

	out = ""
	lines = string.split(msg, '\n')
	for text in lines:
	    cur_len = 0
	    words = string.split(str(text), ' ')
	    for w in words:
		this_word = str(w)
		this_len = len(this_word)
		if cur_len + this_len > 75:
		    if cur_len == 0:	# print single word even if too long
			out = out + this_word
		    else:
			print out
			out = this_word
		    cur_len = this_len
		else:
		    if cur_len != 0:
                        out = "%s %s" % (out, this_word)
			cur_len = cur_len + this_len + 1
		    else:
			out = out + this_word
			cur_len = this_len
	    print out
	    out = ""


    def process_getusertags(self):
        "Process returned user tags."

        self.Cache.load_tags_from_net(self.Got)
        self.GottenTags = 1

        
    def process_getfriendgroups(self):
	"Process returned friend groups."

	self.Cache.load_frgrps_from_net(self.Got)
	self.GottenFriends = 1


    def cli_checkfriends(self, silent = 0):
	"Client request: checkfriends"

	self.client_op("checkfriends", [ "lastupdate", "mask" ])

	ok = self.parse_return("Friends check")
	if ok == 0:
	    return

	try:
	    self.Params["lastupdate"] = self.Got["lastupdate"]
	except KeyError:
	    pass			# hmm, that's not good

	if silent == 0:
	    try:
		if self.Got["new"] == "1":
		    print "You have new friend updates."
		else:
		    print "No new friend updates."
	    except KeyError:
		print "Server error. Try again later."


    def cli_login(self, no_show_info = 0):
	"Client request: login"

	if self.Cache.Mood_Count > 0:
	    self.Params["getmoods"] = str(self.Cache.Mood_Count)

	self.client_op("login", [ "clientversion", "getpickws", "getmoods" ])

	# -- Look for success/failure codes.

	ok = self.parse_return("Login")
	if ok == 0:
	    return

	# -- Welcome the user by name, and, if it exists, print announcement.

	if no_show_info == 0:
	    self.show("Welcome, %s" % (self.Got["name"]))
	    try:
		msg = self.Got["message"]
		print
		self.show(msg)
	    except KeyError:
		pass

	# -- Detect if we're allowed to use the fast servers.

	try:
	    fs_code = self.Got["fastserver"]
	    if fs_code == 1:
		self.FastServer = 1
	except KeyError:
	    pass

	# -- Process journals we can post to.

	self.Cache.load_journals_from_net(self.Got)

	# -- Process friend groups.

	self.process_getfriendgroups()

	# -- Process moods.

	self.Cache.load_moods_from_net(self.Got)

	# -- Process picture keywords.

	self.Cache.load_pickws_from_net(self.Got)

	# -- Note that we logged in successfully.

	self.LoggedIn = 1


    def cli_getdaycounts(self):
	"Client request: getdaycounts"

	self.client_op("getdaycounts", [ "usejournal" ])
	return self.parse_return("Retrieval")


    def cli_postevent(self):
	"Client request: postevent"

	self.client_op("postevent", [ "lineendings", "event" ] +
		       Basic_MetaData)
	return self.parse_return("Post")


    def cli_getevents_list(self, tmp_keys):
	"Client request: getevents (download a list)"
	
	self.Params["truncate"] = "55"
	self.Params["prefersubject"] = "1"
	self.Params["noprops"] = "1"

	print "Retrieving..."
	print

	self.client_op("getevents", [ "lineendings",
				      "truncate", "prefersubject", "noprops",
				      "selecttype", "usejournal" ] + tmp_keys)
	
	# -- Clear out our temporary properties.

	for k in [ "truncate", "prefersubject", "noprops",
		   "selecttype" ] + tmp_keys:
	    del self.Params[k]

	# -- Check return code.

	ok = self.parse_return("Retrieval")
	if ok == 0:
	    return 0

	# -- Read in the returned events.

	try:
	    ecount = int(self.Got["events_count"])
	except KeyError:
	    print "No entries returned."
	    return 0
	if ecount < 1:
	    print "No entries returned."
	    return 0

	self.Entries = []
	try:
	    for n in range(1, ecount + 1):
		ljo = {}
		ljo["itemid"] = self.Got["events_%d_itemid" % (n)]
		ljo["time"] = self.Got["events_%s_eventtime" % (n)]
		ljo["subject"] = urllib.unquote_plus(self.Got["events_%d_event" % (n)])
		self.Entries.append(ljo)
	except KeyError:
	    print "Error while processing retrieved entry %d." % (n)

	return 1

    def event_common_data(self, timetuple):
	"Copy common event data."

	self.populate_time(timetuple)

	# -- Take the mood ID if we have it, otherwise use the text.
        #    if we have both a mood ID and mood text, keep both.

        try:
            m = self.Params["prop_current_moodid"]
	    for k in self.Cache.Moods.keys():
                if self.Cache.Moods[k] == m:
                    if self.Params.has_key("prop_current_mood"):
                        self.Mood = "%s (%s)" % (k, self.Params["prop_current_mood"])
                    else:
                        self.Mood = k
		    break
	except:
	    try:
		self.Mood = self.Params["prop_current_mood"]
	    except KeyError:
		pass


    def cli_getevents_one(self):
	"Retrieve all data about a single event."

	print "Retrieving entry..."
	print

	self.Params["selecttype"] = "one"
	self.Params["itemid"] = self.Entry["itemid"]
	self.client_op("getevents", [ "lineendings",
				      "selecttype", "itemid", "usejournal" ] )
	del self.Params["selecttype"]
	del self.Params["itemid"]

	ok = self.parse_return("Retrieval")
	if ok == 0:
	    return 0

	# -- Read in all our basic data.

	try:
	    if self.Got["events_count"] != "1":
		print "Error. Server returned incorrect entry count: %s" \
		      % (self.Got["events_count"])
		return 0
	except KeyError:
	    print "Error. Server did not return an entry count."
	    return 0

	try:
	    self.Params["itemid"] = self.Got["events_1_itemid"]
	except KeyError:
	    print "Error. Server did not return item ID of entry."
	    return 0

	try:
	    timetuple = time.strptime(self.Got["events_1_eventtime"],
				      "%Y-%m-%d %H:%M:%S")
	except ValueError:
	    try:
		timetuple = time.strptime(self.Got["events_1_eventtime"],
					  "%Y-%m-%d %H:%M")
	    except ValueError:
		print "Server returned malformed entry time. Setting to present."
		timetuple = time.localtime(time.time())

	self.copy_net_data("events_1_", [ "security", "allowmask", "subject" ])

	try:
	    pcstr = self.Got["prop_count"]
	    try:
		pcount = int(pcstr)
		for n in range(1, pcount + 1):
		    self.Params["prop_" + self.Got["prop_%d_name" % (n)]] = self.Got["prop_%d_value" % (n)]
	    except ValueError:
		print "Server returned malformed property count. Ignoring."
	except KeyError:
	    pass

	self.event_common_data(timetuple)

	# -- Now we need to create a draft file.

	timestr = time.strftime("%Y%m%d_%H%M%S", timetuple)
	ok = self.make_draft_file(timestr)
	if ok == 0:
	    return 0			# error message taken care of already

	try:
	    f = open(self.Params["draft_file"], 'w')
	    f.write(urllib.unquote_plus(self.Got["events_1_event"]))
	    f.close()
	except IOError:
	    print "Error writing to draft file: %s" % (errmsg())

	self.save_metadata(timestr)
	return 1


    def cli_getevents_day(self, ttup):
	"Retrieve all data about events on a single day."

	self.Params["year"] = time.strftime("%Y", ttup)
	self.Params["month"] = time.strftime("%m", ttup)
	self.Params["day"] = time.strftime("%d", ttup)
	self.Params["selecttype"] = "day"

	self.client_op("getevents", [ "year", "month", "day", "lineendings",
				      "selecttype", "usejournal" ] )
	del self.Params["selecttype"]

	ok = self.parse_return("Retrieval")
	if ok == 0:
	    raise IOError


    def cli_getevents_sync(self):
        "Retrieve events as part of a synchronization."

        # -- First, we have the task of having to subtract a second from
        #    our sync time.

        if self.Params.has_key("lastsync"):
            last_secs = time.mktime(time.strptime(self.Params["lastsync"],
                                                  "%Y-%m-%d %H:%M:%S"))
            self.Params["lastsync"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_secs - 1))
            print "  Retrieving posts after %s..." % (self.Params["lastsync"])
        else:
            print "  Retrieving all posts..."

        self.Params["selecttype"] = "syncitems"
        self.client_op("getevents", [ "lineendings", "usejournal",
                                      "selecttype", "lastsync" ] )
        return self.parse_return("Synchronization download")
        

    def cli_editevent(self):
	"Client request: editevent"

	self.client_op("editevent", [ "lineendings", "itemid", "event" ] +
		       Basic_MetaData )
	return self.parse_return("Edit")


    def cli_delevent(self):
	"Client request: editevent (delete)"

	# -- Send the post with a forcibly blank entry.

	self.client_op("editevent", [ "itemid" ], [ "event" ])
	return self.parse_return("Deletion")


    def cli_syncitems(self):
        "Client request: syncitems"

        self.client_op("syncitems", [ "lastsync" ] )
        return self.parse_return("Synchronization")


    def cli_getusertags(self):
        "Client request: getusertags"

        self.client_op("getusertags", [])
        ok = self.parse_return("Tag retrieval")
        if ok == 0:
            if self.Cache.Tags != []:
                print
                print "Warning: Using cached tags data."
                print
            return 0
        self.process_getusertags()
        return 1
    

    def cli_getfriendgroups(self):
	"Client request: getfriendgroups"

	self.client_op("getfriendgroups", [])
	ok = self.parse_return("Friend group retrieval")
	if ok == 0:
	    if self.Cache.Friends != {}:
		print
		print "Warning: Using cached friend groups data. If you have recently updated your"
		print "list of groups, double-check these results!"
		print
	    return 0

	self.process_getfriendgroups()
        return 1


    def cli_getfriends(self):
        "Client request: getfriends"

        print "Getting friends..."
        print

        self.cli_xmlrpc("getfriends")
        ok = self.parse_return("Friend retrieval")
        if ok == 0:
            return 0

        # -- Store friends as a dictionary indexed by username.
        
        self.Buddies = {}
        for friend in self.Got["friends"]:
            self.Buddies[friend["username"]] = friend

        return 1    


    def cli_consolecmd(self, cmds):
        "Send and process console commands."

        print "Processing commands..."
        print

        self.cli_xmlrpc("consolecommand", { "commands" : cmds } )
        ok = self.parse_return("Commands")
        if ok == 0:
            return 0

        print barline

        rvals = self.Got["results"]
        for n in range(len(rvals)):
            r = rvals[n]
            print "Command: %s (%s)" % (" ".join(cmds[n]), ("FAILED", "executed")[r["success"]])
            print
            last_ttype = ""
            for (ttype, text) in r["output"]:
                if last_ttype == ttype:
                    print text
                else:
                    if last_ttype in ("info", "error"):
                        print
                    if ttype == "info":
                        print
                        print "INFO:"
                    elif ttype == "error":
                        print
                        print "ERROR:"
                    print text
                last_ttype = ttype    
            print barline


    def cli_addfriend(self, fname, gmask, fgcol, bgcol, is_edit = 0):
        "Add or edit a friend."

        data = { "username" : fname }
        if gmask != 0:
            data["groupmask"] = gmask
        if fgcol != "":
            data["fgcolor"] = fgcol
        if bgcol != "":
            data["bgcolor"] = bgcol

        self.cli_xmlrpc("editfriends", { "add" : [ data ] } )
        ok = self.parse_return("Friending")
        if ok == 0:
            return 0

        for d in self.Got["added"]:
            print "%s: %s (%s)." % ( ("Friended", "Edited")[is_edit],
                                     d["username"], d["fullname"] )
        

    def cli_delfriend(self, fname):
        "Delete a friend."

        self.cli_xmlrpc("editfriends", { "delete" : [ fname ] } )
        ok = self.parse_return("Friend deletion")
        if ok == 0:
            return 0

        print "Un-friending successful."
        

    def cli_mod_friendgroups(self, gname, gnum, gsort, gpub):
        "Add or edit a friend group."
        
        self.Params["efg_set_%d_name" % (gnum)] = gname
        self.Params["efg_set_%d_sort" % (gnum)] = str(gsort)
        self.Params["efg_set_%d_public" % (gnum)] = str(gpub)

        self.client_op("editfriendgroups", [ "efg_set_%d_name" % (gnum),
                                             "efg_set_%d_sort" % (gnum),
                                             "efg_set_%d_public" % (gnum) ] )


    def cli_addfriendgroup(self, gname, gnum, gsort, gpub):
        "Send a new friend group."

        self.cli_mod_friendgroups(gname, gnum, gsort, gpub)
        ok = self.parse_return("Friend group creation")
        if ok == 0:
            return

        print "Group created."


    def cli_editfriendgroup(self, gname, gnum, gsort, gpub):
        "Alter a friend group."

        self.cli_mod_friendgroups(gname, gnum, gsort, gpub)
        ok = self.parse_return("Friend group editing")
        if ok == 0:
            return

        print "Group edited."

        
    def cli_delfriendgroup(self, gnum):
        "Delete a friend group."

        self.Params["efg_delete_%d" % (gnum)] = "1"
        self.client_op("editfriendgroups", [ "efg_delete_%d" % (gnum) ])
        
        ok = self.parse_return("Friend group deletion")
        if ok == 0:
            return

        print "Group deleted."

    # -----
    # Checkfriends mode.
    # -----

    def prepare_checkfriends(self):
	"Process friend group information prior to checkfriends invocation."

	if self.Params.has_key("mask") or self.CheckGroups == []:
	    return
	if self.GottenFriends == 0:
	    self.cli_getfriendgroups()
	if self.Cache.Friends == {}:
	    return

	mask = 0
	fdict = {}
	for k in self.Cache.Friends.keys():
	    fdict[string.lower(k)] = int(self.Cache.Friends[k])
	for k in self.CheckGroups:
	    for g in fdict.keys():
		if k == g:
		    mask = mask | fdict[g]
		    break
	if mask != 0:
	    self.Params["mask"] = str(mask)


    def checkfriends_event(self):
	"Event called by checkfriends scheduler."

	self.cli_checkfriends(1)
	try:
	    if self.Got["new"] == "1":
		print "\n        >> You have new LiveJournal friend updates. <<\n"
	except KeyError:
	    pass


    def checkfriends_loop(self):
	"Run in the background, checking for friend updates."

	while 1:
	    self.checkfriends_event()
	    try:
		n = int(self.Got["interval"])
	    except ValueError:
		n = 0
	    except KeyError:
		n = 0
	    if n > self.CheckDelay:
		time.sleep(n)
	    else:
		time.sleep(self.CheckDelay)


    # -----
    # Post editing.
    # -----

    def edit_post(self):
	"Edit a post."

	try:
	    dfile = self.Params["draft_file"]
	    timestr = string.join((string.split(dfile, '_'))[-2:], '_')
	except KeyError:

	    # -- No drafts file, so we have a new post. The timestamp is
	    #    always the present.

	    timetuple = time.localtime(time.time())
	    timestr = time.strftime("%Y%m%d_%H%M%S", timetuple)
	    ok = self.make_draft_file(timestr)
	    if ok == 0:
		return
	    dfile = self.Params["draft_file"]

	    # -- Since we're doing a new drafts file, we should populate
	    #    it with the privacy line if it makes sense.

	    if self.Params.has_key("showperms"):
		try:
		    hdr_str = ""
		    if self.Params["security"] == "usemask":
			if self.Params["allowmask"] == "1":
			    hdr_str = "[ To my friends. ]\n"
			else:
			    mnum = int(self.Params["allowmask"])
			    olist = []
			    for k in self.sort_friendgroups():
				if (mnum & int(self.Cache.Friends[k])):
				    if self.GroupHeaders.has_key(k):
					olist.append(self.GroupHeaders[k])
				    else:
					olist.append("the %s" % (k))
			    hdr_str = "[ To %s. ]\n" % (commalist(olist))
		    elif self.Params["security"] == "private":
			hdr_str = "[ Private only. ]\n"
		    if hdr_str != "":
			fh = open(dfile, 'w')
			fh.write(hdr_str)
			if self.Params.has_key("prop_opt_preformatted"):
			    fh.write("<P>\n")
			fh.write("\n")
			fh.close()
		except KeyError:
		    pass

	# -- Save the meta-data while we're at it, then invoke the editor.

	self.save_metadata(timestr)
        os.system('%s "%s"' % (self.Params["editor"], dfile))


    def do_spellcheck(self):
        "Invoke a spellchecker on a post."

        try:
            spath = self.Params["spellchecker"]
        except:
            spath = "/usr/bin/aspell -c"

        try:
            os.system('%s "%s"' % (spath, self.Params["draft_file"]))
            try:
                os.unlink("%s.bak" % (self.Params["draft_file"]))
            except:
                pass
        except:
            print "Could not invoke spellchecker."

    def filter_post(self, is_reverse):
        "Pass post through a filter."

        # -- To reverse, just rename the file.

        if is_reverse:
            try:
                os.rename("%s.raw" % (self.Params["draft_file"]), self.Params["draft_file"])
                print "Reverted to pre-filtered post."
            except:
                print "Reversion failed (%s)." % (errmsg())
            return

        # -- Not a reverse. Prompt for filter.

        print """
Please specify the path to a filter command. Your draft will be sent to it
on stdin. The filter must return its output on stdout.
"""
        if self.Params.has_key("default_filter"):
            res = sane_raw_input("Filter to use [default: %s]: " % (self.Params["default_filter"]))
        else:
            res = sane_raw_input("Filter to use: ")
        print

        if res == "":
            if self.Params.has_key("default_filter"):
                res = self.Params["default_filter"]
            else:
                print "No filter chosen."
                print
                return

        # -- Read in the draft, because it's easier to work with a blob.
        
        if not self.slurp_draft("Filter"):
            return

        # -- If we haven't already done a filtering, copy the draft.
        
        if not self.Params.has_key("unfiltered"):
            self.Params["unfiltered"] = self.Params["event"]
            try:
                fb = open("%s.raw" % (self.Params["draft_file"]), "w")
            except:
                print "Error reading draft file (%s)." % (errmsg())
                return
            fb.write(self.Params["event"])
            fb.close()

        try:
            (f_in, f_out) = os.popen2(res)
        except:
            print "Error invoking filter (%s)." % (errmsg())
            return

        try:
            f_in.write(self.Params["event"])
            f_in.close()
            self.read_event(f_out)
            f_out.close()
            if not self.Params.has_key("event") or self.Params["event"] == "":
                print "Filter (%s) failed: returned empty message body." % (res)
                return
            print "Applied filter: %s" % (res)
        except:
            print "Filter (%s) failed: %s" % (res, errmsg())
            return

        try:
            d = open(self.Params["draft_file"], "w")
            d.write(self.Params["event"])
            d.close()
            print "Filtered draft saved."
        except:
            print "Error saving filtered draft (%s)."


    # -----
    # Utilities for user interaction menus.
    # -----

    def get_choice(self):
	"Get menu choice."
	
	res = sane_raw_input("Enter choice, and press return: ")
	print
	return res


    def do_quit(self):
	"Quit gracefully."

	self.save_session(1)
	self.Cache.save_cache(self.Params["user"])

	print "Thank you for using Charm."
	print
	sys.exit(0)

    def handle_interrupt(self, menu_str):
	"Handle a keyboard interrupt exception."

	print "\n\nReceived Ctrl-C or other break signal.\n"
	res = sane_raw_input("Do you want to quit (Y/N)? ")
	print
	res = string.lower(string.strip(res))
	if res in ("y", "yes"):
	    self.do_quit()
	else:
	    print "Returning to %s menu.\n" % (menu_str)


    def show_calendar(self, year, month):
	"Show calendar with post counts."

	print "Retrieving post counts for %s..." % \
	      (time.strftime("%B %Y", (year, month, 0, 0, 0, 0, 0, 0, 0)))
	print
	ok = self.cli_getdaycounts()
	if ok == 0:
	    print
	    print "Displaying ordinary calendar."
	    print
	    calendar.prmonth(year, month)
	    print
	    return

	bstr = "%(year)d-%(month)02d-" % vars()
	mmatrix = calendar.monthcalendar(year, month)
	weeks = len(mmatrix)

	whole_line = "+---------+---------+---------+---------+---------+---------+---------+"
	space_unit = "          "
	bar_unit =   "+---------"
	blank_unit = "         "	# one shorter

	print "  Sunday    Monday    Tuesday  Wednesday  Thursday  Friday   Saturday"

	# -- Handle the first week. We may have partial boxes.

	line = ""
	for d in range(7):
	    if mmatrix[0][d] == 0:
		line = line + space_unit
	    else:
		line = line + bar_unit
	print line + "+"

	for d in range(7):
	    if mmatrix[0][d] == 0:
		print blank_unit,
	    else:
		try:
		    dstr = "%02d" % mmatrix[0][d]
		    print "| %2d %-4s" % (mmatrix[0][d],
					  "(" + self.Got[bstr + dstr] + ")"),
		except KeyError:
		    print "| %2d     " % mmatrix[0][d],
	print "|"

	print whole_line

	# -- Do the middle weeks.

	for w in range(1, weeks - 1):
	    for d in range(7):
		try:
		    dstr = "%02d" % mmatrix[w][d]
		    print "| %2d %-4s" % (mmatrix[w][d],
					  "(" + self.Got[bstr + dstr] + ")"),
		except KeyError:
		    print "| %2d     " % mmatrix[w][d],
	    print "|"
	    print whole_line

	# -- Do the last week.

	for d in range(7):
	    if mmatrix[-1][d] == 0:
		break
	    else:
		try:
		    print "| %2d %-4s" % \
			  (mmatrix[-1][d],
			   "(" + self.Got[bstr + str(mmatrix[-1][d])] + ")"),
		except KeyError:
		    print "| %2d     " % mmatrix[-1][d],
	print "|"

	line = ""
	for d in range(7):
	    if mmatrix[-1][d] == 0:
		break
	    else:
		line = line + bar_unit
	print line + "+"
	print


    def set_pickw(self, pname):
	"Set a picture keyword, if we can."

	# -- We must do a case-insensitive compare (but picture keywords
	#    can be case-sensitive, so we can't just universally lowercase
	#    them when we first store them).

	for k in self.Cache.PicKws:
	    if pname == string.lower(k):
                if k == "default":
                    self.del_param("prop_picture_keyword")
                else:
                    self.Params["prop_picture_keyword"] = k
		break


    # -----
    # Parameter setting.
    # -----

    def set_mood(self, mood_text):
	"Set a mood, given text."

	mood_text = string.lower(string.strip(mood_text))
	self.Mood = mood_text

	# -- Wipe out the old moods.

	self.del_param("prop_current_mood")
	self.del_param("prop_current_moodid")

	if mood_text == "":
	    return

	# -- Do we have this mood pre-defined? If so, use ID. Otherwise, text.

	try:
	    mood_id = self.Cache.Moods[mood_text]
	    self.Params["prop_current_moodid"] = mood_id
	except KeyError:
	    self.Params["prop_current_mood"] = mood_text

	# -- Moods might correspond to picture keywords. Try to set.
	#    (If we don't match anything, no harm done.)

	self.set_pickw(mood_text)


    def set_security(self, pval):
	"Set security level to something."

	if pval == "public":
	    self.Params["security"] = "public"
	    self.del_param("allowmask")
	elif pval == "friends":
	    self.Params["security"] = "usemask"
	    self.Params["allowmask"] = "1"
	elif pval == "private":
	    self.Params["security"] = "private"
	    self.del_param("allowmask")
	else:
	    if self.GottenFriends == 0:
		self.cli_getfriendgroups()
	    if self.Cache.Friends != {}:
                mask = 0
                flist = []
                vlist = string.split(string.lower(pval), ",")
                for v in vlist:
                    flist.append(v.strip())
		for k in self.Cache.Friends.keys():
                    if string.lower(k) in flist:
                        mask |= int(self.Cache.Friends[k])
                if mask == 0:
                    raise ValueError
                self.Params["security"] = "usemask"
                self.Params["allowmask"] = str(mask)
 		return
	    raise ValueError


    # -----
    # Saving and displaying posts.
    # -----

    def write_metadata(self, f):
	"Write out post meta-data to a filehandle."

	if self.Params.has_key("year"):
	    f.write("Date:      " + self.format_time() + "\n")
	else:
	    timetuple = time.localtime(time.time())
	    f.write("Date:      " + time.strftime("%Y-%m-%d %H:%M",
						  timetuple) + "\n")

	if self.Params.has_key("usejournal"):
	    f.write("Journal:   " + self.Params["usejournal"] + "\n")
	    if self.Params.has_key("poster"):
		f.write("Poster:    " + self.Params["poster"] + "\n")

	if self.Params.has_key("subject"):
	    f.write("Subject:   " + self.Params["subject"] + "\n")

        if self.Params["blogapi"] == "lj":
            if self.Params.has_key("prop_taglist"):
                f.write("Tags:      " + self.Params["prop_taglist"] + "\n")
        else:
            if self.Params.has_key("prop_taglist"):
                f.write("Category:  " + self.Params["prop_taglist"] + "\n")
            if self.Params.has_key("prop_keywords"):
                f.write("Tags:      " + self.Params["prop_keywords"] + "\n")

	if self.Mood != "":
	    f.write("Mood:      " + self.Mood + "\n")

	if self.Params.has_key("prop_picture_keyword"):
	    f.write("Picture:   " + self.Params["prop_picture_keyword"] + "\n")

	if self.Params.has_key("prop_current_music"):
	    f.write("Music:     " + self.Params["prop_current_music"] + "\n")

	try:
	    if self.Params["security"] == "usemask":
		if self.Params["allowmask"] == "1":
		    f.write("Security:  friends\n")
		else:
		    f.write("Security:  custom\n");
		    mnum = int(self.Params["allowmask"])
		    olist = []
		    for k in self.sort_friendgroups():
			if (mnum & int(self.Cache.Friends[k])):
			    olist.append(k)
		    f.write("Friends:   " + commalist(olist) + "\n")
	    else:
		f.write("Security:  " + self.Params["security"] + "\n")
	except KeyError:
	    pass

        olist = []
        for k in ("preformatted", "backdated", "nocomments", "noemail"):
            if self.Params.has_key("prop_opt_%s" % (k)):
                olist.append(k)
        if olist != []:
            f.write("Options:   " + string.join(olist) + "\n")

        if self.Params.has_key("itemid"):
	    f.write("ItemID:    " + self.Params["itemid"] + "\n")


    def write_post(self, f):
	"Write out a post to a filehandle."

	self.write_metadata(f)

	try:
            try:
                d = open(self.Params["draft_file"], 'r')
            except IOError:
                print "Error reading draft file: %s" % (errmsg())
                return
	    f.write("\n")
	    line = d.readline()
	    while line != "":
		f.write(line)
		line = d.readline()
	    d.close()
	except:
	    pass


    def display_post(self):
	"Display a post, using a pager if one is available."

	print barline
	print

	try:
	    ppath = self.Params["pager"]
	except KeyError:
	    try:
		ppath = os.environ['PAGER']
	    except KeyError:
		ppath = ""

	if ppath == "":
	    ppath = "/usr/bin/more"

	# -- Make sure we can execute this pager before trying it.
	#    If not, we just splat the file to the screen. 
	#
	#    We have some system-specific things to handle here.
	#    Python doesn't implement popen() on the Mac, and pipes
	#    behave weirdly with Windows (per the Python FAQ).

	if os.access(ppath, os.F_OK | os.X_OK) == 0 or os.name == "mac":
	    f = sys.stdout
	    is_pipe = 0
	else:
	    if sys.platform == "win32":
		import win32pipe
		f = win32pipe.popen(ppath, "w")
	    else:
		f = os.popen(ppath, "w")
	    is_pipe = 1

	self.write_post(f)

	if is_pipe == 1:
	    f.close()

	print
	print barline
	print

    def save_post_file(self):
	"Save post to a file."

	print
	res = sane_raw_input("File name to save under: ")
	print

	afile = os.path.expanduser(res)
	try:
	    f = open(afile, 'w')
	except IOError:
	    print "Error writing to file '%s': %s" % (afile, errmsg())
	    return

	self.write_post(f)
	f.close()
	print "Saved."

    def make_archive(self, is_edit = 0, text_to_output = ""):
	"Archive current post."

	# -- Make sure we have the base archive directory, and then
	#    the subpaths if we need them.
	#
	#    If we have subdirs turned on, each journal type gets its
	#    own subdirectory.
	#
	#    If we can't create subdirectories, we use the upper level.

	adir = self.Params["archive_dir"]
	ok = create_dir(adir, "archive")
	if ok == 0:
	    return ""

	if self.Params["archive_subdirs"] == "1":
	    if self.Params.has_key("usejournal"):
		tmp = adir + "/" + self.Params["usejournal"]
	    else:
		tmp = adir + "/" + self.Params["user"]
	    ok = create_dir(tmp, "archive journal subdirectory")
	    if ok != 0:
		adir = tmp

	if self.Params["organize"] in ("year", "month"):
	    tmp = adir + "/" + self.Params["year"]
	    ok = create_dir(tmp, "archive year")
	    if ok != 0:
		adir = tmp

	if self.Params["organize"] == "month":
	    tmp = adir + "/" + self.Params["mon"]
	    ok = create_dir(tmp, "archive month")
	    if ok != 0:
		adir = tmp

	# -- Write out the new file. If we have a hierarchical directory
	#    structure, leave out the earlier date-parts of the filename.

	if self.Params["organize"] == "none":
	    afdate = self.Params["year"] + self.Params["mon"]
	elif self.Params["organize"] == "year":
	    afdate = self.Params["mon"]
	else:
	    afdate = ""

	afile = "%s/%s%s_%s%s" % (adir, afdate, self.Params["day"],
				  self.Params["hour"], self.Params["min"])

	if (is_edit == 1) and (self.Params["archive_overwrite"] != "1"):
	    timetuple = time.localtime(time.time())
	    afile = afile + "_ed" + time.strftime("%Y%m%d%H%M", timetuple)

	try:
	    f = open(afile, 'w')
	except IOError:
	    print "Error writing to archive file: %s" % (errmsg())
	    return ""

	if text_to_output == "":
	    self.write_post(f)
	else:
	    self.write_metadata(f)
	    f.write("\n")
	    f.write(text_to_output)
	    f.write("\n")
	f.close()
	return afile

    # -----
    # Upload a post.
    # -----

    def go_post(self, is_blog = 0):
	"Send a post to the server."

	# -- Read in the draft file.

	ok = self.slurp_draft("Post")
	if ok == 0:
	    return 0

	# -- Don't post if empty.

        if self.Params["event"] == "":
            print "Nothing to post."
	    return 0

	# -- Save the time of the post, if we don't have one yet.
	#    That way we will always stamp when we tried to post (unless
	#    we're backdating).
	#    Save our session data, just in case.

	if self.Params.has_key("year") == 0:
	    timetuple = time.localtime(time.time())
	    self.populate_time(timetuple)
        if is_blog == 1 and self.Blogger.PostTime == "":
            self.Blogger.PostTime = datetime.datetime.utcnow().isoformat()
	self.save_session()

	# -- Go post it. If we failed, just go back to posting mode.

        if is_blog == 1:
            ok = self.Blogger.blog_postevent()
        else:
            ok = self.cli_postevent()
	if ok == 0:
	    return 0
	else:
	    print "Post successful."

	# -- Archive, if we should.

	if self.getval("archive", "0") == "1":
            afile = self.make_archive(0)
            if afile != "":    
                print "Archived post: %s" % (afile)

	# -- Delete the old files. Clear out meta-data.

	self.clear_session()
	print "Draft cleared. Beginning new session."
	return 1

    # -----
    # Submit a post edit.
    # -----

    def go_edit(self, is_blog = 0):
	"Post an edited entry."

	# -- Save the session data.

	self.save_session()

	# -- Read in the draft file.

	ok = self.slurp_draft("Edit")
	if ok == 0:
	    return 0

	# -- If we are timestamping the edit, append that.

	if self.Params.has_key("edit_times") and self.Params["edit_times"] == "1": 
	    now = time.localtime(time.time())
	    if now[0] == int(self.Params["year"]):
		if now[1] == int(self.Params["mon"]) and \
		   now[2] == int(self.Params["day"]):
		    ts_text = time.strftime("[ Edited at %I:%M %p. ]", now)
		else:
		    ts_text = time.strftime("[ Edited on %B %d at %I:%M %p. ]", now)
	    else:
		ts_text = time.strftime("[ Edited on %B %d, %Y, at %I:%M %p. ]", now)
	    if self.Params.has_key("prop_opt_preformatted") and \
	       self.Params["prop_opt_preformatted"] == "1":
		self.Params["event"] = append_htblock(self.Params["event"],
						      "<I>" + ts_text + "</I>")
	    else:
		self.Params["event"] = "%s\n%s\n" % \
				       (self.Params["event"], ts_text)

	# -- Make an upload attempt.

	print "Sending edited post..."
	print

        if is_blog == 1:
            ok = self.Blogger.blog_editevent()
        else:
            ok = self.cli_editevent()
	if ok == 0:
	    return 0
	else:
	    print "Edit successful."

	# -- Archive editing, if we should.

        if self.getval("archive_edits", "0") == "1":
	    self.make_archive(1)
	    print "Your edited posting has been archived."

	# -- Delete the old files. Clear out meta-data.

	self.clear_session()
	self.Entries = []
	self.Entry = {}
	print "Draft cleared. Beginning new session."
	return 1


    # -----
    # Delete a post.
    # -----

    def go_delete(self, is_blog = 0):
	"Delete a post."

	print "Deleting..."
	print

        if is_blog == 1:
            ok = self.Blogger.blog_delevent()
        else:
            ok = self.cli_delevent()
	if ok == 0:
	    return 0

	# -- Once we're done we should return to blank-slate status.

	self.clear_session()
	self.Entries = []
	self.Entry = {}
	print "Deleted. Beginning new session."
	return 1


    # -----
    # Draft resumption.
    # -----

    def read_metadata(self, mfname):
	"Read and set meta-data from a file."

	try:
	    f = open(mfname, 'r')
	except IOError:
	    return			# no big loss.

	meta_in = {}
	line = f.readline()
	while line != "":
	    line = line[:-1]		# discard newline
	    if line == "":
		pass
	    elif line[0] == "#":	# comment line, discard
		pass
	    else:
		inpair = string.split(line, '=', 1)
		meta_in[inpair[0]] = inpair[1]
		if inpair[0] == "prop_current_mood":
		    self.Mood = inpair[1]
		elif inpair[0] == "prop_current_moodid":
		    for k in self.Cache.Moods.keys():
			if self.Cache.Moods[k] == inpair[1]:
			    self.Mood = k
			    break
	    line = f.readline()
	f.close()

	# -- We only allow ourselves to read what we know we could have
	#    written. Yes, a user could always do something weird here,
	#    but this is good enough.

	for k in meta_in.keys():
	    if k in Basic_MetaData:
		self.Params[k] = meta_in[k]


    def resume_draft(self, dfile, is_virgin = 0):
	"Resume working on a previous draft, given its filename."

	# -- Look for the file. Try the filename as specified, then look
	#    in the drafts directory.

	dfile = os.path.expanduser(dfile)

	if os.path.exists(dfile) == 1:
	    self.Params["draft_file"] = dfile
	else:
	    dfile = self.Params["draft_dir"] + "/" + dfile
	    if os.path.exists(dfile) == 1:
		self.Params["draft_file"] = dfile
	    else:
		print "Session unchanged. The specified draft file was not found."
		return 0

	# -- Find the base timestring.

	base_dfile = os.path.basename(dfile)
	timestr = string.join((string.split(base_dfile, '_'))[-2:], '_')

	# -- Clear out any meta-data that we might have previously had.

	if is_virgin == 0:
	    self.clear_metadata()

	# -- Look for the meta-data file in the same directory. Load it.

	mfname = os.path.dirname(dfile) + "/" + ".meta_" + timestr
	if os.path.exists(mfname) == 1:
	    self.read_metadata(mfname)

	print "Resuming previous draft of post."
	return 1


    def read_archive(self, afile, atype = "archive"):
        "Read in a post from an archive/template."

        afile = os.path.expanduser(afile)
        if os.path.exists(afile) != 1:
            print "Error: That %s file does not exist." % (atype)
            return 0
        try:
            f = open(afile, "r")
        except IOError:
            print "Error opening %sd post: %s" % (atype, errmsg())
            return 0

        # -- Read the meta-data
        
        line = f.readline()
        while line != "":
            line = string.rstrip(line)  # kill newline, trailing whitespace
            if line == "":
                pass
            else:
                (elem, val) = line.split(":", 1)
                val = val.strip()
                if elem == "Date":
                    if atype == "archive":
                        try:
                            ttup = time.strptime(val, "%Y-%m-%d %H:%M")
                        except:
                            print "Malformed entry time. Setting to present."
                            ttup = time.localtime(time.time())
                        self.populate_time(ttup)
                elif elem == "Subject":
                    self.Params["subject"] = val
                elif elem == "Journal":
                    self.Params["usejournal"] = val
                elif elem == "Poster":
                    self.params["poster"] = val
                elif elem == "Category":
                    self.Params["prop_taglist"] = val
                elif elem == "Tags":
                    if self.Params["blogapi"] == "lj":
                        self.Params["prop_taglist"] = val
                    else:
                        self.Params["prop_keywords"] = val
                elif elem == "Mood":
                    self.Mood = val
                elif elem == "Picture":
                    self.Params["prop_picture_keyword"] = val
                elif elem == "Music":
                    self.Params["prop_current_music"] = val
                elif elem == "Security":
                    if val != "custom":
                        self.set_security(val)
                elif elem == "Friends":
                    self.set_security(val)
                elif elem == "Options":
                    eopts = val.split(" ")
                    for e in eopts:
                        self.Params["prop_opt_%s" % (e)] = "1"
                elif elem == "ItemID":
                    pass
                else:
                    print "Warning: Unrecognized directive. %s: %s" % (elem, val)
                # Yes, this really goes under the else clause, since we
                # want to exit the loop if we got a blank line
                line = f.readline()

        # -- Read the post body
        
        body = []
        line = f.readline()
        while line != "":
            body.append(line)
            line = f.readline()
        self.Params["event"] = string.join(body, "")
        f.close()
        return 1


    def read_template(self, template):
        "Read in a template and create a draft file out of it."

        self.clear_metadata()

        # -- Get the data as if it were an archive.

        if self.read_archive(template, "template") == 0:
            return 0

        # -- New draft file. The time is always the present.

        timetuple = time.localtime(time.time())
        timestr = time.strftime("%Y%m%d_%H%M%S", timetuple)
        ok = self.make_draft_file(timestr)
        if ok == 0:
            return 0
        self.save_metadata(timestr)

        try:
            f = open(self.Params["draft_file"], "w")
        except:
            print "Error writing draft file: %s" % (errmsg())
            return 0

        if self.Params.has_key("event"):
            f.write(self.Params["event"])
        f.close()
        print "Successfully read template: %s" % (template)
        return 1

    # -----
    # Friend and friend group management.
    # -----

    def choose_friendgroup(self):
        "Choose what groups to place a friend in."
        
        print "0. Don't put this friend in any groups."
        if self.GottenFriends == 0:
            self.cli_getfriendgroups()
        i = 1
        klist = self.sort_friendgroups()
        for k in klist:
            print "%d. %s" % (i, k)
            i = i + 1
        print
        ginput = sane_raw_input("Group(s) to place friend in (list of numbers): ")
        print
        gmask = 0
        if ginput != "":
            glist = ginput.split(" ")
            for g in glist:
                try:
                    gnum = int(g)
                except ValueError:
                    gnum = -1
                if gnum > 0:
                    gmask |= int(self.Cache.Friends[klist[gnum - 1]])
            if gmask == 0:
                print "No valid groups specified. Defaulting to no group."
                print
        return gmask

                
    def add_friend(self):
        "Manage adding a friend."

        fname = sane_raw_input("Enter the username of your new friend: ").strip()
        print
        if fname == "":
            return
        print "These are your current friend groups."
        print
        gmask = self.choose_friendgroup()
        bgcol = color_input("Background color number to use for friend: ")
        print
        fgcol = color_input("Foreground color number to use for friend: ")
        print
        self.cli_addfriend(fname, gmask, fgcol, bgcol)


    def edit_friend(self):
        "Edit an existing friend."

        # -- We always re-retrieve the friend list, since we may be
        #    changing it. If we fail at that, we can't succeed at this.

        if not self.cli_getfriends():
            return
            
        fname = sane_raw_input("Enter the username of the friend: ").strip()
        print
        if fname == "":
            return

        try:
            friend = self.Buddies[fname]
        except:
            print "That user is not your friend."
            return

        cdict = dict( [ (h, n) for (n, h) in Colors ] )
        frgrps = self.sort_friendgroups()

        try:
            gmask = friend["groupmask"]
        except:
            gmask = 0
        bg = friend["bgcolor"].upper()
        fg = friend["fgcolor"].upper()

        while 1:
            olist = []
            for k in frgrps:
                if (gmask & int(self.Cache.Friends[k])):
                    olist.append(k)
            print "EDIT FRIEND MENU"
            print
            print "[b] Background color: %s" % (cdict[bg])
            print "[f] Foreground color: %s" % (cdict[fg])
            print "[g] Groups: %s" % ( (commalist(olist), "(none)")[gmask == 0] )
            print "[u] Update (send edit for %s)." % (fname)
            print "[r] Return to friends management menu."
            print
            res = self.get_choice()
            if res in ("R", "r"):
                return
            elif res in ("U", "u"):
                self.cli_addfriend(fname, gmask, fg, bg, 1)
                return
            elif res in ("B", "b"):
                bg = color_input("Background color number to use for friend: ")
                print
            elif res in ("F", "f"):
                fg = color_input("Foreground color number to use for friend: ")
                print
            elif res in ("G", "g"):
                gmask = self.choose_friendgroup()
            else:
                print "That is not a valid option."
                print


    def list_friendgroups(self):
        "List friend groups."

        print "Retrieving existing friend groups..."

        # -- Always fetch.

        if not self.cli_getfriendgroups():
            print "Could not obtain current friend groups data."
            return 0
        klist = self.sort_friendgroups()
        
        print """
Friend Group              Order    Public    Bit    Group Mask
------------              -----    ------    ---    ----------"""
        
        for k in klist:
            print "%-25s %5s    %6s    %3d    %10s" % (k, self.Cache.FriendSorter[k], ("No", "Yes")[k in self.Cache.FriendPublic], self.Cache.FriendNums[k], self.Cache.Friends[k])

        return 1
    

    def add_friendgroup(self):
        "Add a new friend group."

        if not self.list_friendgroups():
            return
        print

        # -- We need to find the next unused group number.

        cur_grps = self.Cache.FriendNums.values()
        bitrange = range(1, 31)
        diffs = map(lambda n: ("", n)[n not in cur_grps], bitrange)
        diffs.sort()
        freenum = diffs[0]
        if freenum == "":
            print "You have already created the maximum number of friend groups."
            return

        # -- Now get the group data.

        gname = sane_raw_input("Enter new group name: ").strip()
        if gname == "":
            return
        print

        done = 0
        while not done:
            ssort = sane_raw_input("Enter sort order number (lower numbers come first): ")
            print
            try:
                snum = int(ssort)
            except:
                snum = 0
            if snum < 1 or snum > 255:
                print "That is not a valid sort order number."
                print
            else:
                done = 1

        done = 0
        while not done:
            spub = sane_raw_input("Make this group public? (Y/N): ").strip()
            print
            if spub in ("Y", "y"):
                pub = 1
                done = 1
            elif spub in ("N", "n"):
                pub = 0
                done = 1

        self.cli_addfriendgroup(gname, freenum, snum, pub)


    def get_groupkey(self):
        "Get a group number from an inputed name."
        
        gs = sane_raw_input("Name of group: ").strip().lower()
        if gs == "":
            return ""
        print

        klist = self.Cache.Friends.keys()
        gnames = map(lambda k: k.lower(), klist)
        try:
            gkey = klist[gnames.index(gs)]
            return gkey
        except:
            print "That is not a valid group."
            return ""
        

    def edit_friendgroup(self):
        "Edit an existing friend group."

        if not self.list_friendgroups():
            return
        print

        gname = self.get_groupkey()
        if gname == "":
            return

        gnum = self.Cache.FriendNums[gname]
        gsort = int(self.Cache.FriendSorter[gname])
        if gname in self.Cache.FriendPublic:
            gpub = 1
        else:
            gpub = 0

        while 1:
            print
            print "EDIT FRIEND GROUP MENU"
            print
            print "[n] Name: %s" % (gname)
            print "[s] Sort order: %d" % (gsort)
            print "[p] Public: %s" % ( ("(no)", "(yes)")[gpub == 1] )
            print "[u] Update (send edit for group)."
            print "[r] Return to administrative menu."
            print
            res = self.get_choice()
            if res in ("R", "r"):
                return
            elif res in ("N", "n"):
                ng = sane_raw_input("Enter new group name: ").strip()
                print
                if ng == "":
                    print "That is not a valid group name."
                else:
                    gname = ng
            elif res in ("S", "s"):
                sg = sane_raw_input("Enter new sort order number: ").strip()
                print
                try:
                    snum = int(sg)
                except:
                    snum = 0
                if snum < 1 or snum > 255:
                    print "That is not a valid sort order number."
                else:
                    gsort = snum
            elif res in ("P", "p"):
                if gpub == 0:
                    gpub = 1
                    print "This group will be public."
                else:
                    gpub = 0
                    print "This group will be private."
            elif res in ("U", "u"):
                self.cli_editfriendgroup(gname, gnum, gsort, gpub)
                return
            else:
                print "That is not a valid option."


    def del_friendgroup(self):
        "Delete a friend group."

        if not self.list_friendgroups():
            return
        print

        gkey = self.get_groupkey()
        if gkey == "":
            return

        self.cli_delfriendgroup(self.Cache.FriendNums[gkey])

    # -----
    # User interaction menus.
    # -----

    def drafts_menu(self):
	"Display a menu of old drafts."

	print """
SELECT DRAFT

[f] Enter filename of draft.
[l] Select from a list of old drafts."""
	print
	res = self.get_choice()
	dfile = ""

	if res in ("F", "f"):
	    dfile = sane_raw_input("Enter filename of draft: ")
	    print
	    dfile = string.strip(dfile)

	elif res in ("L", "l"):
	    try:
		import dircache
		import fnmatch
	    except ImportError:
		print "Your Python installation lacks the necessary modules."
		return
	    list = dircache.listdir(self.Params["draft_dir"])
	    fkeys = {}
	    for n in list:
		if fnmatch.fnmatch(n, ".meta_????????_??????"):
		    try:
			mfile = open(self.Params["draft_dir"] + "/" + n)
			fkeys[n[6:]] = "(no subject)"
			line = mfile.readline()
			while line != "":
			    line = line[:-1]
			    if line == "":
				pass
			    elif line[0] == "#":
				pass
			    else:
				inpair = string.split(line, '=', 1)
				if inpair[0] == "subject":
				    fkeys[n[6:]] = inpair[1]
				    break
			    line = mfile.readline()
			mfile.close()
		    except IOError:
			pass

	    klist = fkeys.keys()
	    klist.sort()
	    i = 1
	    for k in klist:
		if i < 10:
		    print "%d. " % (i),
		else:
		    print "%d." % (i),
		print k[:4] + "-" + k[4:6] + "-" + k[6:8],
		print k[9:11] + ":" + k[11:13] + ":" + k[13:15],
		if (len(fkeys[k]) > 45):
		    print truncstr_more(fkeys[k], 45)
		else:
		    print fkeys[k]
		i = i + 1

	    print
	    res = sane_raw_input("Enter draft number: ")
	    print
	    try:
		n = int(res)
	    except ValueError:
		n = 0
	    if n < 1 or n > len(klist):
		print "Invalid choice. You need to choose a valid draft."
	    else:
		dfile = "draft_" + klist[n - 1]

	else:
	    print "That is not a valid option."

	if dfile != "":
	    self.save_session(1)	# save meta-data, since it'll be wiped
	    repeat_ok = self.resume_draft(dfile)
	    while repeat_ok:
		try:
		    repeat_ok = self.post_menu()
		except KeyboardInterrupt:
		    self.handle_interrupt("posting")


    def username_menu(self):
	"Display a username menu."

	print
	print "SELECT USERNAME"
	print

	i = 1
	klist = self.Logins.keys()
	for k in klist:
	    print "%d. %s" % (i, k)
	    i = i + 1

	print
	res = sane_raw_input("Enter username number: ")
	print

	try:
	    n = int(res)
	except ValueError:
	    n = 0
	if n < 1 or n > len(klist):
	    print "Invalid choice. You need to choose a valid username."
	    return 0
	else:
            self.set_user(klist[n - 1])
	    self.Params["hpassword"] = self.Logins[klist[n - 1]]

	return 1


    def select_time(self):
	"Set the posting time."

	print """
The date and time should be entered in YYYY-MM-DD HH:MM format.
The time is 24-hour time (00-23 for midnight - 11 pm).
Just press return without entering anything, to set this to the current time.
"""
	dstr = sane_raw_input("Enter date and time: ")
	print

	dstr = string.strip(dstr)
	if dstr == "":
	    timetuple = time.localtime(time.time())
	else:
	    try:
		timetuple = time.strptime(dstr, "%Y-%m-%d %H:%M")
	    except ValueError:
		print "Time format error. Time not changed."
		return

	self.populate_time(timetuple)
	

    def moodlist_menu(self):
	"Select mood from list."

	klist = self.Cache.Moods.keys()	# must copy, sort() is in-place
	klist.sort()
	column_table(klist, 4)

	print
	res = sane_raw_input("Enter mood number: ")
	print

	try:
	    n = int(res)
	except ValueError:
	    n = 0
	if n < 1 or n > len(klist):
	    print "Invalid choice. Mood unchanged."
	else:
	    mood_text = klist[n - 1]
	    self.set_mood(mood_text)
	    print "Mood set to %s." % (mood_text)


    def mood_menu(self):
	"Mood selection menu."

	print """
MOOD SELECTION MENU

[n] No mood.
[l] Select current mood from pre-defined list.
[o] Select other mood."""
	print
	res = self.get_choice()

	if res in ("N", "n"):
	    self.set_mood("")
	    print "Selected no mood."
	elif res in ("O", "o"):
	    mood_text = sane_raw_input("Mood: ")
	    self.set_mood(mood_text)
	    print
	    print "Mood selected."
	elif res in ("L", "l"):
	    if self.Cache.Moods == {}:
		print "No pre-defined moods are available."
	    else:
		self.moodlist_menu()
	else:
	    print "That is not a valid option."


    def pickw_menu(self):
	"Select picture keyword from list."

	print
	print "PICTURE KEYWORD SELECTION"
	print
	print "0.   (none)"
        maxlen = 0
	for k in self.Cache.PicKws:
            if len(k) > maxlen:
                maxlen = len(k)
        column_table(self.Cache.PicKws, 78 / (maxlen + 6))
	print
	res = self.get_choice()

	try:
	    n = int(res)
	except ValueError:
	    n = -1
	if n == 0:
	    self.del_param("prop_picture_keyword")
	    print "No picture keyword selected."
	elif n < 0:
	    print "Invalid choice. Selection unchanged."
	else:
	    try:
		self.Params["prop_picture_keyword"] = self.Cache.PicKws[n - 1]
		print "Selected " + self.Cache.PicKws[n - 1] + " picture."
	    except IndexError:
		print "Invalid choice. Selection unchanged."


    def option_menu(self):
	"Miscellaneous option menu."

	print
	print "MISCELLANEOUS OPTIONS"
	print
	val_preformat = 0
	print "[a] Change auto-format option to:",
	try:
	    if self.Params["prop_opt_preformatted"] == "1":
		val_preformat = 1
		print "on (post will be formatted for you)"
	    else:
		print "off (format your post yourself)"
	except KeyError:
	    print "off (format your post yourself)"
	val_backdate = 0
	print "[b] Change backdate option to:",
	try:
	    if self.Params["prop_opt_backdated"] == "1":
		val_backdate = 1
		print "no backdating"
	    else:
		print "backdating on"
	except KeyError:
	    print "backdating on"
	val_nocom = 0
	print "[c] Change comments option to:",
	try:
	    if self.Params["prop_opt_nocomments"] == "1":
		val_nocom = 1
		print "comments allowed"
	    else:
		print "comments disallowed"
	except KeyError:
	    print "comments disallowed"
	val_noemail = 0
        print "[s] Screen comments that are posted by:",
        try:
            if self.Params["prop_opt_screening"] == "A":
                print "everyone"
            elif self.Params["prop_opt_screening"] == "R":
                print "anonymous users"
            elif self.Params["prop_opt_screening"] == "F":
                print "non-friends"
            elif self.Params["prop_opt_screening"] == "N":
                print "none (do not screen)"
            else:
                print "unknown option %s" % (self.Params["prop_opt_screening"])
        except:
            print "none (do not screen)"
	print "[e] Change email option to:",
	try:
	    if self.Params["prop_opt_noemail"] == "1":
		val_noemail = 1
		print "email comments"
	    else:
		print "do not email comments"
	except KeyError:
	    print "do not email comments"
	print "[r] Return to the posting menu."
	print
	res = self.get_choice()

	if res in ("A", "a"):
	    if val_preformat == 0:
		self.Params["prop_opt_preformatted"] = "1"
		print "Auto-format turned off."
	    else:
		del self.Params["prop_opt_preformatted"]
		print "Auto-format turned on."
	elif res in ("B", "b"):
	    if val_backdate == 0:
		self.Params["prop_opt_backdated"] = "1"
		print "Post will be backdated."
	    else:
		del self.Params["prop_opt_backdated"]
		print "Post will not be backdated."
	elif res in ("C", "c"):
	    if val_nocom == 0:
		self.Params["prop_opt_nocomments"] = "1"
		print "Comments will be disallowed."
	    else:
		del self.Params["prop_opt_nocomments"]
		print "Comments will be allowed."
	elif res in ("E", "e"):
	    if val_noemail == 0:
		self.Params["prop_opt_noemail"] = "1"
		print "Comments will not be emailed."
	    else:
		del self.Params["prop_opt_noemail"]
		print "Comments will be emailed."
        elif res in ("S", "s"):
            print """
SELECT A SCREENING LEVEL

[n] Don't screen any comments.
[e] Screen comments posted by everyone.
[a] Screen comments posted by anonymous users.
[f] Screen only comments posted by non-friends.
"""
            slev = self.get_choice()
            if slev in ("N", "n"):
                # -- Must explicitly set in order to change if post
                #    is already on server.
                self.Params["prop_opt_screening"] = "N"
                print "Comments will not be screened."
            elif slev in ("E", "e"):
                self.Params["prop_opt_screening"] = "A"
                print "All comments will be screened."
            elif slev in ("A", "a"):
                self.Params["prop_opt_screening"] = "R"
                print "Anonymous comments will be screened."
            elif slev in ("F", "f"):
                self.Params["prop_opt_screening"] = "F"
                print "Non-friend comments will be screened."
            else:
                print "That is not a valid choice."
	elif res in ("R", "r"):
	    pass
	else:
	    print "That is not a valid option."


    def journal_menu(self, changepic = 0):
	"Journal selection menu."

	print 
	print "JOURNAL SELECTION MENU"
	print
	print "0.   (" + self.Params["user"] + ") -- default"
        maxlen = 0
        jlist = []
	for k in self.Cache.Journals:
            if self.CommPics.has_key(k):
                jlist.append("%s (picture: %s)" % (k, self.CommPics[k]))
            else:
                jlist.append(k)
            if len(jlist[-1]) > maxlen:
                maxlen = len(jlist[-1])
        column_table(jlist, 78 / (maxlen + 6))
	print
	res = self.get_choice()

	try:
	    n = int(res)
	except ValueError:
	    n = -1
	if n == 0:
	    self.del_param("usejournal")
	    print "Selected default journal (your own)."
	elif n < 0:
	    print "Invalid choice. Selection unchanged."
	else:
	    try:
		jname = self.Cache.Journals[n - 1]
		self.Params["usejournal"] = jname
		print "Selected %s." % (jname)
		# -- If we don't have a picture keyword set, and this
		#    journal has a valid default picture, set that.
		if changepic and self.CommPics.has_key(jname) and \
		   not self.Params.has_key("prop_picture_keyword"):
		    self.set_pickw(self.CommPics[jname])
	    except IndexError:
		print "Invalid choice. Selection unchanged."

    def friendgroup_menu(self):
	"Select friend group for security permissions."

	# -- Go download the friend groups if we don't have them already.

	if self.GottenFriends == 0:
	    self.cli_getfriendgroups()

	# -- Check for case of no friend groups defined.

	if self.Cache.Friends == {}:
            self.Params["security"] = "usemask"
	    self.Params["allowmask"] = "1"
	    print "No friend groups defined."
	    print "Security level set to friends only."
	    return

	# -- Otherwise show menu.

	print
	print "CHOOSE FRIEND GROUP"
	print
	print "0. All friends"

	i = 1
	klist = self.sort_friendgroups()
	for k in klist:
            print "%d. %s" % (i, k)
	    i = i + 1

	print
	res = sane_raw_input("Friend group(s) permitted (list of numbers): ")
	print

        if res == "":
            print "Nothing selected. Security level not changed."
            return

        nlist = string.split(res, " ")
        succ = 0
        mask = 0
        for num in nlist:
            try:
                n = int(num)
            except ValueError:
                n = -1
            if n == 0:    
                print "Security level set to all friends."
                self.Params["security"] = "usemask"
                self.Params["allowmask"] = "1"
                return
            if n < 0 or n > len(klist):
                print "Warning: '%s' is an invalid choice." % (num)
            else:
                mask |= int(self.Cache.Friends[klist[n - 1]])
                succ += 1
        if succ == 0:
            print "No valid selections. Security level not changed."
            return
        self.Params["security"] = "usemask"
        self.Params["allowmask"] = str(mask)
        olist = []
        for k in self.sort_friendgroups():
            if (mask & int(self.Cache.Friends[k])):
                olist.append(k)
        print "Security level set to friend %s: %s" % ( ("groups", "group")[len(olist) == 1], commalist(olist))


    def security_menu(self):
	"Security permissions level menu."

	print """
SET SECURITY PERMISSIONS FOR POST

[d] Set security level to public (default).
[f] Set security level to friends only.
[c] Set security level to custom (select friend groups).
[p] Set security level to private."""
	print
	res = self.get_choice()

	if res in ("D", "d"):
	    self.Params["security"] = "public"
	    self.del_param("allowmask")
	    print "Security level set to public."
	elif res in ("F", "f"):
	    self.Params["security"] = "usemask"
	    self.Params["allowmask"] = "1"
	    print "Security level set to friends only."
	elif res in ("C", "c"):
	    self.friendgroup_menu()
	elif res in ("P", "p"):
	    self.Params["security"] = "private"
	    self.del_param("allowmask")
	    print "Security level set to private."
	else:
	    print "That is not a valid option."	    


    def menu_opt_subject(self):
        "Menu option for changing subject."

	print "[s] Change subject:",
	if self.Params.has_key("subject"):
	    if len(self.Params["subject"]) > 45:
		print truncstr_more(self.Params["subject"], 45)
	    else:
		print self.Params["subject"]
	else:
	    print "(none)"


    def menu_opt_tags(self, namestr):
        "Menu option for changing category or tags."

        print "[c] Change %s:" % (namestr),
	if self.Params.has_key("prop_taglist"):
	    if len(self.Params["prop_taglist"]) > 45:
		print truncstr_more(self.Params["prop_taglist"], 45)
	    else:
		print self.Params["prop_taglist"]
	else:
	    print "(none)"


    def menu_opt_keywords(self):
        "Menu option for changing non-LJ tags."

        print "[k] Change keyword tags:",
        if self.Params.has_key("prop_keywords") and self.Params["prop_keywords"] != "":
	    if len(self.Params["prop_keywords"]) > 45:
		print truncstr_more(self.Params["prop_keywords"], 45)
	    else:
		print self.Params["prop_keywords"]
	else:
	    print "(none)"


    def tags_menu(self):
        "Change a list of LJ tags, applying pic keywords if necessary."

        print
        print "TAGS MENU"
        print
        print "0.   (use one or more new tags)"

        if self.GottenTags == 0:
            self.cli_getusertags()
        self.Cache.Tags.sort()
        maxlen = 0
        tlist = []
        for t in self.Cache.Tags:
            if self.TagPics.has_key(t):
                tlist.append("%s (picture: %s)" % (t, self.TagPics[t]))
            else:
                tlist.append(t)
            if len(tlist[-1]) > maxlen:
                maxlen = len(tlist[-1])
        column_table(tlist, 78 / (maxlen + 6))
        print
        res = sane_raw_input("Tag(s) to give this post (list of numbers): ")
        print
        post_tags = []
        nlist = res.split(" ")
        
        if "0" in nlist:        
            res = sane_raw_input("Enter one or more new tag names, separated by commas: ")
            if "," in res:
                tlist = res.split(",")
                for t in tlist:
                    t = t.strip()
                    post_tags.append(t)
                    if t not in self.Cache.Tags:
                        self.Cache.Tags.append(t)
                print "New tags defined."
            else:
                t = res
                post_tags.append(t)
                if t not in self.Cache.Tags:
                    self.Cache.Tags.append(t)
                print "New tag defined."
                
        for nstr in nlist:
            try:
                n = int(nstr)
            except ValueError:
                n = 0
            if n > 0 and n <= len(self.Cache.Tags):
                t = self.Cache.Tags[n - 1]
                if t not in post_tags:
                    post_tags.append(t)
                    
        if post_tags == []:
            print "Warning, no valid tags chosen. Tags unchanged."
            return 0
        
        self.Params["prop_taglist"] = string.join(post_tags, ", ")
        print "Tags changed."

        # - If we don't have a picture keyword set, walk the list of
        #   tags until we get a picture match. If we get one, set it.

        if not self.Params.has_key("prop_picture_keyword"):
            try:
                for t in post_tags:
                    if self.TagPics.has_key(t):
                        self.set_pickw(self.TagPics[t])
                        return 0
            except:
                pass                    # don't muck with malformed input
        return 0
    

    def set_tag(self, tname):
        "Set a tag directly."

        if tname not in self.Cache.Tags:
            self.Cache.Tags.append(tname)
        self.Params["prop_taglist"] = tname

    def set_keywords(self, kstr):
        "Set keyword tags directly."

        self.Params["prop_keywords"] = kstr
        

    def menu_opt_common(self, edit_only):
        "Menu option for dealing with drafts."

	print "---"

	dsize = 0
	if self.Params.has_key("draft_file"):
	    try:
		dsize = (os.stat(self.Params["draft_file"]))[stat.ST_SIZE]
	    except OSError:
		dsize = 0
	if dsize == 0:
	    print "[d] Display current post (no text yet)."
	else:
	    print "[d] Display current post (%d bytes)." % (dsize)

	print "[v] Validate/spellcheck this post."
        print "[x] Alter post via external filter (will modify draft)."
        if self.Params.has_key("unfiltered"):
            print "[X] Revert to draft prior to any applied external filters."

	if edit_only == 0:
	    print "[u] Update (send the current post)."
	else:
	    print "[u] Update (submit the edited post)."
	    print "[w] Wipe out this post (delete it from the server)."

	print "[f] Copy current post to file."
	print "[r] Return to main menu."
	print "[q] Quit."            
#	print "[z] Dump debugging info."
	print


    def common_menu(self, header_text, edit_only = 0):
	"Common menu between editing previous post, and regular posting."

	print
	print header_text
	print

	print "[e] Edit text of current post."

	if edit_only == 0 and self.Cache.Journals != []:
	    print "[j] Change journal to post in:",
	    try:
		print self.Params["usejournal"]
	    except KeyError:
		print "(" + self.Params["user"] + ")"

        self.menu_opt_subject()
        self.menu_opt_tags("tags")

	print "[m] Change mood:",
	if self.Mood == "":
	    print "(none)"
	else:
	    print self.Mood

	if self.Cache.PicKws != []:
	    print "[k] Change picture keyword:",
	    print self.getval("prop_picture_keyword", "(default)")

	print "[a] Change current music:",
        if self.Params.has_key("autodetect") == 1:
            print self.autodetect_music()
        else:
            print self.getval("prop_current_music")

	print "[p] Change security permissions:",
	try:
	    if self.Params["security"] == "usemask":
		if self.Params["allowmask"] == "1":
		    print "friends"
		else:
		    mnum = int(self.Params["allowmask"])
		    olist = []
		    for k in self.sort_friendgroups():
			if (mnum & int(self.Cache.Friends[k])):
			    olist.append(k)
		    print "custom (" + commalist(olist) + ")"
	    else:
		print self.Params["security"]
	except KeyError:
	    print "public"

	print "[o] Change other options:",
	if self.Params.has_key("prop_opt_preformatted"):
	    opt_list = [ "don't auto-format" ]
	else:
	    opt_list = [ "auto-format" ]
	if self.Params.has_key("prop_opt_nocomments"):
	    opt_list.append("no comments")
	else:
	    if self.Params.has_key("prop_opt_noemail"):
		opt_list.append("comments okay (but not emailed)")
	    else:
		opt_list.append("comments okay")
	if self.Params.has_key("prop_opt_backdated"):
	    opt_list.append("backdated")
        if self.Params.has_key("prop_opt_screening"):
            opt_list.append("screen %s" % ( { "A" : "everyone",
                                              "R" : "anonymous",
                                              "F" : "non-friends",
                                              "N" : "none" }[self.Params["prop_opt_screening"]] ) )
	print string.join(opt_list, ", ") 

	print "[t] Change time and date of current post:",
	if self.Params.has_key("year"):
	    print self.format_time()
	else:
	    print "(posting time)"

        self.menu_opt_common(edit_only)
	res = self.get_choice()

	if res in ("R", "r"):
	    return 0
	elif res in ("Q", "q"):
	    self.do_quit()
	elif res in ("Z", "z"):
	    self.dump_debug_info()
	elif res in ("D", "d"):
	    self.display_post()
	elif res in ("V", "v"):
	    self.do_spellcheck()
	elif res in ("F", "f"):
	    self.save_post_file()
	elif res in ("E", "e"):
	    self.edit_post()
	elif res in ("J", "j") and edit_only == 0 and \
	     self.Cache.Journals != []:
	    self.journal_menu(not edit_only)
	elif res in ("M", "m"):
	    self.mood_menu()
	elif res in ("K", "k") and self.Cache.PicKws != []:
	    self.pickw_menu()
	elif res in ("O", "o"):
	    self.option_menu()
	elif res in ("P", "p"):
	    self.security_menu()
	elif res in ("T", "t"):
	    self.select_time()
	elif res in ("A", "a"):
	    m_text = sane_raw_input("Current music: ")
	    m_text = string.strip(m_text)
	    if m_text == "":
		self.del_param("prop_current_music")
		print "Selected: no current music."
	    else:
		self.Params["prop_current_music"] = m_text
		print "Selected current music."
            self.del_param("autodetect")
	    print
	elif res in ("S", "s"):
	    subj_text = sane_raw_input("Subject: ")
	    self.Params["subject"] = subj_text[:255] # truncate to max length
	    print
	    if len(subj_text) > 255:
		print "Subject changed. WARNING: Truncated to 255 characters."
	    else:
		print "Subject changed."
        elif res in ("C", "c"):
            repeat_ok = 1
            while repeat_ok:
                repeat_ok = self.tags_menu()
        elif res in ("X", "x"):
            self.filter_post(res == "X")                
	elif res in ("U", "u"):
	    if edit_only == 0:
		ok = self.go_post()
	    else:
		ok = self.go_edit()
	    if ok == 1:		# successful, don't repeat menu
		return 0
	elif res in ("W", "w") and edit_only == 1:
	    ok = self.go_delete()
	    if ok == 1:
		return 0
	else:
	    print "That is not a valid option."

	return 1


    def post_menu(self):
	"Post menu."

	return self.common_menu("POST MENU", 0)


    # -----
    # Console commands and friend group management.
    # -----

    def admin_menu(self):
        "Menu for console commands and other XML-RPC features."

        print """
ADMINISTRATIVE MANAGEMENT MENU

[f] List, add, remove, or edit friends.
[g] Add, remove, or edit friend groups.
[c] Add or remove community users.
[b] Ban or unban users from your journal or community.
[s] Grant or revoke posting access to a shared journal.
[r] Return to main menu.
[q] Quit.
"""
        res = self.get_choice()

        if res in ("R", "r"):
            return 0
        elif res in ("Q", "q"):
            self.do_quit()
        elif res in ("Z", "z"):
            self.dump_debug_info()
        elif res in ("B", "b"):
            self.ban_menu()
        elif res in ("C", "c"):
            self.community_menu()
        elif res in ("F", "f"):
            self.friends_menu()
        elif res in ("G", "g"):
            self.admin_groups_menu()
        elif res in ("S", "s"):
            self.sharedjour_menu()
        else:
            print "That is not a valid option."

        return 1


    def friends_menu(self):
        "Friends management menu."

        print """
FRIENDS MANAGEMENT MENU

[l] List friends.
[f] Add someone as a friend.
[e] Edit the colors and groups of a friend.
[u] Un-friend someone.
[r] Return to administrative menu.
"""
        res = self.get_choice()

        if res in ("R", "r"):
            return
        elif res in ("L", "l"):
            cmd = [ "friend", "list" ]
            self.cli_consolecmd( [ cmd ] )
        elif res in ("F", "f"):
            self.add_friend()
        elif res in ("U", "u"):
            fname = sane_raw_input("Enter the username to un-friend: ")
            print
            self.cli_delfriend(fname.strip())
        elif res in ("E", "e"):
            self.edit_friend()
        else:
            print "That is not a valid option."


    def admin_groups_menu(self):
        "Friend group management: add, remove, update."

        print """
FRIEND GROUP MANAGEMENT MENU

[l] List friend groups.
[a] Add a new friend group.
[d] Delete an existing friend group.
[e] Edit a friend group.
[r] Return to administrative menu.
"""
        res = self.get_choice()
        print

        if res in ("R", "r"):
            return
        elif res in ("L", "l"):
            self.list_friendgroups()
        elif res in ("A", "a"):
            self.add_friendgroup()
        elif res in ("D", "d"):
            self.del_friendgroup()
        elif res in ("E", "e"):
            self.edit_friendgroup()
        else:
            print "That is not a valid option."
            

    def community_menu(self):
        "Community management: add/remove users."

        print """
COMMUNITY MANAGEMENT MENU

[a] Add users to a community.
[u] Unsubscribe users from a community.
[r] Return to administrative menu.
"""
        res = self.get_choice()

        if res in ("R", "r"):
            return
        elif res in ("A", "a", "U", "u"):
            cname = sane_raw_input("Enter the community name: ")
            print
            cmd = [ "community", cname.strip() ]
            if res in ("A", "a"):
                cmd.append("add")
            else:
                cmd.append("remove")
            unames = sane_raw_input("Enter usernames (separated by spaces): ")
            print
            clist = []
            for u in unames.split(" "):
                c = cmd[:]
                c.append(u)
                clist.append(c)
            self.cli_consolecmd(clist)
        else:
            print "That is not a valid option."


    def ban_menu(self):
        "Ban/unban users from a journal or community."

        print """
BAN MANAGEMENT MENU

[b] Ban users from your journal.
[u] Unban users from your journal.
[e] Exile (ban) users from a community.
[a] Allow (unban) users back into a community.
[r] Return to administrative menu.
"""
        res = self.get_choice()
        
        if res in ("R", "r"):
            return
        elif res in ("B", "b", "U", "u", "E", "e", "A", "a"):
            if res in ("B", "b", "E", "e"):
                cmd = [ "ban_set" ]
            else:
                cmd = [ "ban_unset" ]
            if res in ("E", "e", "A", "a"):
                cname = sane_raw_input("Enter the community name: ")
                if cname == "":
                    print "No community entered."
                    return
                cargs = [ "from", cname.strip() ]
                print
            else:
                cargs = []
            unames = sane_raw_input("Enter usernames (separated by spaces): ")
            if unames == "":
                print
                print "No usernames entered."
                return
            print
            clist = []
            for u in unames.split(" "):
                c = cmd[:]
                c.append(u)
                c += cargs
                clist.append(c)
            self.cli_consolecmd(clist)
        else:
            print "That is not a valid option."


    def sharedjour_menu(self):
        "Grant or revoke posting access to shared journal."

        print """
SHARED JOURNAL MANAGEMENT MENU

[a] Allow users to post in a shared journal.
[d] Disallow users from posting in a shared journal.
[r] Return to administrative menu.
"""
        res = self.get_choice()

        if res in ("R", "r"):
            return
        elif res in ("A", "a", "D", "d"):
            jname = sane_raw_input("Enter the shared journal name: ")
            print
            cmd = [ "shared", jname.strip() ]
            if res in ("A", "a"):
                cmd.append("add")
            else:
                cmd.append("remove")
            unames = sane_raw_input("Enter usernames (separated by spaces): ")
            print
            clist = []
            for u in unames.split(" "):
                c = cmd[:]
                c.append(u)
                clist.append(c)
            self.cli_consolecmd(clist)
        else:
            print "That is not a valid option."
            
    # -----
    # Edit a previous post.
    # -----

    def edit_previous_post(self):
	"Edit previous post."

	ok = self.cli_getevents_one()
	if ok == 0:
	    return 1			# we DO want to repeat on failure

	if self.Params.has_key("allowmask"):
	    if self.GottenFriends == 0:
		self.cli_getfriendgroups() # needed for permissions display 

	repeat_ok = 1
	while repeat_ok:
	    try:
		repeat_ok = self.common_menu("EDIT PREVIOUS JOURNAL ENTRY", 1)
	    except KeyboardInterrupt:
		self.handle_interrupt("edit")

	return 0


    # -----
    # Select old post to edit.
    # -----

    def pick_entry(self, eobj):
	"Given an entry object, choose it."

	self.Entry = eobj


    def pick_from_list(self):
	"Pick something from the list of entries."

	llist = len(self.Entries)
	if llist == 0: 
	    print "No entries available."
	    return
	elif llist == 1:
	    print "One entry returned. Selecting."
	    self.pick_entry(self.Entries[0])
	    return

	print
	print "SELECT FROM LIST"
	print

	i = 1
	for elem in self.Entries:
	    if i < 10:
                print "%d. " % (i),
	    else:
                print "%d." % (i),
	    print elem["time"] + " " + elem["subject"]
	    i = i + 1

	print
	res = sane_raw_input("Enter entry number: ")
	print

	try:
	    n = int(res)
	except ValueError:
	    n = 0
	if n < 1 or n > llist:
	    print "Invalid choice."
	else:
	    print "Selected."
	    self.pick_entry(self.Entries[n - 1])
	

    def pick_lastn(self):
	"Select from last N entries."

	res = sane_raw_input("Enter the number of entries to retrieve (max of 50): ")
	print

	try:
	    n = int(res)
	except ValueError:
	    n = 0
	if n < 1 or n > 50:
	    print "You must pick a number between 1 and 50."
	    return

	self.Params["selecttype"] = "lastn"
	self.Params["howmany"] = str(n)
	ok = self.cli_getevents_list([ "howmany" ])
	if ok == 0:
	    return
	self.pick_from_list()


    def select_date(self, none_ok = 0):
	"Choose a date, with the aid of a calendar."

	# -- Display this month's calendar, as a handy aid.

	calendar.setfirstweekday(calendar.SUNDAY)
	timetuple = time.localtime(time.time())
	print
	calendar.prmonth(timetuple[0], timetuple[1])
	print
	print

	# -- Repeat the menu.

	repeat_ok = 1
	while repeat_ok:
	    print """\
You can enter the date in YYYY-MM-DD format to select a date, or YYYY-MM to
see a calendar of that month, which will show the number of posts per day."""
	    print
	    dstr = sane_raw_input("Enter date: ")
	    print
	    dstr = string.strip(dstr)
	    if dstr == "":
                if none_ok:
                    print "No date entered. Synchronization will be used."
                    return ""
                else:
                    print "Invalid date format."
                    raise ValueError
	    try:
		ttup = time.strptime(dstr, "%Y-%m-%d")
		repeat_ok = 0
	    except ValueError:
		try:
		    ttup = time.strptime(dstr, "%Y-%m")
		except ValueError:
		    print "Invalid date format."
		    raise
		self.show_calendar(ttup[0], ttup[1])
		print
	return ttup


    def pick_date(self):
	"Select from entries on a certain date."

	try:
	    ttup = self.select_date()
	except ValueError:
	    return

	self.Params["year"] = time.strftime("%Y", ttup)
        self.Params["month"] = time.strftime("%m", ttup)
        self.Params["day"] = time.strftime("%d", ttup)
	self.Params["selecttype"] = "day"
	ok = self.cli_getevents_list([ "year", "month", "day" ])
	if ok == 0:
	    return
	self.pick_from_list()


    def pick_most_recent(self):
	"Select the most recent post."

	self.Params["selecttype"] = "one"
	self.Params["itemid"] = "-1"
	ok = self.cli_getevents_list([ "itemid" ])
	if ok == 0:
	    return

	if len(self.Entries) > 1:
	    print "Error: Server returned more than one post."
	    return
	self.pick_entry(self.Entries[0])


    def pick_edit_menu(self):
	"Select old post to edit."

	print
	print "SELECT PREVIOUS POST"
	print

	if self.Cache.Journals != []:
	    print "[j] Change journal to take post from:",
	    try:
		print self.Params["usejournal"]
	    except KeyError:
		print "(" + self.Params["user"] + ")"

	print "[l] Select the last (most recent) post."
	print "[n] Select from the last N number of entries."
	print "[d] Select from entries posted on a certain date."

	if self.Entry != {}:
	    print "[e] Edit post:",
	    print self.Entry["time"],
	    if len(self.Entry["subject"]) > 45:
		print truncstr_more(self.Entry["subject"], 45)
	    else:
		print self.Entry["subject"]

	print "[r] Return to main menu."
	print "[q] Quit."
	print
	res = self.get_choice()

	if res in ("R", "r"):
	    return 0
	elif res in ("Q", "q"):
	    self.do_quit()
	elif res in ("Z", "z"):
	    self.dump_debug_info()
	elif res in ("J", "j") and self.Cache.Journals != []:
	    self.journal_menu()
	elif res in ("L", "l"):
	    self.pick_most_recent()
	elif res in ("N", "n"):
	    self.pick_lastn()
	elif res in ("D", "d"):
	    self.pick_date()
	elif res in ("E", "e") and self.Entry != {}:
	    repeat_ok = self.edit_previous_post()
	    return repeat_ok
	else:
	    print "That is not a valid option."
	return 1


    # -----
    # Mass-archive posts.
    # -----

    def copy_event_metadata(self, n, pcmax):
	"Populate data from one of many events."

	try:
	    self.Params["itemid"] = self.Got["events_%d_itemid" % (n)]
	except KeyError:
	    return 0

	# -- We default time to now on an error, but this can be dangerous
	#    if we're using this retrieval for archive purposes.

	try:
	    timetuple = time.strptime(self.Got["events_%d_eventtime" % (n)],
				      "%Y-%m-%d %H:%M:%S")
	except ValueError:
	    try:
		timetuple = time.strptime(self.Got["events_%d_eventtime" % (n)],
					  "%Y-%m-%d %H:%M")
	    except ValueError:
		timetuple = time.localtime(time.time())

	self.copy_net_data("events_%d_" % (n),
			   [ "poster", "security", "allowmask", "subject" ])

	for x in range(1, pcmax + 1):
	    try:
		if self.Got["prop_%d_itemid" % (x)] == self.Params["itemid"]:
		    self.Params["prop_" + self.Got["prop_%d_name" % (x)]] = \
					self.Got["prop_%d_value" % (x)]
	    except KeyError:
		pass

	self.event_common_data(timetuple)
	return 1
	

    def archive_events(self, journal_name):
	"Archive multiple events retrieved from the network. Return errors."

	try:
	    ecount = int(self.Got["events_count"])
	except KeyError:
	    raise ValueError
	if ecount < 1:
	    raise ValueError

	try:
	    pcstr = self.Got["prop_count"]
	    try:
		pcmax = int(pcstr)
	    except ValueError:
		raise ValueError
	except KeyError:
	    pcmax = 0

	err_n = 0
	for n in range(1, ecount + 1):
	    self.clear_metadata()
	    if journal_name != "":
		self.Params["usejournal"] = journal_name
	    ok = self.copy_event_metadata(n, pcmax)
	    if ok == 0:
		err_n = err_n + 1
	    else:
		self.make_archive(0, urllib.unquote_plus(self.Got["events_%d_event" % (n)]))
	return err_n


    def archive_days(self, s_year, s_mon, s_day, e_day, day_counts):
	"Archive posts in a day range (in a single month)."

	# -- Save what journal we're in, because otherwise it will get
	#    wiped by metadata wipeout.

	try:
	    save_journal = self.Params["usejournal"]
	except KeyError:
	    save_journal = ""

	count = 0
	err_n = 0
	bstr = str(s_year) + ("-%02d-" % s_mon)

	for n in range(s_day, e_day + 1):
	    dstr = "%02d" % n
	    if day_counts.has_key(bstr + dstr):
		try:
		    self.cli_getevents_day( (s_year, s_mon, n, 0, 0, 0, 0, 0, 0) )
		    new_errs = self.archive_events(save_journal)
		    print "  %s%s:" % (bstr, dstr),
		    if new_errs > 0:
			err_n = err_n + new_errs
			print "PARTIAL FAILURE. Errors encountered on %d of %s"% (new_errs, day_counts[bstr + dstr]),
		    else:
			print day_counts[bstr + dstr],
		    if day_counts[bstr + dstr] == "1":
			print "post."
		    else:
			print "posts."
		    count = count + int(day_counts[bstr + dstr]) - new_errs
		except IOError:
		    print "  %s%s: FAILED. Network error." % (bstr, dstr)
		    err_n = err_n + int(day_counts[bstr + dstr])
		except ValueError:
		    print "  %s%s: FAILED. No posts retrieved." % (bstr, dstr)
		    err_n = err_n + int(day_counts[bstr + dstr])
		if save_journal != "":
		    self.Params["usejournal"] = save_journal
	return (count, err_n)


    def mass_archive(self):
	"Given two dates, archive posts between those dates, inclusively."

        # -- If we have neither a start nor end date, this is synchronization.

        if not self.Params.has_key("start_ttup") and not self.Params.has_key("end_ttup"):
            self.mass_synchronize()
            return

	# -- Check values. If we don't have an end date, it defaults to today.

	try:
	    stt = self.Params["start_ttup"]
	except KeyError:
	    print "You must specify a start date for archival."
	    return

	try:
	    ett = self.Params["end_ttup"]
	except KeyError:
	    ett = time.localtime(time.time())

	print "Retrieving post counts..."

	ok = self.cli_getdaycounts()
	if ok == 0:
	    return

	# -- Save this so it doesn't get overwritten by later network ops.

	save_counts = {}
	for k in self.Got.keys():
	    save_counts[k] = self.Got[k]

	# -- Get the start date and end dates right, reversing them if
	#    need be.

	ok = 1
	if stt[0] > ett[0]:
	    ok = 0
	elif stt[0] == ett[0]:
	    if stt[1] > ett[1]:
		ok = 0
	    elif stt[1] == ett[1]:
		if stt[2] > ett[2]:
		    ok = 0
	if ok == 0:
	    mtt = stt
	    stt = ett
	    ett = mtt

	# -- Figure out the number of days in the first month. We iterate
	#    from the start day to the end of the month, then into the
	#    next month, doing as many complete months as need be, up until
	#    the last month, which is a partial month. Change of year also
	#    presents a problem.

	if stt[0] == ett[0] and stt[1] == ett[1]:
	    print
	    print "Archiving..."
	    val = self.archive_days(stt[0], stt[1], stt[2], ett[2], save_counts)
	else:
	    mstr = time.strftime("%B", (stt[0], stt[1], 1, 0, 0, 0, 0, 0, 0))
	    print
	    print "Archiving from %s %d, %d..." % (mstr, stt[2], stt[0])
	    val = self.archive_days(stt[0], stt[1], stt[2],
				    calendar.monthrange(stt[0], stt[1])[1],
				    save_counts)
	count = val[0]
	err_n = val[1]

	# -- If the end date is in the next year or beyond, get the entries
	#    for the remaining months of the start year.

	if ett[0] > stt[0] and stt[1] != 12:
	    for i in range(stt[1] + 1, 13):
		mstr = time.strftime("%B", (stt[0], i, 1, 0, 0, 0, 0, 0, 0))
		print
                print "Archiving %s %d..." % (mstr, stt[0])
		val = self.archive_days(stt[0], i, 1,
					calendar.monthrange(stt[0], i)[1],
					save_counts)
		count = count + val[0]
		err_n = err_n + val[1]

	# -- If the end date is more than a year away, retrieve the full
	#    years in-between.

	if ett[0] > stt[0] + 1:
	    for i in range(stt[0] + 1, ett[0]):
		for j in range(1, 13):
		    mstr = time.strftime("%B", (i, j, 1, 0, 0, 0, 0, 0, 0))
		    print
                    print "Archiving %s %d..." % (mstr, i)
		    val = self.archive_days(i, j, 1,
					    calendar.monthrange(i, j)[1],
					    save_counts)
		    count = count + val[0]
		    err_n = err_n + val[1]

	# -- If the end date is in the same year and month as the start
	#    month, we're good.

	if ett[0] == stt[0] and ett[1] == stt[1]:
	    pass
	else:

	    # -- If the end date is in the same year as the start date,
	    #    retrieve entries from the month after the start month, to
	    #    the month before the end month. Otherwise go from 1 to
	    #    the month before the end month.

	    if ett[0] > stt[0] or ett[1] > stt[1] + 1:
		if ett[0] == stt[0]:
		    s_month = stt[1] + 1
		else:
		    s_month = 1
		for i in range(s_month, ett[1]):
		    mstr = time.strftime("%B",
					 (ett[0], i, 1, 0, 0, 0, 0, 0, 0))
		    print
                    print "Archiving %s %d..." % (mstr, ett[0])
		    val = self.archive_days(ett[0], i, 1,
					    calendar.monthrange(ett[0], i)[1],
					    save_counts)
		    count = count + val[0]
		    err_n = err_n + val[1]

	    # -- Get the end month itself.

	    mstr = time.strftime("%B", (ett[0], ett[1], 1, 0, 0, 0, 0, 0, 0))
	    print
	    print "Archiving up until %s %d, %d..." % (mstr, ett[2], ett[0])
	    val = self.archive_days(ett[0], ett[1], 1, ett[2], save_counts)
	    count = count + val[0]
	    err_n = err_n + val[1]

	print
	if count > 1:
            print "Archived a total of %d posts." % (count),
	else:
	    print "Archived one post.",
	if err_n == 0:
	    print "No errors."
	elif err_n == 1:
	    print "Failed to archive one post."
	else:
            print "Failed to archive %d posts." % (err_n)
	self.reset_metadata()


    def mass_synchronize(self):
        "Mass-download the journal since the last sync."

        # -- Begin by attempting to get a total item count and our first
        #    batch of item IDs. If this fails, we bail out of the entire
        #    enterprise.

        if self.Cache.LastSync != "":
            self.Params["lastsync"] = self.Cache.LastSync
            print "Synchronizing posts since %s..." % (self.Cache.LastSync)
        else:
            print "No previous synchronization. Obtaining data..."

        if self.cli_syncitems() == 0:
            print "Failed to retrieve item count. Please try again later."
            return

        try:
            need_to_get = int(self.Got["sync_total"])
        except:
            print "No valid synchronization item count. Please try again later."
            return

        if need_to_get == 0:
            print "No changes since the last synchronization."
            return

        print "Found %d new and changed items..." % (need_to_get)    

        # -- Since we may not have gotten all the items on this first pass,
        #    we need to loop through until our fetched items equal our
        #    original count of items we needed.

        fetch_list = {}
        most_recent = (0, "")
        seen = 0
        while seen < need_to_get:

            # -- If we fail on a call, use exponential backoff for our
            #    retry, but don't exceed more than about 20 minutes.

            if seen != 0:
                print "  Fetching item list, %d items remaining after %s..." % (need_to_get - len(fetch_list), most_recent[1])
                succ = 0
                backoff = 1
                while succ == 0:
                    self.Params["lastsync"] = most_recent[1]
                    succ = self.cli_syncitems()
                    if succ == 0:
                        if 5 * backoff > 60:
                            print "Pausing %d minutes before trying again..." % (backoff / 12)
                        else:
                            print "Pausing %d seconds before trying again..." % (5 * backoff) 
                        time.sleep(5 * backoff)
                        if backoff < 256:
                            backoff *= 2

            # -- Store items as tuples, (item ID, time, time in secs, action).
                
            count = int(self.Got["sync_count"])
            for i in range(1, count + 1):
                seen += 1
                if self.Got["sync_%d_item" % (i)][:2] == "L-":
                    t = self.Got["sync_%d_time" % (i)]
                    secs = time.mktime(time.strptime(t, "%Y-%m-%d %H:%M:%S"))
                    if secs > most_recent[0]:
                        most_recent = (secs, t)
                    fetch_list[self.Got["sync_%d_item" % (i)][2:]] = (t, secs, self.Got["sync_%d_action" % (i)])

        if fetch_list != {}:
            print "Retrieving %d journal entries..." % (len(fetch_list))
        else:
            print "No journal entries to fetch. Synchronization complete."
            return

        try:
            save_journal = self.Params["usejournal"]
        except KeyError:
            save_journal = ""

        if self.Cache.LastSync != "":
            self.Params["lastsync"] = self.Cache.LastSync
        else:
            self.del_param("lastsync")

        while fetch_list != {}:

            succ = 0
            backoff = 1
            while succ == 0:
                succ = self.cli_getevents_sync()
                if succ == 1:
                    try:
                        ecount = int(self.Got["events_count"])
                    except:
                        print "  FAILED. No posts retrieved."                
                        succ = 0
                if succ == 0:
                    if 5 * backoff > 60:
                        print "  Pausing %d minutes before trying again..." % (backoff / 12)
                    else:
                        print "  Pausing %d seconds before trying again..." % (5 * backoff) 
                    time.sleep(5 * backoff)
                    if backoff < 256:
                        backoff *= 2
                
            new_errs = self.archive_events(save_journal)
            if new_errs > 0:
                print "    PARTIAL FAILURE. Errors encountered on %d of %d %s." % (new_errs, ecount, ("entries", "entry")[ecount == 1])
            else:
                print "    Archived %d %s..." % (ecount, ("entries", "entry")[ecount == 1])

            for i in range(1, ecount + 1):
                try:
                    del fetch_list[self.Got["events_%d_itemid" % (i)]]
                except:
                    print "    DUPLICATION. Previously retrieved item ID %s." % (self.Got["events_%d_itemid" % (i)])

            # -- Figure out what to sync next by finding the oldest item
            #    left in our fetch list.

            if fetch_list != {}:
                least_recent = (2147483647, "")
                for (t, secs, act) in fetch_list.values():
                    if secs < least_recent[0]:
                        least_recent = (secs, t)
                self.Params["lastsync"] = least_recent[1]
            if save_journal != "":
                self.Params["usejournal"] = save_journal

        print "Synchronization complete. Most recent item: %s." % (most_recent[1])
        self.Cache.LastSync = most_recent[1]

        
    def organize_menu(self):
	"Select organization method."

	print """
SELECT ARCHIVE ORGANIZATION

[n] Do not create subdirectories.
[y] Create a subdirectory for each year.
[m] Create a subdirectory for each month."""
	print
	res = self.get_choice()

	if res in ("N", "n"):
	    self.Params["organize"] = "none"
	elif res in ("Y", "y"):
	    self.Params["organize"] = "year"
	elif res in ("M", "m"):
	    self.Params["organize"] = "month"
	else:
	    print "That is not a valid option."


    def pick_archive_menu(self):
	"Select posts to archive."

	print
	print "SELECT POSTS TO ARCHIVE"
	print

	if self.Cache.Journals != []:
	    print "[j] Change journal to take posts from:",
	    try:
		print self.Params["usejournal"]
	    except KeyError:
		print "(" + self.Params["user"] + ")"
                
	print "[s] Select start date of posts to archive:",
	try:
	    print time.strftime("%Y-%m-%d", self.Params["start_ttup"])
	except KeyError:
            if self.Cache.LastSync == "":
                print "(synchronize)"
            else:
                print "(synchronize from %s)" % (self.Cache.LastSync[:-3])

	print "[e] Select end date of posts to archive:",
	try:
	    print time.strftime("%Y-%m-%d", self.Params["end_ttup"])
	except KeyError:
	    print "(today)"

	print "[d] Change archive directory: " + self.Params["archive_dir"]
	print "[o] Change archive organization: " + self.Params["organize"]
	print "[a] Run archive."

	print "[r] Return to main menu."
	print "[q] Quit."
	print
	res = self.get_choice()

	if res in ("R", "r"):
	    return 0
	elif res in ("Q", "q"):
	    self.do_quit()
	elif res in ("A", "a"):
	    self.mass_archive()
	elif res in ("J", "j") and self.Cache.Journals != []:
	    self.journal_menu()
	elif res in ("O", "o"):
	    self.organize_menu()
	elif res in ("S", "s"):
	    try:
                t = self.select_date(1)
                if t != "":             # blank is OK, syncitems
                    self.Params["start_ttup"] = t
                else:
                    self.del_param("start_ttup")
	    except ValueError:
		pass
	elif res in ("E", "e"):
	    try:
		self.Params["end_ttup"] = self.select_date()
	    except ValueError:
		pass
	elif res in ("D", "d"):
	    print
	    res = sane_raw_input("Directory to use as base of archive: ")
	    print
	    adir = os.path.expanduser(res)
	    ok = create_dir(adir, "archive")
	    if ok == 0:
		print "Archive directory unchanged."
	    else:
		self.Params["archive_dir"] = adir
	else:
	    print "That is not a valid option."
	return 1


   # -----
   # Main menu.
   # -----

    def main_menu(self):
	"Main menu."

	print
	print "MAIN MENU"
	print
	if self.LoggedIn == 0:
	    print "[l] Log in as " + self.Params["user"] + "."
	print """\
[p] Post a journal entry.
[t] Read in a template, then post a journal entry.
[r] Resume working on a previous draft.
[e] Edit or delete a posted journal entry.
[a] Archive past journal entries.
[v] View your current journal page.
[f] Administrate friends and communities.
[c] Check if your friends have posted updates.
[i] Information about the Charm client.
[q] Quit."""
	print
	res = self.get_choice()

	if self.LoggedIn == 0 and res in ("L", "l"):
	    print barline
	    print
	    self.cli_login()
	    print
	    print barline
	elif res in ("C", "c"):
	    print
	    self.prepare_checkfriends()
	    self.cli_checkfriends()
	    print
	elif res in ("P", "p"):
	    repeat_ok = 1
	    while repeat_ok:
		try:
		    repeat_ok = self.post_menu()
		except KeyboardInterrupt:
		    self.handle_interrupt("posting")
        elif res in ("T", "t"):
            template = sane_raw_input("Enter the template filename: ")
            print
            if template == "":
                print "You did not enter a filename."
            else:
                ok = self.read_template(template)
                if ok:
                    repeat_ok = 1
                    while repeat_ok:
                        try:
                            repeat_ok = self.post_menu()
                        except KeyboardInterrupt:
                            self.handle_interrupt("posting")
        elif res in ("R", "r"):
	    self.drafts_menu()
	elif res in ("E", "e"):
	    self.save_session()
	    self.clear_metadata()
	    repeat_ok = 1
	    while repeat_ok:
		try:
		    repeat_ok = self.pick_edit_menu()
		except KeyboardInterrupt:
		    self.handle_interrupt("selection")
	elif res in ("A", "a"):
	    self.save_session()
	    self.clear_metadata()
	    old_archive_dir = self.Params["archive_dir"]
	    old_archive_subdirs = self.Params["archive_subdirs"]
	    old_organize = self.Params["organize"]
	    self.Params["archive_subdirs"] = "0"
	    repeat_ok = 1
	    while repeat_ok:
		try:
		    repeat_ok = self.pick_archive_menu()
		except KeyboardInterrupt:
		    self.handle_interrupt("selection")
	    self.Params["archive_dir"] = old_archive_dir
	    self.Params["archive_subdirs"] = old_archive_subdirs
	    self.Params["organize"] = old_organize
        elif res in ("F", "f"):
            repeat_ok = 1
            while repeat_ok:
                try:
                    repeat_ok = self.admin_menu()
                except KeyboardInterrupt:
                    self.handle_interrupt("selection")
	elif res in ("Z", "z"):
	    self.dump_debug_info()
	elif res in ("Q", "q"):
	    self.do_quit()
	elif res in ("I", "i"):
	    client_info()
	elif res in ("V", "v"):
	    try:
		import webbrowser
		webbrowser.open("http://%s/users/%s" % (string.split(self.Params["url"], "/")[2], self.Params["user"]))
	    except ImportError:
		print "Sorry. Your Python installation lacks the required webbrowser module."
	else:
	    print "That is not a valid option."

# ----------------------------------------------------------------------------
# Login utility: Username/password determination.
# ----------------------------------------------------------------------------

    def set_user(self, uname):
        "Set the user, setting the URL associated if need be."

        self.Params["user"] = uname
        try:
            x = self.Sites[uname]
            if len(x) == 1:
                self.Params["url"] = x
            elif len(x) == 2:
                self.Params["url"] = x[0]
                self.Params["appkey"] = x[1]
                self.Params["blogapi"] = "metaweb"
            else:
                self.Params["url"] = x[0]
                self.Params["basefeed"] = x[1]
                self.Params["ssl"] = x[2]
                self.Params["blogapi"] = "atom"
        except:
            pass
    

    def get_pass(self):
        "Get a user's password."

        try:
            import getpass
            ustr = getpass.getpass("LiveJournal Password: ")
        except:
            ustr = sane_raw_input("LiveJournal Password: ")
        print
        ustr = string.strip(ustr)
        if ustr == "":
            print "You need to enter a LiveJournal password."
            return 0
        self.Params["hpassword"] = md5digest(ustr)
        print

        self.Logins[self.Params["user"]] = self.Params["hpassword"]
        return 1
    

    def get_userpass(self, def_user = ""):
	"Figure out what username and password we're using."

	# -- If we got no conf directives at all, prompt the user.

	if self.Logins == {}:
	    print
	    ustr = sane_raw_input("LiveJournal Username: ")
	    print
	    ustr = string.strip(ustr)
	    if ustr == "":
		print "You need to enter a LiveJournal username." 
		return 0
            self.set_user(ustr)
            return self.get_pass()


	# -- If we had a default user specified, use that.
        #    If we don't have a password for it, prompt for it.

	if def_user != "":
            self.set_user(def_user)
            if self.Logins.has_key(def_user):
		self.Params["hpassword"] = self.Logins[def_user]
                return 1
            return self.get_pass()

	# -- If we only have one available option, use it.

	if len(self.Logins) == 1:
            self.set_user(self.Logins.keys()[0])
	    self.Params["hpassword"] = self.Logins[self.Logins.keys()[0]]
	    return 1

	# -- We have no default. Prompt for one.

	ok = self.username_menu()
	if ok == 0:
	    return 0
	return 1

# ----------------------------------------------------------------------------
# Handling checkfriends-only mode.
# ----------------------------------------------------------------------------

    def checkfriends_mode(self, retry_secs):
	"Run a checkfriends, standalone or in loop mode, only."

	# -- If we've been given any groups to check, our task is more
	#    complex; we need to obtain the friend groups first. Note
	#    that we could have gotten the groups from the conf file,
	#    not just on the command line. Command-line choices completely
	#    override configuration defaults.

	self.prepare_checkfriends()

	if retry_secs == 0 and self.CheckDelay == 0:
	    self.cli_checkfriends()
	else:
	    if self.CheckDelay == 0:
		self.CheckDelay = retry_secs
	    self.checkfriends_loop()


# ----------------------------------------------------------------------------
# Handling quick mode.
# ----------------------------------------------------------------------------

    def quick_mode(self, draft_name = "", is_blog = 0, retry_secs = 15):
	"Post the text from stdin."

        if self.Params.has_key("event") and self.Params["event"][:-1] != "":
            # We already have the post text. We're fine.
            pass
	elif draft_name == "":
	    self.read_event(sys.stdin)
	else:
	    ok = self.slurp_draft("Post")
	    if ok == 0:
		return

	if self.Params["event"][:-1] == "":
	    print "Error: Empty message body. No post made."
	    return

	if self.Params.has_key("year") == 0:
	    ttup = time.localtime(time.time())
	    self.populate_time(ttup)
        if is_blog == 1 and self.Blogger.PostTime == "":
            self.Blogger.PostTime = datetime.datetime.utcnow().isoformat()
            
	ok = 0
	while ok == 0:
            if is_blog == 1:
                ok = self.Blogger.blog_postevent()
            else:
                ok = self.cli_postevent()
	    if ok == 0:
                print "Waiting %d seconds to retry..." % (retry_secs)
		time.sleep(retry_secs)

	if self.getval("archive", "0") == "1":
	    if draft_name == "":
		self.make_archive(0, self.Params["event"])
	    else:
		self.make_archive(0)

	print "Posted."
	

# ----------------------------------------------------------------------------
# Post-login command-line options.
# ----------------------------------------------------------------------------

    def set_bool_opt(self, kname, sval):
	"Handle boolean command-line options."

	if sval == "":
	    x = 1
	else:
	    x = parse_bool(string.lower(sval))

	if x == -1:
	    print "Invalid value for command-line option %s: %s" % (kname, sval)
	else:
	    if Bool_Opts[kname] == 1:
		if x == 0:
		    x = 1
		else:
		    x = 0
	    if x == 1:
		self.Params[Bool_Map[kname]] = "1"
	    else:
		try:
		    del self.Params[Bool_Map[kname]]
		except:
		    pass


    def set_cmd_opts(self, opts):
	"Handle second half of command-line options."

	for o, a in opts:
	    if o in ("-d", "--drafts"):
		self.Params["draft_dir"] = os.path.expanduser(a)
	    elif o in ("-a", "--archive"):
		self.Params["archive_dir"] = os.path.expanduser(a)
	    elif o in ("-s", "--subject"):
		self.Params["subject"] = a[:255] # truncate to max length
            elif o in ("-S", "--social"):
                if Social_Bookmarks.has_key(a.lower()):
                    self.Params["social"] = a.lower()
                else:
                    print "Warning: invalid social bookmarks service option."
	    elif o in ("-m", "--mood"):
		self.set_mood(a)
	    elif o in ("-k", "--pic", "--keywords"):
                if self.Params["blogapi"] == "lj":
                    if a != "":
                        self.set_pickw(a)
                else:
                    self.set_keywords(a)
            elif o in ("-t", "--tag", "--cat"):
                self.set_tag(a)
	    elif o in ("-p", "--permit", "--security"):
		try:
		    self.set_security(a)
		except ValueError:
		    pass
	    elif o in ("-j", "--journal"):
		self.Params["usejournal"] = string.lower(a)
	    elif o in ("-M", "--music"):
		self.Params["prop_current_music"] = a
            elif o in ("-A", "--autodetect"):
                self.autodetect_music()
	    elif o in ("--debug", "--autoformat",
                       "--backdate", "--comments", "--noemail"):
		self.set_bool_opt(o[2:], a)

# ----------------------------------------------------------------------------
# Functions common to Atom and MetaWebLog APIs.
# ----------------------------------------------------------------------------

    def sanitize_blog(self):
        "Blogger cannot handle blank subjects or content."

        self.Params["subject"] = self.getval("subject", "(no subject)")
        self.Params["event"] = self.getval("event", "(this space intentionally left blank)")


    def blog_category_menu(self):
        "Select a category."
        
        ok = self.Blogger.get_cats()
        if ok == 0:
            return

        if self.Blogger.Categories == []:
            print "You currently do not have any categories defined."
            return
        
        print "CATEGORY MENU"
        print
        
        i = 1
        for t in self.Blogger.Categories:
            if i < 10:
                print "%d. " % (i),
            else:
                print "%d." % (i),
            print t
            i = i + 1

        print
        res = sane_raw_input("Enter category number: ")
        print

        try:
            n = int(res)
        except ValueError:
            n = 0
        if n < 1 or n > len(self.Blogger.Categories):
            print "Invalid choice."
            return
        else:
            print "Selected."
            self.Params["prop_taglist"] = self.Blogger.Categories[n - 1]


    def blog_get_entry(self, text, ttup):
        "Common entry retrieval."

        self.populate_time(ttup)
        timestr = time.strftime("%Y%m%d_%H%M%S", ttup)
        ok = self.make_draft_file(timestr)
        if ok == 0:
            return 0

        try:
            f = open(self.Params["draft_file"], "w")
            f.write(text)
            f.close()
        except IOError:
            print "Error writing to draft file: %s" % (errmsg())

        self.save_metadata(timestr)
        return 1
        

    def blog_common_menu(self, header_text, edit_only = 0):
        "Common menu between regular posting and previous post editing."

        print
        print header_text
        print

        print "[e] Edit text of current post."

        self.menu_opt_subject()
        self.menu_opt_tags("category")
        self.menu_opt_keywords()
        self.menu_opt_common(edit_only)
        res = self.get_choice()

	if res in ("R", "r"):
	    return 0
	elif res in ("Q", "q"):
	    self.do_quit()
        elif res in ("Z", "z"):
            self.dump_debug_info()            
	elif res in ("D", "d"):
	    self.display_post()
	elif res in ("V", "v"):
	    self.do_spellcheck()
	elif res in ("F", "f"):
	    self.save_post_file()
        elif res in ("E", "e"):
            self.edit_post()
	elif res in ("S", "s"):
	    subj_text = sane_raw_input("Subject: ")
	    self.Params["subject"] = subj_text[:255] # truncate to max length
	    print
	    if len(subj_text) > 255:
		print "Subject changed. WARNING: Truncated to 255 characters."
	    else:
		print "Subject changed."
        elif res in ("C", "c"):
            self.blog_category_menu()
        elif res in ("K", "k"):
            kstr = sane_raw_input("Keyword tags (comma-separated): ")
            self.set_keywords(kstr)
        elif res in ("X", "x"):
            self.filter_post(res == "X")
	elif res in ("U", "u"):
	    if edit_only == 0:
		ok = self.go_post(1)
	    else:
		ok = self.go_edit(1)
	    if ok == 1:		# successful, don't repeat menu
		return 0
	elif res in ("W", "w") and edit_only == 1:
	    ok = self.go_delete(1)
	    if ok == 1:
		return 0
	else:
	    print "That is not a valid option."

	return 1


    def blog_post_menu(self):
        "Atom/Metaweb posting menu."

        return self.blog_common_menu("BLOG POSTING MENU", 0)


    def blog_edit_menu(self):
        "Atom/Metaweb editing menu."

        return self.blog_common_menu("BLOG EDITING MENU", 1)


    def blog_select_menu(self):
        "Select a blog."
        
        self.Blogger.get_blogs()
        nblogs = len(self.Blogger.Blogs)
        
        if nblogs == 0:
            print """
Charm could not retrieve any blogs for you. This may because of an
authentication error, or because you have not yet created a blog
on your blogging service.
"""
            sys.exit(0)
            
        if nblogs == 1:
            k = self.Blogger.Blogs.keys()[0]
            print
            print "Selected your only blog, '%s'." % (k)
            self.Blogger.Current = self.Blogger.Blogs[k]
            return 1

        print
        print "SELECT BLOG"
        print
        i = 1
        klist = self.Blogger.Blogs.keys()
        for k in klist:
            print "%d. %s" % (i, k)
            i = i + 1
        print
        res = sane_raw_input("Enter blog number: ")
        print
        try:
            n = int(res)
        except ValueError:
            n = 0
        if n < 1 or n > len(klist):
            print "Invalid choice. You need to choose a valid blog."
            return 0
        else:
            self.Blogger.Current = self.Blogger.Blogs[klist[n - 1]]
        return 1


    def blog_menu(self):
        "Main Atom/MetaWeb menu."

        print
        print "MAIN BLOGGING MENU"
        print """
[p] Post a blog entry.
[e] Edit or delete a posted blog entry.
[i] Information about the Charm client.
[q] Quit.
"""
        res = self.get_choice()
        if res in ("Q", "q"):
            self.do_quit()
        elif res in ("I", "i"):
            client_info()
        elif res in ("Z", "z"):
            self.dump_debug_info()
        elif res in ("P", "p"):
            repeat_ok = 1
            while repeat_ok:
                try:
                    repeat_ok = self.blog_post_menu()
                except KeyboardInterrupt:
                    self.handle_interrupt("posting")
        elif res in ("E", "e"):
            self.save_session()
            self.clear_metadata()
            repeat_ok = self.Blogger.blog_pick_edit_menu()
            while repeat_ok:
                try:
                    repeat_ok = self.blog_edit_menu()
                except KeyboardInterrupt:
                    self.handle_interrupt("selection")
        else:
            print "That is not a valid option."


    def main_blog(self, opts, resumeold, xpostfile, template, quick_opt):
        "Wrapper startup handler for Charm in Atom and MetaWeb modes."

        # -- More processing of command-line options.
        
        self.save_conf_meta()
        if xpostfile != "":
            if self.read_archive(xpostfile) == 0:
                sys.exit(0)
        elif template != "":
            if self.read_template(template) == 0:
                sys.exit(0)
        elif self.Params.has_key("default_template"):
            if self.read_template(self.Params["default_template"]) == 0:
                sys.exit(0)
        elif resumeold != "":
            self.resume_draft(resumeold, 1)
        self.set_cmd_opts(opts)

        # -- If we have quick mode, do that, otherwise loop.

        if quick_opt == 1:
            self.Blogger.get_blogs()
            nblogs = len(self.Blogger.Blogs)
            if nblogs != 1:
                print "Error, could not automatically select blog since you have more than one."
            else:
                self.Blogger.Current = self.Blogger.Blogs[self.Blogger.Blogs.keys()[0]]
                self.quick_mode(resumeold, 1)
            sys.exit(0)

        print Charm_Header
        print "( Fetching blogs... )"
        self.blog_select_menu()

        while 1:
            try:
                self.blog_menu()
            except KeyboardInterrupt:
                self.handle_interrupt("main")


# ----------------------------------------------------------------------------
# MetaWebLog API handlers.
# ----------------------------------------------------------------------------

    def metaweb_server(self):
        "MetaWebLog API XML-RPC interface server handle."

        try:
            import xmlrpclib
        except ImportError:
            self.Got["success"] = "FAIL"
            self.Got["errmsg"] = "Your Python installation lacks the required xmlrpclib module."
            return            

        server = xmlrpclib.ServerProxy(self.Params["url"])
        return server

    def metaweb_get_post(self, server, postid):
        "Get a post by post ID."

        try:
            self.Got = server.metaWeblog.getPost(postid, self.Params["user"], self.Params["hpassword"])
        except:
            print "Error in retrieving post ID %s (%s)." % (postid, errmsg())
            return 0

        entry = self.Got
        self.Params["subject"] = entry["title"]
        self.Params["prop_taglist"] = string.join(entry["categories"], " ")
        self.Params["prop_keywords"] = entry["mt_keywords"]
        if entry.has_key("mt_text_more") and entry["mt_text_more"] != "":
            text = "%s<!--more-->%s" % (entry["description"], entry["mt_text_more"])
        else:
            text = entry["description"]

        if entry.has_key("mt_excerpt") and entry["mt_excerpt"] != "":
            self.Params["excerpt"] = entry["mt_excerpt"]

        if entry.has_key("date_created_gmt"):
            cdate = entry["date_created_gmt"]
        else:
            cdate = entry["dateCreated"]
        ttup = time.localtime(calendar.timegm(time.strptime(str(cdate), "%Y%m%dT%H:%M:%S")))
        return self.blog_get_entry(text, ttup)


    def metaweb_prep_post(self):
        "Prepare a data structure for MetaWeb content."

        data = { "title" : self.Params["subject"],
                 "description" : self.Params["event"] }
        if self.Params.has_key("prop_taglist"):
            data["categories"] = string.split(self.Params["prop_taglist"], ",")
        if self.Params.has_key("prop_keywords"):
            data["mt_keywords"] = self.Params["prop_keywords"]
        if self.Params.has_key("excerpt"):
            data["mt_excerpt"] = self.Params["excerpt"]
        return data

    def metaweb_postevent(self):
        "Send a post to a Metaweb-based blog."

        self.sanitize_blog()
        data = self.metaweb_prep_post()
        server = self.metaweb_server()
        try:
            self.Got = server.metaWeblog.newPost(self.Blogger.Current["blogid"], self.Params["user"], self.Params["hpassword"], data, 1)
        except:
            print "Error in posting entry (%s)." % (errmsg())
            return 0

        # -- If we want to add a social bookmark, we have to do it by
        #    editing our post, since we needed to post in order to find
        #    out what our permalink URL would be.

        if self.Params.has_key("social"):
            postid = self.Got           # just a text string
            print "Posted. Adding social bookmark..."

            ok = 0
            while not ok:
                try:
                    self.Got = server.metaWeblog.getPost(postid, self.Params["user"], self.Params["hpassword"])
                    try:
                        if self.SocialUsers.has_key(self.Params["social"]):
                            bookmark = Social_Bookmarks[self.Params["social"]] % (self.SocialUsers[self.Params["social"]], self.Got["link"], self.Params["subject"])
                        else:
                            bookmark = Social_Bookmarks[self.Params["social"]] % (self.Got["link"], self.Params["subject"])
                    except:
                        print "Malformed parameters for %s." % (self.Params["social"])
                        return 1                # still OK, but stop
                    self.Params["event"] += "\n" + bookmark
                    ok = 1
                except:
                    print "Error in retrieving new post (%s)." % (errmsg())
                    res = sane_raw_input("Retry (Y/N)? ")
                    print
                    res = string.lower(string.strip(res))
                    if res not in ("y", "yes"):
                        return 1                # still OK, but stop

            ok = 0
            while not ok:
                try:
                    data = self.metaweb_prep_post()
                    self.Got = server.metaWeblog.editPost(postid, self.Params["user"], self.Params["hpassword"], data, 1)
                    ok = 1
                except:
                    print "Error in modifying entry with social bookmark (%s)." % (errmsg())
                    res = sane_raw_input("Retry (Y/N)? ")
                    print
                    res = string.lower(string.strip(res))
                    if res not in ("y", "yes"):
                        return 1                # still OK, but stop

        return 1


    def metaweb_editevent(self):
        "Edit an existing MetaWeb entry."

        self.sanitize_blog()
        data = self.metaweb_prep_post()
        server = self.metaweb_server()
        try:
            self.Got = server.metaWeblog.editPost(self.Blogger.Current["edit"], self.Params["user"], self.Params["hpassword"], data, 1)
        except:
            print "Error in posting edited entry (%s)." % (errmsg())
            return 0
        return 1        


    def metaweb_delevent(self):
        "Delete an existing MetaWeb entry."

        server = self.metaweb_server()
        try:
            self.Got = server.metaWeblog.deletePost(self.Params["appkey"], self.Blogger.Current["edit"], self.Params["user"], self.Params["hpassword"], 1)
        except:
            print "Error in posting edited entry (%s)." % (errmsg())
            return 0
        return 1        
        

    def metaweb_get_blogs(self):
        "Get a list of MetaWeb blogs."

        server = self.metaweb_server()
        try:
            self.Got = server.metaWeblog.getUsersBlogs(self.Params["appkey"], self.Params["user"], self.Params["hpassword"])
        except:
            print "Error in retrieving blogs (%s)." % (errmsg())
            return {}

        blogs = {}
        for bdict in self.Got:
            blogs[bdict["blogName"]] = bdict
        self.Blogger.Blogs = blogs


    def metaweb_get_cats(self):
        "Get a list of MetaWeb categories."

        server = self.metaweb_server()
        try:
            self.Got = server.metaWeblog.getCategories(self.Blogger.Current["blogid"], self.Params["user"], self.Params["hpassword"])
        except:
            print "Error in retrieving categories (%s)." % (errmsg())
            return 0

        tags = []
        for cdict in self.Got:
            tags.append(cdict["categoryName"])
        self.Blogger.Categories = tags
        return 1


    def metaweb_pick_edit_menu(self):
        "Choose number of blog posts to retrieve, get list, pick one."

        res = sane_raw_input("Enter the number of entries to retrieve: ")
        print
        
        try:
            n = int(res)
        except ValueError:
            n = 0
        if n < 1:
            print "You must enter a reasonable number."
            return 0

        server = self.metaweb_server()
        try:
            self.Got = server.metaWeblog.getRecentPosts(self.Blogger.Current["blogid"], self.Params["user"], self.Params["hpassword"], n)
        except:
            print "Error in retrieving posts (%s)." % (errmsg())
            return 0

        print "SELECT RECENT POST TO EDIT"
        print

        i = 1
        for e in self.Got:
            if i < 10:
                print "%d. " % (i),
            else:
                print "%d." % (i),
            if e.has_key("date_created_gmt"):
                cdate = e["date_created_gmt"]
            else:
                # anyone's guess what the time zone is
                cdate = e["dateCreated"]
            print "%s %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(calendar.timegm(time.strptime(str(cdate), "%Y%m%dT%H:%M:%S")))), e["title"])
            if e.has_key("link"):
                print "    %s" % (e["link"])
            i = i + 1

        print
        res = sane_raw_input("Enter entry number: ")
        print

        try:
            n = int(res)
        except ValueError:
            n = 0
        if n < 1 or n > len(self.Got):
            print "Invalid choice."
            return 0

        print "Selected. Retrieving..."
        entry = self.Got[n - 1]
        
        self.Blogger.Current["edit"] = entry["postid"]
        return self.metaweb_get_post(server, entry["postid"])


    def do_metaweb(self, opts, resumeold, xpostfile, template, quick_opt):
        "This is the startup handler for Charm in Metaweb mode."

        self.Blogger = BloggerData()
        self.Blogger.get_blogs = self.metaweb_get_blogs
        self.Blogger.get_cats = self.metaweb_get_cats
        self.Blogger.blog_pick_edit_menu = self.metaweb_pick_edit_menu
        self.Blogger.blog_postevent = self.metaweb_postevent
        self.Blogger.blog_editevent = self.metaweb_editevent
        self.Blogger.blog_delevent = self.metaweb_delevent

        self.main_blog(opts, resumeold, xpostfile, template, quick_opt)
        
# ----------------------------------------------------------------------------
# Atom API handlers.
# ----------------------------------------------------------------------------

    def atom_request(self, method, resource, content = None, raw = 0):
        "Generic request and response."

        headers = { "Content-type" : "application/xml",
                    "Host" : self.Params["url"] }

        if self.Params["ssl"] == 1:
            headers["Authorization"] = "BASIC %s" % (self.Params["hpassword"])
            try:
                conn = httplib.HTTPSConnection(self.Params["url"])
            except:
                try:
                    conn = httplib.HTTPConnection(self.Params["url"])
                except:    
                    print "Failed, connection error (%s). Try again later." % (errmsg())
                    return 0
        else:
            # -- With WSSE, hpassword actually still contains our cleartext
            #    password.

            tstamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            nonce = get_nonce(tstamp)
            pdigest = base64.encodestring(sha.new("%s%s%s" % (nonce, tstamp, self.Params["hpassword"])).digest())[:-1]
            
            headers["Authorization"] = 'WSSE profile="UsernameToken"'
            headers["X-WSSE"] = 'UsernameToken Username="%s", PasswordDigest="%s", Created="%s", Nonce="%s"' % (self.Params["user"], pdigest, tstamp, nonce)
            try:
                conn = httplib.HTTPConnection(self.Params["url"])
            except:
                try:
                    conn = httplib.HTTPSConnection(self.Params["url"])
                except:
                    print "Failed, connection error (%s). Try again later." % (errmsg())
                    return 0

        try:
            conn.request(method, resource, content, headers)
            response = conn.getresponse()
        except:
            print "Failed, server error (%s). Try again later." % (errmsg())
            return 0

        if response.status == 401:
            print "Failed, authorization error. Please check your username and password."
            return 0
        if response.status == 404:
            print "Failed, no such URL. Please check your configuration."
            return 0
        if response.status == 500:
            print "Failed, format error. Please edit and try again."
            return 0
        if response.status == 400:
            print "Failed, bad request. This may be the result of a bug in Charm."
            return 0

        try:
            rtext = response.read()
            if raw == 0:
                self.Blogger.Q = feedparser.parse(rtext)
            else:
                self.Blogger.Q = rtext
        except:
            print "Failed, parse error. Try again later."
            return 0

        return 1


    def atom_postevent(self):
        "Send a post to an Atom-based blog."

        self.sanitize_blog()

        if self.Params.has_key("prop_taglist"):
            tagelem = ' xmlns:dc="http://purl.org/dc/elements/1.1/"'
            tagdata = """
   <dc:subject>%s</dc:subject>""" % (self.Params["prop_taglist"])            
        else:
            tagelem = ""
            tagdata = ""
        
        post = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<entry xmlns="http://purl.org/atom/ns#"%s>
   <title mode="escaped" type="text/plain">%s</title>%s
   <issued>%s</issued>
   <generator url="%s">%s</generator>
   <content type="application/xhtml+xml">
   <div xmlns="http://www.w3.org/1999/xhtml">%s</div>
   </content>
</entry>
""" % (tagelem, utf8(self.Params["subject"]), tagdata, utf8(self.Blogger.PostTime), utf8(Client_URL), utf8(self.Params["clientversion"]), utf8(self.Params["event"]))

        ok = self.atom_request("POST", self.Blogger.Current["post"], post)
        return ok

        
    def atom_editevent(self):
        "Edit an existing Atom post."

        post = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<entry xmlns="http://purl.org/atom/ns#">
  <title mode="escaped" type="text/html">%s</title>
  <issued>%s</issued>
  <generator url="%s">%s</generator>
  <content type="application/xhtml+xml" xml:lang="en-US" xml:space="preserve">
  <div xmlns="http://www.w3.org/1999/xhtml">%s</div>
  </content>
</entry>
""" % (utf8(self.Params["subject"]), utf8(self.Blogger.PostTime), utf8(Client_URL), utf8(self.Params["clientversion"]), utf8(self.Params["event"]))

        ok = self.atom_request("PUT", self.Blogger.Current["edit"], post)
        return ok


    def atom_delevent(self):
        "Delete an existing Atom post."

        ok = self.atom_request("DELETE", self.Blogger.Current["edit"])
        return ok
        
        
    def atom_get_recent(self):
        "Get a list of recent entries."

        print "Retrieving recent posts..."
        print

        ok = self.atom_request("GET", self.Blogger.Current["feed"])
        return ok


    def atom_get_entry(self):
        "Get a single entry via Atom."

        print "Retrieving entry..."
        print

        ok = self.atom_request("GET", self.Blogger.Current["edit"])
        if ok == 0:
            return 0

        entry = self.Blogger.Q.entries[0]
        self.Blogger.PostTime = entry["issued"]
        self.Params["subject"] = entry["title"]
        text = entry["content"][0]["value"]

        # -- Strip DIV pairs from the text.

        while text[:5] == "<div>" and text[-6:] == "</div>":
            text = text[5:-6]
            text = text.strip()

        if entry.has_key("category"):
            self.Params["prop_taglist"] = entry["category"]

        ttup = time.localtime(calendar.timegm(entry["issued_parsed"]))
        return self.blog_get_entry(text, ttup)
        

    def atom_get_cats(self):
        "Get a list of categories."

        if not self.Blogger.Current.has_key("cats"):
            print "Sorry, your blog does not have category support."
            return 0

        if self.atom_request("GET", self.Blogger.Current["cats"], None, 1) == 0:
            return 0

        # -- We end up with the XML data raw because apparently feedparser
        #    cannot get the category info. We end up crudely hacking out
        #    the categories.

        tags = []
        for x in self.Blogger.Q.split("</subject>"):
            try:
                t = x.split(">")[-1]
                if t != "" and t != "\n":
                    tags.append(t)
            except:
                pass
        tags.sort()
        self.Blogger.Categories = tags
        return 1
        

    def atom_get_blogs(self):
        "Get a list of the Atom feeds."

        if self.atom_request("GET", self.Params["basefeed"]) == 0:
            return

        blogs = {}
        for link in self.Blogger.Q.feed["links"]:
            h = link["title"]
            if blogs.has_key(h) == 0:
                blogs[h] = {}
            x = "/%s" % ("/".join(link["href"][8:].split("/")[1:]))
            if link["rel"] == "service.feed":
                blogs[h]["feed"] = x
            elif link["rel"] == "service.post":
                blogs[h]["post"] = x
            elif link["rel"] == "service.upload":
                blogs[h]["upload"] = x
            elif link["rel"] == "service.categories":
                blogs[h]["cats"] = x
            else:
                pass                    # skip ones we don't care about
        self.Blogger.Blogs = blogs


    def atom_pick_edit_menu(self):
        "Get list of recent blog posts and pick one."

        ok = self.atom_get_recent()
        if ok == 0:
            return 0

        ents = []
        for e in self.Blogger.Q.entries:
            for x in e["links"]:
                if x["rel"] == "service.edit":
                    h = "/%s" % ("/".join(x["href"][8:].split("/")[1:]))
            ents.append( (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(calendar.timegm(e.issued_parsed))), e.title, h) )

        print "SELECT RECENT POST TO EDIT"
        print

        i = 1
        for e in ents:
            if i < 10:
                print "%d. " % (i),
            else:
                print "%d." % (i),
            print "%s %s" % (e[0], e[1])
            i = i + 1

        print
        res = sane_raw_input("Enter entry number: ")
        print

        try:
            n = int(res)
        except ValueError:
            n = 0
        if n < 1 or n > len(ents):
            print "Invalid choice."
            return 0
        else:
            print "Selected."
            self.Blogger.Current["edit"] = ents[n - 1][2]

        self.atom_get_entry()    
        return 1    


    def do_atom(self, opts, resumeold, xpostfile, template, quick_opt):
        "This is the startup handler for Charm in Atom API (blogger) mode."

        if atom_ok == 0:
            print """
Your Charm installation does not currently support the Atom API.
To support blogging via the Atom API, Charm requires the feedparser module.
"""
            sys.exit(0)

        self.Blogger = BloggerData()
        self.Blogger.get_blogs = self.atom_get_blogs
        self.Blogger.get_cats = self.atom_get_cats
        self.Blogger.blog_pick_edit_menu = self.atom_pick_edit_menu
        self.Blogger.blog_postevent = self.atom_postevent
        self.Blogger.blog_editevent = self.atom_editevent
        self.Blogger.blog_delevent = self.atom_delevent

        self.main_blog(opts, resumeold, xpostfile, template, quick_opt)

# ----------------------------------------------------------------------------
# Main body of execution.
# ----------------------------------------------------------------------------

def usage():
    print "\nUsage: %s [options]" % (sys.argv[0])
    print """
Options:

  -h, --help                  Print this usage message.
  -o, --options               Print additional posting options.

  -f, --file FILENAME         Use this file as your .charmrc
  -u, --user USERNAME         Use this as your initial username.
  -l, --login                 Log in automatically.
  -n, --nologin               Don't log in automatically.
  -d, --drafts DIR            Save drafts in this directory.
  -a, --archive DIR           Archive old posts in this directory.
  -r, --resume DRAFTFILE      Resume working on a previous draft.
  -T, --template TEMPLATE     Read in a post template.
  -q, --quick                 Quick posting mode.
  -x, --xpost ARCHIVEFILE     Crosspost an existing post, as another user.
  -z, --sync                  Synchronize journal mode.
  -c, --check                 Check for friend updates only.
  -i, --interval MINUTES      Check for friend updates this often.
  -g, --group FRIENDGROUP     Check only this friend group for updates. You
                              can specify this option multiple times.
"""


def postopt_usage():
    print "\nUsage: %s [options]" % (sys.argv[0])
    print """
Options:

  -h, --help               Print main usage message and command-line options.
  -o, --options            Print these additional posting options. They all
                           specify an attribute for your next post.

LiveJournal only:

  -s, --subject "SUBJECT"  Specify subject.
  -j, --journal JOURNAL    Specify journal to post to.
  -p, --permit PERMISSION  Specify security permission: friends, private, etc.
  -m, --mood MOOD          Specify mood.
  -k, --pic KEYWORD        Specify picture keyword.
  -t, --tag TAG            Specify a tag.
  -M, --music "MUSIC"      Specify music.
  -A, --autodetect         Autodetect music using XMMS.
  --autoformat=[on|off]    Format your post yourself? Set this to off.
  --backdate=[on|off]      Backdate your post?
  --comments=[on|off]      Allow others to comment on this post?
  --noemail=[on|off]       Don't want comments emailed to you? Set this to off.

Non-LiveJournal only:

  -s, --subject "SUBJECT"  Specify subject.
  -k, --keywords KEYWORD   Specify tag keywords.
  -t, --tag, --cat TAG     Specify a category "tag".
  -S, --social SERVICE     Autogenerate social bookmark.
"""


def main():

    short_opts = "hoDAf:u:clnqzs:m:k:t:p:M:j:d:a:r:x:i:g:S:T:"
    long_opts = [ "help", "options", "debug", "autodetect",
		  "file=", "user=", "check", "login", "nologin",
		  "quick", "sync", "subject=", "mood=", "pic=",
                  "cat=", "tag=", "keywords=",
                  "music=", "journal=", "permit=", "security=",
		  "drafts=", "archive=", "resume=", "xpost=",
                  "interval=", "group=", "autoformat=", "backdate=",
                  "comments=", "noemail=", "social=", "template=" ]

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, long_opts)
    except getopt.GetoptError:
	usage()
	sys.exit(1)

    user_home_dir = get_home_dir()
    rc_file = user_home_dir + "/" + ".charmrc"

    # -- Process the options we need to know about before a login attempt.

    quick_opt = 0
    sync_opt = 0
    xpostfile = ""
    template = ""
    login_opt = -1
    ckfronly = 0
    ckfrdelay = 0
    resumeold = ""
    def_user = ""
    ckfrgroups = []

    for o, a in opts:
	if o in ("-h", "--help"):
	    usage()
	    sys.exit(0)
	elif o in ("-o", "--options"):
	    postopt_usage()
	    sys.exit(0)
	elif o in ("-f", "--file"):
	    rc_file = os.path.expanduser(a)
	elif o in ("-u", "--user"):
	    def_user = a
	elif o in ("-l", "--login"):
	    login_opt = 1
	elif o in ("-n", "--nologin"):
	    login_opt = 0
	elif o in ("-c", "--check"):
	    ckfronly = 1
	elif o in ("-q", "--quick"):
	    quick_opt = 1
        elif o in ("-z", "--sync"):
            sync_opt = 1
	elif o in ("-i", "--interval"):
	    try:
		ckfrdelay = int(a) * 60
		if ckfrdelay < 60:
		    ckfrdelay = 0
	    except ValueError:
		pass
	elif o in ("-g", "--group"):
	    ckfrgroups.append(string.lower(a))
        elif o in ("-T", "--template"):
            template = a
	elif o in ("-r", "--resume"):
	    resumeold = a
        elif o in ("-x", "--xpost"):
            xpostfile = a

    jobj = Jabber()
    jobj.read_rcfile(rc_file);

    # -- Figure out what login ID we're using.

    if def_user != "":
	ok = jobj.get_userpass(def_user)
    elif jobj.Params.has_key("default_user"):
	ok = jobj.get_userpass(jobj.Params["default_user"])
    else:
	ok = jobj.get_userpass()

    if ok == 0:
	sys.exit(1)

    # -- Metaweb/Atom API stuff sends us down a different road.

    if jobj.Params["blogapi"] == "atom":
        jobj.do_atom(opts, resumeold, xpostfile, template, quick_opt)
        sys.exit(0)

    if jobj.Params["blogapi"] == "metaweb":
        jobj.do_metaweb(opts, resumeold, xpostfile, template, quick_opt)
        sys.exit(0)        

    # -- Load cache if we can, and if we need to.

    if ckfronly == 0 or ckfrgroups != []:
	jobj.Cache.load_cache("%s/.charmcache" % (user_home_dir),
			      jobj.Params["user"])

    # -- Synchronization only. Implies we do nothing else.
    #    We have to read the additional options (since they include things
    #    like the archive directory), first. We also need to save the
    #    cache after so the lastsync gets saved.

    if sync_opt == 1:
        jobj.set_cmd_opts(opts)
        jobj.mass_synchronize()
        jobj.Cache.save_cache(jobj.Params["user"])
        sys.exit(0)

    # -- Quick friends check. Implies we do nothing else.

    if ckfrgroups != []:
	jobj.CheckGroups = ckfrgroups

    if ckfronly == 1:
	jobj.checkfriends_mode(ckfrdelay)
	sys.exit(0)

    # -- Welcome banner and login.
    #    We default to logging in. Command-line options override anything
    #    in the conf file. Otherwise, we check for the nologin conf option;
    #    if that's on, don't log in.

    if login_opt == -1:
	if jobj.getval("nologin", "0") == "1":
	    login_opt = 0
	else:
	    login_opt = 1

    if quick_opt == 0:
	if login_opt == 1:
	    print "( Logging in... )"
	print Charm_Header

    if login_opt == 1:
	jobj.cli_login(quick_opt)
	if quick_opt == 0:
	    print
	    print barline

    # -- We have to handle security after logging in, so we can deal
    #    with friends groups.

    try:
	jobj.set_security(jobj.Params["security"])
    except KeyError:
	pass
    except ValueError:
	print "Warning: invalid value for security option."

    # -- Save off conf options we'll want to preserve across operations.

    jobj.save_conf_meta()

    # -- Process the options we should look at after startup.
    #    This means such options override the rc file.

    #    The most instant thing we can do is to cross-post from an existing
    #    archive file. If that's not it, then we need to look to see if we
    #    got a resume directive, because we need to load that up first,
    #    then allow other options to override it.

    if xpostfile != "":
        if jobj.read_archive(xpostfile) == 0:
            sys.exit(0)
    elif template != "":
        if jobj.read_template(template) == 0:
            sys.exit(0)
    elif jobj.Params.has_key("default_template"):
        if jobj.read_template(jobj.Params["default_template"]) == 0:
            sys.exit(0)            
    elif resumeold != "":
	jobj.resume_draft(resumeold, 1)

    jobj.set_cmd_opts(opts)

    # -- If we're in quick mode, we grab the post from stdin and just
    #    send it to the server.

    if quick_opt == 1:
	jobj.quick_mode(resumeold)
	sys.exit(0)

    # -- Loop main menu infinitely.

    while 1:
	try:
	    jobj.main_menu()
	except KeyboardInterrupt:
	    jobj.handle_interrupt("main")
