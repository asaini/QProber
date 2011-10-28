import re
import json
import urllib
import os,sys,subprocess

from collections import defaultdict
import summaryGen

def pingBing(query):
	"""Method which queries Bing with string 'query' and returns the total number of hits for that particular query """

	urlStringPart1  = "http://api.bing.net/json.aspx?AppId="
        AppId           = "9AAF5A7F25051B931FC1E0B32D74A6DF42727EE3"
        urlStringPart2  = "&Version=2.2&Market=en-US&Query=" + query + "&Sources=web&JsonType=raw"
	URL		= urlStringPart1 + AppId + urlStringPart2
	response	= urllib.urlopen(URL)
	receive		= json.load(response)
	
	return receive['SearchResponse']['Web']['Total']



def analyzeDB(directoryFile,dbURL,tc,ts,path):
        
        try:
                f1       = open(directoryFile)
        except Exception:
		return '->' + os.path.splitext(directoryFile)[0]
                print repr(Exception)

        print '\nProbing for Classification as ' + os.path.splitext(directoryFile)[0] + ' Database\n'

        rootLines       = f1.readlines()
	f1.close()
	
	subcategories = set()
	for line in rootLines:
		subcategories.add(line.split()[0])
	
	subcategoriesList = list(subcategories)
	coverage 	= [0]*len(subcategories)
	specificity	= [0.0]*len(subcategories)

        for i,line in enumerate(rootLines):
                keyTerms = re.split('\W+',line.rstrip())
                keyWords = '+'.join(keyTerms[1:])
                numOfHits= pingBing(dbURL + keyWords)
                print '\nQuerying with ' + keyWords + '\n'
		
		for i,subcat in enumerate(subcategoriesList):
			if subcat in line:
				coverage[i] += numOfHits

                print '\n' + repr(subcategoriesList) + ' = ' + repr(coverage) + '\n'


        totalCoverage = float(sum(coverage))

	for i,subcat in enumerate(subcategoriesList):
		specificity[i] = float(coverage[i])/totalCoverage
 
        print '\n======================================\n'
        print 'Database Stats\n'
	print 'Coverage of ' + repr(subcategoriesList) + ' = ' + repr(coverage) + '\n'
	print 'Specificity of '+ repr(subcategoriesList) + ' = ' + repr(specificity) + '\n'
        print '\n======================================\n'

	path  = '->' + os.path.splitext(directoryFile)[0].lower() + path

	if all(spec > ts for spec in specificity) and all(cover > tc for cover in coverage):
		return analyzeDB('computers.txt',dbURL,tc,ts,path) + analyzeDB('sports.txt',dbURL,tc,ts,path) + analyzeDB('health.txt',dbURL,tc,ts,path)
	
	elif (len([spec > ts for spec in specificity]) > 0) and (len([cover > tc for cover in coverage]) > 0):
		
		for i,spec in enumerate(specificity):
			if spec > ts and coverage[i] > tc:
				return path + analyzeDB(subcategoriesList[i].lower() + '.txt',dbURL,tc,ts,'')


	return path

	
        
if __name__== "__main__":
        
	tc       = -1   #Initial Coverage Threshold
        ts       = -1   #Initial Specificity

        while tc < 1:
	        tc	 = raw_input("\nEnter the Coverage Threshold, tc > 1\n")
	        tc       = float(tc)

        while(ts < 0 or ts>1):
	        ts       = raw_input("\nEnter the Specificity Threshold, 0 < ts < 1\n")
                ts       = float(ts)

        dbURL    = raw_input("\nPlease enter the database URL\n")
        dbURL    = re.sub('http:\\\\www\.','',dbURL)
        dbURL    = 'site:' + dbURL + ' '

        analysis = analyzeDB('root.txt',dbURL,tc,ts,'')
	print analysis

	directoryList = analysis.split('->')[1:]

	summaryGen.summarizeDB(directoryList,dbURL)

