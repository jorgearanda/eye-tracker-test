import sys
import copy
import math

def getInquisitData(filename):
    validLines = ["BKclimate_actiongoodRT833", "BKclimate_actionbadRT833", \
                  "BKclimate_actiongoodRT666", "BKclimate_actionbadRT666"]
    lines = open(filename, "r").readlines()
    data = []
    realTask = False
    pid = "0"
    timestamps = {}
    for i in range(1, len(lines)):
        line = lines[i].split()
        if not realTask and line[4] == "pause":
            realTask = True
            pid = line[3]
            if pid not in timestamps:
                timestamps[pid] = line[1]
            elif timestamps[pid] != line[1]:
                pid = line[3] + "000" + line[1][:2] + line[1][3:]
                timestamps[pid] = line[1]
        if realTask and line[9] == "1" and line[-1] in validLines and "background" not in line[4] \
           and "pause" not in line[4] and "reminder" not in line[4] and int(line[7]) >= 300:
            dataPieces = []
            dataPieces.append(pid) # ParticipantID
            dataPieces.append(line[4]) # TrialCode
            dataPieces.append(line[7]) # ResponseTime
            dataPieces.append(line[-1]) # BlockCode
            if "false" in line[4]:
                dataPieces.append("FA")
            else:
                dataPieces.append("HIT")
            data.append(dataPieces)
        if realTask and line[4] == "reminder" or line[4] == "single":
            realTask = False
    return data

def getInquisitDataForRates(filename):
    validLines = ["BKclimate_actiongoodRT833", "BKclimate_actionbadRT833",\
                  "BKclimate_actiongoodRT666", "BKclimate_actionbadRT666"]
    lines = open(filename, "r").readlines()
    data = []
    realTask = False
    pid = "0"
    timestamps = {}
    for i in range(1, len(lines)):
        line = lines[i].split()
        if not realTask and line[4] == "pause":
            realTask = True
            pid = line[3]
            if pid not in timestamps:
                timestamps[pid] = line[1]
            elif timestamps[pid] != line[1]:
                pid = line[3] + "000" + line[1][:2] + line[1][3:]
                timestamps[pid] = line[1]
        if realTask and line[-1] in validLines and "background" not in line[4] \
           and "pause" not in line[4] and "reminder" not in line[4]:
            dataPieces = []
            dataPieces.append(pid) # ParticipantID
            dataPieces.append(line[4]) # TrialCode
            if "true" in line[4]:
                dataPieces.append("PotentialHit")
            elif "false" in line[4]:
                dataPieces.append("PotentialFA")
            else:
                print "Something weird happened."
            if line[9] == "1":
                dataPieces.append(True)
            else:
                dataPieces.append(False)
            dataPieces.append(line[-1]) # BlockCode
            data.append(dataPieces)
        if realTask and line[4] == "reminder" or line[4] == "single":
            realTask = False
    return data

def getInquisitDataForRatesSplitHalf(filename):
    validLines = ["BKclimate_actiongoodRT833", "BKclimate_actionbadRT833",\
                  "BKclimate_actiongoodRT666", "BKclimate_actionbadRT666"]
    lines = open(filename, "r").readlines()
    dataFirst = []
    dataSecond = []
    realTask = False
    pid = "0"
    timestamps = {}
    counter = 0
    goToFirst = True
    for i in range(1, len(lines)):
        line = lines[i].split()
        if not realTask and line[4] == "pause":
            realTask = True
            pid = line[3]
            if pid not in timestamps:
                timestamps[pid] = line[1]
            elif timestamps[pid] != line[1]:
                pid = line[3] + "000" + line[1][:2] + line[1][3:]
                timestamps[pid] = line[1]
        if realTask and line[-1] in validLines and "background" not in line[4]\
           and "pause" not in line[4] and "reminder" not in line[4]:
            dataPieces = []
            dataPieces.append(pid) # ParticipantID
            dataPieces.append(line[4]) # TrialCode
            if "true" in line[4]:
                dataPieces.append("PotentialHit")
            elif "false" in line[4]:
                dataPieces.append("PotentialFA")
            else:
                print "Something weird happened."
            if line[9] == "1":
                dataPieces.append(True)
            else:
                dataPieces.append(False)
            dataPieces.append(line[-1]) # BlockCode
            if counter > 1:
                counter = 0
                goToFirst = not goToFirst
            else:
                counter += 1
            if goToFirst:
                dataFirst.append(dataPieces)
            else:
                dataSecond.append(dataPieces)
        if realTask and line[4] == "reminder" or line[4] == "single":
            realTask = False
    return (dataFirst, dataSecond)

