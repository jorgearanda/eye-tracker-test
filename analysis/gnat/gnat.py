import sys

def getInquisitData(filename):
    validLines = ["BKclimate_actiongoodRT833", "BKclimate_actionbadRT833", "BKclimate_actiongoodRT666", "BKclimate_actionbadRT666"]
    lines = open(filename, "r").readlines()
    data = []
    realTask = False
    for i in range(1, len(lines)):
        line = lines[i].split()
        if not realTask and line[4] == "pause":
            realTask = True
        if realTask and line[9] == "1" and line[11] in validLines and "good_false" not in line[4] and "bad_false" not in line[4]:
            dataPieces = []
            dataPieces.append(line[3]) # ParticipantID
            dataPieces.append(line[4]) # TrialCode
            dataPieces.append(line[7]) # ResponseTime
            dataPieces.append(line[11]) # BlockCode
            data.append(dataPieces)
        if realTask and line[4] == "reminder" or line[4] == "single":
            realTask = False
    return data

def getResponseTimes(data):
    results = {}
    for row in data:
        if int(row[0]) not in results:
            results[int(row[0])] = [0,0,0,0,0,0,0,0]
        pValues = results[int(row[0])]
        rt = int(row[2])
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
        results[int(row[0])] = pValues
    return results

def outputResults(results, filename):
    file = open(filename, "w")
    file.write("PID, CAGood833, CABad833, CAGood666, CABad666\r\n")
    pids = sorted(results.keys())
    for pid in pids:
        file.write(str(pid) + ", ")
        for i in range(4):
            if results[pid][i + 4] != 0:
                file.write(str(results[pid][i] / results[pid][i + 4]) + ", ")
            else:
                file.write("0, ")
        file.write("\r\n")
    file.close()

if __name__ == "__main__":
    resultsFile = ""
    source = ""
    if len(sys.argv) != 3:
        print "Usage: python gnat.py name_of_data_source_file name_of_results_file"
    else:
        source = sys.argv[1]
        resultsFile = sys.argv[2]
        d = getInquisitData(source)
        r = getResponseTimes(d)
        outputResults(r, resultsFile)