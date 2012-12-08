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
# $Id: inlineegg.py,v 1.10 2004/11/17 13:57:26 gera Exp $

import struct
import types

class Variable:
    def __init__(self, offset, size = 4):
        self.offset = offset
        self.size   = size

    def value(self,delta = 0):
        return 'var%d' % (self.offset+delta)

    def addr(self,delta = 0):
        return 'ptr%d' % (self.offset+delta)

    def __add__(self,delta):
        return self.__class__(self.offset-delta,self.size and self.size-delta)

    def __sub__(self,delta):
        return self + -delta

    def startswith(self,string):
        return string == 'var'

    def __len__(self):
        return self.size

class Microprocessor:
    pass

class Microx86(Microprocessor):
    # zero causes:
    #   push    0, push 0x00001234, push 0x00123456, push 0x12000034
    #   mov     dx, 0x400
    #   sub     esp, 0x400
    #   mov     esi, [esp+0x41c]
    #   mov     ebx, [esp]
    #   cmp     eax,0
    def __init__(self):
        self._registers = ['eax','ecx','edx','ebx','esp','ebp','esi','edi']
        self.opcodes = {
            '': {
            # stack
                'pushb':'\x6a%c',
                'pushl':'\x68%s',
                'pushVarb':'\xff\x74\x24%c',
                'pushVarl':'\xff\xb4\x24%s',
                'pushVarPtrb':'\x54\x83\x2c\x24%c',    # push esp; sub $ptr, (%esp)
                'pushVarPtrl':'\x54\x81\x2c\x24%s',    # push esp; sub $ptr, (%esp)
                'cmpbVarb':'\x83\x7c\x24%c%c',         # off, val : cmpl $val, off(%esp) 
                'cmpbVarl':'\x83\xbc\x24%s%c',         # off, val : cmpl $val, off(%esp) 
                'cmplVarb':'\x81\x7c\x24%c%s',         # off, val : cmpl $val, off(%esp) 
                'cmplVarl':'\x81\xbc\x24%s%s',         # off, val : cmpl $val, off(%esp) 
                'callVarb':'\xff\x54\x24%c',
                'callVarl':'\xff\x94\x24%s',
                'incVarb':'\xff\x44\x24%c',
                'incVarl':'\xff\x84\x24%s',
                'decVarb':'\xff\x4c\x24%c',
                'decVarl':'\xff\x8c\x24%s',


            # jumps
                'jmpb':'\xeb%(b)s',
                'jmpl':'\xe9%(l)s',
                'jmpb=':'\x74%(b)s',
                'jmpb!=':'\x75%(b)s',
                '!=':'!=',                             # the oposite condition is used on ifs
                '!!=':'=',
                'jmpb<':'\x72%(b)s',
                'jmpb>=':'\x73%(b)s',
                '!<':'>=',
                '!>=':'<',
            },
            'eax': {
                'value':None,
                'movb':'\xb0%(b)s',
                'movw':'\x66\xb8%(w)s',
                'movl':'\xb8%(l)s',
                'cmpb':'\x83\xf8%(b)s',
                'cmpl':'\x3d%(l)s',
                'zero':'\x31\xc0',
                'moveax':'',
                'movebx':'\x89\xd8',
                'movecx':'\x89\xc8',
                'movedx':'\x89\xd0',
                'movesi':'\x89\xf0',
                'movedi':'\x89\xf8',
                'movebp':'\x89\xe8',
                'movesp':'\x89\xe0',
                'cmpeax':'\x39\xc0',
                'cmpebx':'\x39\xc3',
                'cmpecx':'\x39\xc1',
                'cmpedx':'\x39\xc2',
                'cmpesi':'\x39\xc6',
                'cmpedi':'\x39\xc7',
                'cmpebp':'\x39\xc5',
                'cmpesp':'\x39\xc4',
                'movVarb':'\x8b\x44\x24%(b)s',
                'movVarl':'\x8b\x84\x24%(l)s',
                'movVarPtrb':'\x8d\x44\x24%(b)s',
                'movVarPtrl':'\x8d\x84\x24%(l)s',
                'subb':'\x83\xe8%(b)c',
                'subl':'-%(l)s',
                'subVarb':'\x2b\x44\x24%(b)s',
                'subVarl':'\x2b\x84\x24%(l)s',
                'addb':'\x83\xc0%(b)c',
                'addl':'\x05%(l)s',
                'addVarb':'\x03\x44\x24%(b)s',
                'addVarl':'\x03\x84\x24%(l)s',
            },
            'ebx': {
                'value':None,
                'movb':'\xb3%(b)s',
                'movw':'\x66\xbb%(w)s',
                'movl':'\xbb%(l)s',
                'cmpb':'\x83\xfb%(b)s',
                'cmpl':'\x81\xfb%(l)s',
                'zero':'\x31\xdb',
                'moveax':'\x89\xc3',
                'movebx':'',
                'movecx':'\x89\xcb',
                'movedx':'\x89\xd3',
                'movesi':'\x89\xf3',
                'movedi':'\x89\xfb',
                'movebp':'\x89\xeb',
                'movesp':'\x89\xe3',
                'cmpeax':'\x39\xd8',
                'cmpebx':'\x39\xdb',
                'cmpecx':'\x39\xd9',
                'cmpedx':'\x39\xda',
                'cmpesi':'\x39\xde',
                'cmpedi':'\x39\xdf',
                'cmpebp':'\x39\xdd',
                'cmpesp':'\x39\xdc',
                'movVarb':'\x8b\x5c\x24%(b)s',
                'movVarl':'\x8b\x9c\x24%(l)s',
                'movVarPtrb':'\x8d\x5c\x24%(b)s',
                'movVarPtrl':'\x8d\x9c\x24%(l)s',
                'subb':'\x83\xeb%(b)c',
                'subl':'\x81\xeb%(l)s',
                'subVarb':'\x2b\x5c\x24%(b)s',
                'subVarl':'\x2b\x9c\x24%(l)s',
                'addb':'\x83\xc3%(b)c',
                'addl':'\x81\xc3%(l)s',
                'addVarb':'\x03\x5c\x24%(b)s',
                'addVarl':'\x03\x9c\x24%(l)s',
            },
            'ecx': {
                'value':None,
                'movb':'\xb1%(b)s',
                'movw':'\x66\xb9%(w)s',
                'movl':'\xb9%(l)s',
                'cmpb':'\x83\xf9%(b)s',
                'cmpl':'\x81\xf9%(l)s',
                'zero':'\x31\xc9',
                'moveax':'\x89\xc1',
                'movebx':'\x89\xd9',
                'movecx':'',
                'movedx':'\x89\xd1',
                'movesi':'\x89\xf1',
                'movedi':'\x89\xf9',
                'movebp':'\x89\xe9',
                'movesp':'\x89\xe1',
                'cmpeax':'\x39\xc8',
                'cmpebx':'\x39\xcb',
                'cmpecx':'\x39\xc9',
                'cmpedx':'\x39\xca',
                'cmpesi':'\x39\xce',
                'cmpedi':'\x39\xcf',
                'cmpebp':'\x39\xcd',
                'cmpesp':'\x39\xcc',
                'movVarb':'\x8b\x4c\x24%(b)s',
                'movVarl':'\x8b\x8c\x24%(l)s',
                'movVarPtrb':'\x8d\x4c\x24%(b)s',
                'movVarPtrl':'\x8d\x8c\x24%(l)s',
                'subb':'\x83\xe9%(b)c',
                'subl':'\x81\xe9%(l)s',
                'subVarb':'\x2b\x4c\x24%(b)s',
                'subVarl':'\x2b\x8c\x24%(l)s',
                'addb':'\x83\xc1%(b)c',
                'addl':'\x81\xc1%(l)s',
                'addVarb':'\x03\x4c\x24%(b)s',
                'addVarl':'\x03\x8c\x24%(l)s',
            },
            'edx': {
                'value':None,
                'movb':'\xb2%(b)s',
                'movw':'\x66\xba%(w)s',
                'movl':'\xba%(l)s',
                'cmpb':'\x83\xfa%(b)s',
                'cmpl':'\x81\xfa%(l)s',
                'zero':'\x31\xd2',
                'moveax':'\x89\xc2',
                'movebx':'\x89\xda',
                'movecx':'\x89\xca',
                'movedx':'',
                'movesi':'\x89\xf2',
                'movedi':'\x89\xfa',
                'movebp':'\x89\xea',
                'movesp':'\x89\xe2',
                'cmpeax':'\x39\xd0',
                'cmpebx':'\x39\xd3',
                'cmpecx':'\x39\xd1',
                'cmpedx':'\x39\xd2',
                'cmpesi':'\x39\xd6',
                'cmpedi':'\x39\xd7',
                'cmpebp':'\x39\xd5',
                'cmpesp':'\x39\xd4',
                'movVarb':'\x8b\x54\x24%(b)s',
                'movVarl':'\x8b\x94\x24%(l)s',
                'movVarPtrb':'\x8d\x54\x24%(b)s',
                'movVarPtrl':'\x8d\x94\x24%(l)s',
                'subb':'\x83\xea%(b)c',
                'subl':'\x81\xea%(l)s',
                'subVarb':'\x2b\x54\x24%(b)s',
                'subVarl':'\x2b\x94\x24%(l)s',
                'addb':'\x83\xc2%(b)c',
                'addl':'\x81\xc2%(l)s',
                'addVarb':'\x03\x54\x24%(b)s',
                'addVarl':'\x03\x94\x24%(l)s',
            },
            'esi': {
                'value':None,
                'movb':None,
                'movw':'\x66\xbe%(w)s',
                'movl':'\xbe%(l)s',
                'cmpb':'\x83\xfe%(b)s',
                'cmpl':'\x81\xfe%(l)s',
                'zero':'\x31\xf6',
                'moveax':'\x89\xc6',
                'movebx':'\x89\xde',
                'movecx':'\x89\xce',
                'movedx':'\x89\xd6',
                'movesi':'',
                'movedi':'\x89\xfe',
                'movebp':'\x89\xee',
                'movesp':'\x89\xe6',
                'cmpeax':'\x39\xf0',
                'cmpebx':'\x39\xf3',
                'cmpecx':'\x39\xf1',
                'cmpedx':'\x39\xf2',
                'cmpesi':'\x39\xf6',
                'cmpedi':'\x39\xf7',
                'cmpebp':'\x39\xf5',
                'cmpesp':'\x39\xf4',
                'movVarb':'\x8b\x74\x24%(b)s',
                'movVarl':'\x8b\xb4\x24%(l)s',
                'movVarPtrb':'\x8d\x74\x24%(b)s',
                'movVarPtrl':'\x8d\xb4\x24%(l)s',
                'subb':'\x83\xee%(b)c',
                'subl':'\x81\xee%(l)s',
                'subVarb':'\x2b\x74\x24%(b)s',
                'subVarl':'\x2b\xb4\x24%(l)s',
                'addb':'\x83\xc6%(b)c',
                'addl':'\x81\xc6%(l)s',
                'addVarb':'\x03\x74\x24%(b)s',
                'addVarl':'\x03\xb4\x24%(l)s',
            },
            'edi': {
                'value':None,
                'movb':None,
                'movw':'\x66\xbf%(w)s',
                'movl':'\xbf%(l)s',
                'cmpb':'\x83\xff%(b)s',
                'cmpl':'\x81\xff%(l)s',
                'zero':'\x31\xff',
                'moveax':'\x89\xc7',
                'movebx':'\x89\xdf',
                'movecx':'\x89\xcf',
                'movedx':'\x89\xd7',
                'movesi':'\x89\xf7',
                'movedi':'',
                'movebp':'\x89\xef',
                'movesp':'\x89\xe7',
                'cmpeax':'\x39\xf8',
                'cmpebx':'\x39\xfb',
                'cmpecx':'\x39\xf9',
                'cmpedx':'\x39\xfa',
                'cmpesi':'\x39\xfe',
                'cmpedi':'\x39\xff',
                'cmpebp':'\x39\xfd',
                'cmpesp':'\x39\xfc',
                'movVarb':'\x8b\x7c\x24%(b)s',
                'movVarl':'\x8b\xbc\x24%(l)s',
                'movVarPtrb':'\x8d\x7c\x24%(b)s',
                'movVarPtrl':'\x8d\xbc\x24%(l)s',
                'subb':'\x83\xef%(b)c',
                'subl':'\x81\xef%(l)s',
                'subVarb':'\x2b\x7c\x24%(b)s',
                'subVarl':'\x2b\xbc\x24%(l)s',
                'addb':'\x83\xc7%(b)c',
                'addl':'\x81\xc7%(l)s',
                'addVarb':'\x03\x7c\x24%(b)s',
                'addVarl':'\x03\xbc\x24%(l)s',
            },
            'ebp': {
                'value':None,
                'movb':None,
                'movw':'\x66\xbd%(w)s',
                'movl':'\xbd%(l)s',
                'cmpb':'\x83\xfd%(b)s',
                'cmpl':'\x81\xfd%(l)s',
                'zero':'\x31\xed',
                'moveax':'\x89\xc5',
                'movebx':'\x89\xdd',
                'movecx':'\x89\xcd',
                'movedx':'\x89\xd5',
                'movesi':'\x89\xf5',
                'movedi':'\x89\xfd',
                'movebp':'',
                'movesp':'\x89\xe5',
                'cmpeax':'\x39\xe8',
                'cmpebx':'\x39\xeb',
                'cmpecx':'\x39\xe9',
                'cmpedx':'\x39\xea',
                'cmpesi':'\x39\xee',
                'cmpedi':'\x39\xef',
                'cmpebp':'\x39\xed',
                'cmpesp':'\x39\xec',
                'movVarb':'\x8b\x6c\x24%(b)s',
                'movVarl':'\x8b\xac\x24%(l)s',
                'movVarPtrb':'\x8d\x6c\x24%(b)s',
                'movVarPtrl':'\x8d\xac\x24%(l)s',
                'subb':'\x83\xed%(b)c',
                'subl':'\x81\xed%(l)s',
                'subVarb':'\x2b\x6c\x24%(b)s',
                'subVarl':'\x2b\xac\x24%(l)s',
                'addb':'\x83\xc5%(b)c',
                'addl':'\x81\xc5%(l)s',
                'addVarb':'\x03\x6c\x24%(b)s',
                'addVarl':'\x03\xac\x24%(l)s',
            },
            'esp': {
                'value':None,
                'movb':None,
                'movw':'\x66\xbc%(w)s',
                'movl':'\xbc%(l)s',
                'cmpb':'\x83\xfc%(b)s',
                'cmpl':'\x81\xfc%(l)s',
                'zero':'\x31\xe4',
                'moveax':'\x89\xc4',
                'movebx':'\x89\xdc',
                'movecx':'\x89\xcc',
                'movedx':'\x89\xd4',
                'movesi':'\x89\xf4',
                'movedi':'\x89\xfc',
                'movebp':'\x89\xec',
                'movesp':'',
                'cmpeax':'\x39\xe0',
                'cmpebx':'\x39\xe3',
                'cmpecx':'\x39\xe1',
                'cmpedx':'\x39\xe2',
                'cmpesi':'\x39\xe6',
                'cmpedi':'\x39\xe7',
                'cmpebp':'\x39\xe5',
                'cmpesp':'\x39\xe4',
                'movVarb':'\x8b\x64\x24%(b)s',
                'movVarl':'\x8b\xa4\x24%(l)s',
                'movVarPtrb':'\x8d\x64\x24%(b)s',
                'movVarPtrl':'\x8d\xa4\x24%(l)s',
                'subb':'\x83\xec%(b)c',
                'subl':'\x81\xec%(l)s',
                'subVarb':'\x2b\x64\x24%(b)s',
                'subVarl':'\x2b\xa4\x24%(l)s',
                'addb':'\x83\xc4%(b)c',
                'addl':'\x81\xc4%(l)s',
                'addVarb':'\x03\x64\x24%(b)s',
                'addVarl':'\x03\xa4\x24%(l)s',
            },
        }

        self.reset()
        self.stack = []

    def is_value(self, value):
        return type(value) == types.IntType
    
    def is_register(self, value):
        return value in self.registers()

    def is_variable(self, value):
        return value.startswith('var')

    def is_varpointer(self, value):
        return value.startswith('ptr')

    def is_tuple(self, value):
        return type(value) is types.TupleType or type(value) is types.ListType

    def reset(self):
        for i in self.opcodes.values():
            i['value'] = None

    def nop(self):
        return '\x90'

    def zero(self,reg):
        self.setValue(reg,0)
        return self.opcodes[reg]['zero']

    def incReg(self,reg):
        oldVal = self.getValue(reg)
        if self.is_value(oldVal):
            self.setValue(reg,oldVal+1)

        return '%c' % (0x40+self.regNum(reg))

    def incVar(self,var):
        offset = len(self.stack)*4 - var.offset

        if -128 <= offset <= 127:
            return self.opcodes['']['incVarb'] % (offset & 0xff)
        return self.opcodes['']['incVarl'] % struct.pack('<l',offset)

    def inc(self, operator):
        if self.is_register(operator):
            return self.incReg(operator)
        if self.is_variable(operator):
            return self.incVar(operator)
        raise Exception, ('incrementing (%s) not yet implemented' % operator)

    def subValue(self, reg, value):
        b = value & 0xff
        l = struct.pack('<l',value)

        if -128 <= value <= 127:
            return self.opcodes[reg]['subb'] % vars()
        else:
            return self.opcodes[reg]['subl'] % vars()

    def addValue(self, reg, value):
        b = value & 0xff
        l = struct.pack('<l',value)

        if -128 <= value <= 127:
            return self.opcodes[reg]['addb'] % vars()
        else:
            return self.opcodes[reg]['addl'] % vars()

    def decReg(self,reg):
        oldVal = self.getValue(reg)
        if self.is_value(oldVal):
            self.setValue(reg,oldVal-1)

        return '%c' % (0x48+self.regNum(reg))

    def decVar(self,var):
        offset = len(self.stack)*4 - var.offset

        if -128 <= offset <= 127:
            return self.opcodes['']['decVarb'] % (offset & 0xff)
        return self.opcodes['']['decVarl'] % struct.pack('<l',offset)

    def dec(self, operator):
        if self.is_register(operator):
            return self.decReg(operator)
        if self.is_variable(operator):
            return self.decVar(operator)
        raise Exception, ('decrementing (%s) not yet implemented' % operator)

    def getValue(self,reg):
        return self.opcodes[reg]['value']

    def setValue(self,reg,value):
        self.opcodes[reg]['value'] = value
        
    def findMatch(self,value):
        # find exact match
        for i in self.registers():
            if self.getValue(i) == value:
                return i
        return None
        
    def popReg(self, reg):
        return '%c' % (0x58+self.regNum(reg))

    def pop(self, operator):
        self.unpush(1)
        if self.is_register(operator):
            return self.popReg(operator)
        raise Exception, ('popping non registers (%s) not yet implemented' % value)

    def pushReg(self, reg):
        return '%c' % (0x50+self.regNum(reg))

    def pushVariable(self, var):
        offset = len(self.stack)*4 - var.offset - 4

        if -128 <= offset <= 127:
            return self.opcodes['']['pushVarb'] % (offset & 0xff)
        return self.opcodes['']['pushVarl'] % struct.pack('<l',offset)
        
    def pushVarPtr(self, ptr):
        offset = len(self.stack)*4 - int(ptr[3:]) - 4

        if not offset:
            self.unpush(1) 
            return self.push('esp')
        if -128 <= offset <= 127:
            return self.opcodes['']['pushVarPtrb'] % (offset & 0xff)
        return self.opcodes['']['pushVarPtrl'] % struct.pack('<l',offset)

    def pushTuple(self, tuple, notForTemps = ()):
        code = ''
        temps = self.registers()[:]
        to_push = [0]*len(tuple)
        for r in tuple+notForTemps:
        # first pass, removed the used registers from the possible temp regs
            if r in temps: temps.remove(r)

        # second pass, mov string or tupples into registers
        for i in range(len(tuple)):
            arg = tuple[i]
            if not (self.is_value(arg) or self.is_register(arg) or self.is_variable(arg)):
                # either it's a tupple or a string
                arg = temps[0]
                del temps[0]
                code += self.set(arg, tuple[i])
            to_push[i] = arg

        # third pass, just push arguments
        for i in range(len(to_push)-1,-1,-1):
            code += self.push(to_push[i])

        return code

    def pushString(self, string):
        answer = ''
        string += '\x00\x00\x00\x00'[:4-(len(string) % 4)]
        for i in struct.unpack('<%dl' % (len(string)/4), string):
            answer = self.push(i)+answer
        return answer

    def push(self,value, notForTemps = ()):
        self.stack.append(value)

        if self.is_register(value):
            return self.pushReg(value)

        if self.is_value(value):
            # find register with the same value
            match = self.findMatch(value)
            if match: return self.pushReg(match)

            if -0x80 <= value < 0x7f:
                return self.opcodes['']['pushb'] % (value & 0xff)

            return self.opcodes['']['pushl'] % struct.pack('<L',value)

        if self.is_tuple(value):
            self.unpush(1)
            return self.pushTuple(value, notForTemps = notForTemps)

        if self.is_variable(value):
            return self.pushVariable(value)

        if self.is_varpointer(value):
            return self.pushVarPtr(value)

        self.unpush(1)
        return self.pushString(value)

    def varAtTop(self, size = 4):
        return Variable(len(self.stack)*4, size)
    
    def alloc(self,bytes):
        # will allocate from stack and return a var

        words = (bytes + 3) / 4

        if not words: return ''

        self.stack.extend([None] * words)
        bytes = words * 4

        code = self.subValue('esp',bytes)

        return (self.subValue('esp', bytes), self.varAtTop(bytes))

    def freeVar(self,var):

        offset = len(self.stack)*4 - var.offset

        b = '%c' % (offset & 0xff)
        l = struct.pack('<l',offset)
        
        if -128 <= offset <= 127:
            return self.opcodes['esp']['subVarb'] % vars()
        else:
            return self.opcodes['esp']['subVarl'] % vars()

    def unpush(self, words):
        if not words: return
        del self.stack[-words:]

    def free(self,bytes):
        # will free some bytes from the top of the stack
        # it's blind to stack's contents
        if self.is_value(bytes):
            words = (bytes + 3) / 4
        else:
            return self.freeVar(bytes)

        if not words: return ''

        self.unpush(words)
        bytes = -words * 4

        return self.subValue('esp',bytes)

    def save(self,reg):
        return (self.push(reg), self.varAtTop())

    def setReg(self,dest,src):
        if self.getValue(src) != None and self.getValue(src) == self.getValue(dest):
            return ''
        
        self.setValue(dest,self.getValue(src))
        return self.opcodes[dest]['mov'+src]

    def setRegFromVar(self,reg,var):

        self.setValue(reg,var)

        offset = len(self.stack)*4 - var.offset

        b = '%c' % (offset & 0xff)
        l = struct.pack('<l',offset)
        
        if -128 <= offset <= 127:
            return self.opcodes[reg]['movVarb'] % vars()
        else:
            return self.opcodes[reg]['movVarl'] % vars()
        
    def setRegFromVarPtr(self,reg,offset):
        self.setValue(reg,offset)
        
        offset = int(offset[3:])
        offset = len(self.stack)*4 - offset

        if not offset:
            return self.opcodes[reg]['movesp']

        b = '%c' % (offset & 0xff)
        l = struct.pack('<l',offset)

        if -128 <= offset <= 127:
            return self.opcodes[reg]['movVarPtrb'] % vars()
        else:
            return self.opcodes[reg]['movVarPtrl'] % vars()

    """
    This is not working, because it calls micro.set('ptrXX','register')

    def setTuple(self,reg,tuple):
        code,buf = self.alloc(len(tuple)*4)
        for i in range(len(tuple)):
            code += self.set(reg,tuple[i])
            code += self.set((buf+i*4).addr(),reg)
        code += self.set(reg,buf.addr())
        return code
    """

    def setString(self,reg,string):
        # if the length of the string is over 15, the 5 bytes of overhead
        # for call is worth it, and you save a byte with pop vs mov
        if len(string) > 16:
            answer = self.call(len(string) + 5)
            answer += string
            answer += self.pop(reg)
        else:
            answer = self.set(reg,'esp')
            answer = self.push(string)+answer
        return answer

    def set(self,reg,newValue):

        value   = self.getValue(reg)

        if value == newValue:
            return ''

        # find another register with the same value
        match = self.findMatch(newValue)
        if match: return self.setReg(reg,match)
        
        if not self.is_value(newValue):
            # if int() fails, then newValue is a string
            if self.is_register(newValue):
                # moving from a register
                return self.setReg(reg,newValue)
            else:
                # setting a tuple or list
                if self.is_tuple(newValue):
                    return self.setTuple(reg,newValue)
                
                # setting a Variable or pointer to Variable
                if self.is_variable(newValue):
                    return self.setRegFromVar(reg,newValue)
                if self.is_varpointer(newValue):
                    return self.setRegFromVarPtr(reg,newValue)

                # setting a litteral string
                return self.setString(reg,newValue)

        if newValue == 0:           # even if other reg is zero:
            return self.zero(reg)   # xor has 2 bytes as well as mov reg,reg

        b = '%c' % (newValue & 0xff)
        w = struct.pack('<h',newValue & 0xffff)
        l = struct.pack('<L',newValue)

        opcodes = self.opcodes[reg]
        answer  = None

        # if current value is a number
        if self.is_value(value) and (newValue & ~0xff) == (value & ~0xff) and opcodes['movb']:
            answer = opcodes['movb'] % vars()
            
        elif self.is_value(value) and (newValue & ~0xffff) == (value & ~0xffff):
            answer = opcodes['movw'] % vars()
        else:
            if (0 <= newValue < 0x100):
                answer = self.push(newValue)+self.pop(reg)
            elif 0x100 <= newValue < 0x10000:
                answer = self.zero(reg)+self.set(reg,newValue)

        self.setValue(reg,newValue)
        if answer:
            return answer
        else:
            return opcodes['movl'] % vars()

    # comparitions
    def cmpReg(self,left,right):
