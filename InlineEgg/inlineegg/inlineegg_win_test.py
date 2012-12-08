#!/usr/bin/python 
#--
# Copyright (c) 2002,2003 Core Security Technologies, Core SDI Inc.
# All rights reserved.
#
#    Unless you have express writen permission from the Copyright Holder, any
# use of or distribution of this software or portions of it, including, but not
# limited to, reimplementations, modifications and derived work of it, in
# either source code or any other form, as well as any other software using or
# referencing it in any way, may NOT be sold for commercial gain, must be
# covered by this very same license, and must retain this copyright notice and
# this license.
#    Neither the name of the Copyright Holder nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.
#
# THERE IS NO WARRANTY FOR THE SOFTWARE, TO THE EXTENT PERMITTED BY APPLICABLE
# LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR
# OTHER PARTIES PROVIDE THE SOFTWARE "AS IS" WITHOUT WARRANTY OF ANY KIND,
# EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
# ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE SOFTWARE IS WITH YOU.
# SHOULD THE SOFTWARE PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY
# SERVICING, REPAIR OR CORRECTION.
#
# IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL
# ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
# THE SOFTWARE AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
# GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE
# OR INABILITY TO USE THE SOFTWARE (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR
# DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR
# A FAILURE OF THE SOFTWARE TO OPERATE WITH ANY OTHER SOFTWARE), EVEN IF SUCH
# HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.
#
# gera [at corest.com]
#--
# $Id: inlineegg_win_test.py,v 1.5 2004/10/27 14:12:37 gera Exp $

from WindowsSyscall import *
from inlineegg import *
import sys

class Syscall_test:
    def __init__(self, osClass, filename):
        egg = InlineEgg(osClass)
        # egg += egg.syscall.remember('kernel32.dll.LoadLibrary',0x77e8a254))    # hardcoded for my 2k
        # egg += egg.syscall.remember('kernel32.dll.GetProcAddress',0x77e89ac1)) # hardcoded for my 2k
        # egg += egg.syscall.remember('kernel32.dll.LoadLibrary',0x80486f0))    # hardcoded for my wine
        # egg += egg.syscall.remember('kernel32.dll.GetProcAddress',0x8048750)) # hardcoded for my wine
        egg.syscall.initResolver(egg)
        self.buildEgg(egg)
        egg.dumpExe(filename+'.exe')
        egg.dumpBin(filename+'.bin')

    def buildEgg(self, egg):
        pass

class resolve_dll_test(Syscall_test):
    def buildEgg(self, egg):
        egg += egg.syscall.resolveDll('ntdll.dll')[0]

class resolve_function_test(Syscall_test):
    def buildEgg(self, egg):
        egg += egg.syscall.resolveFunction('ntdll.dll', 'NtWriteFile')[0]

class resolve_dll_function_test(Syscall_test):
    def buildEgg(self, egg):
        egg += egg.syscall.resolveDll('ntdll.dll')[0]
        egg += egg.syscall.resolveFunction('ntdll.dll', 'NtWriteFile')[0]

class winexec_test(Syscall_test):
    def buildEgg(self, egg):
        egg += egg.syscall.syscall('kernel32.dll','WinExec',('notepad.exe',5))[0]
        egg += egg.syscall.syscall('kernel32.dll','WinExec',('progman.exe',5))[0]
        egg += egg.syscall.syscall('kernel32.dll','ExitProcess',(0,))[0]

class winsock_test(Syscall_test):
    def buildEgg(self, egg):
        wsa = egg.save(1000)
        egg += egg.syscall.syscall('ws2_32.dll','WSAStartup',(0x10001,wsa.addr()))[0]
        egg += egg.syscall.syscall('ws2_32.dll','socket',(2,1,0))[0]
        s = egg.save('eax')

class exit_test(Syscall_test):
    def buildEgg(self, egg):
        egg.exit(0)

class stdin_test(Syscall_test):
    def buildEgg(self, egg):
        egg.write(1,"Hola como estas?\n",17)
        egg.exit(1)

class cat_x_test(Syscall_test):
    # this test will cat x
    def buildEgg(self, egg):
        buf = egg.alloc(1000)
        fd = egg.open('x')
        fd = egg.save(fd)
        egg.read(fd,buf.addr(),1000)
        egg.micro.set('ecx',0)                # hack, _read() changes ecx
        egg.write(1,buf.addr(),1000)
        egg.exit(1)

tests = {
   "resolveDll":resolve_dll_test,
   "resolveFunction":resolve_function_test,
   "resolveDllAndFunction":resolve_dll_function_test,
   "winexec":winexec_test,
   "file":cat_x_test,
   "exit":exit_test,
   "stdin":stdin_test,
   "winsock":winsock_test,
   }

all_plats = {
   'win':WindowsSyscall}

to_do = []
plats = []

if len(sys.argv) > 1:
   for test in sys.argv[1:]:
      if test == '-a':
         to_do = tests.values()
         plats = all_plats.values()
         break
      if test[0] == '-':
         plat = test[1:]
         plats.append(all_plats[plat])
      else:
         to_do.append(tests[test])
else:
   print "Use: %s [-a]" % sys.argv[0],
   for i in all_plats.keys():
      print "[-%s]" % i,
   for i in tests.keys():
      print "[%s]" % i,
   print
   sys.exit(1)

if not plats: plats = all_plats.values()
if not to_do: to_do = tests.values()

print "Tests to do: %s" % map(lambda x:x.__name__,to_do)
print "Platforms to test: %s" % map(lambda x:x.__name__,plats)

for plat in plats:
   for test in to_do:
      print "Platform: %s Test: %s" % (plat.__name__,test.__name__)
      test(plat, "%s_%s" % (plat.__name__,test.__name__))
