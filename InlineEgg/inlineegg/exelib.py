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
# $Id: exelib.py,v 1.3 2004/06/10 17:19:23 gera Exp $

import struct
import sys

LITTLE_ENDIAN = '<'
BIG_ENDIAN    = '>'

ELFCLASSNONE    = 0         # Invalid class
ELFCLASS32      = 1         # 32-bit objects
ELFCLASS64      = 2         # 64-bit objects

ELFDATANONE     = 0         # Invalid data encoding
ELFDATA2LSB     = 1         # See below
ELFDATA2MSB     = 2         # See below

ET_NONE         = 0         # No file type
ET_REL          = 1         # Relocatable file
ET_EXEC         = 2         # Executable file
ET_DYN          = 3         # Shared object file
ET_CORE         = 4         # Core file
ET_LOPROC       = 0xff00    # Processor-specific
ET_HIPROC       = 0xffff    # Processor-specific

EM_NONE         = 0         # No machine
EM_M32          = 1         # AT&T WE 32100
EM_SPARC        = 2         # SPARC
EM_386          = 3         # Intel 80386
EM_68K          = 4         # Motorola 68000
EM_88K          = 5         # Motorola 88000
EM_860          = 7         # Intel 80860
EM_MIPS         = 8         # MIPS RS3000

EV_NONE         = 0         # Invalid version
EV_CURRENT      = 1         # Current version

ELFOSABI_SYSV           = 0       # UNIX System V ABI
ELFOSABI_NONE           = ELFOSABI_SYSV   # symbol used in old spec
ELFOSABI_HPUX           = 1       # HP-UX operating system
ELFOSABI_NETBSD         = 2       # NetBSD
ELFOSABI_LINUX          = 3       # GNU/Linux
ELFOSABI_HURD           = 4       # GNU/Hurd
ELFOSABI_86OPEN         = 5       # 86Open common IA32 ABI
ELFOSABI_SOLARIS        = 6       # Solaris
ELFOSABI_MONTEREY       = 7       # Monterey
ELFOSABI_IRIX           = 8       # IRIX
ELFOSABI_FREEBSD        = 9       # FreeBSD 
ELFOSABI_TRU64          = 10      # TRU64 UNIX 
ELFOSABI_MODESTO        = 11      # Novell Modesto
ELFOSABI_OPENBSD        = 12      # OpenBSD
ELFOSABI_ARM            = 97      # ARM
ELFOSABI_STANDALONE     = 255     # Standalone (embedded) application

def align(n,a):
    return ((n-1) & -a) + a

class Elf32Program:
    ARCH_SPARC = 2
    ARCH_I386  = 3

    def __init__(self, os = ELFOSABI_SYSV):
        self.header         = Elf32Header(os)
        self.sectionsTable  = []
        self.programTable   = []

    def bytes(self):
        if   self.arch == self.ARCH_I386:
            self.header.e_machine = EM_386
            self.header.ei_data   = ELFDATA2LSB
            for i in self.sectionsTable+self.programTable:
                i.endianess = LITTLE_ENDIAN
        elif self.arch == self.ARCH_SPARC:
            self.header.e_machine = EM_SPARC
            self.header.ei_data   = ELFDATA2MSB
            for i in self.sectionsTable+self.programTable:
                i.endianness = BIG_ENDIAN
        else:
            raise 'Unsupported architecture'

        dataStart = self.totalHeaderLength()
        data = ''

        answer = self.header.bytes()
        for i in self.sectionsTable+self.programTable:
#            i.setOffset(dataStart)
            answer    += i.bytes()
            data      += i.data
            dataStart += len(i.data)
            
        return answer+data

    def totalHeaderLength(self):
        self.header.e_ehsize = self.header.size()

        if self.sectionsTable:
            self.header.e_shoff = self.header.e_ehsize
            self.header.e_shnum = len(self.sectionsTable)
            self.header.e_shentsize = self.sectionsTable[0].size()
        else:
            self.header.e_shoff = 0
            self.header.e_shnum = 0
            self.header.e_shentsize = 0

        self.header.e_phnum = len(self.programTable)
        if self.programTable:
            if self.header.e_shoff:
                self.header.e_phoff = self.header.e_shoff + self.header.e_shnum*self.header.e_shentsize
            else:
                self.header.e_phoff = self.header.e_ehsize
            self.header.e_phentsize = self.programTable[0].size()
        else:
            self.header.e_phoff = 0
            self.header.e_phentsize = 0

        return self.header.e_ehsize+self.header.e_shnum*self.header.e_shentsize+self.header.e_phnum*self.header.e_phentsize

    def addSectionEntry(self,section):
        self.sectionsTable.append(section)

    def addProgramEntry(self,programEntry):
        self.programTable.append(programEntry)

    def addCode(self,code):
        p = Elf32ProgramHeader()
        self.addProgramEntry(p)

        p.setData(code)
        p.p_type  = p.PT_LOAD
        if self.arch == self.ARCH_I386:
            p.p_vaddr = 0x8048000
            p.p_align = 0x1000
        if self.arch == self.ARCH_SPARC:
            p.p_vaddr = 0x10000
            p.p_align = 0x10000            
        p.p_paddr = p.p_vaddr
        p.p_flags = p.PF_R | p.PF_W | p.PF_X
        p.p_filesz += self.totalHeaderLength()
        
        self.header.e_entry = p.p_vaddr+self.totalHeaderLength()
        
        # s = Elf32SectionHeader()
        # s.sh_type      = s.SHT_PROGBITS
        # s.sh_flags     = s.SHF_WRITE | s.SHF_ALLOC | s.SHF_EXECINSTR
        # s.sh_addr      = p.p_vaddr
        # s.sh_size      = len(code)
        # s.sh_addralign = 16
        # self.addSectionEntry(s)

    def setArch(self,arch):
        self.arch = arch

