#!/usr/bin/python
# coding=utf-8

# Frank Zalkow / Reger-Werkausgabe, 2013-2015
# DocsUpdater

# --- Importing ---
import os
import sys
import shutil
import plistlib
import glob
import Tkinter
from tkFileDialog import *
import tkFont
import tkMessageBox
import string
import subprocess as sub
import tempfile

# get home path
def getHome ():
	return os.getenv("HOME")

class DocsUpdater(object):
	""" Docs Updater """
	
	def __init__(self):
		""" initialize object """
		
		# --- paths ---
		home = os.path.expanduser("~")
		standardArticlesPath = home + "/Documents/Subversion/rwa/trunk/artikel"
		standardImagesPath = "/Volumes/Reger-Daten/RWA/2_DVD/Allgemein/abbildungen/01_Bilder_konvertiert_fuer_edirom"
		
		self.pwd = os.path.dirname(os.path.realpath(__file__))
		
		self.plistPath = home + "/Library/Preferences/de.max-reger-institut.rwa.DocsUpdate.plist"
		self.ediromPath = self.readPlistEntry("currentEdiromApplication")
		self.articlesPath = self.readPlistEntry("currentArticlesDirectory")
		self.imagesPath = self.readPlistEntry("currentImagesDirectory")
		self.imageCopyMode = self.readPlistEntry("currentImageCopyMode")
		self.editionFilePath = self.readPlistEntry("currentEditionFilePath")
		self.annotationPath = self.readPlistEntry("currentAnnotationPath")
		
		# --- GUI ---
		fonttype = ""
		fontsize = 14
		self.bgcolor = "#%02x%02x%02x" % (237, 237, 237)
		self.bluecolor = "#%02x%02x%02x" % (89, 156, 212)
		
		self.main_window = Tkinter.Tk()
		self.main_window.geometry("%dx%d+0+0" % (1250, 300))
		self.main_window.configure(bg=self.bgcolor)
		self.main_window.title("Edirom Docs Updater")
		
		
		# edirom path
		self.ediromPathLabelText = Tkinter.StringVar()
		ediromLabel = Tkinter.Label(self.main_window, text="Pfad zur Edirom-Anwendung: ", font=(fonttype, fontsize), bg=self.bgcolor)
		ediromLabelVar = Tkinter.Label(self.main_window, textvariable=self.ediromPathLabelText, font=("Courier", fontsize-4), bg=self.bgcolor)
		ediromLabel.pack(anchor="w", expand=1)
		ediromLabel.place(relx=0.02, rely=0.1+(0*0.11428), anchor="w")
		ediromLabelVar.pack(anchor="w", expand=1)
		ediromLabelVar.place(relx=0.185, rely=0.1+(0*0.11428)-0.02)
		
		# edition file path
		self.editionFilePathLabelText = Tkinter.StringVar()
		editionLabel = Tkinter.Label(self.main_window, text="Pfad zur Editions-Datei: ", font=(fonttype, fontsize), bg=self.bgcolor)
		editionLabelVar = Tkinter.Label(self.main_window, textvariable=self.editionFilePathLabelText, font=("Courier", fontsize-4), bg=self.bgcolor)
		editionLabel.pack(anchor="w", expand=1)
		editionLabel.place(relx=0.02, rely=0.1+(1*0.11428), anchor="w")
		editionLabelVar.pack(anchor="w", expand=1)
		editionLabelVar.place(relx=0.185, rely=0.1+(1*0.11428)-0.02)
		
		# articles path
		self.articlesPathLabelText = Tkinter.StringVar()
		articlesLabel = Tkinter.Label(self.main_window, text="Pfad zu den Artikeln: ", font=(fonttype, fontsize), bg=self.bgcolor)
		articlesLabelVar = Tkinter.Label(self.main_window, textvariable=self.articlesPathLabelText, font=("Courier", fontsize-4), bg=self.bgcolor)
		articlesLabel.pack(anchor="w", expand=1)
		articlesLabel.place(relx=0.02, rely=0.1+(2*0.11428), anchor="w")
		articlesLabelVar.pack(anchor="w", expand=1)
		articlesLabelVar.place(relx=0.185, rely=0.1+(2*0.11428)-0.02)

		# images path		
		self.imagesPathLabelText = Tkinter.StringVar()
		imagesLabel = Tkinter.Label(self.main_window, text="Pfad zu den Bildern: ", font=(fonttype, fontsize), bg=self.bgcolor)
		imagesLabelVar = Tkinter.Label(self.main_window, textvariable=self.imagesPathLabelText, font=("Courier", fontsize-4), bg=self.bgcolor)
		imagesLabel.pack(anchor="w", expand=1)
		imagesLabel.place(relx=0.02, rely=0.1+(3*0.11428), anchor="w")
		imagesLabelVar.pack(anchor="w", expand=1)
		imagesLabelVar.place(relx=0.185, rely=0.1+(3*0.11428)-0.02)
		
		# annotation path		
		self.annotationPathLabelText = Tkinter.StringVar()
		annotationLabel = Tkinter.Label(self.main_window, text="Pfad zu den FM-Anmerkungen: ", font=(fonttype, fontsize), bg=self.bgcolor)
		annotationLabelVar = Tkinter.Label(self.main_window, textvariable=self.annotationPathLabelText, font=("Courier", fontsize-4), bg=self.bgcolor)
		annotationLabel.pack(anchor="w", expand=1)
		annotationLabel.place(relx=0.02, rely=0.1+(4*0.11428), anchor="w")
		annotationLabelVar.pack(anchor="w", expand=1)
		annotationLabelVar.place(relx=0.185, rely=0.1+(4*0.11428)-0.02)
		
		# check boxes articles
		self.articlesCheck = Tkinter.IntVar()
		self.articlesCheck.set(1)
		articlesCheckBox = Tkinter.Checkbutton(self.main_window, text="", variable=self.articlesCheck, bg=self.bgcolor)
		articlesCheckBox.pack(anchor="w", expand=1)
		articlesCheckBox.place(relx=0.00, rely=0.1+(2*0.11428), anchor="w")
		
		# check boxes images
		self.imagesCheck = Tkinter.IntVar()
		self.imagesCheck.set(0)
		imagesCheckBox = Tkinter.Checkbutton(self.main_window, text="", variable=self.imagesCheck, bg=self.bgcolor)
		imagesCheckBox.pack(anchor="w", expand=1)
		imagesCheckBox.place(relx=0.00, rely=0.1+(3*0.11428), anchor="w")
		
		# set buttons for labels (changing or standard)
		buttonChangeEdiromPath = Tkinter.Button(self.main_window, text="Ändern", font=(fonttype, fontsize), width=5, highlightbackground=self.bgcolor, command = lambda: self.GuiChangeEdiromPath())
		buttonChangeEdiromPath.pack(side="left", expand=1)
		buttonChangeEdiromPath.place(relx=0.85, rely=0.1+(0*0.11428), anchor="w")
		
		buttonChangeEditionPath = Tkinter.Button(self.main_window, text="Ändern", font=(fonttype, fontsize), width=5, highlightbackground=self.bgcolor, command = lambda: self.GuiChangeEditionPath())
		buttonChangeEditionPath.pack(side="left", expand=1)
		buttonChangeEditionPath.place(relx=0.85, rely=0.1+(1*0.11428), anchor="w")
		
		buttonChangeArticlesPath = Tkinter.Button(self.main_window, text="Ändern", font=(fonttype, fontsize), width=5, highlightbackground=self.bgcolor, command = lambda: self.GuiChangeArticlesPath() )
		buttonChangeArticlesPath.pack(side="left", expand=1)
		buttonChangeArticlesPath.place(relx=0.85, rely=0.1+(2*0.11428), anchor="w")
		
		buttonArticlesToStandard = Tkinter.Button(self.main_window, text="Standard", font=(fonttype, fontsize), width=6, highlightbackground=self.bgcolor, command = lambda: self.GuiChangeArticlesPath(newPath=standardArticlesPath) )
		buttonArticlesToStandard.pack(side="left", expand=1)
		buttonArticlesToStandard.place(relx=0.925, rely=0.1+(2*0.11428), anchor="w")
		
		buttonChangeImagesPath = Tkinter.Button(self.main_window, text="Ändern", font=(fonttype, fontsize), width=5, highlightbackground=self.bgcolor, command = lambda: self.GuiChangeImagesPath() )
		buttonChangeImagesPath.pack(side="left", expand=1)
		buttonChangeImagesPath.place(relx=0.85, rely=0.1+(3*0.11428), anchor="w")
		
		buttonImagesToStandard = Tkinter.Button(self.main_window, text="Standard", font=(fonttype, fontsize), width=6, highlightbackground=self.bgcolor, command = lambda: self.GuiChangeImagesPath(plistPath, imagesPath, newPath=standardImagesPath) )
		buttonImagesToStandard.pack(side="left", expand=1)
		buttonImagesToStandard.place(relx=0.925, rely=0.1+(3*0.11428), anchor="w")
		
		buttonChangeAnnotationPath = Tkinter.Button(self.main_window, text="Ändern", font=(fonttype, fontsize), width=5, highlightbackground=self.bgcolor, command = lambda: self.GuiChangeAnnotationPath() )
		buttonChangeAnnotationPath.pack(side="left", expand=1)
		buttonChangeAnnotationPath.place(relx=0.85, rely=0.1+(4*0.11428), anchor="w")
		
		buttonImagesOptions = Tkinter.Button(self.main_window, text="Bilder-Kopieroptionen", font=(fonttype, fontsize), width=18, highlightbackground=self.bgcolor, command = lambda: self.ImageCopyOptions() )
		buttonImagesOptions.pack(side="left", expand=1)
		buttonImagesOptions.place(relx=0.85, rely=0.1+(5*0.11428), anchor="w")
		
		# set image
		picturepath = os.path.dirname(sys.argv[0]) + "/eyes_reger.gif"
		mypic = Tkinter.PhotoImage(file = picturepath)		
		label = Tkinter.Label(image=mypic, bg=self.bgcolor)
		label.image = mypic
		label.place(relx=0.5, rely=0.1+(6*0.11428), anchor="center")
				
		# progressbar
		self.progressText = Tkinter.StringVar()
		self.progressLabelVar = Tkinter.Label(self.main_window, textvariable=self.progressText, font=("Courier", fontsize), bg=self.bgcolor, fg=self.bluecolor)
		self.progressLabelVar.pack(side="right", expand=1)
		self.progressLabelVar.place(relx=0.01, rely=0.1+(6*0.11428), anchor="w")
		self.progressLength = 30
		#progressLabelVar.configure(relief="sunken")
		#self.progressText.set(" ██████████████████████████████ ")
		
		
		# make buttons
		self.buttonUpdate = Tkinter.Button(self.main_window, text="Aktualisiere die Anwendung", default="active", font=(fonttype, fontsize), width=25, highlightbackground=self.bgcolor, command = lambda: self.GuiUpdateEdirom() )
		self.main_window.bind("<Key>", self.shortcut ) # ENTER is shortcut for buttonUpdate#
		self.buttonUpdate.pack(side="left", expand=1)
		self.buttonUpdate.place(relx=0.0, rely=0.1+(7*0.11428), anchor="w")

		self.buttonCheckLinks = Tkinter.Button(self.main_window, text="Check Links!", font=(fonttype, fontsize), width=25, highlightbackground=self.bgcolor, command = lambda: self.GuiCheckLinks() )
		self.buttonCheckLinks.pack(side="right", expand=1)
		self.buttonCheckLinks.place(relx=0.9, rely=0.1+(6*0.11428), anchor="center")
		
		self.buttonClose = Tkinter.Button(self.main_window, text="Schließen", font=(fonttype, fontsize), width=25, highlightbackground=self.bgcolor, command = lambda: sys.exit() )
		self.buttonClose.pack(side="left", expand=1)
		self.buttonClose.place(relx=0.9, rely=0.1+(7*0.11428), anchor="center")
		
		# if there is no edirom path, ask for it
		if self.ediromPath == "":
			self.GuiChangeEdiromPath()
		if self.articlesPath == "":
			self.GuiChangeArticlesPath(newPath=standardArticlesPath)
		if self.imagesPath == "":
			self.GuiChangeImagesPath (newPath=standardImagesPath)
		if self.editionFilePath == "":
			self.GuiChangeEditionPath()
		if self.annotationPath == "":
			self.GuiChangeAnnotationPath()
		if self.imageCopyMode == "":
			self.imageCopyMode = 0
			self.entryToPlist("currentImageCopyMode", self.imageCopyMode)
		
		self.ediromPath = self.readPlistEntry("currentEdiromApplication")
		self.articlesPath = self.readPlistEntry("currentArticlesDirectory")
		self.imagesPath = self.readPlistEntry("currentImagesDirectory")
		self.imageCopyMode = self.readPlistEntry( "currentImageCopyMode")
		self.editionFilePath = self.readPlistEntry("currentEditionFilePath")
		self.annotationPath = self.readPlistEntry("currentAnnotationPath")
		
		# set text of main label
		self.ediromPathLabelText.set("\"" + str(self.ediromPath) + "\"")
		self.articlesPathLabelText.set("\"" + str(self.articlesPath) + "\"")
		self.imagesPathLabelText.set("\"" + str(self.imagesPath) + "\"")
		self.editionFilePathLabelText.set("\"" + str(self.editionFilePath) + "\"")
		self.annotationPathLabelText.set("\"" + str(self.annotationPath) + "\"")
		
		# mainloop
		self.main_window.mainloop()
		
	def getAllFilesWithExt(self, root, ext):
		""" get output of find command -- only possible if unix find is installed.
				attention: searches recursively from the root directory """
		p = sub.Popen("find " + root + " -name \"*." + ext + "\"", stdout=sub.PIPE, shell=True)
		out, err = p.communicate()
		result = out.split("\n")
		result.remove("")
		return result
		
	def GuiChangeEdiromPath(self):
		""" change Edirom Application path """
		newPath = askopenfilename(filetypes=[("Applications", "*.app")], title="Wählen Sie Ihre Edirom Anwendung aus...", initialdir=os.path.dirname(self.ediromPath))
		if newPath != "":
			self.ediromPath = newPath
			self.entryToPlist("currentEdiromApplication", newPath)
			self.ediromPathLabelText.set("\"" + str(newPath) + "\"")
			
	def GuiChangeArticlesPath(self, newPath = ""):
		""" change article directory path """		
		if newPath == "":
			newPath = askdirectory(title="Wählen Sie Ihren Artikel-Ordner...", initialdir=self.articlesPath)
		if newPath != "":
			self.articlesPath = newPath
			self.entryToPlist("currentArticlesDirectory", newPath)
			self.articlesPathLabelText.set("\"" + str(newPath) + "\"")
			
	def GuiChangeImagesPath(self, newPath = ""):
		""" change images directory path """
		if newPath == "":
			newPath = askdirectory(title="Wählen Sie Ihren Bilder-Ordner...", initialdir=self.imagesPath)
		if newPath != "":
			self.imagesPath = newPath
			self.entryToPlist("currentImagesDirectory", newPath)
			self.imagesPathLabelText.set("\"" + str(newPath) + "\"")
			
	def GuiChangeEditionPath(self):
		""" change Edirom Application path """
		newPath = askopenfilename(filetypes=[("XML", "*.xml")], title="Wählen Sie Ihre Editionsdatei aus...", initialdir=os.path.dirname(self.editionFilePath))
		if newPath != "":
			self.editionFilePath = newPath
			self.entryToPlist("currentEditionFilePath", newPath)
			self.editionFilePathLabelText.set("\"" + str(newPath) + "\"")
			
	def GuiChangeAnnotationPath(self, newPath = ""):
		""" change images directory path """
		if newPath == "":
			newPath = askdirectory(title="Wählen Sie den Ordner zum FileMaker-KB-Export...", initialdir=self.annotationPath)
		if newPath != "":
			self.annotationPath = newPath
			self.entryToPlist("currentAnnotationPath", newPath)
			self.annotationPathLabelText.set("\"" + str(newPath) + "\"")
			
	def ImageCopyOptions(self):
		""" seperate window for image copy options """
		self.main_window.withdraw()
	
		def option_window_ok():
			self.imageCopyMode = option.get()
			self.entryToPlist("currentImageCopyMode", self.imageCopyMode)
			option_window.destroy()
	
		option_window = Tkinter.Toplevel()
		option_window.title("Bilder-Kopieroptionen")
		option_window.configure(bg=self.bgcolor)
		option_window.geometry("%dx%d+0+0" % (750, 200))
		
		Tkinter.Label(option_window, text="Sie können\n(1) nur jene Bilder kopieren, die nocht nicht in der Edirom Anwendung vorhanden sind oder\n(2) die alten Bilder durch die neuen überschreiben lassen.\n\n(1) ist schneller, aber falls ein Bild, das es bereits gab, geändert wurde, wird die Änderung nicht mitkopiert.\n(2) dauert länger, aber es werden wirklich alle Bilder kopiert.", bg=self.bgcolor).pack()
		
		option = Tkinter.IntVar()
		option.set(self.imageCopyMode)
		
		Tkinter.Radiobutton(option_window, text="nur neue Bilder kopieren", variable=option, value=0, bg=self.bgcolor).pack()
		Tkinter.Radiobutton(option_window, text="alte Bilder löschen und alle Bilder kopieren", variable=option, value=1, bg=self.bgcolor).pack()
		
		Tkinter.Button(option_window, text="Abbrechen", highlightbackground=self.bgcolor, command = lambda: [option_window.destroy(), self.main_window.update(), self.main_window.deiconify()]).pack(anchor="e", side="left")
		Tkinter.Button(option_window, text="Ok", default="active", highlightbackground=self.bgcolor, command = lambda: [option_window_ok(),self.main_window.update(), self.main_window.deiconify()]).pack(anchor="e", side="left")
		option_window.protocol("WM_DELETE_WINDOW", lambda: [option_window.destroy(), self.main_window.update(), self.main_window.deiconify()])
		
	def GuiUpdateEdirom(self):
	
		self.buttonUpdate.configure(state="disabled")
		self.buttonCheckLinks.configure(state="disabled")
		self.buttonClose.configure(state="disabled")
		self.main_window.update_idletasks()
		
		ediromEditionsDir = self.ediromPath + "/Contents/Resources/Java/editions"
		if (not self.checkPath(ediromEditionsDir, "Fehler (Editions-Ordner)") ):
			self.enableMainButtons()
			return 0
		ediromEditionsPath = glob.glob(ediromEditionsDir + "/RWA_Band*")[0]
		
		articlemode = self.articlesCheck.get()
		imagemode = self.imagesCheck.get()
		
		if articlemode == 1:
			if (not self.checkPath(self.articlesPath, "Fehler (Artikel-Ordner)") ):
				self.enableMainButtons()
				return 0
			
		if imagemode == 1:
			if (not self.checkPath(self.imagesPath, "Fehler (Bilder-Ordner)") ):
				self.enableMainButtons()
				return 0 

		if (articlemode == 1) or (imagemode == 1):
			for path in (self.ediromPath, ediromEditionsPath):
				if (not self.checkPath(path, "Fehler (Edirom-Pfad)") ):
					self.enableMainButtons()
					return 0
			
			removeddoc, copieddoc, removedimage, copiedimage = self.updateEdirom(ediromEditionsPath, articlemode, imagemode)
			print "\a";
			tkMessageBox.showinfo("Anwendung erfolgreich aktualisiert", str(removeddoc) + " alte Dokumente wurden gelöscht.\n" + str(copieddoc) + " Dokumente wurden kopiert.\n" + str(removedimage) + " Bilder wurden gelöscht.\n" + str(copiedimage) + " Bilder wurden kopiert.")
			
			self.progressLabelVar.configure(relief="flat")
			self.progressText.set(" " + " "*self.progressLength + " ")
			
		self.enableMainButtons()
		
	def enableMainButtons(self):
		self.buttonUpdate.configure(state="active")
		self.buttonCheckLinks.configure(state="normal")
		self.buttonClose.configure(state="normal")
			
		
				
	def updateEdirom(self, ediromPath, articlemode, imagemode):
	
		removedoc = []
		copydoc = []
		csscopy = ""
		removeimages = []
		copyimages = []
		copyimagesdir = ediromPath + "/Images"
		copycssdir = ediromPath
		copydocsdir = ediromPath + "/Docs"
	
		if (self.articlesPath != "") and (articlemode == 1):
			removedoc = glob.glob(ediromPath + "/Docs/*.xml")
			copydoc = self.getAllFilesWithExt(self.articlesPath, "xml")
			if copydoc == None: copydoc = []
			
			csscopy = self.articlesPath + "/../css/project_tei.css"
			if os.path.exists(csscopy):
				if os.path.exists(ediromPath + "/project_tei.css"):
					removedoc.append(ediromPath + "/project_tei.css")
					
		
		if (self.imagesPath != "") and (imagemode == 1):
			if self.imageCopyMode == 1:
				copyimages = glob.glob(self.imagesPath + "/*")
				removeimages = []
				for copyfile in copyimages:
					checkfile = ediromPath + "/Images/" + os.path.basename(copyfile)
					if os.path.exists(checkfile):
						removeimages.append(checkfile)
				
			else:
				copyimages = []
				for file in glob.glob(self.imagesPath + "/*"):
					if not os.path.exists(ediromPath + "/Images/" + os.path.basename(file)):
						copyimages.append(file)
		
		# progressbar
		self.progressLabelVar.configure(relief="sunken")
		self.progressText.set(" " + " "*self.progressLength + " ")
		
		if self.checkAccess(removedoc + removeimages + [copyimagesdir, copycssdir, copydocsdir]):
			
			i = 0
			total = len(removedoc) + len(copydoc) + 1 + len(removeimages) + len(copyimages)
			progresRatio = float(total)/float(self.progressLength)
			progressChars = 0
			
			for mode, file in [(0, file) for file in removedoc+removeimages] + [(1, file) for file in copydoc] + [(2, file) for file in copyimages] + [(3, csscopy)]:

				if mode == 0:
					if os.path.exists(file):
						os.remove(file)
				elif mode == 1:
					shutil.copy(file, copydocsdir)
				elif mode == 2:
					shutil.copy(file, copyimagesdir)
				elif (mode == 3) and (file != ""):
					shutil.copy(file, copycssdir)
					
				# progressbar
				if int(i % progresRatio) == 0:
					progressChars += 1
					self.progressText.set(" " + "█"*progressChars + " "*(self.progressLength-progressChars) + " ")
					self.progressLabelVar.update_idletasks()
				
				i += 1
			
			"""
			# for printing copied and removed files, capable for a diff
			print "--"
			printremovedoc = map(os.path.basename, removedoc)
			printremovedoc.sort()
			for doc in printremovedoc: print os.path.basename(doc)
			print "--"
			printcopydoc = map(os.path.basename, copydoc)
			printcopydoc.sort()
			for doc in printcopydoc: print os.path.basename(doc)
			"""
			
			return [len(removedoc), len(copydoc)+1, len(removeimages), len(copyimages)]
		else:
			return [0, 0, 0, 0]
			
	def checkAccess (self, files, log=True):
		check = True
		notToAcess = []
		for file in files:
			checknow = os.access(file, os.W_OK)
			if not checknow:
				notToAcess.append(file)
			check = check and checknow
			
		if len(notToAcess) != 0:
			if log == True:
				logfile = getHome() + "/Desktop/DocsUpdater.log"
				msgString = "Sie haben keine Zugriffsrechte für einige Dateien.\nDie Dateien wurden in " + logfile + " aufgelistet."
				with open(logfile, "w") as logstream:
					logstream.write(string.join(notToAcess, "\n"))
			else:
				msgString = "Sie haben keine Zugriffsrechte für einige Dateien."
		
			tkMessageBox.showerror("Fehler", msgString)
			
		return check
				
	def shortcut(self, event):
		if (repr(event.char) == repr("\x03")) or (repr(event.char) == repr("\r")):
			self.buttonUpdate.invoke()
			
	def checkPath(self, path, head="Fehler"):
		if (not os.path.exists(path) ):
			tkMessageBox.showerror(head, path + " existiert nicht.")
			return False
		else:
			return True
		
		
	def readPlistEntry(self, key):
		""" gets value of key from plist """
		if (not os.path.exists(self.plistPath)):
			return ""
		else:
			plistData = plistlib.readPlist(self.plistPath)
			if key in plistData:
				return plistData[key]
			else:
				return ""
				
	def entryToPlist (self, key, val):
		""" write key/value pair to plist """
		# if file doesn't exist -> create file and make new dictionary
		if (not os.path.exists(self.plistPath)):
			open(self.plistPath, "w").close()
			plistData = {key:val}
		# if file exist -> update dictionary
		else:
			plistData = plistlib.readPlist(self.plistPath)
			plistData.update({key:val})
			
		plistlib.writePlist(plistData, self.plistPath)
		
	def GuiCheckLinks (self):
		
		def checker(case, verbose, foreach):
		
			if (not self.checkPath(self.articlesPath, "Fehler (Artikel-Ordner)") ):
				return 0
			if (not self.checkPath(self.annotationPath, "Fehler (FM-KB-Export-Ordner)") ):
				return 0
			if (not self.checkPath(self.imagesPath, "Fehler (Images-Ordner)") ):
				return 0
			if (not self.checkPath(self.editionFilePath, "Fehler (Editions-Datei)") ):
				return 0
		
			check_ok.configure(state = "disabled")
			check_close.configure(state = "disabled")
			check_window.update_idletasks()
		
			text_window = Tkinter.Toplevel()
			text_window.title("Output of Link Checker")
			text_window.configure(bg=self.bgcolor)
			text_window.geometry("%dx%d+0+0" % (750, 500))
			
			text = Tkinter.Text(text_window, relief="sunken")
			text.pack(side="left", fill="both", expand=True)
			scrollb = Tkinter.Scrollbar(text_window, command=text.yview)
			scrollb.pack(side="right", fill="y", expand=False)
			text.config(yscrollcommand=scrollb.set)
						
			cmd = [self.pwd+"/checkLinks.py", \
									"-s", self.articlesPath, \
									"-a", self.annotationPath, \
									"-i", self.imagesPath+"/..", \
									"-e", self.editionFilePath, \
									"-c", "True" if case == 1 else "False", \
									"-v", "True" if verbose == 1 else "False", \
									"-f", "True" if foreach == 1 else "False"]
		
			#print " ".join(cmd)

			tmp = tempfile.mkstemp()
			with open(tmp[1], "w") as outfile:
			    sub.call(cmd, stdout=outfile)
			with open(tmp[1], "r") as outfile:    
			    text.delete(1.0)
			    text.insert(1.0, outfile.read())
			os.remove(tmp[1])
			    
			check_ok.configure(state = "active")
			check_close.configure(state = "normal")
			check_window.update_idletasks()
			
		self.main_window.withdraw()
		
		check_window = Tkinter.Toplevel()
		check_window.title("Check Links")
		check_window.configure(bg=self.bgcolor)
		check_window.geometry("%dx%d+0+0" % (550, 150))
		
		verboseCheck = Tkinter.IntVar()
		verboseCheck.set(0)
		caseCheck = Tkinter.IntVar()
		caseCheck.set(0)
		foreachCheck = Tkinter.IntVar()
		foreachCheck.set(0)
		
		Tkinter.Label(check_window, text="Optionen zum Link checken:", bg=self.bgcolor).pack()
		Tkinter.Checkbutton(check_window, text="Ausführliche Log-Datei?", variable=verboseCheck, bg=self.bgcolor).pack()
		Tkinter.Checkbutton(check_window, text="Groß/Kleinschreibung zur Pfad-Übereinstimmung beachten?", variable=caseCheck, bg=self.bgcolor).pack()
		Tkinter.Checkbutton(check_window, text="Sollen falsche Links mehrfach angezeigt werden, wenn sie mehrfach verlinkt sind?", variable=foreachCheck, bg=self.bgcolor).pack()
		
		check_ok = Tkinter.Button(check_window, text="Ok", default="active", highlightbackground=self.bgcolor, command = lambda: checker(caseCheck.get(), verboseCheck.get(), foreachCheck.get()))
		check_ok.pack(anchor="w", side="left")
		check_close = Tkinter.Button(check_window, text="Schließen", highlightbackground=self.bgcolor, command = lambda: [check_window.destroy(), self.main_window.update(), self.main_window.deiconify()])
		check_close.pack(anchor="w", side="left")
		check_window.protocol("WM_DELETE_WINDOW", lambda: [check_window.destroy(), self.main_window.update(), self.main_window.deiconify()])
		
		
		

				
myUpdater = DocsUpdater()
