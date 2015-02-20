#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
LinkChecker Frank Zalkow / Reger-Werkausgabe (2013-2015)

checkt in allen files im SVN sowie in den Anmerkungen auf dem Server:
		. values von Attributen (self.linkAttributes) müssen als Datei im SVN enthalten sein, sonst -> Warning
		. wenn ein Value ein File ist (self.fileExtensions), dann muss es einer der bekannten Attributen (self.linkAttributes) sein, sonst -> Warning
		. wenn minidom das File nicht öffnen kann, ist wahrscheinlich an der XML Struktur etwas falsch -> Warning
		. Links in Kommentaren werden nicht beachtet
		. links in die Edirom Edition (edition:// ...) anhand der gegebenen Editionsdatei
		
	nicht gecheckt werden im Moment:
		. Links mit Raute (#) sowohl innerhalb als auch außerhalb der Datei
		. bei Links in die Edition (edition:// ...) wird Editions-, Werk-, Source- und Part-ID gecheckt, NICHT JEDOCH BAR IDs

"""

import xml.dom.minidom as xml
import os.path
import glob
import tempfile
import shutil
import string
import itertools

from optparse import OptionParser

def try_print(mystring):
	try:
		print mystring,
	except UnicodeEncodeError:
		print mystring.encode("utf-8"),

class LinkChecker(object):

	""" Konstruktor """
	def __init__(self, svn=True, annotations=True, images=True, edition=True, case_sensitive=True):
		
		self.__homepath = os.path.expanduser("~")
		self.case_sensitive = case_sensitive
		
		self.linkAttributes = ["target", "url", "ref"]
		self.imageExtensions = [".jpg", ".jpeg"]
		self.textExtensions = [".xml"]
		
		
		# check svn directory path
		if svn:
			self.svndir = svn.replace("~", self.__homepath)
			assert os.path.isdir(self.svndir), "Didn't found the SVN directory. Assumed it should be: " + self.svndir
		else:
			self.svndir = False
		
		# check annotation directory path
		if annotations:
			self.annotationdir = annotations.replace("~", self.__homepath)
			assert os.path.isdir(self.annotationdir), "Didn't found the annotations directory. Are you logged in at reger-max? Assumed it should be: " + self.annotationdir
		else:
			self.annotationdir = False
		
		# check image directory path
		if images:
			self.imagedir = images.replace("~", self.__homepath)
			assert os.path.isdir(self.imagedir), "Didn't found the image directory. Are you logged in at reger-max? Assumed it should be: " + self.imagedir
		else:
			self.imagedir = False
			
		# check edition file path
		if edition:
			self.editionpath = edition.replace("~", self.__homepath)
			assert os.path.isfile(self.editionpath), "Didn't found the edition xml file. Assumed it should be: " + self.editionpath
		else:
			self.editionpath = False
		
		# collect files to process
		self.processfiles = []
		
		self.xmlfiles = []
		for ext in self.textExtensions:
			self.xmlfiles += glob.glob(self.svndir + "/*/*" + ext) + glob.glob(self.svndir + "/*/*/*" + ext)
			
		if svn: self.processfiles += self.xmlfiles
		
		self.annotationfiles = []
		if annotations:
			self.annotationfiles = self.annotationFiles()
			self.processfiles += self.annotationfiles
		
		self.imagefiles = []
		for ext in self.imageExtensions:
			self.imagefiles += glob.glob(self.imagedir + "/*/*" + ext) + glob.glob(self.imagedir + "/*/*/*" + ext)

		self.xmlbasefiles = map(lambda (path): unicode(os.path.basename(path), "utf-8"), self.xmlfiles)
		self.imagebasefiles = map(lambda (path): unicode(os.path.basename(path), "utf-8"), self.imagefiles)
		
		if edition: self.editionInfo = self.parseEdition()
				
		self.svn = svn
		self.annotation = annotations
		self.image = images
		self.edition = edition
		
		self.fileExtensions = self.textExtensions + self.imageExtensions
		self.verbose=True
		self.foreach=True
		self.currentFile= None
		self.wrongLinks = []
		
		if not case_sensitive:
			self.xmlbasefiles = map(string.lower, self.xmlbasefiles)
			self.imagebasefiles = map(string.lower, self.imagebasefiles)
		
		print "Going to process", len(self.processfiles), "XML-Files.\n"
		
		
	""" problem: Export from FileMaker to XML masks every "<" or ">" to "&lt;" or "&gt;" -> solution: copy the XML files into a temp dir and replace these signs """
	def annotationFiles(self):

		tempdir = tempfile.mkdtemp()
		for file in glob.glob(self.annotationdir + "/*.xml"):
			shutil.copy(file, tempdir)
		tmpAnnotations = glob.glob(tempdir + "/*.xml")
		
		for file in tmpAnnotations:
			with open (file, "r+") as f:
				data = f.read()
				data = data.replace("&lt;", "<")
				data = data.replace("&gt;", ">")
				data = data.replace("&quot;", "\"")
				data = data.replace("tei:", "")
				data = data.replace("“", "\"")
				
				f.seek(0)
				f.write(data)
				f.truncate()

		return tmpAnnotations
	
	
	""" run for all files """	
	def check(self, verbose=True, foreach=False):
		self.verbose = verbose
		self.foreach = foreach
		
		for file in self.processfiles:
			self.checkLinksInFile(file)


	""" check Links in single file """
	def checkLinksInFile(self, filepath):
		
		self.currentFile = filepath
		dom = None
		
		try:
			dom = xml.parse(filepath)
		except:
			dom = None
			self.error("Malformed XML file!")
		
		if dom:
			root = dom.documentElement
			links = self.getAttrbiuteValues_recursively(root, [])
			printOrNot = False
			
			for link in links:
					
				checkResult = self.checkLink(link)
			
				if not checkResult:
					if link in self.wrongLinks:
						printOrNot = self.foreach
					else:
						self.wrongLinks += [link]
						printOrNot = True
				
					if printOrNot: self.error("Link not found!", link)
	
	
	""" print error message """
	def error(self, msg, link=None):
		if self.verbose:
			print "*** WARNING ***"
			print msg
			if link:
			    try_print("Link Name: " + link + "\n")
			try_print("In File: " + self.currentFile + "\n\n")
		else:
			print msg,
			if link: try_print("Link to " + link + " ")
			try_print("from " + os.path.basename(self.currentFile) + "\n")
	
	
	""" check xml node recursively, get attribute values for all attribute keys in self.linkAttributes """
	def getAttrbiuteValues_recursively(self, root, result=[]):
		if root.childNodes:
			for node in root.childNodes:
				if node.nodeType == node.ELEMENT_NODE:
					for key in node.attributes.keys():
						value = node.attributes[key].value
						
						# key check -> add Link to Result
						if (key in self.linkAttributes):
							if (not value in result): result += [value]
						else:
						# link must have known attribute
							for ext in self.fileExtensions:
								if ext in value.lower(): self.error("Unexpected attribute name for link: " + key + "!", value)
							
									
					self.getAttrbiuteValues_recursively(node, result=result)
		return result
	
	""" get infos from edition xml: edirom-, work-, sources and part-ids; DOESNT GET BAR IDs AT THE MOMENT """
	def parseEdition(self):
		try:
			dom = xml.parse(self.editionpath)
		except:
			dom = None
			self.error("Malformed Edition XML file!")
		
		edi = []
		if dom:
			
			# edirom edition id
			for node_lvl1 in dom.childNodes:
				if (node_lvl1.nodeType == node_lvl1.ELEMENT_NODE) and (node_lvl1.tagName == "edition"):
					edi += [node_lvl1.attributes["xml:id"].value]
					for node_lvl2 in node_lvl1.childNodes:
						if (node_lvl2.nodeType == node_lvl2.ELEMENT_NODE) and (node_lvl2.tagName == "works"):
							# work
							for node_lvl3 in node_lvl2.childNodes:
								if (node_lvl3.nodeType == node_lvl3.ELEMENT_NODE) and (node_lvl3.tagName == "work"):
									work = [node_lvl3.attributes["xml:id"].value]
									# part
									for node_lvl4 in node_lvl3.childNodes:
										if (node_lvl4.nodeType == node_lvl4.ELEMENT_NODE) and (node_lvl4.tagName == "parts"):
											part = []
											for node_lvl5 in node_lvl4.childNodes:
												if (node_lvl5.nodeType == node_lvl5.ELEMENT_NODE) and (node_lvl5.tagName == "part"):
													part += [node_lvl5.attributes["xml:id"].value]
											work += [part]
									# source
									for node_lvl4 in node_lvl3.childNodes:
										if (node_lvl4.nodeType == node_lvl4.ELEMENT_NODE) and (node_lvl4.tagName == "sources"):
											source = []
											for node_lvl5 in node_lvl4.childNodes:
												if (node_lvl5.nodeType == node_lvl5.ELEMENT_NODE) and (node_lvl5.tagName == "source"):
													source += [node_lvl5.attributes["xml:id"].value]
													for node_lvl6 in node_lvl5.childNodes:
														if (node_lvl6.nodeType == node_lvl6.ELEMENT_NODE) and (node_lvl6.tagName == "facsimiles"):
															facsimiles = []
															# facsimile
															for node_lvl7 in node_lvl6.childNodes:
																if (node_lvl7.nodeType == node_lvl7.ELEMENT_NODE) and (node_lvl7.tagName == "facsimile"):
																	facsimiles += [node_lvl7.attributes["xml:id"].value]
																	bars = []
																	for node_lvl8 in node_lvl7.childNodes:
																		if (node_lvl8.nodeType == node_lvl8.ELEMENT_NODE) and (node_lvl8.tagName == "bars"):
																			for node_lvl9 in node_lvl8.childNodes:
																				if (node_lvl9.nodeType == node_lvl9.ELEMENT_NODE) and (node_lvl9.tagName == "bar"):
																					bars += [node_lvl9.attributes["xml:id"].value]
																			facsimiles += [bars]
															source += [facsimiles]
																	
											work += [source]
									
									edi += [work]

		return edi
								
			

	
	
	""" T or False if link is ok """
	def checkLink(self, link):

		checkResult = True

		textCheck = map(lambda(ext): ext in link.lower(), self.textExtensions)
		imageCheck = map(lambda(ext): ext in link.lower(), self.imageExtensions)
		ediromCheck = "edirom:" in link.lower()

		# links in xml file
		if any(textCheck):
			parts = link.split("/")
			# normalfall
			if len(parts) == 2:
				if not self.case_sensitive: parts[1] = parts[1].lower()
				
				checkResult = (parts[0] == "Docs") and (parts[1] in self.xmlbasefiles)
			# raute link in andere Datei
			elif len(parts) == 3:
				if not self.case_sensitive: parts[1] = parts[1].lower()
				checkResult = (parts[0] == "Docs") and (parts[1] in self.xmlbasefiles) and (parts[2][0] == "#") ## HIER KÖNNTE MAN NOCH SCHAUEN OB DER #LINK FUNKTIONIERT!
			else:
				checkResult = False
				
		# raute link in gleiche Datei
		elif link[0] == "#":
			checkResult = True ## HIER KÖNNTE MAN NOCH SCHAUEN OB DER #LINK FUNKTIONIERT!
		
		# link to image file	
		elif (any(imageCheck)) and self.image:
			parts = link.split("/")
			if not self.case_sensitive: parts[1] = parts[1].lower()
			checkResult = (len(parts) == 2) and (parts[0] == "Images") and (parts[1] in self.imagebasefiles)
		
		# link to edirom edition	
		elif ediromCheck and self.edition:
			checkResult = []
			
			# if [ or ] is in link -> it's probably wrong!
			if ("[" in link) or ("]" in link): checkResult.append(False)
			
			parts = link.split("/")
			
			# check if edition id is ok
			checkResult.append( (parts[0] == "edirom:") and (parts[1] == "") )
			checkResult.append( (parts[2] == self.editionInfo[0]) )
			
			#check if work id is ok (must be item index 3)
			checkResult.append( parts[3] in [item[0] for item in self.editionInfo[1:]] )
			
			if (not all(checkResult)): return False
			
			itemsofwork = filter(lambda (item): item[0] == parts[3], self.editionInfo[1:])
			
			# check all parts, one after the other
			for part in parts[4:]:
				if "source-" in part:
					# source id must begin with part id
					checkResult.append ( part[7:9] == parts[3][5:7] )
					# source id must exist
					checkResult.append( part in filter(lambda (sourceitem): isinstance(sourceitem, basestring), itemsofwork[0][2]) )
				elif "part-" in part:
					# part id must begin with part id
					checkResult.append ( part[5:7] == parts[3][5:7] )
					# part id must exist
					checkResult.append( part in itemsofwork[0][1] )
				elif "facsimile-" in part:
					# facsimile id must begin with part id
					checkResult.append ( part[10:12] == parts[3][5:7] )
					# facsimile id must exist
					checkResult.append( part in filter(lambda (appendeditem): isinstance(appendeditem, basestring), list(itertools.chain.from_iterable( filter(lambda (sourceitem): isinstance(sourceitem, list), itemsofwork[0][2]) ))))
				elif "bar-" in part:
					# bar id must begin with part id
					checkResult.append ( part[4:6] == parts[3][5:7] )
					# bar id must exist
					checkResult.append( part in list(itertools.chain.from_iterable( filter(lambda (appendeditem): isinstance(appendeditem, list), list(itertools.chain.from_iterable( filter(lambda (sourceitem): isinstance(sourceitem, list), itemsofwork[0][2]) ))))))
				elif ("offset=" in part) or ("dimension=" in part) or ("bars=" in part) or ("text-" in part) or ("annotation-" in part) or ("letter-" in part):
					checkResult.append(True)
				else:
					checkResult.append(False)
			
			
			
			checkResult = all(checkResult)
		
		# something else?
		else:
			self.error("Unexpected type of link. Please check this manually.", link)
		
		return checkResult


parser = OptionParser()

parser.add_option("-s", "--svn", dest="svn_directory",
									default="~/Documents/Subversion/rwa/trunk/artikel",
                  help="give directory path to subversion (default ~/Documents/Subversion/rwa/trunk/artikel)", metavar="DIRECTORY")
                  
parser.add_option("-a", "--annotation", dest="annotation_directory",
									default="/Volumes/Reger-Daten/RWA/2_DVD/Allgemein/material_fuer_baende/Band_1_07/fm2ediromExport",
                  help="give directory path to annotations (default /Volumes/Reger-Daten/RWA/2_DVD/Allgemein/material_fuer_baende/Band_1_07/fm2ediromExportt)", metavar="DIRECTORY")
                  
parser.add_option("-i", "--images", dest="images_directory",
									default="/Volumes/Reger-Daten/RWA/2_DVD/Allgemein/abbildungen/01_Bilder_konvertiert_fuer_edirom",
                  help="give directory path to images (default /Volumes/Reger-Daten/RWA/2_DVD/Allgemein/abbildungen/01_Bilder_konvertiert_fuer_edirom)", metavar="DIRECTORY")

parser.add_option("-e", "--edition", dest="edition_file",
									default="~/Documents/Subversion/rwa/trunk/editionen/RWA_Bd_I_7_edition-65916446.xml",
                  help="give path to edition file (default ~/Documents/Subversion/rwa/trunk/editionen/RWA_Bd_I_7_edition-65916446.xml)", metavar="FILE")

parser.add_option("-c", "--casesensitive", dest="case_sensitive",
									default=False,
                  help="case sensitive path matching? (default False)", metavar="True/False")
                  
parser.add_option("-v", "--verbose", dest="verbose",
									default=False,
                  help="print more or less verbose summary? (default False)", metavar="True/False")
                  
parser.add_option("-f", "--foreach", dest="foreach",
									default=False,
                  help="if a wrong link was already found, reprint it if it occurs again? (default False)", metavar="True/False")
                  
(options, args) = parser.parse_args()

case_bool = False
verbose_bool = False
foreach_bool = False
true_vals = ["True", "true", "TRUE", 1, "T", "t", "yes", "YES", "Yes"]
if options.case_sensitive in true_vals: case_bool = True
if options.verbose in true_vals: verbose_bool = True
if options.foreach in true_vals: foreach_bool = True

mychecker = LinkChecker(svn=options.svn_directory, annotations=options.annotation_directory, images=options.images_directory, edition=options.edition_file, case_sensitive=case_bool)
mychecker.check(verbose=verbose_bool, foreach=foreach_bool)