class Elf32Header:

    def __init__(self,ei_osabi):
        self.e_ident    = '\x7fELF%c%c%c%c\x00\x00\x00\x00\x00\x00\x00\x00'
            # ei_class is one of (0:ELFCLASSNONE, 1:ELFCLASS32, 2:ELFCLASS64)
        self.ei_class   = ELFCLASS32
            # ei_data is one of (0:ELFDATANONE, 1:ELFDATA2LSB, 2:ELFDATA2MSB)
        self.ei_data    = ELFDATA2LSB
        self.ei_version = EV_CURRENT
            # ei_osabi is one of (ELFOSABI_SYSV, ELFOSABI_HPUX, ELFOSABI_FREEBSD, etc)
        self.ei_osabi   = ei_osabi

        self.e_type     = ET_EXEC           # Object file type
        self.e_machine  = EM_386            # Architecture
        self.e_version  = EV_CURRENT        # Object file version
        self.e_entry    = 0                 # Entry point (virtual address)
        self.e_phoff    = 0                 # Program Header file offset
        self.e_shoff    = 0                 # Section Header file offset
        self.e_flags    = 0                 # Machine specific flags
        self.e_ehsize   = 0                 # ELF's header size
        self.e_phentsize= 0                 # size of each program entry
        self.e_phnum    = 0                 # program headers count
        self.e_shentsize= 0                 # size of each section entry
        self.e_shnum    = 0                 # section headers count
        self.e_shstrndx = 0                 # index of string table section

    def ident(self):
        return self.e_ident % (self.ei_class % 255, self.ei_data % 255, self.ei_version % 255, self.ei_osabi % 255)

    def bytes(self):
        answer =  self.ident()
        if self.ei_data == ELFDATA2LSB:
            format = '<'
        else:
            format = '>'
        format += 'hhlllllhhhhhh'
        answer += struct.pack(format,
                              self.e_type,
                              self.e_machine,
                              self.e_version,
                              self.e_entry,
                              self.e_phoff,
                              self.e_shoff,
                              self.e_flags,
                              self.e_ehsize,
                              self.e_phentsize,
                              self.e_phnum,
                              self.e_shentsize,
                              self.e_shnum,
                              self.e_shstrndx)
        return answer

    def size(self):
        return len(self.bytes())
    
class Elf32SectionHeader:
    SHN_UNDEF       = 0         # undefined section
    SHN_LORESERVE   = 0xff00    # Lower bound for reserver indexes
    SHN_LOPROC      = 0xff00    # Range reserver for processor specific
    SHN_HIPROC      = 0xff1f    # 
    SHN_ABS         = 0xfff1    # Absolute values
    SHN_COMMON      = 0xfff2    # Common symbols
    SHN_HIRESERVE   = 0xffff    # upper bound for reserved symbols

    SHT_NULL        = 0
    SHT_PROGBITS    = 1
    SHT_SYMTAB      = 2
    SHT_STRTAB	    = 3
    SHT_RELA	    = 4
    SHT_HASH	    = 5
    SHT_DYNAMIC     = 6
    SHT_NOTE	    = 7
    SHT_NOBITS	    = 8
    SHT_REL	    = 9
    SHT_SHLIB       = 10
    SHT_DYNSYM      = 11
    SHT_LOPROC      = 0x70000000
    SHT_HIPROC      = 0x7fffffff
    SHT_LOUSER      = 0x80000000
    SHT_HIUSER      = 0xffffffff

    SHF_WRITE       = 0x1
    SHF_ALLOC       = 0x2
    SHF_EXECINSTR   = 0x4
    SHF_MASKPROC    = 0xf0000000

    def __init__(self):
        self.endianness     = LITTLE_ENDIAN
        
        self.sh_name        = 0         # Section name (index into string section)
        self.sh_type        = 0         # section type
        self.sh_flags       = 0         # Section flags
        self.sh_addr        = 0         # Address in memory
        self.sh_offset      = 0         # Offset of data in file
        self.sh_size        = 0         # Size of section
        self.sh_link        = 0         # Table index link
        self.sh_info        = 0         # Extra info
        self.sh_addralign   = 0         # Alignment
        self.sh_entsize     = 0         # Entry size

        self.data = ''

    def text():
        answer = Elf32SectionHeader()
        answer.sh_type      = self.SHT_PROTBITS
        answer.sh_addralign = 16
        answer.sh_flags     = self.SHF_EXECINSTR | self.SHF_ALLOC

    def bytes(self):
        format = self.endianness+'llllllllll'
        return struct.pack(format,
                        self.sh_name,
                        self.sh_type,
                        self.sh_flags,
                        self.sh_addr,
                        self.sh_offset,
                        self.sh_size,
                        self.sh_link,
                        self.sh_info,
                        self.sh_addralign,
                        self.sh_entsize)

    def setOffset(self,offset):
        self.sh_offset = offset

    def size(self):
        return len(self.bytes())
        
class Elf32ProgramHeader:
    PT_NULL     = 0             # nothing, other fields ignored
    PT_LOAD     = 1             # this segment is to be loaded
    PT_DYNAMIC  = 2             # dynamic linking info
    PT_INTERP   = 3             # ASCIIZ of program interpreter
    PT_NOTE     = 4             # Extra information
    PT_SHLIB    = 5             # Unspecified format, incompatible with ABI
    PT_PHDR     = 6             # Program Table Header
    PT_LOPROC   = 0x70000000    # Processor specific 
    PT_HIPROC   = 0x7fffffff    #

    PF_R        = 1             # readable
    PF_W        = 2             # writable
    PF_X        = 4             # executable
    def __init__(self):
        self.endianness = LITTLE_ENDIAN
        self.p_type     = 0
        self.p_offset   = 0
        self.p_vaddr    = 0
        self.p_paddr    = 0
        self.p_filesz   = 0
        self.p_memsz    = 0
        self.p_flags    = 0
        self.p_align    = 0

        self.data = ''

    def bytes(self):
        self.p_memsz = align(self.p_filesz,self.p_align)

        format = self.endianness+'llllllll'
        return struct.pack(format,
                           self.p_type,
                           self.p_offset,
                           self.p_vaddr,
                           self.p_paddr,
                           self.p_filesz,
                           self.p_memsz,
                           self.p_flags,
                           self.p_align)

    def setData(self,data):
        self.data    = data
        self.p_filesz  = len(self.data)

    def setOffset(self,offset):
        self.p_offset = offset
        
    def size(self):
        return len(self.bytes())