#        if self.getValue(src) != None and self.getValue(src) == self.getValue(dest):
#            return ''
#        
        return self.opcodes[left]['cmp'+right]

    def cmpValue(self, reg, value):
#        if self.getValue(reg) == value:
#            return ''
        b = '%c' % (value & 0xff)
        l = struct.pack('<L',value)

        if (-0x80 <= value < 0x7f):
            return self.opcodes[reg]['cmpb'] % vars()

        return self.opcodes[reg]['cmpl'] % vars()

    def cmpRegVar(self, reg, var):
        # compares a register and a variable
        raise Exception, "Not implemented yet"

    def cmpVarValue(self, var, value):
        # compares a variable with an immediate value
        if -128 <= value <= 127:
            # the value is a byte
            key = 'cmpb'
            value &= 0xff
        else:
            key = 'cmpl'
            value = struct.pack('<l',value)

        offset = len(self.stack)*4 - var.offset

        if -128 <= offset <= 127:
            # variable's offset is a byte
            return self.opcodes[''][key+'Varb'] % (offset & 0xff, value)
        else:
            return self.opcodes[''][key+'Varl'] % (struct.pack('<l', offset), value)
        

    def cmp(self, left, right):
        if self.is_register(left):
            if self.is_value(right):
                return self.cmpValue(left,right)
            if self.is_register(right):
                return self.cmpReg(left,right)
            if self.is_variable(right):
                return self.cmpReg(left,right)
        else:
            if self.is_value(right):
                return self.cmpVarValue(left,right)
