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
# $Id: WindowsSyscall.py,v 1.6 2004/08/27 18:23:04 gera Exp $

import inlineegg

class WindowsSyscall(inlineegg.StackBasedSyscall):
    microClass = inlineegg.Microx86
    STDCALL = 0
    CCALL   = 1

    syscalls = {
        # we need 1 to 1 args mapping for the simple translation to work
        # we'll do better translation in the future
        'exit':('kernel32.dll','ExitProcess',STDCALL),
        'open':('msvcrt.dll','_open',CCALL),
        'read':('msvcrt.dll','_read',CCALL),
        'write':('msvcrt.dll','_write',CCALL),
        'close':('msvcrt.dll','_close',CCALL)
    }
    def __init__(self, micro, LoadLibraryA = 0, GetProcAddress = 0):
        inlineegg.StackBasedSyscall.__init__(self, micro)
        self.names={}

    def remember(self, name, addr):
        code, var = self.micro.save(addr)
        self.names[name] = var
        return code

    def copyFrom(self, other):
        self.names = other.names.copy()

    def initResolver(self,egg):

        resolver = egg.Function()

        resolver += (
            "\xfc"+                       # cld    
            "\x31\xc0"+                	# xor    %eax,%eax
            "\x64\x8b\x48\x30"          	# mov    %fs:0x30(%eax),%ecx
            "\x8b\x79\x0c"+             	# mov    0xc(%ecx),%edi
            "\x8d\x7f\x0c"+             	# lea    0xc(%edi),%edi

# <loop0>:
            "\x8b\x7f\x04"+             	# mov    0x4(%edi),%edi
            "\x8b\x77\x30"+             	# mov    0x30(%edi),%esi
            "\x89\xd1"+                	# mov    %edx,%ecx

# <_hash2>:
            "\x29\xc1"+                	# sub    %eax,%ecx
            "\x66\xad"+                	# lods   %ds:(%esi),%ax
            "\x24\xdf"+                	# and    $0xdf,%al
            "\x75\xf8"+                	# jne    <_hash2>
            "\x67\xe3\x02"+             	# jcxz   <l2>
            "\xeb\xe9"+                	# jmp    <loop0>

# <l2>:
            "\xc1\xea\x10"+             	# shr    $0x10,%edx
            "\x8b\x7f\x18"+             	# mov    0x18(%edi),%edi
            "\x8b\x5f\x3c"+             	# mov    0x3c(%edi),%ebx
            "\x8b\x5c\x3b\x78"+         	# mov    0x78(%ebx,%edi,1),%ebx
            "\x01\xfb"+                	# add    %edi,%ebx
            "\x53"+                       # push   %ebx
            "\x8b\x6b\x20"+             	# mov    0x20(%ebx),%ebp
            "\x8b\x5b\x24"+             	# mov    0x24(%ebx),%ebx

# <loop1>:
            "\x8b\x34\x2f"+               # mov    (%edi,%ebp,1),%esi
            "\x01\xfe"+                	# add    %edi,%esi
            "\x89\xd1"+                	# mov    %edx,%ecx

# <_hash1>:
            "\x29\xc1"+                	# sub    %eax,%ecx
            "\xac"+                       # lods   %ds:(%esi),%al
            "\x24\xdf"+                	# and    $0xdf,%al
            "\x75\xf9"+                	# jne    <_hash1>
            "\x67\xe3\x07"+             	# jcxz   <found>
            "\x8d\x6d\x04"+             	# lea    0x4(%ebp),%ebp
            "\x43"+                       # inc    %ebx
            "\x43"+                       # inc    %ebx
            "\xeb\xe8"+                	# jmp    <loop1>

# <found>:
            "\x0f\xb7\x2c\x3b"+         	# movzwl (%ebx,%edi,1),%ebp
            "\x5b"+                       # pop    %ebx
            "\x8b\x5b\x1c"+             	# mov    0x1c(%ebx),%ebx
            "\x01\xfb"+                	# add    %edi,%ebx
            "\x8b\x1c\xab"+             	# mov    (%ebx,%ebp,4),%ebx
            "\x01\xfb")                	# add    %edi,%ebx

            # returns function pointer in ebx and dll pointer in edi

        resolver.end()

        dllName = 'kernel32.dll'
        functionName = 'GetProcAddress'
        egg += self.micro.set('edx', self.__hash(dllName, functionName))
        egg.call(resolver)
        egg += self.remember(dllName, 'edi')
        egg += self.remember('%s.%s' % (dllName,functionName), 'ebx')

        functionName = 'LoadLibraryA'
        egg += self.micro.set('edx', self.__hash(dllName, functionName))
        egg.call(resolver)
        egg += self.remember('%s.%s' % (dllName,functionName), 'ebx')


    def __hash(self, dllName, functionName):
        return (self.__basicHash(functionName) << 16) + self.__basicHash(dllName)
    
    def __basicHash(self, name):
        answer = 0
        for c in name:
            answer += ord(c) & 0xdf
        return answer

    def resolveDll(self, dllName):
        # print "resolving %s" % dllName
        code, addr = self.syscall('kernel32.dll','LoadLibraryA', (dllName,))
        code += self.remember(dllName, addr)
        return code, addr

    def resolveFunction(self, dllName, functionName):
        # print "resolving %s.%s" % (dllName, functionName)
        if not self.names.has_key(dllName):
            code, addr = self.resolveDll(dllName)
        else:
            code, addr = ('', self.names[dllName])

        more_code, addr = self.syscall('kernel32.dll','GetProcAddress',(addr, functionName,))
        code += more_code
        code += self.remember("%s.%s" % (dllName, functionName), addr)
        return code, addr
        
    def resolve(self, dllName, functionName):
        if not self.names.has_key(dllName):
            code, addr = self.resolveDLL(dllName)
        
    def syscall(self, dllName, functionName, args, callingConvention = STDCALL):
        # print "calling %s.%s" % (dllName, functionName)
        if not self.names.has_key("%s.%s" % (dllName, functionName)):
            code, addr = self.resolveFunction(dllName, functionName)
        else:
            code, addr = ('', self.names["%s.%s" % (dllName, functionName)])

        code += self.setArgs(args,notForTemps = (addr,))
        code += self.micro.call(addr)
        if callingConvention == self.STDCALL:
            self.micro.unpush(len(args))

        return code, self.answer()

    def call(self, function, args):
        dll, function, callingConvention = self.syscalls[function]
        return self.syscall(dll,function,args, callingConvention)
