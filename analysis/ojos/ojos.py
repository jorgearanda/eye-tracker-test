NUM_PAIRS = 19
NOBLOCK = 0
CROSSBLOCK = 3
BOTTOMBLOCK = 2
TOPBLOCK = 1
INTERVAL = 5070 # milliseconds. Represents the time between image switches in the task.
MARGIN = 200 # milliseconds. Giving us a bit extra time before and after images are displayed.
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
    threshold = inverval * 20 # After this number of milliseconds, we assume the task must have started already
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
    # Returns a dictionary with the relevant values from lines coming from <id>FXD.txt format
    # Very much like getValues above.
    v = {}
    t = line.split('\t')
    v['fixnum'] = int(t[0])
    v['timestamp'] = int(t[1])
    v['duration'] = int(t[2])
    v['x'] = int(t[3])
    v['y'] = int(t[4])
    return v

def getArea(values):
    # Returns TOPBLOCK if gaze is in top image, BOTTOMBLOCK if on bottom image, CROSSBLOCK if on cross area, NOBLOCK otherwise.
    # Values is a dictionary with the keys x and y representing coordinates.
    x = values['x']
    y = values['y']
    if x > TOPBLOCKBEGINX and y > TOPBLOCKBEGINY and x < TOPBLOCKENDX and y < TOPBLOCKENDY:
        return TOPBLOCK
    elif x > BOTTOMBLOCKBEGINX and y > BOTTOMBLOCKBEGINY and x < BOTTOMBLOCKENDX and y < BOTTOMBLOCKENDY:
        return BOTTOMBLOCK
    elif x > CROSSBLOCKBEGINX and y > CROSSBLOCKBEGINY and x < CROSSBLOCKENDX and y < CROSSBLOCKENDY:
        return CROSSBLOCK
    else:
        return NOBLOCK

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
    # TODO: Continue cleaning code beginning at this point.
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
    pupils = [[0,0,0,0],[0,0,0,0]]
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
                    if v['pupilLeft'] > 0:
                        pupils[0][0] += 1
                        pupils[0][1] += v['pupilLeft']
                        pupils[0][2] = max(pupils[0][2], v['pupilLeft'])
                        if pupils[0][3] == 0:
                            pupils[0][3] = v['pupilLeft']
                        else:
                            pupils[0][3] = min(pupils[0][3], v['pupilLeft'])
                    if v['pupilRight'] > 0:
                        pupils[0][0] += 1
                        pupils[0][1] += v['pupilRight']
                        pupils[0][2] = max(pupils[0][2], v['pupilRight'])
                        if pupils[0][3] == 0:
                            pupils[0][3] = v['pupilRight']
                        else:
                            pupils[0][3] = min(pupils[0][3], v['pupilRight'])
                elif gaze == 2:
                    durationBelow += duration
                    if firstGaze < 0:
                        firstGaze = 1
                    if v['pupilLeft'] > 0:
                        pupils[1][0] += 1
                        pupils[1][1] += v['pupilLeft']
                        pupils[1][2] = max(pupils[1][2], v['pupilLeft'])
                        if pupils[1][3] == 0:
                            pupils[1][3] = v['pupilLeft']
                        else:
                            pupils[1][3] = min(pupils[1][3], v['pupilLeft'])
                    if v['pupilRight'] > 0:
                        pupils[1][0] += 1
                        pupils[1][1] += v['pupilRight']
                        pupils[1][2] = max(pupils[1][2], v['pupilRight'])
                        if pupils[1][3] == 0:
                            pupils[1][3] = v['pupilRight']
                        else:
                            pupils[1][3] = min(pupils[1][3], v['pupilRight'])
                else:
                    durationCross += duration
            lastGaze = gaze
            lastTimestamp = v['timestamp']
        elif v['timestamp'] > timeBlocks[currentTimeBlock][1]:
            currentTimeBlock += 1
            lastGaze = 0
            durations.append([durationAbove, durationBelow, durationCross, firstGaze, pupils])
            durationAbove = 0
            durationBelow = 0
            durationCross = 0
            pupils = [[0,0,0,0],[0,0,0,0]]
            firstGaze = -1
            if currentTimeBlock == NUM_PAIRS:
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
            if currentTimeBlock == NUM_PAIRS:
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
    for i in range(NUM_PAIRS):
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
    for i in range(NUM_PAIRS):
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

