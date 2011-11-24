import sys

FIRSTGAZEBOTTOM = 1
FIRSTGAZETOP = 0
NOFIRSTGAZE = -1
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
    # This is where we get most of our data.
    # The basic idea is to check whether each row in the CMD file falls within our range
    # If so, get its information. If not, discard.
    cmd = open(id + "CMD.txt").readlines()
    currentTimeBlock = 0
    lastGaze = 0
    lastTimestamp = 0
    gaze = 0
    durations = []
    duration = 0
    durationAbove = durationBelow = durationCross = 0  # we don't actually care about gazes at the cross.

    # Format for pupils: [0] for top block, [1] for bottom block. And then within each row, the four items are:
    # [0] count
    # [1] sum of sizes (these two will give us the mean size)
    # [2] maximum size
    # [3] minimum size (when we can actually get a reading)
    pupils = [[0,0,0,0],[0,0,0,0]]

    firstGaze = NOFIRSTGAZE # Should take values 0 for Top and 1 for Bottom. -1 means no first gaze detected yet.
    for i in range(20, len(cmd)):  # no valid timestamps before line 20
        v = getValues(cmd[i])
        if v['timestamp'] < timeBlocks[currentTimeBlock][0]:
            # Before the official start time of our current time block
            continue
        elif v['timestamp'] >= timeBlocks[currentTimeBlock][0] and v['timestamp'] <= timeBlocks[currentTimeBlock][1]:
            # Within our time window
            gaze = getArea(v)
            if gaze != 0 and gaze == lastGaze:  # We only count after two gazes in the same area, for duration to make sense.
                duration = v['timestamp'] - lastTimestamp
                if gaze == TOPBLOCK:
                    durationAbove += duration
                    if firstGaze == NOFIRSTGAZE:
                        firstGaze = FIRSTGAZETOP
                    if v['pupilLeft'] > 0: # We actually have a reading on this pupil
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
                elif gaze == BOTTOMBLOCK:
                    durationBelow += duration
                    if firstGaze == NOFIRSTGAZE:
                        firstGaze = FIRSTGAZEBOTTOM
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
            # Prepping for the next timestamp
            lastGaze = gaze
            lastTimestamp = v['timestamp']
        elif v['timestamp'] > timeBlocks[currentTimeBlock][1]:
            # After the end of our current time block.
            # Should only happen once per block, as we immediately get ready for the next time block.
            durations.append([durationAbove, durationBelow, durationCross, firstGaze, pupils])
            # Note above that "durations" actually reports on more than durations!
            currentTimeBlock += 1
            lastGaze = 0
            durationAbove = durationBelow = durationCross = 0
            pupils = [[0,0,0,0],[0,0,0,0]]
            firstGaze = NOFIRSTGAZE
            if currentTimeBlock == NUM_PAIRS: # We're done!
                break
            continue
        else:
            # We really shouldn't be able to get here.
            print "something weird happened"
    return durations

def parseFXD(id, timeBlocks):
    # Works with the same principle as parseCMD. But in this case we parse the fixations file
    fxd = open(id + "FXD.txt", "r").readlines()
    currentTimeBlock = 0
    gaze = 0
    fixations = []
    fixationAbove = fixationBelow = 0
    for i in range(20, len(fxd)): # No valid timestamps before this row
        v = getValuesFXD(fxd[i])
        if v['timestamp'] < timeBlocks[currentTimeBlock][0]:
            continue
        elif v['timestamp'] >= timeBlocks[currentTimeBlock][0] and v['timestamp'] <= timeBlocks[currentTimeBlock][1]:
            # Within our time window
            gaze = getArea(v)
            if gaze == TOPBLOCK:
                fixationAbove += 1
            elif gaze == BOTTOMBLOCK:
                fixationBelow += 1
        elif v['timestamp'] > timeBlocks[currentTimeBlock][1]:
            currentTimeBlock += 1
            fixations.append([fixationAbove, fixationBelow])
            fixationAbove = fixationBelow = 0
            if currentTimeBlock == NUM_PAIRS:
                break
            continue
        else:
            print "something weird happened"
    return fixations