class AOutProgram:
    """ this class knows how to write an a.out file
    information taken from OpenBSD:/usr/include/sys/exec_aout.h """

    # a_magic
    OMAGIC          = 0407    # old impure format
    NMAGIC          = 0410    # read-only text
    ZMAGIC          = 0413    # demand load format
    QMAGIC          = 0314    # "compact" demand load format; deprecated

    # a_mid
    MID_ZERO        = 0       # unknown - implementation dependent
    MID_SUN010      = 1       # sun 68010/68020 binary
    MID_SUN020      = 2       # sun 68020-only binary
    MID_PC386       = 100     # 386 PC binary. (so quoth BFD)
    MID_ROMPAOS     = 104     # old IBM RT
    MID_I386        = 134     # i386 BSD binary
    MID_M68K        = 135     # m68k BSD binary with 8K page sizes
    MID_M68K4K      = 136     # DO NOT USE: m68k BSD binary with 4K page sizes
    MID_NS32532     = 137     # ns32532
    MID_SPARC       = 138     # sparc 
    MID_PMAX        = 139     # pmax
    MID_VAX1K       = 140     # vax 1k page size
    MID_ALPHA       = 141     # Alpha BSD binary
    MID_MIPS        = 142     # big-endian MIPS
    MID_ARM6        = 143     # ARM6
    MID_POWERPC     = 149     # big-endian PowerPC
    MID_VAX         = 150     # vax
    MID_SPARC64     = 151     # LP64 sparc
    MID_M88K        = 153     # m88k BSD binary
    MID_HP200       = 200     # hp200 (68010) BSD binary
    MID_HP300       = 300     # hp300 (68020+68881) BSD binary
    MID_HPUX        = 0x20C   # hp200/300 HP-UX binary
    MID_HPUX800     = 0x20B   # hp800 HP-UX binary

    # a_flags
    EX_TRADITIONAL  = 0x00    # traditional executable or object file
    EX_DYNAMIC      = 0x20    # object file contains PIC code (set by `as -k')
    EX_PIC          = 0x10    # dynamic executable
    EX_DPMASK       = 0x30    # Mask


    #########

    ARCH_I386       = MID_I386

    def __init__(self):
        self.text      = ''
        self.data      = ''
        self.textreloc = ''
        self.datareloc = ''
        self.syms      = ''
        self.strings   = ''

            # a_midmag is htonl(flags<<26|mid<<16|magic)
        self.a_magic  = self.OMAGIC
        self.a_mid    = self.MID_I386
        self.a_flags  = self.EX_TRADITIONAL

        self.a_text   = 0      # text segment size
        self.a_data   = 0      # initialized data size
        self.a_bss    = 0      # uninitialized data size
        self.a_syms   = 0      # symbol table size
        self.a_entry  = 0x1000 # entry point (BASE + sizeof header)
        self.a_trsize = 0      # text relocation size
        self.a_drsize = 0      # data relocation size

    def setCode(self,bytes):
#        bytes += '\000'*(0x20-(len(bytes)%0x20)-0x20)
        self.text = bytes
        self.a_text = len(bytes)

    def setData(self,bytes):
        self.data = bytes
        self.a_data = len(bytes)

    def setSyms(self,bytes):
        self.syms = data
        self.a_syms = len(bytes)

    def setTextReloc(self,bytes):
        self.textreloc = data
        self.a_trsize = len(bytes)

    def setDataReloc(self,bytes):
        self.datareloc = data
        self.a_drsize = len(bytes)

    def addCode(self,bytes):
        self.setCode(self.text+bytes)

    def setArch(self,arch):
        self.a_mid = arch

    def arch(self):
        return self.a_mid

    def bytes(self):
        if (self.arch() in (    # big enadian archs
            self.MID_SUN010,
            self.MID_SUN020,
            self.MID_M68K,
            self.MID_M68K4K,
            self.MID_SPARC,
            self.MID_ALPHA,
            self.MID_MIPS,
            self.MID_ARM6,
            self.MID_POWERPC,
            self.MID_SPARC64,
            self.MID_M88K,
            self.MID_HP200,
            self.MID_HP300,
            self.MID_HPUX,
            self.MID_HPUX800)):
            endianness = '>'

        elif (self.arch() in (      # little endian archs 
            self.MID_PC386,
            self.MID_I386,
            self.MID_VAX1K,
            self.MID_VAX,
            self.MID_PMAX,
            self.MID_NS32532)):
            endianness = '<'

        else:       # if (self.arch() in (      # unknown archs, sorry
                    #   self.MID_ZERO,
                    #   self.MID_ROMPAOS)):
            raise "Unknown endianness"
              
        if self.a_magic == self.ZMAGIC:
            self.a_text  += 0x20     # (header size loaded as text only in ZMAGIC)
            self.a_entry += 0x20
        # a_midmag is htonl(flags<<26|mid<<16|magic)
        migmag = struct.pack('!L',0L+self.a_flags << 26 | self.a_mid << 16 | self.a_magic)
        answer = struct.pack(endianness+'lllllll',
                             self.a_text,
                             self.a_data,
                             self.a_bss,
                             self.a_syms,
                             self.a_entry,
                             self.a_trsize,
                             self.a_drsize)
        strings = struct.pack(endianness+'l',len(self.strings)+4)+self.strings
        return migmag+answer+self.text+self.data+self.textreloc+self.datareloc+self.syms+strings

