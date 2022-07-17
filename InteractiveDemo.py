'''
Script to explore using Redis in an interactive manner

Author Siggi Bjarnason JUL 2022
Copyright 2022

Following packages need to be installed
pip install redis

'''
# Import libraries
import sys
import os
import time
import re
import subprocess

try:
  import redis
except ImportError:
  subprocess.check_call([sys.executable, "-m", "pip", "install", 'redis'])
finally:
    import redis

# End imports

# Some Globals
lstSysArg = sys.argv
bInteractive = False
strRedisHost = "localhost"
iRedisPort = 6379
iRedisDB = 0
strListOfList = "ListNames"

# functions

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

def GetListName():
  strListName = ""
  if objRedis.llen(strListOfList) == 1:
    strListName = objRedis.lindex(strListOfList,0)
    print("There is only one list defined, named {}. So using that list".format(strListName.decode()))
  elif objRedis.llen(strListOfList) == 0:
    print("No Lists have been defined")
    return None
  else:
    while strListName == "":
      print("Which of these lists do you want to use:")
      lstMembers = objRedis.lrange(strListOfList,0,-1)
      i = 0
      for strMember in lstMembers:
        print("{} - {}".format(i,strMember.decode()))
        i += 1
      print("{} - {}".format(i,"None"))
      strCmd = input("Please select a list: ")
      if strCmd.lower() == "none" or strCmd == str(i):
        return None
      if isInt(strCmd):
        strListName = objRedis.lindex(strListOfList,strCmd)
        if strListName is None:
          print("{} is not a valid selection".format(strCmd))
          strListName = ""
      else:
        if isInt(objRedis.lpos(strListOfList,strCmd)):
          strListName = strCmd
        else:
          print("{} is not a valid selection".format(strCmd))
  return strListName

def GetListMembers(strListName,strPrompt):
    if strListName is None:
      return None
    if strListName != strListOfList:
      print ("Fetching members of list {}".format(strListName))
    iListLen = objRedis.llen(strListName)
    print ("Printing out all the {}. There are {} entries.".format(strPrompt, iListLen))
    lstMembers = objRedis.lrange(strListName,0,-1)
    for strMember in lstMembers:
      print(strMember.decode())

def Add2List(lstCmd, strListName, strPrompt):
  if strListName is None:
    return None
  if strListName != strListOfList:
    print ("Adding to list {}".format(strListName))

  iCmdLen = len(lstCmd)
  if iCmdLen == 0:
    strCmd = input("Please provide {}, you can specify multiple comma seperate values: ".format(strPrompt))
    lstCmd = strCmd.split(",")
  for strValue in lstCmd:
    strValue = strValue.strip()
    print("Adding {}".format(strValue))
    objRedis.rpush(strListName,strValue)

def RemoveItem(strListName,strItem,strPrompt):
  if strListName is not None and strItem is not None:
    if strListName != strListOfList:
      print ("Removing {} from {}".format(strItem,strListName))
    print("Deleting {} {}".format(strPrompt, strItem))
    iTemp = objRedis.lrem(strListName, 0, strItem)
    print("{} {} removed".format(iTemp,strPrompt))

def CheckListName(strListName):
  if isInt(objRedis.lpos(strListOfList,strListName)):
    return True
  else:
    return False

def DefineMenu():
  global dictMenu

  dictMenu = {}
  dictMenu["help"]        = "Displays this message. Can also use /h -h and --help"
  dictMenu["interactive"] = "Use interactive mode, where you always go back to the menu. Can also use /i and -i. Use quit to exit interactive mode"
  dictMenu["reset"]       = "Reset and initialize everything"
  dictMenu["add"]         = "Adds a new entry to a specified list"
  dictMenu["list"]        = "List out all entries of a specified list"
  dictMenu["show"]        = "Shows all the list names"
  dictMenu["new"]         = "Creates a new list"
  dictMenu["clear"]       = "Clear out a specified list"
  dictMenu["remove"]      = "Remove a specified list"
  dictMenu["del"]         = "Remove specified item from the specified list"

