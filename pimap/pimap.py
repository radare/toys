import array, time, os, signal, sys, getpass, imaplib
import smtplib, commands

import config

user = config.user
password = config.password
host = config.host
port = config.port
email = config.email
folders = []

if user == '':
	print "User: ",
	user = sys.stdin.readline().strip()
if password == '':
	print "Password: ",
	password = getpass.getpass()
if email == '':
	email = user + '@' + host
if host == '':
	print "IMAP host: ",
	host = sys.stdin.readline().strip()
if port == '':
	print "IMAP port: ",
	port = sys.stdin.readline().strip()

M=0
def mail(serverURL=None, sender='', to='', subject='', text=''):
	"""
	Usage:
	mail('somemailserver.com', 'me@example.com', 'someone@example.com', 'test', 'This is a test')
	"""
	headers = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (sender, to, subject)
	message = headers + text
	mailServer = smtplib.SMTP(serverURL)
	mailServer.sendmail(sender, to, message)
	mailServer.quit()

def slurp(filename):
	"Slurp all the lines of a file into an array"
	try:
		f = open(filename)
	except IOError:
		print "IOError: ", sys.exc_value
		return None
	str = f.readlines()
	f.close()
	foo = ''.join(str)
	return foo

def do_mail():
	print "To: ",
	to = sys.stdin.readline().strip()
	print "Subject: ",
	subject = sys.stdin.readline().strip()
	fd = open('.mail.pimap.tmp', 'w');
	fd.write('')
	#fd.write('To: ' + to + '\n' + 'Subject: ' + subject + '\n\n\n')
	fd.close()
	os.system("vim +999 .mail.pimap.tmp")
	smtp = commands.getstatusoutput('mx ' + to)
	mail(smtp, email, to, subject, slurp('.mail.pimap.tmp'))
	# wipe? :)
	os.unlink('.mail.pimap.tmp')

# After a >0 response all messages are reset!!
# this command forces an update of the imap status
def imap_new(P, boxes, verbose):
	global M
	n = 0
	for i, box in enumerate(boxes):
		M.select(box)
		try:
			typ, recent = M.recent()
			p = int(recent[0])
			n = n + p
			if p > 0:
				print recent[0] + ' ' + box
		except:
			pass
	if n > 0:
		print n,
		print ' new messages.'
	else:
		if verbose > 0:
			print 'No new messages.'
	

def imap_list_folders(M):
	global folders
	folders = []
	typ, list = M.lsub('')
	for i, box in enumerate(list):
		foo = box.split('"."')[1].replace('"',' ').strip()
		folders.append(foo)
		print '\r' + foo

def imap_last_mails(M, folder):
	M.select(folder)
	typ, list = M.search(None, 'ALL')
	elems = list[0].split()
	for num in elems:
		if int(num) > len(elems)-10:
			typ, data = M.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT)])')
			print '\r%3d: %s' % (int(num), data[0][1].strip())

def imap_list_mails(M, folder):
	M.select(folder)
	typ, list = M.search(None, 'ALL')
	for num in list[0].split():
		typ, data = M.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT)])')
		print '\r%3d: %s' % (int(num), data[0][1].strip())

def imap_view(M, num):
	typ, data = M.fetch(num, 'RFC822')
	header = True
	msg = data[0][1].strip()
	for a in msg.split('\n'):
		print a
		if header == True:
			if a == '':
				header = False
		if header == False:
			print "%3d %s" % (i, a)
	print "ok"

def imap_cat(M, num):
	typ, data = M.fetch(num, 'RFC822')
	print '\r%3d: %s' % (int(num), data[0][1].strip())

def imap_vim(M, num):
	typ, data = M.fetch(num, 'RFC822')
	msg = data[0][1].strip()
	fd = open('.mail.pimap.tmp','w');
	fd.write(msg)
	fd.close()
	os.system("vim .mail.pimap.tmp")
	os.unlink('.mail.pimap.tmp')

