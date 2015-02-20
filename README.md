# Reger-Werkausgabe (RWA) DocsUpdater

The DocsUpdater is a tool for conveniently updating the encyclopedia- texts and -images of an Edirom Application. It is strongly adapted to the Reger-Werkausgabe (RWA), see below for details. It also supplies a tool for checking all links within the encyclopedia and the annotations of the Edirom Application.

If you want more information about Edirom see [edirom.de](http://www.edirom.de).

## Dependencies

At the moment only Python 2.6 or 2.7 is needed. It only works on Mac OS X because of the use of Python's built-in `plistlib`. But you should easily be able to use the script under any other OS if you remove any uses of plists.

Some remarks regarding future development: The script could be greatly improved and simplified by using [`lxml`](http://lxml.de) instead of `xml.dom.minidom` as well as using [`PyQt`](http://www.riverbankcomputing.co.uk/software/pyqt/) istead of `Tkinter`. But then the process of building an app would be a bit more involved because these libraries would have to be included in the app.

## File structure

The DocsUpdater is strongly adapted to the file structure of the RWA. The following structure is assumed:

* **svn_directory**: This is a directory with subdirectories. In these subdirectories all XML files (e.g. TEI) files for the encyclopedia are to be found.
* **annotation_directory**: This is a directory with XML files. The XML files contain the annotations to be included in the edition file.
* **images_directory**: A directory with images in sub- or sub-sub-directories for the encyclopedia.
* **edition_file**: The master edition file used to create or update the Edirom Application.

## LinkChecker

The LinkChecker is a python script that can be used as a standalone command line script and is used by the DocsUpdater. It has the purpose to check links within the encyclopedia XML files as well as the annotation XML files.

### Usage

You can get help by `python checkLinks.py --help`:

    Usage: checkLinks.py [options]
    
    Options:
      -h, --help            show this help message and exit
      -s DIRECTORY, --svn=DIRECTORY
                            give directory path to subversion (default
                            ~/Documents/Subversion/rwa/trunk/artikel)
      -a DIRECTORY, --annotation=DIRECTORY
                            give directory path to annotations (default /Volumes
                            /Reger-Daten/RWA/2_DVD/Allgemein/material_fuer_baende/
                            Band_1_07/fm2ediromExportt)
      -i DIRECTORY, --images=DIRECTORY
                            give directory path to images (default /Volumes/Reger-
                            Daten/RWA/2_DVD/Allgemein/abbildungen/01_Bilder_konver
                            tiert_fuer_edirom)
      -e FILE, --edition=FILE
                            give path to edition file (default ~/Documents/Subvers
                            ion/rwa/trunk/editionen/RWA_Bd_I_7_edition-65916446.xm
                            l)
      -c True/False, --casesensitive=True/False
                            case sensitive path matching? (default False)
      -v True/False, --verbose=True/False
                            print more or less verbose summary? (default False)
      -f True/False, --foreach=True/False
                            if a wrong link was already found, reprint it if it
                            occurs again? (default False)

### Known issues

* This LinkChecker doesn't check anchors yet. That means in the case of a link to "file.ext#id", only "file.ext" is checked. In the case of a self-link to "#id", the link isn't checked at all.
* Links in the facsimiles (target="edition://...") are checked in respect to their edition-, work-, source- and part-IDs but **not** for their bar-IDs.

## Building an app

You can build your Application by [py2app](https://pythonhosted.org/py2app/).

First build your setup-script by running:

    py2applet --extra-scripts=src/checkLinks.py --iconfile=src/regericon.icns --resources=src/eyes_reger.gif --plist=src/Info.plist --make-setup src/DocsUpdater.py

Than create the app by:

    python setup.py py2app

Than your Application should be created under `dist/DocsUpdater.app`. You can copy it and if you want to get rid of all the created files

    rm setup.py && rm -R build && rm -R dist

## License

This is MIT license so you can do what you want with the code, just give proper attribution. Anyway, if you make any improvements to the code we are happy if you share it with us or even contribute directly to our project. Please contact rwa@max-reger-institut.de.