#       the problem with this is that an if(var, reg) must have the oposite condition
#            if self.is_register(right):
#                return self.cmpRegVar(right,left)

        raise Exception, "Invalid comparision between %s and %s" % (left, right)

    # jumps
    def jumpRel(self,delta,condition = ''):
        # the jump is relative to the first byte of the jump

        b = '%c' % (delta - 2 & 0xff)
        l = struct.pack('<L',delta-5)

        if -128 < delta-2 < 127:
            return self.opcodes['']['jmpb'+condition] % vars()
        else:
            if condition:
                answer  = self.jumpRel(7,self.opositeCondition(condition))
                answer += self.jumpRel(delta-2)
                answer += '\x90'*(7-len(answer))
                return answer
            return self.opcodes['']['jmpl'] % vars()
     
    def opositeCondition(self, condition):
        return self.opcodes['']['!'+condition]

    def callVar(self, var):
        offset = len(self.stack)*4 - var.offset

        if -128 <= offset <= 127:
            # variable's offset is a byte
            return self.opcodes['']['callVarb'] % (offset & 0xff)
        else:
            return self.opcodes['']['callVarl'] % (struct.pack('<l', offset))
 
    def callRel(self,delta):
        # the jump is relative to the first byte of the jump

        return '\xe8'+(struct.pack('<l',delta-5))

    def jumpReg(self, reg):
        return '\xff%c' % (0xe0+self.regNum(reg))

    def callReg(self, reg):
        return '\xff%c' % (0xd0+self.regNum(reg))

    def call(self, dest):
        # XXX: next reset should not be reset but, for example,
        # when calling a function, the registers should be set
        # as left by the called function (some changed some not)

        self.reset()
        if self.is_value(dest):
            return self.callRel(dest)
        if self.is_variable(dest):
            return self.callVar(dest)
        if self.is_register(dest):
            return self.callReg(dest)
        raise Exception, ("Unsupported call type, calling (%s)" % dest)
        
    def ret(self,n = 0):
        if n:
            return '\xc2'+struct.pack('<h',n)
        else:
            return '\xc3'

    def regNum(self, reg):
        return self.registers().index(reg)
        
    # interactive utils
    def registers(self):
        return self._registers
    