#MZ Header Format
#typedef struct _IMAGE_DOS_HEADER {      // DOS .EXE header
#    WORD   e_magic;                     // Magic number
#    WORD   e_cblp;                      // Bytes on last page of file
#    WORD   e_cp;                        // Pages in file
#    WORD   e_crlc;                      // Relocations
#    WORD   e_cparhdr;                   // Size of header in paragraphs
#    WORD   e_minalloc;                  // Minimum extra paragraphs needed
#    WORD   e_maxalloc;                  // Maximum extra paragraphs needed
#    WORD   e_ss;                        // Initial (relative) SS value
#    WORD   e_sp;                        // Initial SP value
#    WORD   e_csum;                      // Checksum
#    WORD   e_ip;                        // Initial IP value
#    WORD   e_cs;                        // Initial (relative) CS value
#    WORD   e_lfarlc;                    // File address of relocation table
#    WORD   e_ovno;                      // Overlay number
#    WORD   e_res[4];                    // Reserved words
#    WORD   e_oemid;                     // OEM identifier (for e_oeminfo)
#    WORD   e_oeminfo;                   // OEM information; e_oemid specific
#    WORD   e_res2[10];                  // Reserved words
#    LONG   e_lfanew;                    // File address of new exe header
#  } IMAGE_DOS_HEADER, *PIMAGE_DOS_HEADER;

# Regular DOS Stub
# push cs
# pop ds
# mov dx, 000e
# mov ah, 9
# int 21h
# mov ax, 4c00h
# int 21h
# db 'This program cannot be run in DOS mode'

class MZHeader:

	def __init__(self):
		self.e_magic = 'MZ'
		self.e_cblp = 0
		self.e_cp = 0
		self.e_crlc = 0
		self.e_cparhdr = 0
		self.e_minalloc = 0
		self.e_maxalloc = 0 
		self.e_ss = 0
		self.e_sp = 0                        
		self.e_csum = 0                      
		self.e_ip = 0                       
		self.e_cs = 0                        
		self.e_lfarlc = 0                    
		self.e_ovno = 0                      
		self.e_res = '\x00' * 4
		self.e_oemid = 0                     
		self.e_oeminfo = 0                   
		self.e_res2 = '\x00' * 24
		self.e_lfanew = 0L

	def bytes(self):
		return self.e_magic + struct.pack("HHHHHHHHHHHHH" , self.e_cblp, self.e_cp, self.e_crlc, self.e_cparhdr, self.e_minalloc, self.e_maxalloc, self.e_ss, self.e_sp, self.e_csum, self.e_ip, self.e_cs, self.e_lfarlc, self.e_ovno) + self.e_res + struct.pack("HH", self.e_oemid, self.e_oeminfo) + self.e_res2 + struct.pack("L", self.e_lfanew) 


# In practice, this DOS program does not actually work. But this is the smallest 'DOS EXE' program we can
# build to reach our goal that is building a small a PE Program.
class DOSEXEProgram:
	def __init__(self):
		self.MZHeader = MZHeader()
		self.code =  ''

	def bytes(self):
		if self.code == '':
			self.code = self.dosStub()

		self.MZHeader.e_cblp = 0x050
		self.MZHeader.e_cp = 2 
		self.MZHeader.e_crlc = 0x0000
		self.MZHeader.e_cparhdr = 0x04
		self.MZHeader.e_minalloc = 0x0F
		self.MZHeader.e_maxalloc = 0xFFFF
		self.MZHeader.e_ss = 0x0000 
		self.MZHeader.e_sp = 0xB8
		self.MZHeader.e_csum = 0x0000
		self.MZHeader.e_cs = 0x0000 
		self.MZHeader.e_ip = 0x0000
		self.MZHeader.e_lfarlc = 0x40
		self.MZHeader.e_ovno = 0x1A
		self.MZHeader.e_oeimd = 0xDB0
		self.MZHeader.e_oeminfo = 0
		self.MZHeader.e_lfanew = 0x100

		return self.MZHeader.bytes() + self.code + ('\x00' * (0x100-(len(self.MZHeader.bytes())) - len(self.code) ) )

	def addCode(self, aCode):
		self.code = aCode

	def dosStub(self):
		# Regular DOS Stub
		# push cs
		# pop ds
		# mov dx, 000e
		# mov ah, 9
		# int 21h
		# mov ax, 4c00h
		# int 21h
		# db 'This program cannot be run in DOS mode'
		return '\x0e\x1f\xba\x0e\x00\xb4\x09\xCD\x21\xb8\x01\x4c\xcd\x21' + 'This program cannot be run in DOS mode$'

	def smallDosStub(self):
		# mov ax, 4c00h
		# int 21h
		return '\xb8\x01\x4c\xcd\x21'

	def tinyDosStub(self):
		# int 20h
		return '\xcd\x20'
	

#typedef struct _IMAGE_FILE_HEADER {  
#WORD Machine;  
#WORD NumberOfSections;  
#DWORD TimeDateStamp;  
#DWORD PointerToSymbolTable;  
#DWORD NumberOfSymbols;  
#WORD SizeOfOptionalHeader;  
#WORD Characteristics;
#} IMAGE_FILE_HEADER, *PIMAGE_FILE_HEADER;

