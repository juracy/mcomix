import os
import sys
import glob
import zipfile
import shutil

""" Wrapper for py2exe, to compensate some shortcomings of the build process.

This file should be run from MComix' root directory, in order to avoid
having to play around with relative path names. """

def list_files(basedir, *patterns):
	""" Locates all files in <basedir> that match one of <patterns>. """

	all_files = []
	for dirpath, dirnames, filenames in os.walk(basedir):

		for pattern in patterns:
			cur_pattern = os.path.join(dirpath, pattern)
			all_files.extend([ os.path.normpath(path) for path in glob.glob(cur_pattern) ])
	
	return all_files

def add_files_to_archive(ziparchive, files):
	""" Add the files passed as <files> to <ziparchive>, using the same
	relative path. """

	for file in files:
		ziparchive.write(file)

def clear_distdir(distdir):
	""" Removes files from <distdir>. """
	if not os.path.isdir(distdir):
		return

	files = [os.path.join(distdir, file) 
			for file in os.listdir(distdir)
			if os.path.isfile(os.path.join(distdir, file))]

	print 'Cleaning %s...' % distdir
	for file in files:
		os.unlink(file)

def create_py2exe():
	""" Runs setup.py py2exe. """
	print 'Executing py2exe...'
	return os.system('setup.py py2exe')

def complete_library_zip():
	""" Adds required data files to the Library.zip generated by py2exe. """

	library = zipfile.ZipFile('dist_py2exe/library.zip', 'a')

	messages = list_files('mcomix/messages', '*.mo')
	print 'Adding messages to library.zip...'
	add_files_to_archive(library, messages)

	images = list_files('mcomix/images', '*.png')
	to_remove = ('mcomix/images/mcomix-large.png', 
		'mcomix/images/screenshot-monkey.png',
		'mcomix/images/screenshot-original.png')
	
	for img in to_remove:
		fixed_path = os.path.normpath(img)
		if fixed_path in images:
			images.remove(fixed_path)
	
	print 'Adding images to library.zip...'
	add_files_to_archive(library, images)
	
	library.close()

def rename_executable():
	""" Rename the executable into something reasonable. """
	print 'Renaming executable...'
	if os.path.isfile('dist_py2exe/MComix.exe'):
		os.unlink('dist_py2exe/MComix.exe')
	if os.path.isfile('dist_py2exe/mcomix_py2exe.exe'):
		shutil.move('dist_py2exe/mcomix_py2exe.exe', 'dist_py2exe/MComix.exe')

def copy_other_files():
	""" Copy other relevant files into dist directory. """
	print "Copying misc files into dist directory..."
	shutil.copy('ChangeLog', 'dist_py2exe/ChangeLog.txt')
	shutil.copy('README', 'dist_py2exe/README.txt')
	shutil.copy('COPYING', 'dist_py2exe/COPYING.txt')

if __name__ == '__main__':
	clear_distdir('dist_py2exe')

	success = create_py2exe() == 0
	
	if not success: sys.exit(1)
	
	complete_library_zip()

	rename_executable()

	copy_other_files()