class Syscall:
    def __init__(self,micro):
        self.micro = micro

    def call(self, name, args = ()):
        code = self.setArgs(args)
        code += self.syscall(self.syscalls[name])
        
        return code, self.answer()

    def copyFrom(self, other):
        pass

class Linuxx86Syscall(Syscall):
    microClass = Microx86
    syscalls = {
        'exit':   1,
        'fork':   2,
        'read':   3,
        'write':   4,
        'open':   5,
        'close':   6,
        'waitpid':   7,
        'creat':   8,
        'link':   9,
        'unlink':  10,
        'execve':  11,
        'chdir':  12,
        'time':  13,
        'mknod':  14,
        'chmod':  15,
        'lchown':  16,
        'break':  17,
        'oldstat':  18,
        'lseek':  19,
        'getpid':  20,
        'mount':  21,
        'umount':  22,
        'setuid':  23,
        'getuid':  24,
        'stime':  25,
        'ptrace':  26,
        'alarm':  27,
        'oldfstat':  28,
        'pause':  29,
        'utime':  30,
        'stty':  31,
        'gtty':  32,
        'access':  33,
        'nice':  34,
        'ftime':  35,
        'sync':  36,
        'kill':  37,
        'rename':  38,
        'mkdir':  39,
        'rmdir':  40,
        'dup':  41,
        'pipe':  42,
        'times':  43,
        'prof':  44,
        'brk':  45,
        'setgid':  46,
        'getgid':  47,
        'signal':  48,
        'geteuid':  49,
        'getegid':  50,
        'acct':  51,
        'umount2':  52,
        'lock':  53,
        'ioctl':  54,
        'fcntl':  55,
        'mpx':  56,
        'setpgid':  57,
        'ulimit':  58,
        'oldolduname':  59,
        'umask':  60,
        'chroot':  61,
        'ustat':  62,
        'dup2':  63,
        'getppid':  64,
        'getpgrp':  65,
        'setsid':  66,
        'sigaction':  67,
        'sgetmask':  68,
        'ssetmask':  69,
        'setreuid':  70,
        'setregid':  71,
        'sigsuspend':  72,
        'sigpending':  73,
        'sethostname':  74,
        'setrlimit':  75,
        'getrlimit':  76,
        'getrusage':  77,
        'gettimeofday':  78,
        'settimeofday':  79,
        'getgroups':  80,
        'setgroups':  81,
        'select':  82,
        'symlink':  83,
        'oldlstat':  84,
        'readlink':  85,
        'uselib':  86,
        'swapon':  87,
        'reboot':  88,
        'readdir':  89,
        'mmap':  90,
        'munmap':  91,
        'truncate':  92,
        'ftruncate':  93,
        'fchmod':  94,
        'fchown':  95,
        'getpriority':  96,
        'setpriority':  97,
        'profil':  98,
        'statfs':  99,
        'fstatfs': 100,
        'ioperm': 101,
        'socketcall': 102,
        'syslog': 103,
        'setitimer': 104,
        'getitimer': 105,
        'stat': 106,
        'lstat': 107,
        'fstat': 108,
        'olduname': 109,
        'iopl': 110,
        'vhangup': 111,
        'idle': 112,
        'vm86old': 113,
        'wait4': 114,
        'swapoff': 115,
        'sysinfo': 116,
        'ipc': 117,
        'fsync': 118,
        'sigreturn': 119,
        'clone': 120,
        'setdomainname': 121,
        'uname': 122,
        'modify_ldt': 123,
        'adjtimex': 124,
        'mprotect': 125,
        'sigprocmask': 126,
        'create_module': 127,
        'init_module': 128,
        'delete_module': 129,
        'get_kernel_syms': 130,
        'quotactl': 131,
        'getpgid': 132,
        'fchdir': 133,
        'bdflush': 134,
        'sysfs': 135,
        'personality': 136,
        'afs_syscall': 137,
        'setfsuid': 138,
        'setfsgid': 139,
        '_llseek': 140,
        'getdents': 141,
        '_newselect': 142,
        'flock': 143,
        'msync': 144,
        'readv': 145,
        'writev': 146,
        'getsid': 147,
        'fdatasync': 148,
        '_sysctl': 149,
        'mlock': 150,
        'munlock': 151,
        'mlockall': 152,
        'munlockall': 153,
        'sched_setparam': 154,
        'sched_getparam': 155,
        'sched_setscheduler': 156,
        'sched_getscheduler': 157,
        'sched_yield': 158,
        'sched_get_priority_max': 159,
        'sched_get_priority_min': 160,
        'sched_rr_get_interval': 161,
        'nanosleep': 162,
        'mremap': 163,
        'setresuid': 164,
        'getresuid': 165,
        'vm86': 166,
        'query_module': 167,
        'poll': 168,
        'nfsservctl': 169,
        'setresgid': 170,
        'getresgid': 171,
        'prctl':172,
        'rt_sigreturn': 173,
        'rt_sigaction': 174,
        'rt_sigprocmask': 175,
        'rt_sigpending': 176,
        'rt_sigtimedwait': 177,
        'rt_sigqueueinfo': 178,
        'rt_sigsuspend': 179,
        'pread': 180,
        'pwrite': 181,
        'chown': 182,
        'getcwd': 183,
        'capget': 184,
        'capset': 185,
        'sigaltstack': 186,
        'sendfile': 187,
        'getpmsg': 188,
        'putpmsg': 189,
        'vfork': 190,
        'ugetrlimit': 191,
        'mmap2': 192,
        'truncate64': 193,
        'ftruncate64': 194,
        'stat64': 195,
        'lstat64': 196,
        'fstat64': 197,
        'lchown32': 198,
        'getuid32': 199,
        'getgid32': 200,
        'geteuid32': 201,
        'getegid32': 202,
        'setreuid32': 203,
        'setregid32': 204,
        'getgroups32': 205,
        'setgroups32': 206,
        'fchown32': 207,
        'setresuid32': 208,
        'getresuid32': 209,
        'setresgid32': 210,
        'getresgid32': 211,
        'chown32': 212,
        'setuid32': 213,
        'setgid32': 214,
        'setfsuid32': 215,
        'setfsgid32': 216,
        'pivot_root': 217,
        'mincore': 218,
        'madvise': 219,
        'madvise1': 219,
        'getdents64': 220,
        'fcntl64': 221,
        'security': 223,
        'gettid': 224,
        'readahead': 225,
        'setxattr': 226,
        'lsetxattr': 227,
        'fsetxattr': 228,
        'getxattr': 229,
        'lgetxattr': 230,
        'fgetxattr': 231,
        'listxattr': 232,
        'llistxattr': 233,
        'flistxattr': 234,
        'removexattr': 235,
        'lremovexattr': 236,
        'fremovexattr': 237,
        'tkill': 238,
        'sendfile64': 239,
        'futex': 240,
        'sched_setaffinity': 241,
        'sched_getaffinity': 242,
        'set_thread_area ': 243,
    }
    # socket calls
    socketcalls= {
        'socket': 1,
        'bind': 2,
        'connect': 3,
        'listen': 4,
        'accept': 5,
        'getsockname': 6,
        'getpeername': 7,
        'socketpair': 8,
        'send': 9,
        'recv': 10,
        'sendto': 11,
        'recvfrom': 12,
        'shutdown': 13,
        'setsockopt': 14,
        'getsockopt': 15,
        'sendmsg': 16,
        'recvmsg': 17
    }

    def __init__(self,micro):
        Syscall.__init__(self,micro)
        self.args  = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp']

    def setArg(self, argNumber, value):
        return self.micro.set(self.args[argNumber],value)

    def setArgs(self, args = ()):
        code = ''
        for i in range(len(args)):
            code += self.setArg(i+1,args[i])
        
        return code

    def call(self, name, args = ()):
        if self.socketcalls.has_key(name):
            return self.socketCall(name,args)
        else:
            return Syscall.call(self,name,args)

    def syscall(self, number):
        answer = self.setArg(0,number)+'\xcd\x80'   # int $0x80
        self.micro.setValue(self.args[0],None)
        return answer

    def inet_addr(self, ip):
        ipaddr = map(lambda x:int(x),ip.split('.'))
        ipaddr = apply(struct.pack,['BBBB']+ipaddr)
        return ipaddr

    def make_sockaddr(self, addr, family, len=16):
        ipaddr = self.inet_addr(addr[0])
        port   = struct.pack('!h',addr[1])
        family = struct.pack('<h',family)
        return '%s%s%s%s' % (family, port, ipaddr, '\x00'*(len-8))

    def socketCall(self,name,args):
        code = ''
        code += self.micro.push(args)
        sysCode, answer = self.call('socketcall',
            (self.socketcalls[name],self.micro.varAtTop().addr()))
        code += sysCode
        code += self.micro.free(4*len(args))
        return code, answer
        
    def answer(self):
        return 'eax'

