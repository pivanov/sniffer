################################################################################
# IMPORTS NEEDED
################################################################################
import os,sys,time,datetime,calendar,subprocess

################################################################################
# CONSTANTS USED
################################################################################
TIMEOUT = 10    # time the program pauses until next scan (in seconds)
TIMEDOT = 10     # the number of waiting dots to print out (must be less than TIMEOUT)
TIMEFMT = "%Y-%m-%d %H:%M:%S"    # how the timestamp is formatted
RECORD_AGAIN = 10    # how long to wait to recond a recurring device again (in minutes)
DEVICES_FILE = 'discovered.dat'    # the location of the discovered devices dat
ADMIN_DEVICES = ["00:18:31:60:B5:42","00:00:00:00:00:00"]    # our devices (admins)

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
def alreadyDiscovered(bmac, timestamp):

  # create the file if it does not exist and add the device
  if not os.path.isfile('discovered.dat'):
    file = open(DEVICES_FILE, 'a')
    print "  Seen for the first time :)"
    line = (bmac,timestamp.strftime(TIMEFMT))
    file.write(','.join(line))
    file.write('\n')

  # if it does exist see if the device is already discovered
  else:
    file = open(DEVICES_FILE, 'a+')
    file_split = file.readlines()
    seen = 0
    file_time_last = ""
    for line in file_split:
      line_split = line.split(',')
      file_bmac = line_split.pop(0)
      file_time = line_split.pop(0).strip()
      if bmac == file_bmac:
        file_time_last = file_time
        seen = 1

    if seen:
      time_last_seen = beenLongEnough(file_time_last, timestamp)
      if time_last_seen:
        print "  Last seen",time_last_seen,"seconds ago... writting to file again"
        line = (bmac,timestamp.strftime(TIMEFMT),str(time_last_seen))
        file.write(','.join(line))
        file.write('\n')
      else :
        print "  Seen too soon ago... not writting to file"
    else:
      print "  Seen for the first time :)"
      line = (bmac,timestamp.strftime(TIMEFMT))
      file.write(','.join(line))
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
  print "  Need to push file to admin device"

################################################################################
# RUN FOREVER TO LISTEN FOR DEVICES
################################################################################
while 1:

  try:

    # inform the user that scanning is under way
    print "Scanning for discoverable bluetooth devices..."

    # scan for available bluetooth devices (discoverable)
    p = subprocess.Popen(["hcitool", "scan"], stdout=subprocess.PIPE)
    out, err = p.communicate()

    # get the appropriate data from the scan
    out_split = out.split('\n')
    out_split.pop(0)
    for s in out_split:
      line = s.strip()
      if line:
        curr_time = datetime.datetime.now()
        bluetooth_mac = line.split().pop(0)
        line = (bluetooth_mac, curr_time)
        if isAdminDevice(bluetooth_mac):
          print " Admin Device:",bluetooth_mac
          pushFileToAdminDevice()
        else:
          print " Sniffed Device:",bluetooth_mac
          alreadyDiscovered(bluetooth_mac, curr_time)

    # pause an appropriate amount of time until next scan
    sys.stdout.write(' Waiting')
    sys.stdout.flush()
    for inc in range(TIMEDOT):
      time.sleep(TIMEOUT/TIMEDOT)
      sys.stdout.write('.')
      sys.stdout.flush()
    print ""

  except KeyboardInterrupt:
    print "\nStopping scan for discoverable bluetooth devices..."
    time.sleep(2)
    sys.exit()