# Machine
IMAGE_FILE_MACHINE_UNKNOWN	=	0x0000
IMAGE_FILE_MACHINE_I386		=	0x014C
IMAGE_FILE_MACHINE_R3000	=	0x0162
IMAGE_FILE_MACHINE_R4000	=	0x0166
IMAGE_FILE_MACHINE_R10000	=	0x0168
IMAGE_FILE_MACHINE_WCEMIPSV2	=	0x0169
IMAGE_FILE_MACHINE_ALPHA	=	0x0184
IMAGE_FILE_MACHINE_POWERPC	=	0x01F0
IMAGE_FILE_MACHINE_SH3		=	0x01A2
IMAGE_FILE_MACHINE_SH3E		=	0x01A4
IMAGE_FILE_MACHINE_SH4		=	0x01A6
IMAGE_FILE_MACHINE_ARM		=	0x01C0
IMAGE_FILE_MACHINE_THUMB	=	0x01C2
IMAGE_FILE_MACHINE_IA64		=	0x0200
IMAGE_FILE_MACHINE_MIPS16	=	0x0266
IMAGE_FILE_MACHINE_MIPSFPU	=	0x0366
IMAGE_FILE_MACHINE_MIPSFPU16	=	0x0466
IMAGE_FILE_MACHINE_ALPHA64	=	0x0284
IMAGE_FILE_MACHINE_AXP64	=	IMAGE_FILE_MACHINE_ALPHA64

# Characteristics
IMAGE_FILE_RELOCS_STRIPPED	=	0x0001
IMAGE_FILE_EXECUTABLE_IMAGE	=	0x0002
IMAGE_FILE_LINE_NUMS_STRIPPED	=	0x0004
IMAGE_FILE_LOCAL_SYMS_STRIPPED	=	0x0008
IMAGE_FILE_AGGRESIVE_WS_TRIM	=	0x0010
IMAGE_FILE_LARGE_ADDRESS_AWARE	=	0x0020
IMAGE_FILE_BYTES_REVERSED_LO	=	0x0080
IMAGE_FILE_32BIT_MACHINE	=	0x0100
IMAGE_FILE_DEBUG_STRIPPED	=	0x0200
IMAGE_FILE_REMOVABLE_RUN_FROM_SWAP	=	0x0400
IMAGE_FILE_NET_RUN_FROM_SWAP	=	0x0800
IMAGE_FILE_SYSTEM		=	0x1000
IMAGE_FILE_DLL			=	0x2000
IMAGE_FILE_UP_SYSTEM_ONLY	=	0x4000
IMAGE_FILE_BYTES_REVERSED_HI	=	0x8000

class IMAGE_FILE_HEADER:
	def __init__(self):
		self.Machine = 0
		self.NumberOfSections = 0
		self.TimeDateStamp = 0
		self.PointerToSymbolTable = 0
		self.NumberOfSymbols = 0
		self.SizeOfOptionalHeader = 0
		self.Characteristics = 0

	def bytes(self):
		return struct.pack("HHLLLHH", self.Machine, self.NumberOfSections, self.TimeDateStamp, self.PointerToSymbolTable, self.NumberOfSymbols, self.SizeOfOptionalHeader, self.Characteristics)

class IMAGE_IMPORT_DESCRIPTOR:
	def __init__(self):
		self.ImageThunkDataArrayRVA  = 0
		self.TimeDateStamp = 0
		self.ForwarderChain = 0
		self.DLLNameRVA = 0
		self.FirstThunkRVA = 0

	def bytes(self):
		return struct.pack("LLLLL", self.ImageThunkDataArraRVA, self.TimeDateStamp, self.ForwarderChain, self.DLLNameRVA, self.FirstThunkRVA)

class IMAGE_THUNK_DATA:
	def __init__(self):
		self.Hint	=	0
		self.FunctionName	=	''

	def bytes(self):
		return struct.pack('H', Hint) + self.FunctionName + '\x00'


#typedef struct _IMAGE_OPTIONAL_HEADER {  
#WORD Magic;  
#BYTE MajorLinkerVersion;  
#BYTE MinorLinkerVersion;  
#DWORD SizeOfCode;  
#DWORD SizeOfInitializedData;  
#DWORD SizeOfUninitializedData;  
#DWORD AddressOfEntryPoint;  
#DWORD BaseOfCode;  
#DWORD BaseOfData;  
#DWORD ImageBase;  
#DWORD SectionAlignment;  
#DWORD FileAlignment; 
#WORD MajorOperatingSystemVersion;  
#WORD MinorOperatingSystemVersion;  
#WORD MajorImageVersion;
#WORD MinorImageVersion;  
#WORD MajorSubsystemVersion;  
#WORD MinorSubsystemVersion;
#DWORD Win32VersionValue; 
#DWORD SizeOfImage; 
#DWORD SizeOfHeaders; 
#DWORD CheckSum;  
#WORD Subsystem;  
#WORD DllCharacteristics; 
#DWORD SizeOfStackReserve; 
#DWORD SizeOfStackCommit;
#DWORD SizeOfHeapReserve;
#DWORD SizeOfHeapCommit;
#DWORD LoaderFlags;  
#DWORD NumberOfRvaAndSizes;  
#IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];
#} IMAGE_OPTIONAL_HEADER, *PIMAGE_OPTIONAL_HEADER;


#typedef struct _IMAGE_DATA_DIRECTORY {
#  DWORD   VirtualAddress;
#  DWORD   Size;
#} IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;

class IMAGE_DATA_DIRECTORY:
	def __init__(self):
		self.VirtualAddress = 0
		self.Size = 0

	def bytes(self):
		return struct.pack("LL", self.VirtualAddress, self.Size)