class StackBasedSyscall(Syscall):
    def __init__(self,micro):
        self.micro = micro

    def setArgs(self, args = (), notForTemps = ()):
        return self.micro.push(args, notForTemps = notForTemps)

    def answer(self):
        return 'eax'

class OpenBSDx86Syscall(StackBasedSyscall):
    microClass = Microx86
    syscalls = {
        'syscall': 0,
        'exit': 1,
        'fork': 2,
        'read': 3,
        'write': 4,
        'open': 5,
        'close': 6,
        'wait4': 7,
        'link': 9,
        'unlink': 10,
        'chdir': 12,
        'fchdir': 13,
        'mknod': 14,
        'chmod': 15,
        'chown': 16,
        'break': 17,
        'ogetfsstat': 18,
        'getpid': 20,
        'mount': 21,
        'unmount': 22,
        'setuid': 23,
        'getuid': 24,
        'geteuid': 25,
        'ptrace': 26,
        'recvmsg': 27,
        'sendmsg': 28,
        'recvfrom': 29,
        'accept': 30,
        'getpeername': 31,
        'getsockname': 32,
        'access': 33,
        'chflags': 34,
        'fchflags': 35,
        'sync': 36,
        'kill': 37,
        'getppid': 39,
        'dup': 41,
        'opipe': 42,
        'getegid': 43,
        'profil': 44,
        'ktrace': 45,
        'sigaction': 46,
        'getgid': 47,
        'sigprocmask': 48,
        'getlogin': 49,
        'setlogin': 50,
        'acct': 51,
        'sigpending': 52,
        'sigaltstack': 53,
        'ioctl': 54,
        'reboot': 55,
        'revoke': 56,
        'symlink': 57,
        'readlink': 58,
        'execve': 59,
        'umask': 60,
        'chroot': 61,
        'omsync': 65,
        'vfork': 66,
        'sbrk': 69,
        'sstk': 70,
        'vadvise': 72,
        'munmap': 73,
        'mprotect': 74,
        'madvise': 75,
        'mincore': 78,
        'getgroups': 79,
        'setgroups': 80,
        'getpgrp': 81,
        'setpgid': 82,
        'setitimer': 83,
        'swapon': 85,
        'getitimer': 86,
        'dup2': 90,
        'fcntl': 92,
        'select': 93,
        'fsync': 95,
        'setpriority': 96,
        'socket': 97,
        'connect': 98,
        'getpriority': 100,
        'sigreturn': 103,
        'bind': 104,
        'setsockopt': 105,
        'listen': 106,
        'sigsuspend': 111,
        'gettimeofday': 116,
        'getrusage': 117,
        'getsockopt': 118,
        'readv': 120,
        'writev': 121,
        'settimeofday': 122,
        'fchown': 123,
        'fchmod': 124,
        'rename': 128,
        'flock': 131,
        'mkfifo': 132,
        'sendto': 133,
        'shutdown': 134,
        'socketpair': 135,
        'mkdir': 136,
        'rmdir': 137,
        'utimes': 138,
        'adjtime': 140,
        'setsid': 147,
        'quotactl': 148,
        'nfssvc': 155,
        'ostatfs': 157,
        'ofstatfs': 158,
        'getfh': 161,
        'sysarch': 165,
        'pread': 173,
        'pwrite': 174,
        'ntp_gettime': 175,
        'ntp_adjtime': 176,
        'setgid': 181,
        'setegid': 182,
        'seteuid': 183,
        'lfs_bmapv': 184,
        'lfs_markv': 185,
        'lfs_segclean': 186,
        'lfs_segwait': 187,
        'stat': 188,
        'fstat': 189,
        'lstat': 190,
        'pathconf': 191,
        'fpathconf': 192,
        'swapctl': 193,
        'getrlimit': 194,
        'setrlimit': 195,
        'getdirentries': 196,
        'mmap': 197,
        '__syscall': 198,
        'lseek': 199,
        'truncate': 200,
        'ftruncate': 201,
        '__sysctl': 202,
        'mlock': 203,
        'munlock': 204,
        'undelete': 205,
        'futimes': 206,
        'getpgid': 207,
        'xfspioctl': 208,
        '__osemctl': 220,
        'semget': 221,
        'semop': 222,
        'omsgctl': 224,
        'msgget': 225,
        'msgsnd': 226,
        'msgrcv': 227,
        'shmat': 228,
        'oshmctl': 229,
        'shmdt': 230,
        'shmget': 231,
        'clock_gettime': 232,
        'clock_settime': 233,
        'clock_getres': 234,
        'nanosleep': 240,
        'minherit': 250,
        'rfork': 251,
        'poll': 252,
        'issetugid': 253,
        'lchown': 254,
        'getsid': 255,
        'msync': 256,
        '__semctl': 257,
        'shmctl': 258,
        'msgctl': 259,
        'getfsstat': 260,
        'statfs': 261,
        'fstatfs': 262,
        'pipe': 263,
        'fhopen': 264,
        'fhstat': 265,
        'fhstatfs': 266,
        'preadv': 267,
        'pwritev': 268,
        'kqueue': 269,
        'kevent': 270,
        'mlockall': 271,
        'munlockall': 272,
    }
    def syscall(self, number):
        answer = self.micro.push('eax')
        answer += self.micro.set('eax',number)+'\xcd\x80'   # int $0x80
        self.micro.setValue('eax',None)
        return answer

    def inet_addr(self, ip):
        ipaddr = map(lambda x:int(x),ip.split('.'))
        ipaddr = apply(struct.pack,['BBBB']+ipaddr)
        return ipaddr

    def make_sockaddr(self, addr, family, len=16):
        ipaddr = self.inet_addr(addr[0])
        port   = struct.pack('!h',addr[1])
        family = struct.pack('b',family)
        slen   = struct.pack('b',len)
        return '%s%s%s%s%s' % (slen, family, port, ipaddr, '\x00'*(len-8))

