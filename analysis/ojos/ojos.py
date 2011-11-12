def getAllEvents(id):
    events = open(id + "EVD.txt").readlines()
    s = ""
    for i in range(13, len(events)):
        event = events[i].split()
        if event[1] != "Keyboard":
            s += "<" + event[1] + ">"
        elif len(event[5]) > 1:
            continue
        else:
            s += event[5]
    print s

def beginningTimestamp(id):
    threshold = 150000 # After this number of milliseconds, we assume the task must've started already
    events = open(id + "EVD.txt").readlines()
    lastLMouseButton = 0
    for i in range(13, len(events)):
        event = events[i].split()
        if event[1] == "LMouseButton" and int(event[0]) < threshold:
            lastLMouseButton = int(event[0])
    return lastLMouseButton

def fixClassification(id, beginTimestamp):
    topBlockBeginX = 360
    topBlockBeginY = 50
    topBlockEndX = 910
    topBlockEndY = 440
    bottomBlockBeginX = 360
    bottomBlockBeginY = 560
    bottomBlockEndX = 910
    bottomBlockEndY = 970
    crossBlockBeginX = 600
    crossBlockBeginY = 460
    crossBlockEndX = 680
    crossBlockEndY = 540
    fixations = open(id + "FXD.txt").readlines()
    for i in range(20, len(fixations)):
        fixation = fixations[i].split()
        ts = int(fixation[1])
        if ts > beginTimestamp:
            print ts - beginTimestamp,
            x = int(fixation[-2])
            y = int(fixation[-1])
            if x > topBlockBeginX and y > topBlockBeginY and x < topBlockEndX and y < topBlockEndY:
                print ": Top (",
                print x, y,
                print ")"
            elif x > bottomBlockBeginX and y > bottomBlockBeginY and x < bottomBlockEndX and y < bottomBlockEndY:
                print ": Bottom (",
                print x, y,
                print ")"
            elif x > crossBlockBeginX and y > crossBlockBeginY and x < crossBlockEndX and y < crossBlockEndY:
                print ": Cross (",
                print x, y,
                print ")"
            else:
                print ": Miss (",
                print x, y,
                print ")"


def getValues(line):
    # Returns a dictionary with the relevant values from lines coming from ParticipantIDCMD.txt format
    v = {}
    t = line.split('\t')
    v['timestamp'] = int(t[0])
    if len(t[7].strip()) > 0:
        v['pupilLeft'] = float(t[7])
    else:
        v['pupilLeft'] = 0.0
    if len(t[14].strip()) > 0:
        v['pupilRight'] = float(t[14])
    else:
        v['pupilRight'] = 0.0
    if len(t[17].strip()) > 0:
        v['x'] = int(t[17])
    else:
        v['x'] = 0
    if len(t[18].strip()) > 0:
        v['y'] = int(t[18])
    else:
        v['y'] = 0
    v['event'] = t[19].strip()
    v['eventKey'] = t[20].strip()
    return v

def getValuesFXD(line):
    # Returns a dictionary with the relevant values from lines coming from ParticipantIDFXD.txt format
    v = {}
    t = line.split('\t')
    v['fixnum'] = int(t[0])
    v['timestamp'] = int(t[1])
    v['duration'] = int(t[2])
    v['x'] = int(t[3])
    v['y'] = int(t[4])
    return v

def getArea(values):
    # Returns 1 if gaze is in top image, 2 if on bottom image, 3 if on cross area, 0 if none of the above.
    # Values is a dictionary with the keys x and y representing coordinates.
    topBlockBeginX = 360
    topBlockBeginY = 50
    topBlockEndX = 910
    topBlockEndY = 440
    bottomBlockBeginX = 360
    bottomBlockBeginY = 560
    bottomBlockEndX = 910
    bottomBlockEndY = 970
    crossBlockBeginX = 600
    crossBlockBeginY = 460
    crossBlockEndX = 680
    crossBlockEndY = 540
    x = values['x']
    y = values['y']
    if x > topBlockBeginX and y > topBlockBeginY and x < topBlockEndX and y < topBlockEndY:
        return 1
    elif x > bottomBlockBeginX and y > bottomBlockBeginY and x < bottomBlockEndX and y < bottomBlockEndY:
        return 2
    elif x > crossBlockBeginX and y > crossBlockBeginY and x < crossBlockEndX and y < crossBlockEndY:
        return 3
    else:
        return 0

def defineBeginEndTimes(ts):
    # Based on the timestamp ts and the interval specified, returns a list of beginning and ending timestamps for
    # each image pair
    interval = 5070 #miliseconds
    margin = 200 #miliseconds
    timeBlocks = []
    for i in range(19):
        begin = ts + interval * 2 * i + interval - margin
        end = begin + interval + margin * 2
        timeBlocks.append([begin, end])
    return timeBlocks

