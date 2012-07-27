import sys

FIRSTGAZEBOTTOM = 1
FIRSTGAZETOP = 0
NOFIRSTGAZE = -1
NUM_PAIRS = 19
NOBLOCK = 0
CROSSBLOCK = 3
BOTTOMBLOCK = 2
TOPBLOCK = 1
INTERVAL = 5030 # milliseconds. Represents the time between image switches in the task.
MARGIN = 100 # milliseconds. Giving us a bit extra time before and after images are displayed.
TOPBLOCKBEGINX = 360
TOPBLOCKBEGINY = 50
TOPBLOCKENDX = 910
TOPBLOCKENDY = 440
BOTTOMBLOCKBEGINX = 360
BOTTOMBLOCKBEGINY = 560
BOTTOMBLOCKENDX = 910
BOTTOMBLOCKENDY = 970
CROSSBLOCKBEGINX = 600
CROSSBLOCKBEGINY = 460
CROSSBLOCKENDX = 680
CROSSBLOCKENDY = 540

def beginningTimestamp(id):
    # Determine the most likely beginning timestamp for the task.
    # That is, the timestamp (in milliseconds) that most probably represents the mouse click to tell the
    # browser to get started with the sequence of images.
    # This would be the *last* LMouseButton event that happens *before* a generous threshold.
    threshold = INTERVAL * 20 # After this number of milliseconds, we assume the task must have started already
    events = open(id + "EVD.txt").readlines()
    lastLMouseButton = 0
    for i in range(13, len(events)): # Before line 13 it's all header data.
        event = events[i].split()
        if event[1] == "LMouseButton" and int(event[0]) < threshold:
            # event[0] is the timestamp, event[1] the type of event
            lastLMouseButton = int(event[0])
    return lastLMouseButton

def getValues(line):
    # Returns a dictionary with the relevant values from lines coming from the format used in <id>CMD.txt
    # t[0] = timestamp
    # t[7], t[14] = pupil data
    # t[17], t[18] = coordinates
    # t[19], t[20] = event information, if any
    v = {}
    t = line.split('\t')
    v['timestamp'] = int(t[0])
    if len(t[17].strip()) > 0:
        v['x'] = int(t[17])
    else:
        v['x'] = -1
    if len(t[18].strip()) > 0:
        v['y'] = int(t[18])
    else:
        v['y'] = -1
    v['event'] = t[19].strip()
    v['eventKey'] = t[20].strip()
    return v

def isGoodTimestamp(values):
    # Returns True if both x and y values are positive, False otherwise
    return values['x'] >= 0 and values['y'] >= 0

def defineBeginEndTimes(ts):
    # Based on the timestamp ts and the interval specified, returns a list of beginning and ending timestamps for
    # each image pair
    # The intervals allow for a margin time (sometimes images don't load up right on time)
    # This is alright because the image pairs are separated by long periods with the cross.
    timeBlocks = []
    # Each item in timeBlocks is a list [beginTimestamp, endTimestamp]
    for i in range(NUM_PAIRS):
        begin = ts + INTERVAL * 2 * i + INTERVAL - MARGIN
        end = begin + INTERVAL + MARGIN * 2
        timeBlocks.append([begin, end])
    return timeBlocks

def parseCMD(id, timeBlocks):
    # This is where we get most of our data.
    # The basic idea is to check whether each row in the CMD file falls within our range
    # If so, get its information. If not, discard.
    cmd = open(id + "CMD.txt").readlines()
    currentTimeBlock = 0
    interruptions = {}
    for i in range(1, 201):
        interruptions[i] = 0
    currentInterruption = 0
    totalTimestamps = 0

    for i in range(20, len(cmd)):  # no valid timestamps before line 20
        v = getValues(cmd[i])
        if v['timestamp'] < timeBlocks[currentTimeBlock][0]:
            # Before the official start time of our current time block
            continue
        elif v['timestamp'] >= timeBlocks[currentTimeBlock][0] and v['timestamp'] <= timeBlocks[currentTimeBlock][1]:
            # Within our time window
            totalTimestamps +=1
            if isGoodTimestamp(v):
                if currentInterruption > 0:
                    if currentInterruption <= 200:
                        interruptions[currentInterruption] += 1
                    else:
                        interruptions[200] += 1
                currentInterruption = 0
            else:
                currentInterruption += 1
        elif v['timestamp'] > timeBlocks[currentTimeBlock][1]:
            # After the end of our current time block.
            # Should only happen once per block, as we immediately get ready for the next time block.
            if currentInterruption > 0:
                if currentInterruption <= 200:
                    interruptions[currentInterruption] += 1
                else:
                    interruptions[200] += 1
            currentTimeBlock += 1
            if currentTimeBlock == NUM_PAIRS: # We're done!
                break
            continue
        else:
            # We really shouldn't be able to get here.
            print "something weird happened"
    return interruptions

def getAllSequences(filename):
    # Get the sequences for all participants that we're going to analyze.
    # All the lines in the sequences file should be in the form of participantID = sequence
    sequenceLines = open(filename, 'r').readlines()
    sequences = []
    for sequence in sequenceLines:
        sequences.append(sequence.strip().split(' = '))
    return sequences

def outputResultsHeader(res):
    # Nothing interesting; just write the header for the data
    res.write("Participant, ")
    for i in range(1, 201):
        res.write(str(i) + ", ")
    res.write("\n")

def outputResults(res, pid, interruptions):
    # Participant ID
    res.write(pid + ", ")
    for i in range(1, 201):
        res.write(str(interruptions[i]) + ", ")
    res.write("\n")

if __name__ == "__main__":
    resultsFile = ""
    sequencesSource = ""
    if len(sys.argv) != 3:
        print "Usage: python interruptions.py name_of_sequences_source_file name_of_results_file"
    else:
        sequencesSource = sys.argv[1]
        resultsFile = sys.argv[2]
        seqs = getAllSequences(sequencesSource)
        res = open(resultsFile, "w")
        outputResultsHeader(res)
        for seq in seqs:
            pid = seq[0]
            print "Processing " + pid + "."
            seqDetails = seq[1]
            ts = beginningTimestamp(pid)
            interruptions = parseCMD(pid, defineBeginEndTimes(ts))
            outputResults(res, pid, interruptions)