def linkPupilsToImages(sequence, durations):
    maxPupils = []
    minPupils = []
    sumPupils = []
    countPupils = []
    for i in range(2):
        maxPupils.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        minPupils.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        sumPupils.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
        countPupils.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    for i in range(NUM_PAIRS):
        pair = sequence[i * 6: i * 6 + 6]
        firstID = int(pair[1:3]) - 1
        secondID = int(pair[4:]) - 1
        if pair[0] == 'a':
            maxPupils[0][firstID] = durations[i][4][0][2]
            minPupils[0][firstID] = durations[i][4][0][3]
            sumPupils[0][firstID] = durations[i][4][0][1]
            countPupils[0][firstID] = durations[i][4][0][0]
            maxPupils[1][secondID] = durations[i][4][1][2]
            minPupils[1][secondID] = durations[i][4][1][3]
            sumPupils[1][secondID] = durations[i][4][1][1]
            countPupils[1][secondID] = durations[i][4][1][0]
        else:
            maxPupils[0][secondID] = durations[i][4][1][2]
            minPupils[0][secondID] = durations[i][4][1][3]
            sumPupils[0][secondID] = durations[i][4][1][1]
            countPupils[0][secondID] = durations[i][4][1][0]
            maxPupils[1][firstID] = durations[i][4][0][2]
            minPupils[1][firstID] = durations[i][4][0][3]
            sumPupils[1][firstID] = durations[i][4][0][1]
            countPupils[1][firstID] = durations[i][4][0][0]
    ps = [maxPupils, minPupils, sumPupils, countPupils]
    return ps