def getResponseTimes(data):
    results = {}
    for row in data:
        if int(row[0]) not in results:
            results[int(row[0])] = [0] * 16
        pValues = results[int(row[0])]
        rt = int(row[2])
        if row[-1] == "HIT":
            if row[3] == "BKclimate_actiongoodRT833":
                pValues[0] += rt
                pValues[4] += 1
            elif row[3] == "BKclimate_actionbadRT833":
                pValues[1] += rt
                pValues[5] += 1
            elif row[3] == "BKclimate_actiongoodRT666":
                pValues[2] += rt
                pValues[6] += 1
            elif row[3] == "BKclimate_actionbadRT666":
                pValues[3] += rt
                pValues[7] += 1
            else:
                print "Something weird happened"
                break
        else:
            if row[3] == "BKclimate_actiongoodRT833":
                pValues[8] += rt
                pValues[12] += 1
            elif row[3] == "BKclimate_actionbadRT833":
                pValues[9] += rt
                pValues[13] += 1
            elif row[3] == "BKclimate_actiongoodRT666":
                pValues[10] += rt
                pValues[14] += 1
            elif row[3] == "BKclimate_actionbadRT666":
                pValues[11] += rt
                pValues[15] += 1
            else:
                print "Something weird happened"
                break
        results[int(row[0])] = pValues
    return results

def getCounts(data):
    results = {}
    block = 0
    for row in data:
        if int(row[0]) not in results:          # PID
            results[int(row[0])] = [0] * 16
        pValues = results[int(row[0])]
        if row[-1] == "BKclimate_actiongoodRT833":
            block = 0
        elif row[-1] == "BKclimate_actionbadRT833":
            block = 1
        elif row[-1] == "BKclimate_actiongoodRT666":
            block = 2
        elif row[-1] == "BKclimate_actionbadRT666":
            block = 3
        else:
            print "Unrecognized block"
        if row[2] == "PotentialHit":
            pValues[block * 4] += 1
            if row[3]:
                pValues[block * 4 + 1] += 1
        if row[2] == "PotentialFA":
            pValues[block * 4 + 2] += 1
            if row[3]:
                pValues[block * 4 + 3] += 1
        results[int(row[0])] = pValues
    return results

def getMeans(results):
    means = [0.0] * 8
    tries = [0] * 8
    hits = [0] * 8
    for key in results.keys():
        result = results[key]
        for i in range(8):
            tries[i] += result[i * 2]
            hits[i] += result[i * 2 + 1]
    for i in range(8):
        means[i] = 1.0 * hits[i] / tries[i]
    return means

def correctCounts(results, means):
    for key in results.keys():
        result = results[key]
        for i in range(8):
            if not result[i * 2 + 1] or result[i * 2 + 1] == result[i * 2]:
                result[i * 2] += 1
                result[i * 2 + 1] += means[i]
        results[key] = result
    return results

def getStdDevs(newresults):
    stddevs = [0.0] * 8
    s0 = [0] * 8
    s1 = [0] * 8
    s2 = [0] * 8
    for key in newresults.keys():
        result = newresults[key]
        for i in range(8):
            rate = 1.0 * result[i * 2 + 1] / result[i * 2]
            s0[i] += 1
            s1[i] += rate
            s2[i] += rate * rate
    for i in range(8):
        stddevs[i] = math.sqrt(s0[i] * s2[i] - s1[i] * s1[i]) / s0[i]
    return stddevs