class Solarisx86Syscall(StackBasedSyscall):
    microClass = Microx86
    syscalls = {
        'syscall': 0,
        'exit': 1,
        'fork': 2,
        'read': 3,
        'write': 4,
        'open': 5,
        'close': 6,
        'wait': 7,
        'creat': 8,
        'link': 9,
        'unlink': 10,
        'exec': 11,
        'chdir': 12,
        'time': 13,
        'mknod': 14,
        'chmod': 15,
        'chown': 16,
        'brk':  17,
        'stat': 18,
        'lseek': 19,
        'getpid': 20,
        'mount': 21,
        'umount': 22,
        'setuid': 23,
        'getuid': 24,
        'stime': 25,
        'pcsample': 26,
        'alarm': 27,
        'fstat': 28,
        'pause': 29,
        'utime': 30,
        'stty': 31,
        'gtty': 32,
        'access': 33,
        'nice': 34,
        'statfs': 35,
        'sync': 36,
        'kill': 37,
        'fstatfs': 38,
        'pgrpsys': 39,
              #
              # subcodes:
              # getpgrp()   :: syscall(39,0)
              # setpgrp()   :: syscall(39,1)
              # getsid(pid)   :: syscall(39,2,pid)
              # setsid()   :: syscall(39,3)
              # getpgid(pid)   :: syscall(39,4,pid)
              # setpgid(pid,pgid) :: syscall(39,5,pid,pgid)
              #
        'xenix': 40,
              #
              # subcodes:
              # syscall(40, code, ...)
              #
        'dup':  41,
        'pipe': 42,
        'times': 43,
        'profil': 44,
        'plock': 45,
        'setgid': 46,
        'getgid': 47,
        'signal': 48,
              #
              # subcodes:
              # signal(sig, f) :: signal(sig, f)    ((sig&SIGNO_MASK) == sig)
              # sigset(sig, f) :: signal(sig|SIGDEFER, f)
              # sighold(sig)   :: signal(sig|SIGHOLD)
              # sigrelse(sig)  :: signal(sig|SIGRELSE)
              # sigignore(sig) :: signal(sig|SIGIGNORE)
              # sigpause(sig)  :: signal(sig|SIGPAUSE)
              # see <sys/signal.h>
              #
        'msgsys': 49,
              #
              # subcodes:
              # msgget(...)  :: msgsys(0, ...)
              # msgctl(...)  :: msgsys(1, ...)
              # msgrcv(...)  :: msgsys(2, ...)
              # msgsnd(...)  :: msgsys(3, ...)
              # msgids(...)  :: msgsys(4, ...)
              # msgsnap(...) :: msgsys(5, ...)
              # see <sys/msg.h>
              #
        'syssun': 50,
        'sysi86': 50,
              #
              # subcodes:
              # syssun(code, ...)
              # see <sys/sys3b.h>
              #
        'acct': 51,
        'shmsys': 52,
              #
              # subcodes:
              # shmat (...) :: shmsys(0, ...)
              # shmctl(...) :: shmsys(1, ...)
              # shmdt (...) :: shmsys(2, ...)
              # shmget(...) :: shmsys(3, ...)
              # shmids(...) :: shmsys(4, ...)
              # see <sys/shm.h>
              #
        'semsys': 53,
              #
              # subcodes:
              # semctl(...) :: semsys(0, ...)
              # semget(...) :: semsys(1, ...)
              # semop (...) :: semsys(2, ...)
              # semids(...) :: semsys(3, ...)
              # semtimedop(...) :: semsys(4, ...)
              # see <sys/sem.h>
              #
        'ioctl': 54,
        'uadmin': 55,
              # 56 reserved for exch() 
        'utssys': 57,
              #
              #subcodes (third argument):
              # uname(obuf)  (obsolete)   :: syscall(57, obuf, ign, 0)
              #     subcode 1 unused
              # ustat(dev, obuf)   :: syscall(57, obuf, dev, 2)
              # fusers(path, flags, obuf) :: syscall(57, path, flags, 3, obuf)
              # see <sys/utssys.h>
              #
        'fdsync': 58,
        'execve': 59,
        'umask': 60,
        'chroot': 61,
        'fcntl': 62,
        'ulimit': 63,
              # 64-69 reserved for UNIX PC
        'tasksys': 70,
              #
              # subcodes:
              #  settaskid(...) :: tasksys(0, ...)
              #  gettaskid(...) :: tasksys(1, ...)
              #  getprojid(...) :: tasksys(2, ...)
              #
        'acctctl': 71,
        'exacctsys': 72,
              #
              # subcodes:
              #  getacct(...) :: exacct(0, ...)
              #  putacct(...) :: exacct(1, ...)
              #  wracct(...) :: exacct(2, ...)
              # 
        'reserved_73': 73, # 73 reserved
        'reserved_74': 74, # 74 reserved
        'reserved_75': 75, # 75 reserved
        'reserved_76': 76, # 76 reserved
        'reserved_77': 77, # 77 reserved
        'reserved_78': 78, # 78 reserved
        'rmdir': 79,
        'mkdir': 80,
        'getdents': 81,
              # 82 not used, was libattach
              # 83 not used, was libdetach
        'sysfs': 84,
              #
              # subcodes:
              # sysfs(code, ...)
              # see <sys/fstyp.h>
              # 
        'getmsg': 85,
        'putmsg': 86,
        'poll': 87,

        'lstat': 88,
        'symlink': 89,
        'readlink': 90,
        'setgroups': 91,
        'getgroups': 92,
        'fchmod': 93,
        'fchown': 94,
        'sigprocmask': 95,
        'sigsuspend': 96,
        'sigaltstack': 97,
        'sigaction': 98,
        'sigpending': 99,
              #
              # subcodes:
              #   subcode 0 unused
              # sigpending(...) :: syscall(99, 1, ...)
              # sigfillset(...) :: syscall(99, 2, ...)
              # 
        'context': 100,
              #
              # subcodes:
              # getcontext(...) :: syscall(100, 0, ...)
              # setcontext(...) :: syscall(100, 1, ...)
              # 
        'evsys': 101,
        'evtrapret': 102,
        'statvfs': 103,
        'fstatvfs': 104,
        'getloadavg': 105,
        'nfssys': 106,
        'waitsys': 107,
        'sigsendsys': 108,
        'hrtsys': 109,
        'acancel': 110,
        'async': 111,
        'priocntlsys': 112,
        'pathconf': 113,
        'mincore': 114,
        'mmap': 115,
        'mprotect': 116,
        'munmap': 117,
        'fpathconf': 118,
        'vfork': 119,
        'fchdir': 120,
        'readv': 121,
        'writev': 122,
        'xstat': 123,
        'lxstat': 124,
        'fxstat': 125,
        'xmknod': 126,
        'clocal': 127,
        'setrlimit': 128,
        'getrlimit': 129,
        'lchown': 130,
        'memcntl': 131,
        'getpmsg': 132,
        'putpmsg': 133,
        'rename': 134,
        'uname': 135,
        'setegid': 136,
        'sysconfig': 137,
        'adjtime': 138,
        'systeminfo': 139,
        'seteuid': 141,
        'vtrace': 142,
        'fork1': 143,
        'sigtimedwait': 144,
        'lwp_info': 145,
        'yield': 146,
        'lwp_sema_wait': 147,
        'lwp_sema_post': 148,
        'lwp_sema_trywait': 149,
        'corectl': 151,
        'modctl': 152,
        'fchroot': 153,
        'utimes': 154,
        'vhangup': 155,
        'gettimeofday': 156,
        'getitimer': 157,
        'setitimer': 158,
        'lwp_create': 159,
        'lwp_exit': 160,
        'lwp_suspend': 161,
        'lwp_continue': 162,
        'lwp_kill': 163,
        'lwp_self': 164,
        'lwp_setprivate': 165,
        'lwp_getprivate': 166,
        'lwp_wait': 167,
        'lwp_mutex_wakeup': 168,
        'lwp_mutex_lock': 169,
        'lwp_cond_wait': 170,
        'lwp_cond_signal': 171,
        'lwp_cond_broadcast': 172,
        'pread': 173,
        'pwrite': 174,
        'llseek': 175,
        'inst_sync': 176,
        'srmlimitsys': 177,
        'kaio': 178,
              #
              # subcodes:
              # aioread(...) :: kaio(AIOREAD, ...)
              # aiowrite(...) :: kaio(AIOWRITE, ...)
              # aiowait(...) :: kaio(AIOWAIT, ...)
              # aiocancel(...) :: kaio(AIOCANCEL, ...)
              # aionotify() :: kaio(AIONOTIFY)
              # aioinit() :: kaio(AIOINIT)
              # aiostart() :: kaio(AIOSTART)
              # see <sys/aio.h>
              # 
        'cpc': 179,
        'tsolsys': 184,
        'acl': 185,
        'auditsys': 186,
        'processor_bind': 187,
        'processor_info': 188,
        'p_online': 189,
        'sigqueue': 190,
        'clock_gettime': 191,
        'clock_settime': 192,
        'clock_getres': 193,
        'timer_create': 194,
        'timer_delete': 195,
        'timer_settime': 196,
        'timer_gettime': 197,
        'timer_getoverrun': 198,
        'nanosleep': 199,
        'facl': 200,
        'door': 201,
              #
              # Door Subcodes:
              # 0 door_create
              # 1 door_revoke
              # 2 door_info
              # 3 door_call
              # 4 door_return
              # 
        'setreuid': 202,
        'setregid': 203,
        'install_utrap': 204,
        'signotify': 205,
        'schedctl': 206,
        'pset': 207,
        'sparc_utrap_install': 208,
        'resolvepath': 209,
        'signotifywait': 210,
        'lwp_sigredirect': 211,
        'lwp_alarm': 212,
              # system calls for large file ( > 2 gigabyte) support
        'getdents64': 213,
        'mmap64': 214,
        'stat64': 215,
        'lstat64': 216,
        'fstat64': 217,
        'statvfs64': 218,
        'fstatvfs64': 219,
        'setrlimit64': 220,
        'getrlimit64': 221,
        'pread64': 222,
        'pwrite64': 223,
        'creat64': 224,
        'open64': 225,
        'rpcsys': 226,
        'socket': 230,
        'socketpair': 231,
        'bind': 232,
        'listen': 233,
        'accept': 234,
        'connect': 235,
        'shutdown': 236,
        'recv': 237,
        'recvfrom': 238,
        'recvmsg': 239,
        'send': 240,
        'sendmsg': 241,
        'sendto': 242,
        'getpeername': 243,
        'getsockname': 244,
        'getsockopt': 245,
        'setsockopt': 246,
        'sockconfig': 247,
              #
              # NTP codes
              #
        'ntp_gettime': 248,
        'ntp_adjtime': 249,
        'lwp_mutex_unlock': 250,
        'lwp_mutex_trylock': 251,
        'lwp_mutex_init': 252,
        'cladm': 253,
        'lwp_sigtimedwait': 254,
        'umount2': 255,
    }

    def syscall(self, number):
       answer = self.micro.push('eax')
       answer += self.micro.set('eax',number)+'\x9a\x00\x00\x00\x00\x07\x00' # callf 07:00000000
       self.micro.setValue('eax',None)
       return answer