def parseCMD(id, timeBlocks):
    cmd = open(id + "CMD.txt").readlines()
    currentTimeBlock = 0
    lastGaze = 0
    lastTimestamp = 0
    gaze = 0
    durations = []
    duration = 0
    durationAbove = 0
    durationBelow = 0
    durationCross = 0
    firstGaze = -1 #Should take values 0 for Top and 1 for Bottom
    for i in range(20, len(cmd)):
        v = getValues(cmd[i])
        if v['timestamp'] < timeBlocks[currentTimeBlock][0]:
            continue
        elif v['timestamp'] >= timeBlocks[currentTimeBlock][0] and v['timestamp'] <= timeBlocks[currentTimeBlock][1]:
            # Within our time window
            # Find where the gaze lies
            gaze = getArea(v)
            if gaze != 0 and gaze == lastGaze:
                duration = v['timestamp'] - lastTimestamp
                if gaze == 1:
                    durationAbove += duration
                    if firstGaze < 0:
                        firstGaze = 0
                elif gaze == 2:
                    durationBelow += duration
                    if firstGaze < 0:
                        firstGaze = 1
                else:
                    durationCross += duration
            lastGaze = gaze
            lastTimestamp = v['timestamp']
        elif v['timestamp'] > timeBlocks[currentTimeBlock][1]:
            currentTimeBlock += 1
            lastGaze = 0
            durations.append([durationAbove, durationBelow, durationCross, firstGaze])
            durationAbove = 0
            durationBelow = 0
            durationCross = 0
            firstGaze = -1
            if currentTimeBlock == 19:
                break
            continue
        else:
            print "something weird happened"
    return durations

def parseFXD(id, timeBlocks):
    fxd = open(id + "FXD.txt", "r").readlines()
    currentTimeBlock = 0
    gaze = 0
    fixations = []
    fixationAbove = 0
    fixationBelow = 0
    for i in range(20, len(fxd)):
        v = getValuesFXD(fxd[i])
        if v['timestamp'] < timeBlocks[currentTimeBlock][0]:
            continue
        elif v['timestamp'] >= timeBlocks[currentTimeBlock][0] and v['timestamp'] <= timeBlocks[currentTimeBlock][1]:
            # Within our time window
            # Find where the gaze lies
            gaze = getArea(v)
            if gaze == 1:
                fixationAbove += 1
            elif gaze == 2:
                fixationBelow += 1
        elif v['timestamp'] > timeBlocks[currentTimeBlock][1]:
            currentTimeBlock += 1
            fixations.append([fixationAbove, fixationBelow])
            fixationAbove = 0
            fixationBelow = 0
            if currentTimeBlock == 19:
                break
            continue
        else:
            print "something weird happened"
    return fixations


def writeValues(id):
    cmd = open(id + "CMD.txt").readlines()
    for i in range(20, len(cmd)):
        print getValues(cmd[i])

def linkTimesToImages(sequence, durations):
    imageTimes = []
    for i in range(2):
        imageTimes.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    for i in range(19):
        pair = sequence[i * 6: i * 6 + 6]
        firstID = int(pair[1:3]) - 1
        secondID = int(pair[4:]) - 1
        if pair[0] == 'a':
            imageTimes[0][firstID] = durations[i][0]
            imageTimes[1][secondID] = durations[i][1]
        else:
            imageTimes[0][secondID] = durations[i][1]
            imageTimes[1][firstID] = durations[i][0]
    return imageTimes

def linkFirstGazeToImages(sequence, durations):
    firstGazes = []
    for i in range(2):
        firstGazes.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    for i in range(19):
        pair = sequence[i * 6: i * 6 + 6]
        firstID = int(pair[1:3]) - 1
        secondID = int(pair[4:]) - 1
        if pair[0] == 'a':
            if durations[i][3] == 0: # Top was first gaze
                firstGazes[0][firstID] = 1
            elif durations[i][3] == 1: # Bottom was first gaze
                firstGazes[1][secondID] = 1
        else:
            if durations[i][3] == 0: # Top was first gaze
                firstGazes[1][firstID] = 1
            elif durations[i][3] == 1: # Bottom was first gaze
                firstGazes[0][secondID] = 1
    return firstGazes

def linkFixationsToImages(sequence, fixations):
    fixes = []
    for i in range(2):
        fixes.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    for i in range(19):
        pair = sequence[i * 6: i * 6 + 6]
        firstID = int(pair[1:3]) - 1
        secondID = int(pair[4:]) - 1
        if pair[0] == 'a':
            fixes[0][firstID] = fixations[i][0]
            fixes[1][secondID] = fixations[i][1]
        else:
            fixes[0][secondID] = fixations[i][1]
            fixes[1][firstID] = fixations[i][0]
    return fixes

