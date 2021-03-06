#
# Author: Chema Garcia (aka sch3m4)
#         @sch3m4
#         https://github.com/thiber-org/userline
#

import sys
import time
import hashlib
import collections

from dateutil import parser as dateparser
from elasticsearch_dsl import Search,Q
from elasticsearch_dsl.connections import connections

from lib import config,extract

# based on the code written by Sam Jordan http://stackoverflow.com/users/4006081/sam-jordan
def draw_progress_bar(percent, start, prevlen=0,barLen=20):
#	sys.stdout.write("\r")
	progress = ""
	for i in range(barLen):
		aux = int(barLen*percent)
		if i < aux:
			progress += "="
		elif i == aux:
			progress += ">"
		else:
			progress += " "

	elapsedTime = time.time() - start;
	estimatedRemaining = int(elapsedTime * (1.0/percent) - elapsedTime)

#	if (percent == 1.0):
#		msg = "[%s] %.1f%% Elapsed: %im %02is ETA: Done!" % (progress, percent * 100, int(elapsedTime)/60, int(elapsedTime)%60)
#	else:
	msg = "[%s] %.1f%% Elapsed: %im %02is ETA: %im%02is" % (progress, percent * 100, int(elapsedTime)/60, int(elapsedTime)%60, estimatedRemaining/60, estimatedRemaining%60)

	sys.stdout.write("\b"*(prevlen+1))
	sys.stdout.write(msg)
	curlen = len(msg)
	if curlen < prevlen:
		sys.stdout.write(" "*(prevlen-curlen))

	return curlen

def update_relations(rel,new):
	for k, v in new.items():
		if isinstance(v, collections.Mapping):
			r = update_relations(rel.get(k, {}), v)
			rel[k] = r
		else:
			rel[k] = new[k]
	return rel


def get_dsl_logoff_query():
	q = None
	for evtid in config.EVENTS_LOGOFF:
		tmp = Q("match",event_identifier=evtid)
		if q is None:
			q = tmp
		else:
			q = q | tmp

	return q

def get_dsl_logon_query():
	q = None
	for evtid in config.EVENTS_LOGON:
		tmp = Q("match",event_identifier=evtid)
		if q is None:
			q = tmp
		else:
			q = q | tmp
	return q


def get_logout_event(index,logonid,timestamp,maxtstamp):
	"""
	Look for the logoff event belonging to the given logon id or a shutdown event.
	"""
	conn = connections.get_connection()

	logoff = get_dsl_logoff_query()
	q = [ \
		Q('match',data_type='windows:evtx:record') , \
		Q('match',xml_string=logonid) , \
		logoff \
	]

	s = Search(using=conn, index=index).query(Q('bool',must=q)).filter('range',datetime={'gte':timestamp,'lte':maxtstamp}).sort('-datetime')
	res = s.execute()
	try:
		evt = res[0]
	except:
		evt = None

	if evt is None:
		q = [ Q('match',event_identifier=config.EVENT_SHUTDOWN) ]
		s = Search(using=conn, index=index).query(Q('bool',must=q)).filter('range',datetime={'gte':timestamp,'lte':maxtstamp}).sort('-datetime')
		res = s.execute()
		try:
			evt = res[0]
		except:
			evt = None

	return evt


