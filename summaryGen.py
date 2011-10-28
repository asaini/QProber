import os,sys,subprocess
import re
import urllib
import json

from collections import defaultdict


def returnTop4URLs(query):
	"""Method which queries Bing with string 'query' and returns the total number of hits for that particular query """

	urlStringPart1  = "http://api.bing.net/json.aspx?AppId="
        AppId           = "9AAF5A7F25051B931FC1E0B32D74A6DF42727EE3"
        urlStringPart2  = "&Version=2.2&Market=en-US&Query=" + query + "&Sources=web&Web.Count=20&JsonType=raw"
	URL		= urlStringPart1 + AppId + urlStringPart2
	response	= urllib.urlopen(URL)
	receive		= json.load(response)
	
	numResults	= receive['SearchResponse']['Web']['Total']

	urlList		= list()
	i = 0

	#import code;code.interact(local = locals())	
	while((i < 20) and (i < numResults) and (len(urlList) < 4)):
		url = receive['SearchResponse']['Web']['Results'][i]['Url']
		if url.endswith('.pdf') or url.endswith('.ppt'):
			i = i + 1
			continue
		urlList.append(url)
		i = i + 1
	
	return urlList
		

def summarizeDB(directoryTraversalList, dbURL):
	"""Method which generates content summary of a database based on a small 'sample' of the pages or documents in the database"""
	
	for directory in directoryTraversalList:

		try:
			f1 = open(directory + '.txt','r')
		except Exception:
			print '\nNo directory-file by the name of ' + directory + ' exists, program will exit\n'
			sys.exit('System will terminate')
		
		rootLines = f1.readlines()
		masterDict = defaultdict(int)

		for i,line in enumerate(rootLines):
			keyTerms = re.split('\W+',line.rstrip())
			keyWords = '+'.join(keyTerms[1:])
			urlList  = returnTop4URLs(dbURL + keyWords)
			print 'Fetching webpages with URLs corresponding to keywords: ' + ' '.join(keyTerms[1:]) + '\n' 
			#import code; code.interact(local = locals())
			
			for url in urlList:
				print '\tFetching URL :\t' + url + '\n' 
				fetchProcess 	= subprocess.Popen(['lynx','-dump',url],stdout = subprocess.PIPE)
				textData,err 	= fetchProcess.communicate()
				refPoint 	= textData.find('\nReferences\n')
				preRefData 	= textData[:refPoint].lower()

				wordList	= re.findall('[a-zA-Z]+',preRefData)

				for word in wordList:
					masterDict[word] += 1

		#print sorted(masterDict.items())

		f2 = open('sample-' + directory + '.txt','w')
		for word,count in sorted(masterDict.items()):
			f2.write(word + '  ' + str(count) + '\n')

		f1.close()
		f2.close()

if __name__=="__main__":
	
        dbURL    = raw_input("\nPlease enter the database URL\n")
        dbURL    = re.sub('http:\\\\www\.','',dbURL)
        dbURL    = 'site:' + dbURL + ' '

	summarizeDB(['testSummary'],dbURL)