def getAllSequences(filename):
    sequenceLines = open(filename, 'r').readlines()
    sequences = []
    for sequence in sequenceLines:
        sequences.append(sequence.strip().split(' = '))
    return sequences

def getSequenceNumbers(seq):
    seqNumbers = []
    for i in range(2):
        seqNumbers.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    for i in range(19):
        pair = seq[i * 6: i * 6 + 6]
        firstID = int(pair[1:3]) - 1
        secondID = int(pair[4:]) - 1
        if pair[0] == 'a':
            seqNumbers[0][firstID] = i + 1
            seqNumbers[1][secondID] = i + 1
        else:
            seqNumbers[0][secondID] = i + 1
            seqNumbers[1][firstID] = i + 1
    return seqNumbers

def outputResultsHeader():
    print "Participant,",
    print "TotalATime,",
    print "MeanATime,",
    print "TotalAFixations,",
    print "MeanAFixations,",
    for i in range(1, 20):
        currentImage = "0" + str(i)
        currentImage = currentImage[-2:]
        print "A" + currentImage + "Time,",
        print "A" + currentImage + "Fixations,",
        print "A" + currentImage + "FirstGaze,",
        print "A" + currentImage + "SequenceNum,",
    print "TotalBTime,",
    print "MeanBTime,",
    print "TotalBFixations,",
    print "MeanBFixations,",
    for i in range(1, 20):
        currentImage = "0" + str(i)
        currentImage = currentImage[-2:]
        print "B" + currentImage + "Time,",
        print "B" + currentImage + "Fixations,",
        print "B" + currentImage + "FirstGaze,",
        print "B" + currentImage + "SequenceNum,",
    print "diffTotalATime-BTime,",
    print "diffMeanATime-BTime,",
    print "diffTotalAFirstGazes-BFirstGazes,",
    print "TotalTime-(TotalATime+TotalBTime),"

def outputResults(pid, imageTimes, firstGazes, fixes, seqNumbers):
    print pid + ",",
    totalATime = 0
    totalBTime = 0
    totalAFixes = 0
    totalBFixes = 0
    diffGazes = 0
    for i in range(19):
        totalATime += imageTimes[0][i]
        totalBTime += imageTimes[1][i]
        totalAFixes += fixes[0][i]
        totalBFixes += fixes[1][i]
    print str(totalATime) + ",",
    print str(totalATime / 19) + ",",
    print str(totalAFixes) + ",",
    print str(totalAFixes / 19) + ",",
    for i in range(19):
        print str(imageTimes[0][i]) + ",", # Time
        print str(fixes[0][i]) + ",", # Fixations
        if firstGazes[0][i] == 1:
            print "1,", # FirstGaze
            diffGazes += 1
        else:
            print "0,",
        print str(seqNumbers[0][i]) + ",", # Sequence Number
    print str(totalBTime) + ",",
    print str(totalBTime / 19) + ",",
    print str(totalBFixes) + ",",
    print str(totalBFixes / 19) + ",",
    for i in range(19):
        print str(imageTimes[1][i]) + ",", # Time
        print str(fixes[1][i]) + ",", # Fixations
        if firstGazes[1][i] == 1:
            print "1,", # FirstGaze
            diffGazes -= 1
        else:
            print "0,",
        print str(seqNumbers[1][i]) + ",", # Sequence Number

    print str(totalATime - totalBTime) + ",",
    print str((totalATime - totalBTime) / 19) + ",",
    print str(diffGazes) + ",",
    print str(19 * 5470 - (totalATime + totalBTime)) # TODO: Fix 19 * 5470. It represents interval + margin * 2.


if __name__ == "__main__":
    seqs = getAllSequences('sequences.txt')
    outputResultsHeader()
    for seq in seqs:
        pid = seq[0]
        seqDetails = seq[1]
        ts = beginningTimestamp(pid)
        durations = parseCMD(pid, defineBeginEndTimes(ts))
        fixations = parseFXD(pid, defineBeginEndTimes(ts))
        imageTimes = linkTimesToImages(seqDetails, durations)
        firstGazes = linkFirstGazeToImages(seqDetails, durations)
        fixes = linkFixationsToImages(seqDetails, fixations)
        seqNumbers = getSequenceNumbers(seqDetails)
        outputResults(pid, imageTimes, firstGazes, fixes, seqNumbers)
    #getAllEvents(pid)
    #fixClassification(pid, timestamp)