def linkTimesToImages(sequence, durations):
    # OK so we've parsed the combined file already, and we have a sequence of images. Now we need to tell apart
    # which image corresponds to which set of durations.
    # In order to do so, we parse the sequences string, and at each point figure out which image was shown on top,
    # and which one on bottom, and we give each of them their corresponding durations, first gazes, and pupil sizes.

    imageTimes = [[0] * NUM_PAIRS, [0] * NUM_PAIRS]
    # For imageTimes, the first set of numbers corresponds to climate-related images; the second to non-related

    for i in range(NUM_PAIRS):
        pair = sequence[i * 6: i * 6 + 6] # Each pair takes six characters in the string (e.g. "a04b12")
        firstID = int(pair[1:3]) - 1
        secondID = int(pair[4:]) - 1
        if pair[0] == 'a': # The top image is the climate-related image
            imageTimes[0][firstID] = durations[i][0]
            imageTimes[1][secondID] = durations[i][1]
        else:
            imageTimes[0][secondID] = durations[i][1]
            imageTimes[1][firstID] = durations[i][0]
    return imageTimes

def linkFirstGazeToImages(sequence, durations):
    # Exact same principle as linkTimesToImages above; same comments apply
    firstGazes = [[0] * NUM_PAIRS, [0] * NUM_PAIRS]
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
    # Note that it's possible for neither image to be assigned firstGaze
    return firstGazes

def linkPupilsToImages(sequence, durations):
    # Again, same principle as above. The wrinkle is that we care about more pupil metrics, so it's a bit more messy.
    maxPupils = [[0] * NUM_PAIRS, [0] * NUM_PAIRS]
    minPupils = [[0] * NUM_PAIRS, [0] * NUM_PAIRS]
    sumPupils = [[0] * NUM_PAIRS, [0] * NUM_PAIRS]
    countPupils = [[0] * NUM_PAIRS, [0] * NUM_PAIRS]
    for i in range(NUM_PAIRS):
        pair = sequence[i * 6: i * 6 + 6]
        firstID = int(pair[1:3]) - 1
        secondID = int(pair[4:]) - 1
        if pair[0] == 'a':
            # durations[i][4][...] holds the pupils list. (durations[i][0-3] have durations and firstGazes)
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
    # One more with the same principle as above.
    fixes = [[0] * NUM_PAIRS, [0] * NUM_PAIRS]
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

def getSequenceNumbers(seq):
    # Once again, same principle. Which indicates there might be a way to abstract all of these, but each is
    # different enough that it seems more effort than it's worth.
    # Anyway, in this case, seqNumbers tells us, for each image, when in the sequence did it appear.
    seqNumbers = [[0] * NUM_PAIRS, [0] * NUM_PAIRS]
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
    res.write("Participant, TotalATime, MeanATime, TotalAFixations, MeanAFixations, MaxAPupils, MinAPupils, MeanAPupils, ")
    for i in range(1, NUM_PAIRS + 1):
        currentImage = "0" + str(i)
        currentImage = "A" + currentImage[-2:]
        res.write(currentImage + "Time, ")
        res.write(currentImage + "Fixations, ")
        res.write(currentImage + "FirstGaze, ")
        res.write(currentImage + "SequenceNum, ")
        res.write(currentImage + "MaxPupil, ")
        res.write(currentImage + "MinPupil, ")
        res.write(currentImage + "MeanPupil, ")
    res.write("TotalBTime, MeanBTime, TotalBFixations, MeanBFixations, MaxBPupils, MinBPupils, MeanBPupils, ")
    for i in range(1, NUM_PAIRS + 1):
        currentImage = "0" + str(i)
        currentImage = "B" + currentImage[-2:]
        res.write(currentImage + "Time, ")
        res.write(currentImage + "Fixations, ")
        res.write(currentImage + "FirstGaze, ")
        res.write(currentImage + "SequenceNum, ")
        res.write(currentImage + "MaxPupil, ")
        res.write(currentImage + "MinPupil, ")
        res.write(currentImage + "MeanPupil, ")
    res.write("diffTotalATime-BTime, diffMeanATime-BTime, diffTotalAFirstGazes-BFirstGazes, ")
    res.write("diffTotalAFixations-BFixations, percentMeanAPupil-MeanBPupil, TotalTime-(TotalATime+TotalBTime)\n")