class FreeBSDx86Syscall(OpenBSDx86Syscall):
    pass

class InlineEgg:
    # base
    
    def __init__(self,syscallClass = None, microClass = None):
        if not syscallClass:
            raise Exception, "You need to build an InlineEgg with the SyscallClass as argument"
        self.code = ''
        if not microClass:
           self.micro = syscallClass.microClass()
        else:
           self.micro = microClass()
        self.syscall  = syscallClass(self.micro)
        self.setBaseAddr(0)
        
    def setBaseAddr(self, addr):
        self.base_addr = addr

    def __iadd__(self, code):
        self.addCode(code)
        return self

    def addCode(self,code):
        self.code += "%s" % code

    def __str__(self):
        return self.getCode()

    def getCode(self):
        return self.code

    def __len__(self):
        return len(self.getCode())

    # generic syscall calling
    class CallSyscall:
        def __init__(self, egg, syscall_name):
            self.egg = egg
            self.syscall = syscall_name
        def __call__(self, *args):
            return self.egg._SysCall(self.syscall, args)

    def __getattr__(self, name):
        if self.syscall.syscalls.has_key(name):
            self.__dict__[name] = self.CallSyscall(self, name)
            return self.__dict__[name]
        else: raise AttributeError, ("%s instance has no attribute '%s'" % (self.__class__, name))

    # system calls
    def _SysCall(self,name,args = ()):
        code,answer = self.syscall.call(name,args)
        self.addCode(code)
        return answer

    def exit(self, retVal = 0):
        return self._SysCall('exit',(retVal,))

    def fork(self):
        # XXX It would be nice to implement a language fork() no just syscall
        # like moving all the If('eax','=',0) etc here
        return self._SysCall('fork')

    def write(self,fd,buf,count = None):
        if count is None: count = len(buf)
        return self._SysCall('write',(fd,buf,count))
    
    def open(self,fileName,flags=0,mode=0):
        return self._SysCall('open',(fileName,flags,mode))

    def fcntl(self,fd, cmd = None, arg = None):
        args = (fd,)
        if None != cmd: args += (cmd,)
        if None != arg: args += (arg,)
        return self._SysCall('fcntl',args)
        
    def execve(self,fileName,argv = 0,envp = 0):
        if self.micro.is_tuple(argv):
            argv = self.save(argv+(0,)).addr()
        if self.micro.is_tuple(envp):
            envp = self.save(envp+(0,)).addr()
        return self._SysCall('execve',(fileName,argv, envp))

    def ptrace(self,request,pid,addr = None, data = None):
        args = (request,pid)
        if None != addr: args += (addr,)
        if None != data: args += (data,)
        return self._SysCall('ptrace',args)

    def prctl(self, option, arg2):
        # linux only?
        return self._SysCall('prctl',(option, arg2))
    
    def mkdir(self, dir, mode = 0777):
        return self._SysCall('mkdir',(dir,mode))

    def chroot(self, dir):
        return self._SysCall('chroot',(dir,))

    def stat(self,fileName,statBuf):
        return self._SysCall('stat',(fileName,statBuf))

    def dup(self,fd):
        return self._SysCall('dup',(fd,))

    def dup2(self,fd1,fd2):
        return self._SysCall('dup2',(fd1,fd2))

    def fstat(self, fd, stat_buf):
        return self._SysCall('fstat',(fd, stat_buf))

    def signal(self,signal,action):
        return self._SysCall('signal',(signal,action))

    def kill(self, pid, signal):
        return self._SysCall('kill',(pid, signal))

    def sigaction(self,signal,action):
        print "Warning: this is not finished!"
        self.save(action)
        sigaction = self.micro.varAtTop().addr()
        self.alloc(4*4)
        self._SysCall('sigaction',(signal,sigaction,0,8))
        self.free(4*5)