def build_event_from_source(item):
	event = dict(config.EVENT_SKEL)

	if item is None:
		return event

	event['eventid'] = item['event_identifier']

	# get event id from datasource
	event['sourceid'] = item.meta['id']
	item = item.to_dict()

	# get logon type
	aux = extract.re_logontype.search(item['xml_string'])
	try:
		val = int(aux.group(1))
	except:
		val = ''
	event['type'] = val

	try:
		val = config.EVENT_DESCRIPTION[event['eventid']]
		if event['type'] in config.LOGON_TYPES.keys():
			val += " - {}".format(config.LOGON_TYPES[event['type']])
	except:
		val = ''

	event['description'] = val

	# get datetime
	aux = extract.re_time.search(item['xml_string'])
	try:
		val = dateparser.parse(aux.group(1))
		event['timestamp'] = int(val.timestamp() * 10**3)
	except:
		val = '0'
	event['datetime'] = str(val)

	# get logonid
	aux = extract.re_logonid.search(item['xml_string'])
	try:
		val = aux.group(1)
	except:
		val = ''
	event['logonid'] = val

	# get logonguid
	aux = extract.re_logonsrcid.search(item['xml_string'])
	try:
		val = aux.group(1)
	except:
		val = ''
	event['logonsrcid'] = val

	# get computer
	aux = extract.re_computer.search(item['xml_string'])
	try:
		val = aux.group(1)
	except:
		val = ''
	event['computer'] = val

	# get target username
	aux = extract.re_tusername.search(item['xml_string'])
	try:
		val = aux.group(1)
	except:
		val = ''
	event['username'] = val

	# get target domain
	aux = extract.re_domain.search(item['xml_string'])
	try:
		val = aux.group(1)
	except:
		val = ''
	event['domain'] = val

	try:
		if config.EVENT_ACTION[event['eventid']] == config.EVENT_ACTION_LOGON:
			# get source ip
			aux = extract.re_ipaddress.search(item['xml_string'])
			try:
				val = aux.group(1)
				if val == '-':
					val = ''
			except:
				val = ''
			event['ipaddress'] = val
	except:
		event['ipaddress'] = ''

	event['raw'] = item['xml_string']
	idval = hashlib.sha256('{}{}'.format(event['timestamp'],event['logonid']).encode('utf8'))
	event['id'] = idval.hexdigest()

	# Fix some values
#	if event['ipaddress'] == '-':
#		event['ipaddress'] = ''

	return event


def build_logon_sequence(duration,login,logout=None):
	ret = dict(config.EVENT_STRUCT)
	ret.update({ \
			# logon data
			'duration': duration, \
			'logon.type': login['type'], \
			'logon.eventid': login['eventid'], \
			'logon.description': login['description'], \
			'logon.username': login['username'], \
			'logon.computer': login['computer'], \
			'logon.domain': login['domain'], \
			'logon.srcip': login['ipaddress'], \
			'logon.datetime': login['datetime'], \
			'logon.timestamp': login['timestamp'], \
			'logon.id': login['logonid'], \
			'logon.srcid': login['logonsrcid']
		})

	if logout is not None:
		ret.update({ \
				# logoff data
				'logoff.type': logout['type'], \
				'logoff.eventid': logout['eventid'], \
				'logoff.description': logout['description'], \
				'logoff.username': logout['username'], \
				'logoff.domain': logout['domain'], \
				'logoff.computer': logout['computer'], \
				'logoff.datetime': logout['datetime'], \
				'logoff.timestamp': logout['timestamp'], \
				'logoff.id': logout['logonid']
			})

	ret.update({
			# metadata
			'logon.meta.uid': login['id'], \
			'logon.meta.id': login['sourceid']
		})

	if logout is not None:
		ret.update({ \
				'logoff.meta.uid': logout['id'], \
				'logoff.meta.id': logout['sourceid'] \
			})

	return ret


def get_last_shutdown(index,maxtstamp):
	"""
	Look for the last shutdown event
	"""

	conn = connections.get_connection()

	q = [ \
		Q('match',data_type='windows:evtx:record') , \
		Q('match',event_identifier=config.EVENT_SHUTDOWN)
	]

	s = Search(using=conn, index=index).query(Q('bool',must=q)).filter('range',datetime={'lte':maxtstamp}).sort('-datetime')

	res = s.execute()
	try:
		evt = res[0]
	except:
		evt = None

	return evt

def get_last_event(index):
	conn = connections.get_connection()
	q = [ \
		Q('match',data_type='windows:evtx:record')
	]

	s = Search(using=conn, index=index).query(Q('bool',must=q)).sort('-datetime')

	res = s.execute()
	try:
		evt = res[0]
	except:
		evt = None

	return evt