def imap_help():
	print "\rls            list messages of the current folder"
	print "lsf           list folders"
	print "cd [folder]   change to another folder"
	print "new           check for new messages"
	print "mail          compose a new mail"
	print "last          show last 10 messages of the current folder"
	print "wait          wait for new messages"
	print "type [num]    types the contents of a message"
	print "cat [num]     shows the contents of a message"
	print "vim [num]     vims the contents of a message"
	print "rm [num]      removes the target message"
	print "exit          finishes the session"

def imap_exit():
	print 'byebye'
	os._exit(0)

def imap_version():
	print "pimap v0.1"

def imap_shell(M):
	folder = 'INBOX'
	while 1:
		print '\r' + folder + '> ',
		try:
			line = sys.stdin.readline().strip()
			args = line.split(' ')
			cmd = args[0].strip()
			if cmd == '?':
				imap_help()
			elif cmd == 'help':
				imap_help()
			elif 'version' == cmd:
				imap_version
			elif 'cd' == cmd:
				if len(args) > 1:
					folder = args[1]
				print folder
			elif 'wait' == cmd:
				while 1:
					imap_new(M, folders, 0)
					time.sleep(5)
			elif 'new' == cmd:
				imap_new(M, folders, 1)
			elif 'cp' == cmd:
				if len(args) > 2:
					M.append(args[2], '', '', args[1])
					print args[1] + ' => ' + args[2]
				else:
					print "cp [msg] [folder-src]"
			elif 'rename' == cmd:
				if len(args) > 2:
					M.rename(args[1], args[2])
					print args[1] + ' => ' + args[2]
				else:
					print "rename [folder-src] [folder-dst]"
			elif 'rm' == cmd:
				if len(args) > 1:
					M.store(args[1], '+FLAGS', '\\Deleted')
					M.expunge()
					print 'Message ' + args[1] + ' removed.'
				else:
					print "rm [msg-number]"
			elif 'folders' == cmd:
				imap_list_folders(M)
			elif 'lsf' == cmd:
				imap_list_folders(M)
			elif 'vim' == cmd:
				if len(args) > 1:
					imap_vim(M, args[1])
				else:
					print 'cat [number]'
			elif 'mail' == cmd:
				do_mail()
			elif 'ls' == cmd:
				imap_list_mails(M, folder) #args[1].strip())
			elif 'v' == cmd:
				if len(args) > 1:
					imap_view(M, args[1])
				else:
					print 'view [number]'
			elif 'cat' == cmd:
				if len(args) > 1:
					imap_cat(M, args[1])
				else:
					print 'cat [number]'
			elif 'last' == cmd:
				imap_last_mails(M, folder) #args[1].strip())
			elif 'quit' == cmd:
				imap_exit()
			elif 'exit' == cmd:
				imap_exit()
			elif 'q' == cmd:
				imap_exit()
#			try:
#				{
#					'?': imap_help,
#					'help': imap_help,
#					'version': imap_version,
#					'ls': imap_list_mails(M, args[1].strip()),
#					'quit': imap_exit,
#					'exit':	imap_exit
#				} [cmd](M)
#			except:
#				print "..."
		except 0:
			pass

def imap_connect(host, port, user, password):
	global M
	print "Connecting... ",
	M = imaplib.IMAP4_SSL(host, port)
	M.login(user, password)
	print "ok"
	return M

M = imap_connect(host, port, user, password)
imap_shell(M)
imap_new(M, folders,1)
imap_list_folders(M)
imap_list_mails(M,'INBOX.Important')
M.close()
M.logout()

#M.select('INBOX.Important')
#typ, data = M.list('INBOX')
#for num in data[0].split():
#    print 'BOX '+ num

#typ, data = M.status('INBOX','ALL')
#print data
#typ, recent = M.recent()
#print recent

#typ, data = M.search(None, 'ALL')
#for num in data[0].split():
#    typ, data = M.fetch(num, 'FROM')#'(RFC822)')
#    print 'Message %s\n%s\n' % (num, data[0][1])