class IMAGE_OPTIONAL_HEADER:
	def __init__(self):
		self.Magic = 0
		self.MajorLinkerVersion   = 0
		self.MinorLinkerVersion   = 0
		self.SizeOfCode   = 0
		self.SizeOfInitializedData  = 0
		self.SizeOfUninitializedData  = 0
		self.AddressOfEntryPoint   = 0
		self.BaseOfCode   = 0
		self.BaseOfData   = 0
		self.ImageBase   = 0
		self.SectionAlignment   = 0
		self.FileAlignment  = 0
		self.MajorOperatingSystemVersion   = 0
		self.MinorOperatingSystemVersion  = 0	
		self.MajorImageVersion = 0
		self.MinorImageVersion   = 0
		self.MajorSubsystemVersion   = 0
		self.MinorSubsystemVersion = 0
		self.Win32VersionValue  = 0
		self.SizeOfImage  = 0
		self.SizeOfHeaders = 0
		self.CheckSum   = 0
		self.Subsystem  = 0
		self.DllCharacteristics = 0
		self.SizeOfStackReserve = 0
		self.SizeOfStackCommit = 0
		self.SizeOfHeapReserve = 0
		self.SizeOfHeapCommit = 0
		self.LoaderFlags   = 0
		self.NumberOfRvaAndSizes   = 0
		self.DataDir_ExportTable = IMAGE_DATA_DIRECTORY()
		self.DataDir_ImportTable = IMAGE_DATA_DIRECTORY()
		self.DataDir_ResourceTable = IMAGE_DATA_DIRECTORY()
		self.DataDir_ExceptionTable = IMAGE_DATA_DIRECTORY()
		self.DataDir_CertificateTable = IMAGE_DATA_DIRECTORY()
		self.DataDir_RelocationTable = IMAGE_DATA_DIRECTORY()
		self.DataDir_DebugData = IMAGE_DATA_DIRECTORY()
		self.DataDir_ArchSpecificData = IMAGE_DATA_DIRECTORY()
		self.DataDir_MachineValueMIPSGP = IMAGE_DATA_DIRECTORY()
		self.DataDir_TLSTable = IMAGE_DATA_DIRECTORY()
		self.DataDir_LoadConfigTable = IMAGE_DATA_DIRECTORY()
		self.DataDir_BoundImportTable = IMAGE_DATA_DIRECTORY()
		self.DataDir_ImportAddressTable = IMAGE_DATA_DIRECTORY()
		self.DataDir_DelayImportDescriptor = IMAGE_DATA_DIRECTORY()
		self.DataDir_COMPlusRuntimeHeader = IMAGE_DATA_DIRECTORY()
		self.DataDir_Reserved = IMAGE_DATA_DIRECTORY()
		
	def bytesDataDir(self):
		return self.DataDir_ExportTable.bytes() + self.DataDir_ImportTable.bytes() + self.DataDir_ResourceTable.bytes() + self.DataDir_ExceptionTable.bytes() + self.DataDir_CertificateTable.bytes() + self.DataDir_RelocationTable.bytes() + self.DataDir_DebugData.bytes() + self.DataDir_ArchSpecificData.bytes() + self.DataDir_MachineValueMIPSGP.bytes() + self.DataDir_TLSTable.bytes() + self.DataDir_LoadConfigTable.bytes() + self.DataDir_BoundImportTable.bytes() + self.DataDir_ImportAddressTable.bytes() + self.DataDir_DelayImportDescriptor.bytes() + self.DataDir_COMPlusRuntimeHeader.bytes() + self.DataDir_Reserved.bytes()
	
	def bytes(self):
		return struct.pack("HBBLLLLLLLLLHHHHHHLLLLHHLLLLLL", self.Magic, self.MajorLinkerVersion, self.MinorLinkerVersion, self.SizeOfCode, self.SizeOfInitializedData, self.SizeOfUninitializedData, self.AddressOfEntryPoint, self.BaseOfCode, self.BaseOfData, self.ImageBase, self.SectionAlignment, self.FileAlignment, self.MajorOperatingSystemVersion, self.MinorOperatingSystemVersion, self.MajorImageVersion,  self.MinorImageVersion, self.MajorSubsystemVersion, self.MinorSubsystemVersion, self.Win32VersionValue, self.SizeOfImage , self.SizeOfHeaders,  self.CheckSum, self.Subsystem, self.DllCharacteristics,  self.SizeOfStackReserve,  self.SizeOfStackCommit, self.SizeOfHeapReserve,  self.SizeOfHeapCommit,  self.LoaderFlags ,  self.NumberOfRvaAndSizes ) + self.bytesDataDir()



#IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES];

#typedef struct _IMAGE_SECTION_HEADER {
#  BYTE    Name[IMAGE_SIZEOF_SHORT_NAME];
#  union {
#      DWORD   PhysicalAddress;
#      DWORD   VirtualSize;
#  } Misc;
#  DWORD   VirtualAddress;
#  DWORD   SizeOfRawData;
#  DWORD   PointerToRawData;
#  DWORD   PointerToRelocations;
#  DWORD   PointerToLinenumbers;
#  WORD    NumberOfRelocations;
#  WORD    NumberOfLinenumbers;
#  DWORD   Characteristics;
#} IMAGE_SECTION_HEADER, *PIMAGE_SECTION_HEADER;