def standardize(newresults, means, stddevs):
    stdscores = {}
    for key in newresults.keys():
        result = newresults[key]
        stdscore = [0.0] * 8
        for i in range(8):
            stdscore[i] = (1.0 * result[i * 2 + 1] / result[i * 2] - means[i]) / stddevs[i]
        stdscores[key] = stdscore
    return stdscores

def outputResults(results, filename):
    file = open(filename, "w")
    file.write("PID, CAGood833, CABad833, CAGood666, CABad666, Bad-Good833, Bad-Good666, FalseCAGood833, FalseCABad833, FalseCAGood666, FalseCABad666\r\n")
    pids = sorted(results.keys())
    for pid in pids:
        file.write(str(pid) + ", ")
        good833 = bad833 = good666 = bad666 = falsegood833 = falsebad833 = falsegood666 = falsebad666 = 0.0
        if results[pid][4]:
            good833 = 1.0 * results[pid][0] / results[pid][4]
        if results[pid][5]:
            bad833 = 1.0 * results[pid][1] / results[pid][5]
        if results[pid][6]:
            good666 = 1.0 * results[pid][2] / results[pid][6]
        if results[pid][7]:
            bad666 = 1.0 * results[pid][3] / results[pid][7]
        if results[pid][12] != 0:
            falsegood833 = 1.0 * results[pid][8] / results[pid][12]
        if results[pid][13] != 0:
            falsebad833 = 1.0 * results[pid][9] / results[pid][13]
        if results[pid][14] != 0:
            falsegood666 = 1.0 * results[pid][10] / results[pid][14]
        if results[pid][15] != 0:
            falsebad666 = 1.0 * results[pid][11] / results[pid][15]
        file.write(str(good833) + ", " + str(bad833) + ", " + str(good666) + ", " + str(bad666) + ", ")
        file.write(str(bad833 - good833) + ", " + str(bad666 - good666) + ", ")
        file.write(str(falsegood833) + ", " + str(falsebad833) + ", " + str(falsegood666) + ", " + str(falsebad666))
        file.write("\r\n")
    file.close()

def outputSplits(scores0, scores1, filename):
    file = open(filename, "w")
    file.write("Split-half Scores\r\n\r\n")

    file.write("PID, Half, Good833-z-Hits, Good833-z-FAlarms, Bad833-z-Hits, Bad833-z-FAlarms,")
    file.write("Good666-z-Hits, Good666-z-FAlarms, Bad666-z-Hits, Bad666-z-FAlarms,,")
    file.write("Good833-d-prime, Bad833-d-prime, Good666-d-prime, Bad666-d-prime\r\n")
    pids = sorted(scores0.keys())
    for pid in pids:
        file.write(str(pid) + ", first, ")
        for i in range(8):
            file.write(str(scores0[pid][i]) + ", ")
        file.write(", ")
        for i in range(4):
            file.write(str(scores0[pid][i * 2] - scores0[pid][i * 2 + 1]) + ", ")
        file.write("\r\n")

        file.write(str(pid) + ", second, ")
        for i in range(8):
            file.write(str(scores1[pid][i]) + ", ")
        file.write(", ")
        for i in range(4):
            file.write(str(scores1[pid][i * 2] - scores1[pid][i * 2 + 1]) + ", ")
        file.write("\r\n")
    file.close()

