from collections import OrderedDict, Counter, defaultdict
import pairoptions

class plotoptions(object):
	'''
	PLOTOPTIONS class definition

		Usage:
			plotoptions=plotoptions(*arg)
	'''

	def __init__(self,*arg):# {{{
		self.numberofplots = 0
		self.figurenumber  = 1
		self.list          = OrderedDict()

		self.buildlist(*arg)
		#}}}
	def __repr__(self): #{{{
		s="\n"
		s+="	numberofplots: %i\n" % self.numberofplots
		s+="	figurenumber: %i\n"  % self.figurenumber
		if self.list:
			s+="	list: (%ix%i)\n" % (len(self.list),2)
			for item in self.list.iteritems():
				#s+="	options of plot number %i\n" % item
				if   isinstance(item[1],(str,unicode)):
					s+="	field: %-10s value: '%s'\n" % (item[0],item[1])
				elif isinstance(item[1],(bool,int,long,float)):
					s+="	field: %-10s value: '%g'\n" % (item[0],item[1])
				else:
					s+="	field: %-10s value: '%s'\n" % (item[0],item[1])
		else:
			s+="	list: empty\n"
		return s
	#}}}
	def buildlist(self,*arg): #{{{
		#check length of input
		if len(arg) % 2:
			raise TypeError('Invalid parameter/value pair arguments')

		#go through args and build list (like pairoptions)
		rawoptions=pairoptions.pairoptions(*arg)
		numoptions=len(arg)/2
		rawlist=[] # cannot be a dict since they do not support duplicate keys

		for i in xrange(numoptions):
			if isinstance(arg[2*i],(str,unicode)):
				rawlist.append([arg[2*i],arg[2*i+1]])
			else:
				#option is not a string, ignore it
				print "WARNING: option number %d is not a string and will be ignored." % (i+1)

		#get figure number 
		self.figurenumber=rawoptions.getfieldvalue('figure',1)
		rawoptions.removefield('figure',0)

		#get number of subplots 
		numberofplots=Counter(x for sublist in rawlist for x in sublist if isinstance(x,(str,unicode)))['data']
		self.numberofplots=numberofplots

		#figure out whether alloptions flag is on
		if rawoptions.getfieldvalue('alloptions','off') is 'on':
			allflag=1
		else:
			allflag=0

		#initialize self.list (will need a list of dict's (or nested dict) for numberofplots>1)
		#self.list=defaultdict(dict)
		for i in xrange(numberofplots):
			self.list[i]=pairoptions.pairoptions()

		#process plot options
		for i in xrange(len(rawlist)):

			#if alloptions flag is on, apply to all plots
			if (allflag and 'data' not in rawlist[i][0] and '#' not in rawlist[i][0]):
				
				for j in xrange(numberofplots):
					self.list[j].addfield(rawlist[i][0],rawlist[i][1])

			elif '#' in rawlist[i][0]:

				#get subplots associated
				string=rawlist[i][0].split('#')
				plotnums=string[-1].split(',')
				field=string[0]

				#loop over plotnums
				for k in xrange(len(plotnums)):
					plotnum=plotnums[k]

					#Empty
					if not plotnum: continue

					# '#all'
					elif 'all' in plotnum:
						for j in xrange(numberofplots):
							self.list[j].addfield(field,rawlist[i][1])

					# '#i-j'
					elif '-' in plotnum:
						nums=plotnum.split('-')
						if len(nums)!=2: continue
						if False in [x.isdigit() for x in nums]:
							raise ValueError('error: in option i-j both i and j must be integers')
						for j in xrange(int(nums[0])-1,int(nums[1])):
							self.list[j].addfield(field,rawlist[i][1])	

					# Deal with #i
					else:
						#assign to subplot
						if int(plotnum)>numberofplots:
							raise ValueError('error: %s cannot be assigned %d which exceeds the number of subplots' % (field,plotnum))
						self.list[int(plotnum)-1].addfield(field,rawlist[i][1])
			else:
				
				#go through all subplots and assign key-value pairs
				j=0
				while j <= numberofplots-1:
					if not self.list[j].exist(rawlist[i][0]):
						self.list[j].addfield(rawlist[i][0],rawlist[i][1])
						break
					else:
						j=j+1
				if j+1>numberofplots:
					print "WARNING: too many instances of '%s' in options" % rawlist[i][0]
	#}}}