def ProcessCmd(strCmd):
  global bInteractive
  global lstSysArg

  strCmd = strCmd.replace("-","")
  strCmd = strCmd.replace("/","")
  strCmd = strCmd.replace("\\","")
  strCmd = strCmd.replace("<","")
  strCmd = strCmd.replace(">","")
  strCmd = strCmd.lower()
  strListName = ""

  if strCmd[0] == "i":
    print("Entering interactive mode. Use command exit or quit to end")
    bInteractive = True
    return

  lstCmd = re.split(",|\s+",strCmd)
  if len(lstCmd) > 1:
    strCmd = lstCmd[0]
    del lstCmd[0]
    if CheckListName(lstCmd[0]):
      strListName = lstCmd[0]
      del lstCmd[0]
  else:
    if bInteractive or len(lstSysArg) < 3:
      lstCmd = []
    else:
      lstCmd = lstSysArg
      del lstCmd[0]
      del lstCmd[0]
      if CheckListName(lstCmd[0]):
        strListName = lstCmd[0]
        del lstCmd[0]
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
    if strListName == "":
      strListName = GetListName()
    Add2List(lstCmd,strListName,"values to be added")
  elif strCmd == "new":
    Add2List(lstCmd,strListOfList,"the name of the list to be created")
  elif strCmd == "list":
    if strListName == "":
      strListName = GetListName()
    GetListMembers(strListName,"entries")
  elif strCmd == "show":
    GetListMembers(strListOfList,"List names")
  elif strCmd == "clear":
    if strListName == "":
      strListName = GetListName()
    if strListName is not None:
      strListName = strListName.decode()
      print("Clearing list {}".format(strListName))
      iTemp = objRedis.delete(strListName)
      if iTemp == 0:
        print("List already empty")
      else:
        print("List emptied out")
  elif strCmd == "remove":
    if len(lstCmd) > 0 and strListName == "":
      print("Invalid list name {} ...".format(lstCmd[0]))
    if strListName == "":
      strListName = GetListName()
    RemoveItem(strListOfList,strListName,"list")
  elif strCmd == "del":
    if strListName == "":
      strListName = GetListName()
    if len(lstCmd) > 0:
      strItem = lstCmd[0]
    else:
      strItem = input("Please provide the item to be removed from list '{}': ".format(strListName))
    RemoveItem(strListName,strItem,"item")
  else:
    print("{} not implemented".format(strCmd))

def DisplayHelp():
  print("\nHere are the commands you can use:")
  for strItem in dictMenu:
    print("{} : {}".format(strItem,dictMenu[strItem]))

def main():
  global objRedis

  DefineMenu()

  objRedis = redis.Redis(host=strRedisHost, port=iRedisPort, db=iRedisDB)

  strRealPath = os.path.realpath(sys.argv[0])
  strRealPath = strRealPath.replace("\\","/")

  strVersion = "{0}.{1}.{2}".format(sys.version_info[0],sys.version_info[1],sys.version_info[2])

  print("This is a script to play around with Redis. "
    "This is running under Python Version {}".format(strVersion))
  print("Running from: {}".format(strRealPath))
  dtNow = time.asctime()
  print("The time now is {}".format(dtNow))

  if objRedis.exists("AppName") == 0:
    print("\nThis is first time this is run again this Redis instance.")
    strAppName = input("Please provide a name for this demo: ")
    objRedis.set("AppName",strAppName)
  else:
    strAppName = objRedis.get("AppName")
    strAppName = strAppName.decode()
  print("\nWelcome to {}".format(strAppName))

  if objRedis.exists(strListOfList) == 0:
    print("\nNo Lists have been setup, please create one or more lists.")
    ProcessCmd("new")
  strCommand = ""
  if len(lstSysArg) > 1:
    strCommand = lstSysArg[1]
    ProcessCmd(strCommand)
  else:
    DisplayHelp()
    strCommand = input("Please provide command: ")
    ProcessCmd(strCommand)
  while bInteractive:
    input("Please hit enter to continue ...")
    DisplayHelp()
    strCommand = input("Please provide command: ")
    ProcessCmd(strCommand)

if __name__ == '__main__':
    main()
