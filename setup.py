from distutils.core import setup

setup(name = "charm",
      version = "1.9.1",
      description = "Text-based console client for LiveJournal",
      author = "Lydia Leong",
      author_email = "evilhat@livejournal.com",
      url = "http://ljcharm.sourceforge.net/",
      py_modules = ["ljcharm"],
      scripts = ["charm"],
      data_files = [ ("share/doc/charm", ["charm.html", "sample.charmrc"]),
                     ("share/man/man1", ["charm.1"]),
                     ("share/man/man5", ["charmrc.5"]) ] )