def linkFixationsToImages(sequence, fixations):
    fixes = []
    for i in range(2):
        fixes.append([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
    for i in range(NUM_PAIRS):
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
    for i in range(NUM_PAIRS):
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
    print "MaxAPupils,",
    print "MinAPupils,",
    print "MeanAPupils,",
    for i in range(1, 20):
        currentImage = "0" + str(i)
        currentImage = currentImage[-2:]
        print "A" + currentImage + "Time,",
        print "A" + currentImage + "Fixations,",
        print "A" + currentImage + "FirstGaze,",
        print "A" + currentImage + "SequenceNum,",
        print "A" + currentImage + "MaxPupil,",
        print "A" + currentImage + "MinPupil,",
        print "A" + currentImage + "MeanPupil,",
    print "TotalBTime,",
    print "MeanBTime,",
    print "TotalBFixations,",
    print "MeanBFixations,",
    print "MaxBPupils,",
    print "MinBPupils,",
    print "MeanBPupils,",
    for i in range(1, 20):
        currentImage = "0" + str(i)
        currentImage = currentImage[-2:]
        print "B" + currentImage + "Time,",
        print "B" + currentImage + "Fixations,",
        print "B" + currentImage + "FirstGaze,",
        print "B" + currentImage + "SequenceNum,",
        print "B" + currentImage + "MaxPupil,",
        print "B" + currentImage + "MinPupil,",
        print "B" + currentImage + "MeanPupil,",
    print "diffTotalATime-BTime,",
    print "diffMeanATime-BTime,",
    print "diffTotalAFirstGazes-BFirstGazes,",
    print "diffTotalAFixations-BFixations,",
    print "percentMeanAPupil-MeanBPupil,",
    print "TotalTime-(TotalATime+TotalBTime),"

def outputResults(pid, imageTimes, firstGazes, fixes, pups, seqNumbers):
    print pid + ",",
    totalATime = 0
    totalBTime = 0
    totalAFixes = 0
    totalBFixes = 0
    diffGazes = 0
    for i in range(NUM_PAIRS):
        totalATime += imageTimes[0][i]
        totalBTime += imageTimes[1][i]
        totalAFixes += fixes[0][i]
        totalBFixes += fixes[1][i]
    print str(totalATime) + ",",
    print str(totalATime / NUM_PAIRS) + ",",
    print str(totalAFixes) + ",",
    print str(totalAFixes / NUM_PAIRS) + ",",

    maxAPupils = maxBPupils = sumAPupils = sumBPupils = countAPupils = countBPupils = 0
    minAPupils = minBPupils = 10000
    for i in range(NUM_PAIRS):
        maxAPupils = max(maxAPupils, pups[0][0][i])
        maxBPupils = max(maxBPupils, pups[0][1][i])
        if pups[1][0][i] > 0:
            minAPupils = min(minAPupils, pups[1][0][i])
        if pups[1][1][i] > 0:
            minBPupils = min(minBPupils, pups[1][1][i])
        sumAPupils += pups[2][0][i]
        sumBPupils += pups[2][1][i]
        countAPupils += pups[3][0][i]
        countBPupils += pups[3][1][i]
    print str(maxAPupils) + ", ",
    print str(minAPupils) + ", ",
    if countAPupils > 0:
        print str(1.0 * sumAPupils / countAPupils) + ", ",
    else:
        print "0.0, ",

    for i in range(NUM_PAIRS):
        print str(imageTimes[0][i]) + ",", # Time
        print str(fixes[0][i]) + ",", # Fixations
        if firstGazes[0][i] == 1:
            print "1,", # FirstGaze
            diffGazes += 1
        else:
            print "0,",
        print str(seqNumbers[0][i]) + ",", # Sequence Number
        print str(pups[0][0][i]) + ",", # MaxPupil
        print str(pups[1][0][i]) + ",", # MinPupil
        if pups[3][0][i] > 0:
            print str(1.0 * pups[2][0][i] / pups[3][0][i]) + ",", #MeanPupil
        else:
            print "0.0,",

    print str(totalBTime) + ",",
    print str(totalBTime / NUM_PAIRS) + ",",
    print str(totalBFixes) + ",",
    print str(totalBFixes / NUM_PAIRS) + ",",
    print str(maxBPupils) + ", ",
    print str(minBPupils) + ", ",
    if countBPupils > 0:
        print str(1.0 * sumBPupils / countBPupils) + ", ",
    else:
        print "0.0, ",

    for i in range(NUM_PAIRS):
        print str(imageTimes[1][i]) + ",", # Time
        print str(fixes[1][i]) + ",", # Fixations
        if firstGazes[1][i] == 1:
            print "1,", # FirstGaze
            diffGazes -= 1
        else:
            print "0,",
        print str(seqNumbers[1][i]) + ",", # Sequence Number
        print str(pups[0][1][i]) + ",", # MaxPupil
        print str(pups[1][1][i]) + ",", # MinPupil
        if pups[3][1][i] > 0:
            print str(1.0 * pups[2][1][i] / pups[3][1][i]) + ",", #MeanPupil
        else:
            print "0.0,",

    print str(totalATime - totalBTime) + ",",
    print str((totalATime - totalBTime) / NUM_PAIRS) + ",",
    print str(diffGazes) + ",",
    print str(totalAFixes - totalBFixes) + ",",
    if countAPupils > 0 and countBPupils > 0 and sumBPupils > 0:
        print str((1.0 * sumAPupils / countAPupils) / (1.0 * sumBPupils / countBPupils)) + ",",
    else:
        print "---,",
    print str(NUM_PAIRS * (INTERVAL + MARGIN * 2) - (totalATime + totalBTime))


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
        pups = linkPupilsToImages(seqDetails, durations)
        seqNumbers = getSequenceNumbers(seqDetails)
        outputResults(pid, imageTimes, firstGazes, fixes, pups, seqNumbers)
