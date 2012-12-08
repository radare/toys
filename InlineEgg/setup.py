#!/usr/bin/python
# $Id: setup.py,v 1.6 2004/11/09 20:13:29 gera Exp $

import glob
import os

from distutils.core import setup

setup(name = "InlineEgg",
      version = "1.08",
      description = "Collection of classes for creating small assembly programs. These are specially tailored for eggs/shellcode creation.",
      url = "http://oss.coresecurity.com/projects/inlineegg.html",
      author = "Gerardo Richarte",
      author_email = "gera@coresecurity.com",
      packages = ['inlineegg'],
      )

