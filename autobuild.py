#!/usr/bin/env python
# -*- coding:utf-8 -*-

#./autobuild.py -p youproject.xcodeproj
#./autobuild.py -w youproject.xcworkspace

import argparse
import subprocess
import requests
import os
import sys
import datetime

# input
TARGET = 'choose'
CONFIGURATION = "Debug"	# Release|Debug
PLIST_PATH = "/Users/.../choose-Info.plist"
EXPORT_OPTIONS_PLIST = "./exportOptions.plist"
VERSION = '1.2'
BUILD = '0'	# when BUILD = 0, BUILD = plist.build

# input option (Apple Store)
APPLEID = 'xxxxxx'
APPLEPWD = 'xxxxx'

# output
EXPORT_MAIN_DIRECTORY = "~/Desktop/" + TARGET + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
ARCHIVEPATH = EXPORT_MAIN_DIRECTORY + "/%s%s.xcarchive" %(TARGET,VERSION)
IPAPATH = EXPORT_MAIN_DIRECTORY + "/%s.ipa" %(TARGET)


# 蒲公英 configuration
PGYER_UPLOAD_URL = "http://www.pgyer.com/apiv1/app/upload"
DOWNLOAD_BASE_URL = "http://www.pgyer.com"
USER_KEY = "xxxxxx"
API_KEY = "xxxxx"
PYGER_PASSWORD = "xxxxx"	#设置从蒲公英下载应用时的密码


def printConfiguration():
	print(EXPORT_MAIN_DIRECTORY)
	print('xcarchive\t:' + ARCHIVEPATH)
	print('ipa\t:' + IPAPATH)


def exportArchive():
	exportCmd = "xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s" %(ARCHIVEPATH, EXPORT_MAIN_DIRECTORY, EXPORT_OPTIONS_PLIST)
	process = subprocess.Popen(exportCmd, shell=True)
	(stdoutdata, stderrdata) = process.communicate()

	signReturnCode = process.returncode
	if signReturnCode != 0:
		print ("export %s failed" %(TARGET))
		return "export faild"
	else:
		return EXPORT_MAIN_DIRECTORY

def buildProject(project):
    archiveCmd = 'xcodebuild -project %s -scheme %s -configuration %s archive -archivePath %s -destination generic/platform=iOS' %(project, TARGET, CONFIGURATION, ARCHIVEPATH)
    process = subprocess.Popen(archiveCmd, shell=True)
    process.wait()
    archiveReturnCode = process.returncode
    if archiveReturnCode != 0:
        print ("archive project %s failed" %(project)) 
        cleanArchiveFile()

def buildWorkspace(workspace):
	archiveCmd = 'xcodebuild -workspace %s -scheme %s -configuration %s archive -archivePath %s -destination generic/platform=iOS' %(workspace, TARGET, CONFIGURATION, ARCHIVEPATH)
	process = subprocess.Popen(archiveCmd, shell=True)
	process.wait()

	archiveReturnCode = process.returncode
	if archiveReturnCode != 0:
		print ("archive workspace %s failed" %(workspace))
		cleanArchiveFile()


def upload2Pgyer():
	print ("~~~~~~~~~~~~~~~~是否上传到蒲公英~~~~~~~~~~~~~~~~")
	print ("        1 不上传 (默认)")
	print ("        2 上传 ")
	isuploadpgyer = raw_input("您的决定：")
	# if isuploadpgyer == "2" and exportarchive != "":
	if isuploadpgyer == '2':
		uploadIpaToPgyer(IPAPATH)

def uploadIpaToPgyer(ipaPath):
	print ("ipaPath:"+ipaPath)
	ipaPath = os.path.expanduser(ipaPath)
	ipaPath = unicode(ipaPath, "utf-8")
	files = {'file': open(ipaPath, 'rb')}
	headers = {'enctype':'multipart/form-data'}
	payload = {'uKey':USER_KEY,'_api_key':API_KEY,'publishRange':'2','isPublishToPublic':'2', 'password':PYGER_PASSWORD}
	print ("uploading....")
	r = requests.post(PGYER_UPLOAD_URL, data = payload ,files=files,headers=headers)
	if r.status_code == requests.codes.ok:
		result = r.json()
		parserPgyerUploadResult(result)
	else:
		print ('HTTPError,Code:'+r.status_code)

