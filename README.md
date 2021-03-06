# UserLine

This tool automates the process of creating logon relations from MS Windows Security Events by showing a graphical realtion among users domains, source and destination logons as well as session duration.

![](https://raw.githubusercontent.com/thiber-org/userline/master/img/graph.png)

It has three output modes:
  1. Standard output
  2. CSV file
  3. Neo4J graph

## Install dependencies

	sudo pip3 install -U -r requirements.txt
  
## Command line

	$ ./userline.py -h
	
	 /\ /\  ___  ___ _ __ / /(_)_ __   ___ 
	/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \
	\ \_/ /\__ \  __/ | / /__| | | | |  __/
	 \___/ |___/\___|_| \____/_|_| |_|\___|  v0.2.1b
	
	Author: Chema Garcia (aka sch3m4)
	        @sch3m4
	        https://github.com/thiber-org/userline
	
	usage: userline.py [-h] [-H ESHOSTS] [-S POOL_SIZE] -i INDEX
	                   (-L | -E | -l | -w DATE) [-c PATH] [-n BOLT] [-f] [-s]
	                   [-t MIN_DATE] [-T MAX_DATE] [-p PATTERN] [-I] [-m DATETIME]
	                   [-v]
	
	optional arguments:
	  -h, --help            show this help message and exit
	
	Required arguments:
	  -H ESHOSTS, --eshosts ESHOSTS
	                        Single or comma separated list of ElasticSearch hosts
	                        to query (default: localhost)
	  -S POOL_SIZE, --pool-size POOL_SIZE
	                        Connection pool size (default: 5)
	  -i INDEX, --index INDEX
	                        Index name/pattern
	
	Actions:
	  -L, --last-shutdown   Gets last shutdown data
	  -E, --last-event      Gets last event data
	  -l, --logons          Shows user logon activity
	  -w DATE, --who-was-at DATE
	                        Shows logged in users at a given time
	
	Output:
	  -c PATH, --csv-output PATH
	                        CSV Output file
	  -n BOLT, --neo4j BOLT
	                        Neo4j bolt with auth (format:
	                        bolt://user:pass@host:port)
	
	Neo4J options:
	  -f, --neo4j-full-info
	                        Saves full logon/logoff info in Neo4j relations
	  -s, --unique-logon-rels
	                        Sets unique logon relations
	
	Optional filtering arguments:
	  -t MIN_DATE, --min-date MIN_DATE
	                        Searches since specified date (default: 2016-04-17)
	  -T MAX_DATE, --max-date MAX_DATE
	                        Searches up to specified date (default: 2017-04-17)
	  -p PATTERN, --pattern PATTERN
	                        Includes pattern in search
	  -I, --include-local   Includes local services logons (default: Excluded)
	  -m DATETIME, --mark-if-logged-at DATETIME
	                        Marks logged in users at a given time
	  -v, --verbose         Enables verbose mode


## EVTx Analisys

Analyze EVTx files with [plaso](https://github.com/log2timeline/plaso)

	$ docker run -v /mnt/IR/1329585/:/data log2timeline/plaso log2timeline --hashers md5,sha256 -z Europe/Madrid /data/processed/events/windows/security/sec-evtx.plaso /data/evidences/events/windows/security/


## Indexing

Note: psort elastic output is really slow, for better performance upload the .plaso file to [TimeSketch](https://github.com/google/timesketch)

If your image does not already support it, enable elastic output psort module

	$ docker run -ti --entry-point=/bin/bash -v /mnt/IR/1329585/:/data log2timeline/plaso
	root@@d3a8d0e1f0ac:/home/plaso# apt-get update && apt-get install -y python-pip && pip install pyelasticsearch

Process the events and store them into elasticsearch

	root@@d3a8d0e1f0ac:/home/plaso# psort.py -o elastic --server 172.21.0.2 --port 9200 --doc_type plaso --index_name ir-1329585-events-security-windows /data/processed/events/windows/security/sec-evtx.plaso


## Using the tool

Getting the last shutdown event:

	$ ./userline.py -i ir-1329585-events-security-windows --last-shutdown
	
	 /\ /\  ___  ___ _ __ / /(_)_ __   ___ 
	/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \
	\ \_/ /\__ \  __/ | / /__| | | | |  __/
	 \___/ |___/\___|_| \____/_|_| |_|\___|  v0.2.1b
	
	Author: Chema Garcia (aka sch3m4)
	        @sch3m4
	        https://github.com/thiber-org/userline
	
	INFO - Last shutdown:
	INFO - 	- Datetime: 2016-07-12 18:56:33+00:00
	INFO - 	- Computer: ws01.evil.corp
	INFO - 	- Uptime:   124 days, 23:24:03

Getting the last event:

	$ ./userline.py -i ir-1329585-events-security-windows --last-event
	
	 /\ /\  ___  ___ _ __ / /(_)_ __   ___ 
	/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \
	\ \_/ /\__ \  __/ | / /__| | | | |  __/
	 \___/ |___/\___|_| \____/_|_| |_|\___|  v0.2.1b
	
	Author: Chema Garcia (aka sch3m4)
	        @sch3m4
	        https://github.com/thiber-org/userline
	
	INFO - Last event:
	
	INFO - {
	    "computer": "ws01.evil.corp",
	    "datetime": "2017-02-14 05:04:36+00:00",
	    "description": "",
	    "domain": "",
	    "eventid": 6006,
	    "id": "cbc2794961fa5ced4366ef52673479faf4df5a53ca66280263526bbe0bee13af",
	    "ipaddress": "",
	    "logonid": "",
	    "logonsrcid": "",
	    "raw": "<Event xmlns=\"http://schemas.microsoft.com/win/2004/08/events/event\">\n  <System>\n    <Provider Name=\"EventLog\"/>\n    <EventID Qualifiers=\"32768\">6006</EventID>\n    <Level>4</Level>\n    <Task>0</Task>\n    <Keywords>0x0080000000000000</Keywords>\n    <TimeCreated SystemTime=\"2017-02-14T05:44:36.000000000Z\"/>\n    <EventRecordID>784</EventRecordID>\n    <Channel>System</Channel>\n    <Computer>ws01.evil.corp</Computer>\n    <Security/>\n  </System>\n  <EventData>\n    <Binary>0100000000000000</Binary>\n  </EventData>\n</Event>\n",
	    "sourceid": "AOsBX5IrkRtSdYVCbxr4",
	    "srcid": "",
	    "timestamp": 1492458753000,
	    "type": "",
	    "username": ""
	}

Getting logon relations between two dates into a CSV file:

	$ ./userline.py -l -i ir-1329585-events-security-windows -t 2016-11-20T11:00:00 -T 2016-11-21T11:00:00 -c output.csv
	
	 /\ /\  ___  ___ _ __ / /(_)_ __   ___ 
	/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \
	\ \_/ /\__ \  __/ | / /__| | | | |  __/
	 \___/ |___/\___|_| \____/_|_| |_|\___|  v0.2.1b
	
	Author: Chema Garcia (aka sch3m4)
	        @sch3m4
	        https://github.com/thiber-org/userline
	
	INFO - Building query
	INFO - Processing events
	[====================] 100.0% Elapsed: 0m 02s ETA: 0m00s
	INFO - 44 Logons processed in 0:00:02.051880

Getting logon relations into Neo4J graph:

	$ docker run -d -p 7474:7474 -p 7687:7687 -v $HOME/neo4j/data:/data neo4j
	$ ./userline.py -l -i ir-1329585-events-security-windows -t 2016-11-20T11:00:00 -T 2016-11-21T11:00:00 -n "bolt://user:pass@172.17.0.2:7687/"
	
	 /\ /\  ___  ___ _ __ / /(_)_ __   ___ 
	/ / \ \/ __|/ _ \ '__/ / | | '_ \ / _ \
	\ \_/ /\__ \  __/ | / /__| | | | |  __/
	 \___/ |___/\___|_| \____/_|_| |_|\___|  v0.2.1b
	
	Author: Chema Garcia (aka sch3m4)
	        @sch3m4
	        https://github.com/thiber-org/userline
	
	INFO - Building query
	INFO - Processing events
	[====================] 100.0% Elapsed: 0m 02s ETA: 0m00s
	INFO - 44 Logons processed in 0:00:02.051880

Query the results using Neo4J CQL
![](https://raw.githubusercontent.com/thiber-org/userline/master/img/result.png)


## Querying Neo4J data

	MATCH(n) RETURN(n)


## Removing Neo4J data

	MATCH(n)-[r]-(m) DELETE n,r,m
	MATCH(n) DELETE n


