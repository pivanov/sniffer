################################################################################
# IMPORTS NEEDED
################################################################################
import os,sys,json,time,datetime,calendar,subprocess

################################################################################
# CONSTANTS USED
################################################################################
TIMEOUT = 10    # time the program pauses until next scan (in seconds)
TIMEDOT = 10     # the number of waiting dots to print out (must be less than TIMEOUT)
TIMEFMT = "%Y-%m-%d %H:%M:%S"    # how the timestamp is formatted
RECORD_AGAIN = 10    # how long to wait to recond a recurring device again (in minutes)
DEVICES_FILE = 'd_'    # the location of the discovered devices dat
DEVICES_FILE_EXT = '.dat'    # the device file file extention
ADMIN_DEVICES = ["00:18:31:60:B5:42","C8:14:79:BC:16:E3"]    # our devices (admins)

################################################################################
# DETERMINES WHETHER TO RECORD THE DEVICE AGAIN
################################################################################
def beenLongEnough(ft, ts):
  if not ft or not ts:
    return 0
  file_time_unix = calendar.timegm(datetime.datetime.strptime(ft, TIMEFMT).utctimetuple())
  curr_time_unix = calendar.timegm(ts.utctimetuple())
  return curr_time_unix - file_time_unix if curr_time_unix - file_time_unix > RECORD_AGAIN*60 else 0

################################################################################
# CHECK IF THE DEVICE HAS ALREADY BEEN RECORDED (RECORD IT IF IT HAS NOT)
################################################################################
def alreadyDiscovered(bmac, timestamp, pi):

  # create the file if it does not exist and add the device
  if not os.path.isfile(DEVICES_FILE+pi+DEVICES_FILE_EXT):
    file = open(DEVICES_FILE+pi+DEVICES_FILE_EXT, 'a')
    log('first time\n')
    file.write(json.dumps({'time': timestamp.strftime(TIMEFMT),'mac': bmac,'pi': pi}))
    file.write('\n')

  # if it does exist see if the device is already discovered
  else:
    file = open(DEVICES_FILE+pi+DEVICES_FILE_EXT, 'a+')
    file_split = file.readlines()
    seen = 0
    file_time_last = ""
    for line in file_split:
      line_json = json.loads(line)
      file_mac = line_json['mac']
      file_time = line_json['time']
      if bmac == file_mac:
        file_time_last = file_time
        seen = 1

    if seen:
      time_last_seen = beenLongEnough(file_time_last, timestamp)
      if time_last_seen:
        log('updated\n')
        file.write(json.dumps({'time': timestamp.strftime(TIMEFMT),'mac': bmac,'pi': pi}))
        file.write('\n')
      else :
        log('ignored\n')
    else:
      log('first time\n')
      file.write(json.dumps({'time': timestamp.strftime(TIMEFMT),'mac': bmac,'pi': pi}))
      file.write('\n')

  # close the discovered devices file
  file.close()


################################################################################
# CHECK IF THE DEVICE IS AN ADMIN DEVICE
################################################################################
def isAdminDevice(bmac):
  return 1 if bmac in ADMIN_DEVICES else 0


################################################################################
# PUSHES THE DISCOVERED DEVICES FILE TO THE ADMIN DEVICE
################################################################################
def pushFileToAdminDevice():
  log('file pushed\n')


################################################################################
# REQUESTS THE ADMIN DEVICES FILE
################################################################################
def requestFileFromAdminDevice():
  log('files requested - ')
  return 0


################################################################################
# TAKES THE REQUESTED FILE AND UPDATES/ANALYZES THE DATA
################################################################################
def combineFileWithOthers(f):
  log('combined - ')
  return 0


################################################################################
# TAKES THE COMBINED AND ANALYZED DATA AND PUSHED IT TO THE WEBSITE
################################################################################
def pushDataToWebsite(device_set):
  log('pushed\n')


################################################################################
# PRINT THE USAFE OF THERE WAS A MISTAKE ON INPUT
################################################################################
def printUsage():
  err(' usage: python sniffer.py <master/slave> <1/2/3/...>\n')
  err('  master - the single raspberry pi that takes files and analyzes then\n')
  err('  slave - one of the many raspberry pi\'s that sniff and transfer to admin\n')
  err('  1/2/3/... - a number representing the pi that sniffed the device\n')
  err('           - note that masters number is irrelevant\n')
  time.sleep(2)
  sys.exit()

################################################################################
# PRINT THE MESSAGE TO BYPASS NEWLINE
################################################################################
def log(message):
  sys.stdout.write(message)
  sys.stdout.flush()

################################################################################
# PRINT THE ERROR TO BYPASS NEWLINE
################################################################################
def err(message):
  sys.stderr.write(message)
  sys.stderr.flush()

################################################################################
# RUN FOREVER TO LISTEN FOR DEVICES
################################################################################
while 1:

  # if the user didn't specify master or slave
  if(len(sys.argv) < 2):
    printUsage()

  # if the user specified master or slave but cannot spell (just to rub it in)
  if(sys.argv[1] != "master" and sys.argv[1] != "slave"):
    printUsage()

  # if the use didn't enter a number for pi identification when in slave mode
  if(sys.argv[1] == "slave" and len(sys.argv) < 3):
    printUsage()

  # if it's all good run the script (unless there's a keyboard interrupt)
  try:

    # inform the user that scanning is under way
    log("scanning for discoverable bluetooth devices...\n")

    # scan for available bluetooth devices (discoverable)
    p = subprocess.Popen(["hcitool", "scan", "--flush"], stdout=subprocess.PIPE)
    out, err = p.communicate()

    # get the appropriate data from the scan
    out_split = out.split('\n')
    out_split.pop(0)
    for s in out_split:
      line = s.strip()
      if line:
        curr_time = datetime.datetime.now()
        bluetooth_mac = line.split().pop(0)
        if(sys.argv[1] == "master"):
          pi_ident = '0'
        else:
          pi_ident = sys.argv[2]
        line = (bluetooth_mac, curr_time)
        if isAdminDevice(bluetooth_mac):
          log(" "+bluetooth_mac+" admin - ")
          if(sys.argv[1] == "slave"):
            pushFileToAdminDevice()
          elif(sys.argv[1] == "master"):
            file = requestFileFromAdminDevice()
            device_set = combineFileWithOthers(file)
            pushDataToWebsite(device_set)
        else:
          log(" "+bluetooth_mac+" sniffed - ")
          alreadyDiscovered(bluetooth_mac, curr_time, pi_ident)

    # pause an appropriate amount of time until next scan
    log(' waiting')
    for inc in range(TIMEDOT):
      time.sleep(TIMEOUT/TIMEDOT)
      log('.')
    log('\n')

  except KeyboardInterrupt:
    log('\nstopping scan for discoverable bluetooth devices...\n')
    sys.exit()