def parserPgyerUploadResult(jsonResult):
	resultCode = jsonResult['code']
	if resultCode == 0:
		downUrl = DOWNLOAD_BASE_URL +"/"+jsonResult['data']['appShortcutUrl']
		print ("Upload Success\n" + "DownUrl is:" + downUrl)
	else:
		print ("Upload Fail! \n" + "Reason:"+jsonResult['message'])

def upload2AppleStore():	
	print ("~~~~~~~~~~~~~~~~是否上传到AppStore~~~~~~~~~~~~~~~~")
	print ("        1 不上传 (默认)")
	print ("        2 上传 ")
	isuploadappstore = raw_input("您的决定：")
	if isuploadappstore == '2':
		uploadIpaToAppStore()

def uploadIpaToAppStore():
	print ("iPA上传中....")
	altoolPath = "/Applications/Xcode.app/Contents/Applications/Application\ Loader.app/Contents/Frameworks/ITunesSoftwareService.framework/Versions/A/Support/altool"

	exportCmd = "%s --validate-app -f %s -u %s -p %s -t ios --output-format xml" % (altoolPath, IPAPATH, APPLEID,APPLEPWD)
	process = subprocess.Popen(exportCmd, shell=True)
	(stdoutdata, stderrdata) = process.communicate()

	validateResult = process.returncode
	if validateResult == 0:
		print ('~~~~~~~~~~~~~~~~iPA验证通过~~~~~~~~~~~~~~~~')
		exportCmd = "%s --upload-app -f %s -u %s -p %s -t ios --output-format normal" % (
		altoolPath, IPAPATH, APPLEID, APPLEPWD)
		process = subprocess.Popen(exportCmd, shell=True)
		(stdoutdata, stderrdata) = process.communicate()

		uploadresult = process.returncode
		if uploadresult == 0:
			print ('~~~~~~~~~~~~~~~~iPA上传成功')
		else:
			print ('~~~~~~~~~~~~~~~~iPA上传失败')
	else:
		print ("~~~~~~~~~~~~~~~~iPA验证失败~~~~~~~~~~~~~~~~")
		

def cleanArchiveFile():
	cleanCmd = "rm -r %s" %(ARCHIVEPATH)
	process = subprocess.Popen(cleanCmd, shell = True)
	process.wait()
	print ("cleaned archiveFile: %s" %(ARCHIVEPATH))

def Cleanup():
	print ("~~~~~~~~~~~~~~~~是否删除archive文件~~~~~~~~~~~~~~~~")
	print ("        1 保留 (默认)")
	print ("        2 删除 ")
	iscleararchive = raw_input("您的决定：")
	if iscleararchive == "2":
		cleanArchiveFile()

def writeConfig2InfoPlist():
	os.system('/usr/libexec/PlistBuddy -c "Set:CFBundleShortVersionString %s" %s' % (VERSION, PLIST_PATH))
	global BUILD
	if BUILD == '0':
		cmd = '/usr/libexec/PlistBuddy -c "Print:CFBundleVersion" %s' % (PLIST_PATH)
		buildNumber = int(os.popen(cmd).read().replace("\n", "")) + 1
		BUILD = str(buildNumber)
		print (BUILD)
	else:
		os.system('/usr/libexec/PlistBuddy -c "Set:CFBundleVersion %s" %s' % (BUILD, PLIST_PATH))


def xcbuild(options):
	print ('options:', options)

	project = options.project
	workspace = options.workspace

	if project is None and workspace is None:
		print('project and workspace is None, exit.')
		return
	
	printConfiguration()
	writeConfig2InfoPlist()

	if project is not None:
		print('build project')
		buildProject(project)
	elif workspace is not None:
		print('workspace')
		buildWorkspace(workspace)

	#导出ipa文件
	exportArchive()
	# exportarchive = exportArchive()
	# upload2Pgyer()
	# upload2AppleStore()

def checkBuildConfiguration():
	print (sys._getframe().f_code.co_name)
	if os.path.exists(PLIST_PATH) != True:
		print ('plist not exists!')
		return False
	return True


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-w", "--workspace", help="Build the workspace name.xcworkspace.", metavar="name.xcworkspace")
	parser.add_argument("-p", "--project", help="Build the project name.xcodeproj.", metavar="name.xcodeproj")
	options = parser.parse_args()
	# xcbuild(options)

	if checkBuildConfiguration():
		return
	# writeConfig2InfoPlist()

if __name__ == '__main__':
	main()
