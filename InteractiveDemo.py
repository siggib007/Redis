'''
Script to explore using Redis in an interactive manner

Author Siggi Bjarnason JUL 2022
Copyright 2022

Following packages need to be installed
pip install redis

'''
# Import libraries
from glob import glob
import sys
import os
import time
import platform
import redis
import re

# End imports

# Some Globals
lstSysArg = sys.argv
iSysArgLen = len(lstSysArg)
bInteractive = False
strRedisHost = "localhost"
iRedisPort = 6379
iRedisDB = 0

def CleanExit(strCause):
  """
  Handles cleaning things up before unexpected exit in case of an error.
  Things such as closing down open file handles, open database connections, etc.
  Logs any cause given, closes everything down then terminates the script.
  Parameters:
    Cause: simple string indicating cause of the termination, can be blank
  Returns:
    nothing as it terminates the script
  """
  if strCause != "":
    LogEntry("{} is exiting abnormally on {}: {}".format (strScriptName,strScriptHost,strCause))

  objLogOut.close()
  print("objLogOut closed")
  sys.exit(9)

def LogEntry(strMsg,bAbort=False):
  """
  This handles writing all event logs into the appropriate log facilities
  This could be a simple text log file, a database connection, etc.
  Needs to be customized as needed
  Parameters:
    Message: Simple string with the event to be logged
    Abort: Optional, defaults to false. A boolean to indicate if CleanExit should be called.
  Returns:
    Nothing
  """
  strTimeStamp = time.strftime("%m-%d-%Y %H:%M:%S")
  objLogOut.write("{0} : {1}\n".format(strTimeStamp,strMsg))
  print(strMsg)
  if bAbort:
    CleanExit("")

def isInt(CheckValue):
  """
  function to safely check if a value can be interpreded as an int
  Parameter:
    Value: A object to be evaluated
  Returns:
    Boolean indicating if the object is an integer or not.
  """
  if isinstance(CheckValue,int):
    return True
  elif isinstance(CheckValue,str):
    if CheckValue.isnumeric():
      return True
    else:
      return False
  else:
    return False

def DefineMenu():
  global dictMenu

  dictMenu = {}
  dictMenu["help"] = "Displays this message. Can also use /h -h and --help"
  dictMenu["interactive"] = "Use interactive mode, where you always go back to the menu. Can also use /i and -i. Use quit to exit interactive mode"
  dictMenu["reset"] = "Reset and initialize everything"
  dictMenu["add"]  = "Adds a new entry"
  dictMenu["list"] = "List out all entries"

def ProcessCmd(strCmd):
  global bInteractive
  global iSysArgLen
  global lstSysArg

  strCmd = strCmd.replace("-","")
  strCmd = strCmd.replace("/","")
  strCmd = strCmd.replace("\\","")
  strCmd = strCmd.replace("<","")
  strCmd = strCmd.replace(">","")
  strCmd = strCmd.lower()

  if strCmd[0] == "i":
    print("Entering interactive mode. Use command exit or quit to end")
    bInteractive = True
    return

  lstCmd = re.split(",|\s+",strCmd)
  if len(lstCmd) > 1:
    strCmd = lstCmd[0]
    del lstCmd[0]
    iCmdLen = len(lstCmd)
  else:
    if bInteractive or len(lstSysArg) < 3:
      lstCmd = []
      iCmdLen = 0
    else:
      lstCmd = lstSysArg
      del lstCmd[0]
      del lstCmd[0]
      iCmdLen = len(lstCmd)
  if strCmd == "q" or strCmd == "quit" or strCmd == "exit":
    bInteractive = False
    print("Goodbye!!!")
    return
  if strCmd == "h":
    strCmd = "help"
  if strCmd not in dictMenu:
    print("command {} not valid".format(strCmd))
    return
  if strCmd == "interactive":
    bInteractive = True
  if strCmd == "help":
    DisplayHelp()
  elif strCmd == "reset":
    objRedis.flushdb()
    print("Redis DB has been flushed. Have a nice day")
    bInteractive = False
  elif strCmd == "add":
    if iCmdLen == 0:
      strCmd = input("Please provide values to be added, you can specify multiple comma seperate values: ")
      lstCmd = strCmd.split(",")
    for strValue in lstCmd:
      strValue = strValue.strip()
      print("Adding {}".format(strValue))
      objRedis.lpush("MyList",strValue)
  elif strCmd == "list":
    iListLen = objRedis.llen("MyList")
    print ("Printing out all the entries. There are {} entries.".format(iListLen))
    lstMembers = objRedis.lrange("MyList",0,-1)
    for strMember in lstMembers:
      print(strMember.decode())
  else:
    print("{} not implemented".format(strCmd))

def DisplayHelp():
  print("\nHere are the commands you can use:")
  for strItem in dictMenu:
    print("{} : {}".format(strItem,dictMenu[strItem]))

def main():
  global objLogOut
  global strScriptName
  global strScriptHost
  global strBaseDir
  global objRedis

  DefineMenu()

  ISO = time.strftime("-%Y-%m-%d-%H-%M-%S")
  objRedis = redis.Redis(host=strRedisHost, port=iRedisPort, db=iRedisDB)

  strBaseDir = os.path.dirname(sys.argv[0])
  strRealPath = os.path.realpath(sys.argv[0])
  strRealPath = strRealPath.replace("\\","/")
  if strBaseDir == "":
    iLoc = strRealPath.rfind("/")
    strBaseDir = strRealPath[:iLoc]
  if strBaseDir[-1:] != "/":
    strBaseDir += "/"
  strLogDir  = strBaseDir + "Logs/"
  if strLogDir[-1:] != "/":
    strLogDir += "/"

  # if not os.path.exists (strLogDir) :
  #   os.makedirs(strLogDir)
  #   print("\nPath '{0}' for log files didn't exists, so I create it!\n".format(strLogDir))

  strScriptName = os.path.basename(sys.argv[0])
  # iLoc = strScriptName.rfind(".")
  # strLogFile = strLogDir + strScriptName[:iLoc] + ISO + ".log"
  strVersion = "{0}.{1}.{2}".format(sys.version_info[0],sys.version_info[1],sys.version_info[2])
  strScriptHost = platform.node().upper()

  print("This is a script to play around with Redis. "
    "This is running under Python Version {}".format(strVersion))
  print("Running from: {}".format(strRealPath))
  dtNow = time.asctime()
  print("The time now is {}".format(dtNow))
  # print("Logs saved to {}".format(strLogFile))
  # objLogOut = open(strLogFile,"w",1)

  if objRedis.exists("AppName") == 0:
    print("\nThis is first time this is run again this Redis instance.")
    strAppName = input("Please provide a name for this demo: ")
    objRedis.set("AppName",strAppName)
  else:
    strAppName = objRedis.get("AppName")
    strAppName = strAppName.decode()
  print("\nWelcome to {}".format(strAppName))
  strCommand = ""
  if iSysArgLen > 1:
    strCommand = lstSysArg[1]
    print("command {} detected in parameters".format(strCommand))
    ProcessCmd(strCommand)
  else:
    DisplayHelp()
    strCommand = input("Please provide command: ")
    ProcessCmd(strCommand)
  while bInteractive:
    DisplayHelp()
    strCommand = input("Please provide command: ")
    ProcessCmd(strCommand)

if __name__ == '__main__':
    main()