IMAGE_SCN_TYPE_NO_PAD	=	0x8
IMAGE_SCN_CNT_CODE	=	0x20
IMAGE_SCN_CNT_INITIALIZED_DATA	=	0x40
IMAGE_SCN_CNT_UNINITIALIZED_DATA	= 0x80
IMAGE_SCN_LNK_OTHER	=	0x100
IMAGE_SCN_LNK_INFO	=	0x200
IMAGE_SCN_LNK_REMOVE	=	0x800
IMAGE_SCN_LNK_COMDAT	=	0x1000
IMAGE_SCN_NO_DEFER_SPEC_EXEC	=	0x4000
IMAGE_SCN_GPREL	=	0x8000
IMAGE_SCN_MEM_FARDATA	=	0x8000
IMAGE_SCN_MEM_PURGEABLE	=	0x20000
IMAGE_SCN_MEM_16BIT	=	0x20000
IMAGE_SCN_MEM_LOCKED	=	0x40000
IMAGE_SCN_MEM_PRELOAD	=	0x80000
IMAGE_SCN_ALIGN_1BYTES	=	0x100000
IMAGE_SCN_ALIGN_2BYTES	=	0x200000
IMAGE_SCN_ALIGN_4BYTES	=	0x300000
IMAGE_SCN_ALIGN_8BYTES	=	0x400000
IMAGE_SCN_ALIGN_16BYTES	=	0x500000
IMAGE_SCN_ALIGN_32BYTES	=	0x600000
IMAGE_SCN_ALIGN_64BYTES	=	0x700000
IMAGE_SCN_ALIGN_128BYTES	=	0x800000
IMAGE_SCN_ALIGN_256BYTES	=	0x900000
IMAGE_SCN_ALIGN_512BYTES	=	0xA00000
IMAGE_SCN_ALIGN_1024BYTES	=	0xB00000
IMAGE_SCN_ALIGN_2048BYTES	=	0xC00000
IMAGE_SCN_ALIGN_4096BYTES	=	0xD00000
IMAGE_SCN_ALIGN_8192BYTES	=	0xE00000
IMAGE_SCN_LNK_NRELOC_OVFL	=	0x1000000
IMAGE_SCN_MEM_DISCARDABLE	=	0x2000000
IMAGE_SCN_MEM_NOT_CACHED	=	0x4000000
IMAGE_SCN_MEM_NOT_PAGED		=	0x8000000
IMAGE_SCN_MEM_SHARED		=	0x10000000
IMAGE_SCN_MEM_EXECUTE		=	0x20000000
IMAGE_SCN_MEM_READ		=	0x40000000
IMAGE_SCN_MEM_WRITE		=	0x80000000
IMAGE_SCN_SCALE_INDEX		=	0x1

class IMAGE_SECTION_HEADER:
	def __init__(self):
		self.Name = '12345678'
		self.VirtualSize = 0 # (also PhysicalAddress)
		self.VirtualAddress = 0
		self.SizeOfRawData = 0
		self.PointerToRawData = 0
		self.PointerToRelocations = 0
		self.PointerToLinenumbers = 0
		self.NumberOfRelocations = 0
		self.NumberofLinenumbers = 0
		self.Characteristics = 0
		
	def bytes(self):
		return self.Name + struct.pack("LLLLLLHHL", self.VirtualSize, self.VirtualAddress, self.SizeOfRawData, self.PointerToRawData, self.PointerToRelocations, self.PointerToLinenumbers, self.NumberOfRelocations, self.NumberOfLinenumbers, self.Characteristics)

class IMAGE_NT_HEADERS:
	def __init__(self):
		self.Signature = "PE\x00\x00"
		self.FileHeader = IMAGE_FILE_HEADER()
		self.OptionalHeader = IMAGE_OPTIONAL_HEADER()
		return

	def bytes(self):
		return self.Signature + self.FileHeader.bytes() + self.OptionalHeader.bytes()

		
class PEHeader:
	def __init__(self):
		self.mzHeader = MZHeader()
		self.imageNTHeader = IMAGE_NT_HEADERS()	
		return
	

	def bytes(self):
		return self.imageNTHeader.bytes()