def outputResults(res, pid, imageTimes, firstGazes, fixes, pups, seqNumbers):
    # Long method! Here we output all the stuff we've been collecting.

    # Participant ID
    res.write(pid + ", ")

    # Times and fixes
    totalATime = totalBTime = totalAFixes = totalBFixes = diffGazes = 0
    for i in range(NUM_PAIRS):
        totalATime += imageTimes[0][i]
        totalBTime += imageTimes[1][i]
        totalAFixes += fixes[0][i]
        totalBFixes += fixes[1][i]
    res.write(str(totalATime) + ", ")
    res.write(str(totalATime / NUM_PAIRS) + ", ")
    res.write(str(totalAFixes) + ", ")
    res.write(str(totalAFixes / NUM_PAIRS) + ", ")

    # Pupil summaries
    maxAPupils = maxBPupils = sumAPupils = sumBPupils = countAPupils = countBPupils = 0
    minAPupils = minBPupils = 10000 # 10000 is a high initialization to be disposed of
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
    res.write(str(maxAPupils) + ", ")
    if minAPupils != 10000:
        res.write(str(minAPupils) + ", ")
    else:
        res.write("--, ")
    if countAPupils > 0:
        res.write(str(1.0 * sumAPupils / countAPupils) + ", ")
    else:
        res.write("0.0, ")

    for i in range(NUM_PAIRS):
        res.write(str(imageTimes[0][i]) + ", ") # Time
        res.write(str(fixes[0][i]) + ", ") # Fixations
        if firstGazes[0][i] == 1:
            res.write("1, ") # FirstGaze
            diffGazes += 1
        else:
            res.write("0, ")
        res.write(str(seqNumbers[0][i]) + ", ") # Sequence Number
        res.write(str(pups[0][0][i]) + ", ") # MaxPupil
        res.write(str(pups[1][0][i]) + ", ") # MinPupil
        if pups[3][0][i] > 0:
            res.write(str(1.0 * pups[2][0][i] / pups[3][0][i]) + ", ") #MeanPupil
        else:
            res.write("0.0, ")

    # Non-climate images information
    res.write(str(totalBTime) + ", ")
    res.write(str(totalBTime / NUM_PAIRS) + ", ")
    res.write(str(totalBFixes) + ", ")
    res.write(str(totalBFixes / NUM_PAIRS) + ", ")
    res.write(str(maxBPupils) + ", ")
    res.write(str(minBPupils) + ", ")
    if countBPupils > 0:
        res.write(str(1.0 * sumBPupils / countBPupils) + ", ")
    else:
        res.write("0.0, ")

    for i in range(NUM_PAIRS):
        res.write(str(imageTimes[1][i]) + ", ") # Time
        res.write(str(fixes[1][i]) + ", ") # Fixations
        if firstGazes[1][i] == 1:
            res.write("1, ") # FirstGaze
            diffGazes -= 1
        else:
            res.write("0, ")
        res.write(str(seqNumbers[1][i]) + ", ") # Sequence Number
        res.write(str(pups[0][1][i]) + ", ") # MaxPupil
        res.write(str(pups[1][1][i]) + ", ") # MinPupil
        if pups[3][1][i] > 0:
            res.write(str(1.0 * pups[2][1][i] / pups[3][1][i]) + ", ") #MeanPupil
        else:
            res.write("0.0, ")

    res.write(str(totalATime - totalBTime) + ", ")
    res.write(str((totalATime - totalBTime) / NUM_PAIRS) + ", ")
    res.write(str(diffGazes) + ", ")
    res.write(str(totalAFixes - totalBFixes) + ", ")
    if countAPupils > 0 and countBPupils > 0 and sumBPupils > 0:
        res.write(str((1.0 * sumAPupils / countAPupils) / (1.0 * sumBPupils / countBPupils)) + ", ")
    else:
        res.write("---, ")
    res.write(str(NUM_PAIRS * (INTERVAL + MARGIN * 2) - (totalATime + totalBTime)) + "\n")


if __name__ == "__main__":
    resultsFile = ""
    sequencesSource = ""
    if len(sys.argv) != 3:
        print "Usage: python ojos.py name_of_sequences_source_file name_of_results_file"
    else:
        sequencesSource = sys.argv[1]
        resultsFile = sys.argv[2]
        seqs = getAllSequences(sequencesSource)
        res = open(resultsFile, "w")
        outputResultsHeader(res)
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
            outputResults(res, pid, imageTimes, firstGazes, fixes, pups, seqNumbers)