def outputRates(results, means, newresults, scores, filename):
    file = open(filename, "w")
    file.write("PID, Good833PotentialHits, Good833Hits, Good833HitRate, ")
    file.write("Good833PotentialFAlarms, Good833FAlarms, Good833FAlarmRate, ")
    file.write("Bad833PotentialHits, Bad833Hits, Bad833HitRate, ")
    file.write("Bad833PotentialFAlarms, Bad833FAlarms, Bad833FAlarmRate, ")
    file.write("Good666PotentialHits, Good666Hits, Good666HitRate, ")
    file.write("Good666PotentialFAlarms, Good666FAlarms, Good666FAlarmRate, ")
    file.write("Bad666PotentialHits, Bad666Hits, Bad666HitRate, ")
    file.write("Bad666PotentialFAlarms, Bad666FAlarms, Bad666FAlarmRate\r\n")
    pids = sorted(results.keys())
    for pid in pids:
        file.write(str(pid) + ", ")
        for i in range(8):
            file.write(str(results[pid][i * 2]) + ", ")
            file.write(str(results[pid][i * 2 + 1]) + ", ")
            if results[pid][i * 2] > 0:
                file.write(str(1.0 * results[pid][i * 2 + 1] / results[pid][i * 2]) + ", ")
            else:
                file.write("0.00, ")
        file.write("\r\n")
    file.write("Means")
    for i in range(8):
        file.write(", , , " + str(means[i]))

    file.write("\r\n\r\n")
    file.write("Corrected results\r\n")
    file.write("PID, Good833PotentialHits, Good833Hits, Good833HitRate, ")
    file.write("Good833PotentialFAlarms, Good833FAlarms, Good833FAlarmRate, ")
    file.write("Bad833PotentialHits, Bad833Hits, Bad833HitRate, ")
    file.write("Bad833PotentialFAlarms, Bad833FAlarms, Bad833FAlarmRate, ")
    file.write("Good666PotentialHits, Good666Hits, Good666HitRate, ")
    file.write("Good666PotentialFAlarms, Good666FAlarms, Good666FAlarmRate, ")
    file.write("Bad666PotentialHits, Bad666Hits, Bad666HitRate, ")
    file.write("Bad666PotentialFAlarms, Bad666FAlarms, Bad666FAlarmRate\r\n")
    pids = sorted(newresults.keys())
    for pid in pids:
        file.write(str(pid) + ", ")
        for i in range(8):
            file.write(str(newresults[pid][i * 2]) + ", ")
            file.write(str(newresults[pid][i * 2 + 1]) + ", ")
            file.write(str(1.0 * newresults[pid][i * 2 + 1] / newresults[pid][i * 2]) + ", ")
        file.write("\r\n")

    file.write("\r\n\r\n")
    file.write("Standard Scores\r\n")
    file.write("PID, Good833-z-Hits, Good833-z-FAlarms, Bad833-z-Hits, Bad833-z-FAlarms,")
    file.write("Good666-z-Hits, Good666-z-FAlarms, Bad666-z-Hits, Bad666-z-FAlarms,,")
    file.write("Good833-d-prime, Bad833-d-prime, Good666-d-prime, Bad666-d-prime\r\n")
    pids = sorted(scores.keys())
    for pid in pids:
        file.write(str(pid) + ", ")
        for i in range(8):
            file.write(str(scores[pid][i]) + ", ")
        file.write(", ")
        for i in range(4):
            file.write(str(scores[pid][i * 2] - scores[pid][i * 2 + 1]) + ", ")
        file.write("\r\n")
    file.close()

if __name__ == "__main__":
    report = ""
    resultsFile = ""
    source = ""
    if len(sys.argv) != 4:
        print "Usage: python gnat.py [means | kinds | split] name_of_data_source_file name_of_results_file"
    else:
        report = sys.argv[1]
        source = sys.argv[2]
        resultsFile = sys.argv[3]
        if report == "means":
            d = getInquisitData(source)
            r = getResponseTimes(d)
            outputResults(r, resultsFile)
        elif report == "kinds":
            d = getInquisitDataForRates(source)
            r = getCounts(d)
            m = getMeans(r)
            nr = copy.deepcopy(r)
            nr = correctCounts(nr, m)
            s = getStdDevs(nr)
            scores = standardize(nr, m, s)
            outputRates(r, m, nr, scores, resultsFile)
        else:
            # split
            d = getInquisitDataForRatesSplitHalf(source)
            r0 = getCounts(d[0])
            m0 = getMeans(r0)
            nr0 = copy.deepcopy(r0)
            nr0 = correctCounts(nr0, m0)
            s0 = getStdDevs(nr0)
            scores0 = standardize(nr0, m0, s0)
            r1 = getCounts(d[1])
            m1 = getMeans(r1)
            nr1 = copy.deepcopy(r1)
            nr1 = correctCounts(nr1, m1)
            s1 = getStdDevs(nr1)
            scores1 = standardize(nr1, m1, s1)
            outputSplits(scores0, scores1, resultsFile)
