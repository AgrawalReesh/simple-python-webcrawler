
from pygoogle import pygoogle
import htmllib, formatter
from urlparse import urlparse
from urlparse import urljoin
#import test_timeout
import time
import robotparser
import math
import Queue as Q
import mimetypes
import urllib
import re
import sys
import os


start_time = time.time()			#record start time of execution

#take user input of keywords
keywords = raw_input("enter the search keywords: \n")
keywords_list = keywords.split(" ")	 #gives an array of search query terms
num_links = input("enter the number of pages: \n")


pages_crawled = 0					#break once num_links pages crawled
current_level  = 0					#to find distance from root

#making priority queue
q = Q.PriorityQueue()

#query google using pygoogle 
g = pygoogle(keywords)
g.pages = 1
top_results = g.get_urls()

#Making a class which has url and level member variables
#objects of this class will be added to priority queue
class UrlScore(object):
	def __init__(self, _url, _level):
		self.url = _url
		self.level = _level


visited = {"test":""}				#dictionary for previously visited links
visited_robots = {"": True}			#for visited robots.text
rp = robotparser.RobotFileParser()	#creating object of robot parser

#adding google results to PriorityQueue
#all the results have the same priority => 0
#their level is 0
for result in top_results:
	url_obj = UrlScore(result, 0)
	url_priority = 0
	tup = (url_priority, url_obj)
	q.put(tup)

page_score = 1                       #pagescore will be added each time data is encountered
file_no = 0							 #file number increments => file0.txt, file1.txt
url_inc = 0							 #this increases the serial number of the logs in the log file 
url_logs = open("{}/logs/log_main.txt".format(os.getcwd()), 'w+') #storing url logs
file_on_disk = None					 # object where f
keywords_count = 0					 # NOT USED
count_404 = 0						 # counter for number of 404s
total_size = 0						 # counter for total size of downloaded pages

#create derived class of HTMLParser
class MyHTMLParser(htmllib.HTMLParser):
	
	def __init__(self, formatter):
		htmllib.HTMLParser.__init__(self, formatter)
		self.temp_list = []			#creates temp list that will store all encountered links

	def start_a(self, attrs):
		if len(attrs)>0:
			for attr in attrs:	
				if attr[0] == 'href':
					self.temp_list.append(attr[1])

	def handle_data(self, data):
		#Everytime data part is encountered the pagescore
		#is incremented by the number of terms that matched
		#in the keyword list. This final page score can be 
		#accessed since it's a global variable. So for example,
		#www.wikipedia.com has 80 occurences of the keyword 'dog'
		#then every link that originates from this page will be 
		#stored with this page_score of 80 as priority
		global page_score
		temp_score = len(re.findall("|".join(keywords_list), data))
		if temp_score != 0:
			page_score = page_score + temp_score

	def get_temp_list(self):
		return self.temp_list

#extending class to change user-agent variable indicated by 'version'
#this class handles password-protected pages by prompting the user to
#add login credentials and hence the concerned function has been 
#overridden to 'do nothing' meaning ignore such pages.
class MyUrlOpener(urllib.FancyURLopener):
	version = "Mozilla/5.0"

	def http_error_401(self, url, fp, errcode, errmsg, headers, data=None):
		return None
  
					
#create object of the derived class of HTMLParser
format = formatter.NullFormatter()
parser = MyHTMLParser(format)

#dequeueing priority queue starts here
while q.empty() != True:


	if pages_crawled > num_links:
		break

	try:
		item = q.get()  				#dequeue element, the element returns
		q_url = item[1].url 			# (priority , object)
		q_level = item[1].level     	# object has url field and level field

		#checking if the link has been visited 
		#before using the visted dictionary
		if visited.has_key(q_url):
			continue
		#if not then add to dictionary	
		visited[q_url] = ""

		#checking if robots.txt allows by creating the main [domain]/robots.txt
		rob = "https://{}/robots.txt".format(urlparse(q_url).netloc)
		if visited_robots.has_key(rob):
			if visited_robots[rob] == False:
				continue
		else:		
			rp.set_url(rob)						#rp is robotparser object
			rp.read()							#it reads the robot.tx
			robot_flag = rp.can_fetch("*", rob)	#store appropriate flag
			visited_robots[rob] = robot_flag

		#opening url 
		print "url: {} level: {}".format(q_url.encode('utf-8'), q_level)
		link_opener = MyUrlOpener()
		file = link_opener.open(q_url)
		#file = test_timeout.gotry(link_opener, q_url)

		if file.getcode() == 404:
			count_404 = count_404 + 1

	
		#parsinf the opened url and logging its details
		#file[Number].txt => stores the file content
		#url_logs.txt => sr. no | url | level | time | size | code | score
		encoding = file.headers.getparam('content-encoding')
		if encoding == None:
			content = file.read()
			parser.feed(content)
			file_on_disk = open("{}/files/file{}.txt".format(os.getcwd(), file_no), 'w+')
			file_on_disk.write(content)
			url_logs.write("{} {} {} {} {} {} \n".format(url_inc, q_url, q_level, time.strftime("%Y-%m-%d %H:%M:%S"), sys.getsizeof(content), file.getcode(), int(1000000 - page_score) ))
			file_no = file_no + 1
			url_inc = url_inc + 1
			total_size = total_size + sys.getsizeof(content)
			file_on_disk.close()
		else: 
			content = file.read().decode(encoding)
			parser.feed(content)
			file_on_disk = open("{}/files/file{}.txt".format(os.getcwd(), file_no), 'w+')
			file_on_disk.write(content)
			url_logs.write("{} {} {} {} {} {} \n".format(url_inc, q_url,  q_level, time.strftime("%Y-%m-%d %H:%M:%S"), sys.getsizeof(content), file.getcode(), int(1000000 - page_score) ))
			file_no = file_no + 1
			url_inc = url_inc + 1
			total_size = total_size + sys.getsizeof(content)
			file_on_disk.close()

		#regex for looking at sub-directories
		sub = re.compile('/|#')
		tl =  parser.get_temp_list()
		for raw_link in tl:
			#check if the link is a subdirectory, and join
			if sub.match(raw_link) != None:
				raw_link = urljoin(q_url, raw_link)

			#guess file type	
			file_type = mimetypes.guess_type(raw_link)[0]

			#only insert in queue if filetype is None or text/html
			if file_type == None or file_type == 'text/html':

				#the score of the parent becomes priority in (priority, object)
				#object is of type UrlScore(url, level)
				# parent + 1 for the level
				final_page_score = int(1000000 - page_score)
				tup = (final_page_score, UrlScore(raw_link, q_level+1))
				q.put(tup)
		#printing page score here		
		print "score: {}".format(final_page_score)
		#making it zero since it is a global variable
		page_score = 0

		#print links_to_visit
		pages_crawled = pages_crawled + 1
		print pages_crawled

	except Exception as e:
		print e
		#print "for link" + q_url

end_time = time.time()							#calculating endtime
total_time = end_time - start_time				#calculating total time for summary
url_logs.write("************ SUMMARY *************\n")
url_logs.write("number of file downloaded: {} \n total size: {} \n total time: {} \n number of 404: {}".format(url_inc, total_size, total_time, count_404 ))
url_logs.close()								#closing log file


	