# mmap gets arguments on stack
#    def mmap(self,start,length,prot,flags,fd,offset):
#        return self._SysCall('mmap',(start,length,prot,flags,fd,offset))

    def munmap(self,start,length):
        return self._SysCall('munmap',(start,length))

    def ioctl(self,fd,request,arg):
        return self._SysCall('ioctl',(fd,request,arg))

    # socket
    def socket(self, domain, type,proto = 0):
        return self._SysCall('socket',(domain,type,proto))

    def socketpair(self, domain, type, protocol,answer):
        return self._SysCall('socketpair',(domain,type,protocol,answer))

    def connect(self, sock, addr):
        # as socket.socket().connect(addr) addr is a pair: (ip_addr, port)
        sa = self.syscall.make_sockaddr(addr, 2)
        return self._SysCall('connect',(sock, sa, len(sa)))
    
    def bind(self, socket, addr):
        # as socket.socket().bind(addr) addr is a pair: (ip_addr, port)
        sa = self.syscall.make_sockaddr(addr, 2)
        return self._SysCall('bind',(socket, sa, len(sa)))

    def listen(self, sock, backlog):
        return self._SysCall('listen',(sock, backlog))

    def accept(self, sock, sa, salen):
        return self._SysCall('accept',(sock, sa, salen))

    def getpeername(self, socket, addr, lenp):
        answer = self._SysCall('getpeername',(socket,addr,lenp))
        return answer

    # language

    def save(self,value):
        save = self.micro.save(value)
        self.addCode(save[0])
        return save[1]

    def alloc(self,bytes):
        alloc = self.micro.alloc(bytes)
        self.addCode(alloc[0])
        return alloc[1]

    def free(self,bytes):
        self.addCode(self.micro.free(bytes))

    def freeStack(self, leave = 0):
        self.free(4*(len(self.micro.stack)-leave))

    def pop(self,reg):
        self.addCode(self.micro.pop(reg))

    def While1(self):
        return While1InlineEgg(self)

    def While(self, left, condition, right):
        return WhileInlineEgg(self, left, condition, right)

    def Do(self):
        return DoInlineEgg(self)

    def Function(self):
        return FunctionInlineEgg(self)

    def call(self,function):
        if type(function) == types.IntType:
            code = self.micro.call(int(function)-len(self.code)-self.base_addr)
        else:
            code = self.micro.call(int(function.address[5:])-len(self.code))
        self.addCode(code)

    def label(self, delta = 0):
        return 'label%d' % (len(self.code)+delta)

    def jump(self,label,condition = ''):
        if type(label) == types.IntType:
            code = self.micro.jumpRel(int(label)-len(self.code)-self.base_addr)
        else:
            code = self.micro.jumpRel(int(label[5:])-len(self.code),condition)
        self.addCode(code)

    def If(self, left, condition, right):
        return IfInlineEgg(self, left, condition, right)

    def ret(self, n = 0):
        self.addCode(self.micro.ret(n))

    # utils

    def dumpBin(self, fileName):
        open(fileName,'w').write(self.getCode())

    def dumpS(self,fileName):
        f = open(fileName,'w')
        f.write("""
    .text
    .align  4
    .globl  _start
    .type   _start,@function

_start:
    .byte   """)
        bytes = struct.unpack('%db' % len(self.code), self.code)
        bytes = map(lambda x: '0x%02x' % (x & 0xff),bytes)
        bytes = ','.join(bytes)
        f.write(bytes+'\n')
        f.close()

    def dumpElf(self,fileName, base = 0x8048000):
        import exelib
        import os

        ei_osabi_mapping = {
           Linuxx86Syscall:     exelib.ELFOSABI_SYSV,
           FreeBSDx86Syscall:   exelib.ELFOSABI_FREEBSD,
           OpenBSDx86Syscall:   exelib.ELFOSABI_OPENBSD,
           Solarisx86Syscall:   exelib.ELFOSABI_SYSV,
        }
        elf = exelib.Elf32Program(ei_osabi_mapping[self.syscall.__class__])
        elf.setArch(elf.ARCH_I386)
        elf.addCode(self.code)

        p = elf.programTable[0]
        p.p_vaddr = base
        elf.header.e_entry = p.p_vaddr+elf.totalHeaderLength()

        f = open(fileName,'w')
        f.write(elf.bytes())
        f.close()
        os.chmod(fileName,0755)

    def dumpAOut(self,fileName):
        import exelib
        import os
        elf = exelib.AOutProgram()
        elf.setArch(elf.ARCH_I386)
        elf.addCode(self.code)

        f = open(fileName,'w')
        f.write(elf.bytes())
        f.close()
        os.chmod(fileName,0755)

    def dumpExe(self, fileName):
        import exelib
        exe = exelib.PEProgram()
        exe.addCode(self.code)
        f = open(fileName, "w")
        f.write(exe.bytes())
        f.close()


# XXX: This classes still have problems saving/restoring/tracking registers
#      for example, If will not be careful enough with registers, and may
#      wronly assume a register is set to some value, after exiting the If

class LanguageInlineEgg(InlineEgg):
    def __init__(self,outer):
        InlineEgg.__init__(self,outer.syscall.__class__,outer.micro.__class__)
        self.outer = outer
        self.original_stack_size = 0
        self.setBaseAddr(self.outer.base_addr+len(self.outer))

    def freeStack(self):
        self.free(4*(len(self.micro.stack)-self.original_stack_size))

    # private
    def stackFromOuter(self):
        # we need to copy the stack so variables declared outside the statement
        # can be accessed inside it
        self.micro.stack = self.outer.micro.stack
        self.original_stack_size = len(self.micro.stack)

    def codeFromOuter(self):
        # the initial size of code must match that of outer
        # so jumps and labels are coherent inside and outside
        self.code = '.'*len(self.outer.code)

    def syscallFromOuter(self):
        # copy syscall state from outer
        # mainly needed for WindowsSyscall
        self.syscall.copyFrom(self.outer.syscall)


class While1InlineEgg(LanguageInlineEgg):
    def __init__(self,outer):
        LanguageInlineEgg.__init__(self,outer)
        self.stackFromOuter()
        self.syscallFromOuter()

    def end(self):
        loop = self.outer.label()
        self.freeStack()
        self.outer.addCode(self.code)
        self.outer.jump(loop)


class FunctionInlineEgg(LanguageInlineEgg):
    def __init__(self,outer):
        LanguageInlineEgg.__init__(self,outer)

        # only for recursion, and only possible this easy if
        # calls and jumps are relative
        self.address = self.label()

    def end(self):
        self.freeStack()
        self.ret()

        real_size = len(self)
        self.jump(self.address)
        self.outer.jump(self.outer.label(len(self)))
        self.address = self.outer.label()
        self.outer.addCode(self.getCode()[:real_size])

class IfInlineEgg(LanguageInlineEgg):
    def __init__(self,outer, left, condition, right):
        LanguageInlineEgg.__init__(self,outer)
        self.condition = condition
        if left:
            outer.addCode(outer.micro.cmp(left, right))
        self.top_label = self.label()
        self.stackFromOuter()
        self.syscallFromOuter()

    def end(self):
        self.freeStack()

        real_size = len(self)
        self.jump(self.top_label,self.micro.opositeCondition(self.condition))
        self.outer.jump(self.outer.label(len(self)),self.micro.opositeCondition(self.condition))
        self.outer.addCode(self.getCode()[:real_size])

class WhileInlineEgg(LanguageInlineEgg):
    def __init__(self,outer, left, condition, right):
        LanguageInlineEgg.__init__(self,outer)
        self.condition = condition

        self.top_label = self.label()
        self.loop = self.outer.label()
        self.outer.addCode(outer.micro.cmp(left, right))
        self.stackFromOuter()
        self.syscallFromOuter()

    def end(self):
        self.freeStack()

        real_size = len(self)
        self.jump(self.top_label,self.micro.opositeCondition(self.condition))
        self.jump(self.top_label)
        self.outer.jump(self.outer.label(len(self)),self.micro.opositeCondition(self.condition))
        self.outer.addCode(self.getCode()[:real_size])
        self.outer.jump(self.loop)

class DoInlineEgg(LanguageInlineEgg):
    def __init__(self,outer):
        LanguageInlineEgg.__init__(self,outer)

        self.loop = self.outer.label()
        self.stackFromOuter()
        self.syscallFromOuter()

    def While(self, left, condition, right):
        self.freeStack()
        self.outer.addCode(self.code)
        self.outer.addCode(self.micro.cmp(left, right))
        self.outer.jump(self.loop,condition)