# The PE EXE file created by this class, has only one code section, with a limit of 4kb. so code has to be
# < 4kb. This can be easily modified though.
class PEProgram:
	GUI_APPLICATION         =       0x2     # WIN32 GUI Application
	CONSOLE_APPLICATION     =       0x3     # WIN32 Console application
	def __init__(self):
		self.DOSExePrg = DOSEXEProgram()
		self.PEHdr	= PEHeader()
		self.code	=	''
		self._subsystem = PEProgram.GUI_APPLICATION

	def set_subsystem(self, aSubsystemType):
		self._subsystem = aSubsystemType

	def get_subsystem(self):
		return self._subsystem

	def bytes(self):

		self.PEHdr.imageNTHeader.FileHeader.Machine = IMAGE_FILE_MACHINE_I386
		self.PEHdr.imageNTHeader.FileHeader.NumberOfSections =  3 
		self.PEHdr.imageNTHeader.FileHeader.TimeDateStamp = 0 
		self.PEHdr.imageNTHeader.FileHeader.PointerToSymbolTable = 0
		self.PEHdr.imageNTHeader.FileHeader.NumberOfSymbols = 0
		self.PEHdr.imageNTHeader.FileHeader.SizeOfOptionalHeader = 0xE0 
		self.PEHdr.imageNTHeader.FileHeader.Characteristics = 0x818e
		#self.PEHdr.imageNTHeader.FileHeader.Characteristics = IMAGE_FILE_EXECUTABLE_IMAGE | IMAGE_FILE_LINE_NUMS_STRIPPED | IMAGE_FILE_LOCAL_SYMS_STRIPPED | IMAGE_FILE_BYTES_REVERSED_LO | IMAGE_FILE_BYTES_REVERSED_HI


		self.PEHdr.imageNTHeader.OptionalHeader.Magic = 0x10B 
		self.PEHdr.imageNTHeader.OptionalHeader.MajorLinkerVersion   = 0x02
		self.PEHdr.imageNTHeader.OptionalHeader.MinorLinkerVersion   = 0x19
		self.PEHdr.imageNTHeader.OptionalHeader.SizeOfCode   = 0x200
		self.PEHdr.imageNTHeader.OptionalHeader.SizeOfInitializedData  = 0x400
		self.PEHdr.imageNTHeader.OptionalHeader.SizeOfUninitializedData  = 0
		self.PEHdr.imageNTHeader.OptionalHeader.AddressOfEntryPoint   = 0x1000 
		self.PEHdr.imageNTHeader.OptionalHeader.BaseOfCode = 0x1000
		self.PEHdr.imageNTHeader.OptionalHeader.BaseOfData   = 0x2000
		self.PEHdr.imageNTHeader.OptionalHeader.ImageBase   = 0x400000
		self.PEHdr.imageNTHeader.OptionalHeader.SectionAlignment   = 0x1000
		self.PEHdr.imageNTHeader.OptionalHeader.FileAlignment  = 0x200
		self.PEHdr.imageNTHeader.OptionalHeader.MajorOperatingSystemVersion   = 4 
		self.PEHdr.imageNTHeader.OptionalHeader.MinorOperatingSystemVersion  = 0	
		self.PEHdr.imageNTHeader.OptionalHeader.MajorImageVersion = 0
		self.PEHdr.imageNTHeader.OptionalHeader.MinorImageVersion   = 0
		self.PEHdr.imageNTHeader.OptionalHeader.MajorSubsystemVersion   = 4
		self.PEHdr.imageNTHeader.OptionalHeader.MinorSubsystemVersion = 0
		self.PEHdr.imageNTHeader.OptionalHeader.Win32VersionValue = 0
		self.PEHdr.imageNTHeader.OptionalHeader.SizeOfImage = 0x4000
		self.PEHdr.imageNTHeader.OptionalHeader.SizeOfHeaders = 0x400
		self.PEHdr.imageNTHeader.OptionalHeader.CheckSum = 0
		self.PEHdr.imageNTHeader.OptionalHeader.Subsystem = self._subsystem
		self.PEHdr.imageNTHeader.OptionalHeader.DllCharacteristics = 0
		self.PEHdr.imageNTHeader.OptionalHeader.SizeOfStackReserve = 0x100000
		self.PEHdr.imageNTHeader.OptionalHeader.SizeOfStackCommit = 0x2000
		self.PEHdr.imageNTHeader.OptionalHeader.SizeOfHeapReserve = 0x100000
		self.PEHdr.imageNTHeader.OptionalHeader.SizeOfHeapCommit = 0x1000
		self.PEHdr.imageNTHeader.OptionalHeader.LoaderFlags = 0
		self.PEHdr.imageNTHeader.OptionalHeader.NumberOfRvaAndSizes = 0x10


		self.section = IMAGE_SECTION_HEADER()
		self.section.Name = '.text\x00\x00\x00'
		self.section.VirtualSize = 0x1000 
		self.section.VirtualAddress = 0x001000
		self.section.SizeOfRawData = 0x1000
		self.section.PointerToRawData = 0x600 
		self.section.PointerToRelocations = 0
		self.section.PointerToLinenumbers = 0
		self.section.NumberOfRelocations = 0
		self.section.NumberOfLinenumbers = 0
		self.section.Characteristics = 0xE0000020   # read / write / execute so xored egg works ;]

		self.section_data = IMAGE_SECTION_HEADER()
		self.section_data.Name = 'DATA\x00\x00\x00\x00'
		self.section_data.VirtualSize = 0x1000
		self.section_data.VirtualAddress = 0x2000
		self.section_data.SizeOfRawData = 0x200
		self.section_data.PointerToRawData = 0x800 + 0xE00
		self.section_data.PointerToRelocations = 0
		self.section_data.PointerToLinenumbers = 0
		self.section_data.NumberOfRelocations = 0
		self.section_data.NumberOfLinenumbers = 0
		self.section_data.Characteristics = 0xC0000040


		self.section_itable = IMAGE_SECTION_HEADER()
		self.section_itable.Name = '.idata\x00\x00'
		self.section_itable.VirtualSize = 0x1000
		self.section_itable.VirtualAddress = 0x3000
		self.section_itable.SizeOfRawData = 0x200
		self.section_itable.PointerToRawData = 0xA00  + 0xE00
		self.section_itable.PointerToRelocations = 0
		self.section_itable.PointerToLinenumbers = 0
		self.section_itable.NumberOfRelocations = 0
		self.section_itable.NumberOfLinenumbers = 0
		self.section_itable.Characteristics = 0xC0000040

		self.PEHdr.imageNTHeader.OptionalHeader.DataDir_ImportTable.VirtualAddress = 0x3000
		self.PEHdr.imageNTHeader.OptionalHeader.DataDir_ImportTable.Size = 0x70
		#self.PEHdr.imageNTHeader.OptionalHeader.DataDir_ImportAddressTable.VirtualAddress = 0x2100
		#self.PEHdr.imageNTHeader.OptionalHeader.DataDir_ImportAddressTable.Size = 0x70
		
		if self.code == '':
			self.code = "\xCC\xCC\xCC"

		self.rdata =  "\x28\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\x30\x00\x00"
		self.rdata +=   "\x34\x30\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
		self.rdata +=   "\x00\x00\x00\x00\x00\x00\x00\x00\x4E\x30\x00\x00\x5E\x30\x00\x00"
		self.rdata +=   "\x00\x00\x00\x00\x4E\x30\x00\x00\x5E\x30\x00\x00\x00\x00\x00\x00"
		self.rdata +=   "\x4B\x45\x52\x4E\x45\x4C\x33\x32\x2E\x64\x6C\x6C\x00\x00\x00\x00"
		self.rdata +=   "\x4C\x6F\x61\x64\x4C\x69\x62\x72\x61\x72\x79\x41\x00\x00\x00\x00"
		self.rdata +=   "\x47\x65\x74\x50\x72\x6F\x63\x41\x64\x64\x72\x65\x73\x73\x00\x00"

#		return self.DOSExePrg.bytes() + self.PEHdr.bytes() + self.section.bytes() + self.section_itable.bytes() + ('\x00' * (0x600-0x248) ) + self.code + ("\x00" * (0x1000 - 0x600 - len(self.code)) ) + self.rdata + ("\x00" * (0x1000-len(self.rdata)))
		return (
			self.DOSExePrg.bytes() +
			self.PEHdr.bytes() +
			self.section.bytes() +
			self.section_data.bytes() +
			self.section_itable.bytes() +
			('\x00' * (0x600-0x270) ) +
			self.code +
			("\x00" * (0x1000 - len(self.code))) +
			("\x00" * 0x200) +
			self.rdata +
			("\x00" * (0x200-len(self.rdata))))
		
			
		
	def addCode(self, aCode):
		self.code = aCode


