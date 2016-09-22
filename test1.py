#for GUI
import Tkinter, tkFileDialog
from Tkinter import *
#for messageboxes
import tkMessageBox
#to find if files/folders exist
import os.path
#this is unused, it was used for testing
import ctypes

top = Tkinter.Tk() #set up basic GUI
top.configure(background="#a1dbcd")

top.title("Video Creator")

El = Entry #Upload video entry
#variable that corresponds to upload video entry
v = StringVar(top, value='')
#variable that corresponds to upload config file entry
v2 = StringVar(top, value='')
#this is unused, was used for testing
v3 = '/home/joseph/Downloads/ffmpeg-3.1.1/test.mp4'
startLine = "" #unused
endLine = "" #unused
#output folder for created video
outFolder = StringVar(top, value='')
#These two correspond to the 'Stalls' and 'Resolution' checkboxes
CheckStalls = IntVar()
CheckRes = IntVar()

CheckYUV = IntVar()
CheckDash = IntVar()

lstDash = []

def dashify(dashVideo): #This creates a DASH video from an MP4 file, unused in final version

    dashedTemp = stringFrame = str(v.get()).rpartition('.')[0]
    dashedTemp2 = stringFrame = str(dashedTemp).rpartition('/')[2]
    #print dashedTemp2
    dashVideo = dashedTemp2 + "_dashinit.mp4"
    
    bashCommand = "MP4Box -frag " + txtFrag.get() + " -dash " + txtSeg.get() + " "+ dashVideo + ""
    print bashCommand
    
    import subprocess
    process = subprocess.Popen([bashCommand], stdout=subprocess.PIPE, shell=True)
    output = process.communicate()[0]

#initial function called
def createVideoInitial():

#clears lists, to check if config file is configures correctly (readcolumnFirst)
    del lstTimes[:]
    del lstStalls[:]
    del lstRes[:]

    #Start of Error Checking

    #Check if video file exists
    if not fileExists(v.get()):
        tkMessageBox.showwarning('Warning', 'The video file does not exist')
        return
    #Check if config file exists
    if not fileExists(v2.get()):
        tkMessageBox.showwarning('Warning', 'The config file does not exist')
        return
    #Check if config file is a text file
    if not fileType(v2.get(), '.txt'):
        tkMessageBox.showwarning('Warning', 'The config file must be a text file')
        return
    #Check if config file is configured correctly
    if not readColumnFirst():
        tkMessageBox.showwarning('Warning', 'The config file is not configured properly')
        return
    #Check that the start line is a number
    if txtStart.get() != '':
        if not txtStart.get().isdigit():
            tkMessageBox.showwarning('Warning', 'You must enter a number in the Start Line')
            return
    #Check that the end line is a number
    if txtEnd.get() != '':
        if not txtEnd.get().isdigit():
            tkMessageBox.showwarning('Warning', 'You must enter a number in the End Line')
            return
    #Check that the start line is smaller than the end line    
    if txtStart.get() != '' and txtEnd.get() != '':
        if int(txtStart.get()) > int(txtEnd.get()):
            tkMessageBox.showwarning('Warning', 'The number in the Start Line must be smaller than the number in the End Line')
            return
    #Check that the output folder isn't empty
    if outFolder.get() == '':
        tkMessageBox.showwarning('Warning', 'You must choose an output folder')
    else:
        #Check that the output folder exists
        if not folderExists(outFolder.get()):
            tkMessageBox.showwarning('Warning', 'The output folder does not exist')
            return
        #Check that output file doesn't already exist (to avoid Bash Y/N replacement prompt)
    if fileExists(outFolder.get() + '/' + txtName.get()):
        tkMessageBox.showwarning('Warning', 'The file already exists. Please choose a different name.')
        return
    
    #if fileType(v.get(), '.mp4'):
     #   createvideo()
    #if fileType(v.get(), '.yuv'):
     #   createVideoYUV()

    if CheckYUV.get() == 1:
        createVideoYUV()
    elif CheckDash.get() == 1:
        createVideoDash()
    else:
        createVideo()
    return

#This creates the MP4 DASH output video.
def createVideoDash():

#Look at the createVideo() function first, which creates MP4 video, for full comments on the BASH command.

    #Start of Error Checking
   
    #Check if video file is mp4
    if not fileType(v.get(), '.mp4'):
        tkMessageBox.showwarning('Warning', 'The video file must be an .mp4 file')
        return
    #Check that the name of the output video ends in .mp4    
    if not fileType(txtName.get(), '.mp4'):
        tkMessageBox.showwarning('Warning', 'The output file must be an .mp4 file')
        return

    #End of Error Checking
    
    audioTest = ""
    audioTest = str(checkForAudio())

    #gets resolution of video
    res = getResolution()

    #get number of frames of video
    numFrames = getNumberOfFrames()
    #print 'numframes: ' + str(numFrames)

    #clears lists after error checking
    del lstTimes[:]
    del lstStalls[:]
    del lstRes[:]
    del lstDash[:]

    #checks what method to use (depending if the user has specified lines to use in config file or not)
    if txtStart.get() != "" and txtEnd.get() != "":
        readColumnLines()
    else:
        readColumn()

    #Used to create Bash string
    j = 0

    #Main bulk of video statement; includes start, end, loops, res changes, etc.
    strVid = ""

    #Used to split video
    strVid3 = ""

    numLines = len(lstTimes)

    occurences = v.get().count('/')

#From the next line to 'dashify(dashvideo)' (and 'dashVideo = str(v.get()) can be uncommented if you want to use the dashify() function above, which creates a dashed MP4 file from a standard MP4 file. At present this simply reads in a dashed MP4 file.

    #dashedTemp = stringFrame = str(v.get()).rpartition('.')[0]
    #dashedTemp2 = stringFrame = str(dashedTemp).rpartition('/')[2]
    #print dashedTemp2
    #dashVideo = dashedTemp2 + "_dashinit.mp4"

    dashVideo = str(v.get())

    #dashify(dashVideo)


    #Beginning statement
    strVid5 = "ffmpeg -i " + dashVideo + " -filter_complex \"[0:v] split = "

    #Comes immediately before concat at end
    strVid2 = ""

    #Used to create audio part of script
    strAud2 = ""

#This gets the frames per second, and divides it by 1000 to get the frames per millisecond. This can then be multiplied, first by the segment length (specified in the GUI), and then by the segment specified in the current row of the config file.
    stringFrame = getFrameRate(dashVideo).rpartition('/')[0]
    frameRate = float(stringFrame)
    miniFrame = frameRate/1000

    #This adds to the script
    while (j < numLines):
        strVid3 += "[v" + str(j) + "]"
        if audioTest != "":
            strAud2 += "[a" + str(j) + "]"
        strVid2 += "[" + str(j) + "v]"
        if audioTest != "":
            strVid2 += "[" + str(j) + "a]"
            
        j += 1

    i = 0 #counter to go through the three lists
    int1 = 0 #This holds the last 'end frame'.
    extraFrames = 0 #this is unused

    #Loop through the lists
    for p in lstTimes:

        segment = int(txtSeg.get())*int(lstTimes[i])
        #print "segment: " + str(segment)
        endTime1 = float(miniFrame) * float(segment)
        #print "miniFrame: " + str(miniFrame)
        #print "endtime1: " + str(endTime1)
        endTime = int(round(endTime1))
        #print "endtime: " + str(endTime)

         #Check that the end frame is bigger than the start frame
        if int(endTime) + 1 < int1:
            return
        
        
        #Start of the Bash command
        strVid += "; \
        [v" + str(i) +"]trim=start_frame=" + str(int1) + ":end_frame=" + str(int(endTime)+1) + ", "

        #Checks if the user has checked the CheckRes checkbox (handles resolution changes)
        if CheckRes.get() == 1:
            if lstRes[i] != res:
                strVid += "scale=" + lstRes[i] + ", scale=" + res + ", "

        #Checks if the user has checked the CheckStalls checkbox (handles stalls)
        #Adds loops based on the config file
        if CheckStalls.get() == 1:
            print "Stalls: " + lstStalls[i]
            strVid += "loop=" + lstStalls[i] + ":1:" + str(int(endTime) - int1) + ", "

        #End of one line of the bash command
        strVid += "setpts=N/FRAME_RATE/TB[" + str(i) + "v]"

        #Changes int1 to be the end time of the previous line
        lstDash.append(str(endTime))
        int1 = int(endTime)+1
        i += 1 #increments i

    #This creates a last line to complete the video, if the user did not specify the last frame
    if (int(numFrames)+1) - int1 > 0:
        strVid += "; \
        [v" + str(i) + "]trim=start_frame=" + str(int1) + ":end_frame=" + str(int(numFrames)) + ", setpts=N/FRAME_RATE/TB[" + str(i) + "v]"
        strVid2 += "[" + str(j) + "v]"
        if audioTest != "":
            strVid2 += "[" + str(j) + "a]"
        strVid3 += "[v" + str(j) + "]"
        if audioTest != "":
            strAud2 += "[a" + str(j) + "]"
        numLines += 1

    strVid5 += str(numLines) + strVid3

    #Audio Starts Here

    

    if audioTest != "":
        
        #gets frame rate, takes the part before the '/' e.g. 25/1 becomes 25
        stringFrame = getFrameRate(dashVideo).rpartition('/')[0]
        frameRate = int(stringFrame) 
        sampleRate = int(getSampleRate()) #gets audio sample rate
        samplesPerFrame = sampleRate/frameRate #calculates samples per frame
    

        k = 0 #incremetor
        intAud = 0 #this becomes the end_pts (end sample) of the previous line

        #beginning of audio line
        strAud = "; \
        [0:a]asplit=" + str(numLines) + strAud2

        #calculates the start and end samples based on the frames specified in the config file
        #start and end samples correspond to start and end frames above
        for r in lstTimes:

            segment = int(txtSeg.get())*int(lstTimes[k])
            #print "segment: " + str(segment)
            endTime1 = float(miniFrame) * float(segment)
            #print "miniFrame: " + str(miniFrame)
            #print "endtime1: " + str(endTime1)
            endTime = int(round(endTime1))
            #print "endtime: " + str(endTime)
            
            lstTimes1 = int(endTime)+1
            strAud += "; \
            [a" + str(k) + "]atrim=start_pts=" + str(intAud) + ":end_pts=" + str(samplesPerFrame*lstTimes1) + ",asetpts=N/SR/TB[" + str(k) + "a]"

            intAud = samplesPerFrame*lstTimes1 #start sample of next line becomes end sample of last line
            k+=1 #increment k

    
        #Add extra line if the last frame wasn't specified in the config file
        if (int(numFrames)+1) - int1 > 0:
            strAud += "; \
            [a" + str(k) + "]atrim=start_pts=" + str(intAud) + ":end_pts=" + str(samplesPerFrame*int(numFrames)) + ", asetpts=N/SR/TB[" + str(k) + "a]"

        #Audio Ends Here
    else:
        strAud = ""

    #This nearly completes the Bash command.
    
    strVid += strAud + ";\
    " + strVid2 + "concat=n=" + str(numLines)

    if audioTest == "":
        if CheckStalls.get() == 1:
            strVid += ":v=1[v]\" -map \"[v]\"  outputNew.mp4"
        else:
            strVid += ":v=1[v]\" -map \"[v]\"  " + outFolder.get() + "/" + txtName.get()
    else:
        if CheckStalls.get() == 1:
            strVid += ":v=1:a=1[v][a]\" -map \"[v]\" -map \"[a]\"  outputNew.mp4"
        else:
            strVid += ":v=1:a=1[v][a]\" -map \"[v]\" -map \"[a]\"  " + outFolder.get() + "/" + txtName.get()

    #This adds the first line to complete the command
    strVid4 = strVid5 + strVid

    print strVid4 #testing

    print str(CheckStalls) #testing
    print str(CheckRes) #testing

    #Bash command output logic
    import subprocess
    #process = subprocess.Popen([strVid], stdout=subprocess.PIPE, shell=True)
    #output = process.communicate()[0]

    #outputs strVid4 to Bash
    try:
        subprocess.check_call(strVid4, shell=True)
    except OSError as e: #happens if ffmpeg is not installed
        if e.errno == os.errno.ENOENT:
            tkMessageBox.showwarning('Warning', 'FFmpeg not installed')
            return
    except:
        tkMessageBox.showwarning('Warning', 'An error has occurred.')




    #Start of overlay
    if CheckStalls.get() == 1:
        temp = ""
        l = 0
        k = 0

        strOvr = "ffmpeg -i outputNew.mp4 -i 27.gif -filter_complex \"[0][1]"

        extra = 0
        last = 0
        #print "Start"

        if len(lstDash) > 1:

            for s in lstDash[:-1]:
                #print "Start2"
        
                if l == 0:
                    strOvr += " overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(n," + str(int(lstDash[l]) + extra) + "," + str(int(lstDash[l]) + int(lstStalls[l])) + ")'[tmp" + str(k)+"]"    
                else:
                    print "PROBLEM2"
                    extra += int(lstStalls[l-1])
                    #last =
                    if int(lstStalls[l]) != 0:
                        strOvr += "; \
                        " + temp + "[1]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(n," + str(int(lstDash[l]) + extra) + "," + str(int(lstDash[l]) + extra + int(lstStalls[l])) + ")'[tmp" + str(k)+"]"
    
                if int(lstStalls[l]) != 0:
                    temp = "[tmp" + str(k) + "]"
                    k += 1
                l += 1
        
            else:
                print "PROBLEM"
                extra += int(lstStalls[l-1])
                strOvr += "; \
                " + temp + "[1]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(n," + str(int(lstDash[l]) + extra) + "," + str(int(lstDash[l]) + extra + int(lstStalls[l])) + ")'"
        else:
            strOvr += " overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(n," + str(int(lstDash[l]) + extra) + "," + str(int(lstDash[l]) + int(lstStalls[l])) + ")'"     
        


        strOvr += "\" -c:a copy " + outFolder.get() + "/" + txtName.get()

        print strOvr

        #Bash command output logic
        import subprocess
        #process = subprocess.Popen([strVid], stdout=subprocess.PIPE, shell=True)
        #output = process.communicate()[0]

        #outputs strVid4 to Bash
    
        subprocess.check_call(strOvr, shell=True)

    #End of overlay
        
    if fileExists("outputNew.mp4"):
        remove = "rm outputNew.mp4"
        subprocess.check_call(remove, shell=True)
        
    return

#This creates the YUV output video.
def createVideoYUV():

    #Start of Error Checking
    
    #Check if video file is yuv
    if not fileType(v.get(), '.yuv'):
        tkMessageBox.showwarning('Warning', 'The video file must be a .yuv file')
        return
    
    #Check that the name of the output video ends in .yuv    
    if not fileType(txtName.get(), '.yuv'):
        tkMessageBox.showwarning('Warning', 'The output file must be a .yuv file')
        return

    #Check that the resolution text box isn't empty
    if txtRes.get() == '':
        tkMessageBox.showwarning('Warning', 'You must enter a resolution for YUV files.')
        return

    #Check that the frame rate textbox isn't empty
    if txtFrame.get() == '':
        tkMessageBox.showwarning('Warning', 'You must enter a frame rate for YUV files.')
        return

    #Check that the duration textbox isn't empty
    if txtDur.get() == '':
        tkMessageBox.showwarning('Warning', 'You must enter a duration for YUV files.')
        return

    #Check that the start line is a number
    if not txtFrame.get().isdigit():
        tkMessageBox.showwarning('Warning', 'You must enter a number for the frame rate')
        return

    #Check that the duration is a number
    if not txtDur.get().isdigit():
        tkMessageBox.showwarning('Warning', 'You must enter a number for the duration')
        return

    #End of Error Checking

    #gets resolution of video
    res = txtRes.get()

    #get number of frames of video
    numFrames = txtDur.get()

    #clears lists after error checking
    del lstTimes[:]
    del lstStalls[:]
    del lstRes[:]

    #checks what method to use (depending if the user has specified lines to use in config file or not)
    if txtStart.get() != "" and txtEnd.get() != "":
        readColumnLines()
    else:
        readColumn()

    #Used to create Bash string
    j = 0

    #Main bulk of video statement; includes start, end, loops, res changes, etc.
    strVid = ""

    #Used to split video
    strVid3 = ""

    numLines = len(lstTimes)

    #Beginning of Bash statement - includes extra parta for YUV (between -f and -i)
    strVid5 = "ffmpeg -f rawvideo -vcodec rawvideo -s " + txtRes.get() + " -r " + txtFrame.get() + " -pix_fmt yuv420p -i " + str(v.get()) + " -filter_complex \"[0:v] split = "

    #Comes immediately before concat at end
    strVid2 = ""

    #This adds to the script
    while (j < numLines):
        strVid3 += "[v" + str(j) + "]"
        strVid2 += "[" + str(j) + "v]"
    
        j += 1

    i = 0 #counter to go through the three lists
    int1 = 0 #This holds the last 'end frame'. 
    extraFrames = 0 #This is unused

    #Loop through the lists
    for p in lstTimes:
        #Check that the end frame is bigger than the start frame
        if int(lstTimes[i]) + 1 < int1:
            return
        #Start of the Bash command
        strVid += "; \
        [v" + str(i) +"]trim=start_frame=" + str(int1) + ":end_frame=" + str(int(lstTimes[i])+1) + ", "

        #Checks if the user has checked the CheckRes checkbox (handles resolution changes)
        if CheckRes.get() == 1:
            if lstRes[i] != res:
                strVid += "scale=" + lstRes[i] + ", scale=" + res + ", "

        #Checks if the user has checked the CheckStalls checkbox (handles stalls)
        #Adds loops based on the config file
        if CheckStalls.get() == 1:
            strVid += "loop=" + lstStalls[i] + ":1:" + str(int(lstTimes[i]) - int1) + ", "

        #End of one line of the bash command
        strVid += "setpts=N/FRAME_RATE/TB[" + str(i) + "v]"

        #Changes int1 to be the end time of the previous line
        int1 = int(lstTimes[i])+1
        #extraFrames += int(lstStalls[i])
        i += 1 #increments i

    #This creates a last line to complete the video, if the user did not specify the last frame in the config file.
    if (int(numFrames)+1) - int1 > 0:
        strVid += "; \
        [v" + str(i) + "]trim=start_frame=" + str(int1) + ":end_frame=" + str(int(numFrames)) + ", setpts=N/FRAME_RATE/TB[" + str(i) + "v]"
        strVid2 += "[" + str(j) + "v]"
        strVid3 += "[v" + str(j) + "]"
        numLines += 1

    #This concatenates the video string together.
    strVid5 += str(numLines) + strVid3
    
    strVid += ";\
    " + strVid2 + "concat=n=" + str(numLines) + ":v=1[v]\" -map \"[v]\" " + outFolder.get() + "/" + txtName.get()

    #This adds the first line to complete the command
    strVid4 = strVid5 + strVid

    print strVid4 #testing

    print str(CheckStalls) #testing
    print str(CheckRes) #testing

    #Bash command output logic
    import subprocess
    #process = subprocess.Popen([strVid], stdout=subprocess.PIPE, shell=True)
    #output = process.communicate()[0]

    #outputs strVid4 to Bash
    try:
        subprocess.check_call(strVid4, shell=True)
    except OSError as e: #happens if ffmpeg is not installed
        if e.errno == os.errno.ENOENT:
            tkMessageBox.showwarning('Warning', 'FFmpeg not installed')
            return
    except:
        tkMessageBox.showwarning('Warning', 'An error has occurred.')


    #Start of overlay

    temp = ""
    l= 0
    k = 0

    strOvr = "ffmpeg -f rawvideo -vcodec rawvideo -s " + txtRes.get() + " -r " + txtFrame.get() + " -pix_fmt yuv420p -i outputNew.yuv -i 27.gif -filter_complex \"[0][1]"

    extra = 0
    last = 0
        

    for s in lstTimes[:-1]:

        if l == 0:
            strOvr += " overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(n," + str(int(lstTimes[l]) + extra) + "," + str(int(lstTimes[l]) + int(lstStalls[l])) + ")'[tmp" + str(k)+"]"    
        else:
            extra += int(lstStalls[l-1])
            #last =
            if int(lstStalls[l]) != 0:
                strOvr += "; \
                " + temp + "[1]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(n," + str(int(lstTimes[l]) + extra) + "," + str(int(lstTimes[l]) + extra + int(lstStalls[l])) + ")'[tmp" + str(k)+"]"
    
        if int(lstStalls[l]) != 0:
            temp = "[tmp" + str(k) + "]"
            k += 1
        l += 1
        
    else:
        extra += int(lstStalls[l-1])
        strOvr += "; \
        " + temp + "[1]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(n," + str(int(lstTimes[l]) + extra) + "," + str(int(lstTimes[l]) + extra + int(lstStalls[l])) + ")'"
        


    strOvr += "\" -c:a copy " + outFolder.get() + "/" + txtName.get()

    print strOvr

    #Bash command output logic
    import subprocess
    #process = subprocess.Popen([strVid], stdout=subprocess.PIPE, shell=True)
    #output = process.communicate()[0]

    #outputs strVid4 to Bash
    
    subprocess.check_call(strOvr, shell=True)

    #End of overlay

    remove = "rm outputNew.yuv"
    subprocess.check_call(remove, shell=True)

    return


#Lists to hold data from config file
lstTimes = []
lstStalls = []
lstRes = []

# Code to add widgets will go here...

#Used for video upload
def test():
    #top.withdraw() #use to hide tkinter window
    currdir = "/home"
    #currdir = "/home/joseph/Downloads/ffmpeg-3.1.1"
    tempdir = tkFileDialog.askopenfilename(parent=top, initialdir=currdir, title='Please select a file')
    if len(tempdir) > 0:
        print "You chose %s" % tempdir
        v.set(tempdir)
        top.update()
        #top.deiconify()
        return

#used to set output folder
def outputFolder():
    #top.withdraw() #use to hide tkinter window
    currdir = "/home"
    tempdir = tkFileDialog.askdirectory(parent=top, initialdir=currdir, title='Please select a directory')
    if len(tempdir) > 0:
        #print "You chose %s" % tempdir
        outFolder.set(tempdir)
        top.update()
        #top.deiconify()
        return

def readConfig():
    #top.withdraw() #use to hide tkinter window
    currdir = "/home"
    #currdir = "/home/joseph"
    tempdir = tkFileDialog.askopenfilename(parent=top, initialdir=currdir, title='Please select a file')
    if len(tempdir) > 0:
        print "You chose %s" % tempdir
        v2.set(tempdir)
        top.update()
        #top.deiconify()
        return

#Used to get native resolution of video
def getResolution():
    bashCommand = "eval $(ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height,width " + str(v.get()) + ")"
    bashCommand2 = "size=${streams_stream_0_width}x${streams_stream_0_height}"
    bashCommand3 = "echo $size"
    
    #This communicates with a bash window
    import subprocess
    process = subprocess.Popen("{}; {}; {}".format(bashCommand, bashCommand2, bashCommand3), stdout=subprocess.PIPE, shell=True)
    process2 = subprocess.Popen([bashCommand2], stdout=subprocess.PIPE, shell=True)
    process3 = subprocess.Popen([bashCommand3], stdout=subprocess.PIPE, shell=True)
    output = process.communicate()[0]
    print "Output: " + output
    #subprocess.call(["./trim.sh", "HELP"], shell=True)
    return output

#Gets the video frame rate
def getFrameRate(string):
    bashCommand = "ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate -of default=noprint_wrappers=1:nokey=1 " + string + ""
    #print v
    
    import subprocess
    process = subprocess.Popen([bashCommand], stdout=subprocess.PIPE, shell=True)
    output = process.communicate()[0]
    #print "Output: " + str(48000/int(output))
    #print output.rpartition('/')[0]
    return str(output)

#Gets the audio sample rate
def getSampleRate():
    bashCommand = "ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of default=noprint_wrappers=1:nokey=1 " + str(v.get())
    
    import subprocess
    process = subprocess.Popen([bashCommand], stdout=subprocess.PIPE, shell=True)
    output = process.communicate()[0]
    print output
    return str(output)

#Gets the total number of frames in the video
def getNumberOfFrames():
    bashCommand = "ffprobe -v error -count_frames -select_streams v:0 \
  -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 \
  " + str(v.get()) + ""
    print v
    
    import subprocess
    process = subprocess.Popen([bashCommand], stdout=subprocess.PIPE, shell=True)
    output = process.communicate()[0]
    print "Output Frames: " + output
    return str(output)

#Used to check if the first line of the config file is configured correctly
def readColumnFirst():
    
    crs = open(str(v2.get()), "r")
    #crs.readline()
    for columns in ( raw.strip().split() for raw in crs ):  
        #print "Output: " + columns[0]
        
        try:
            lstTimes.append(str(columns[0]))
        except:
            tkMessageBox.showwarning('Warning', 'The config file is not configured properly.')
        try:
            lstStalls.append(str(columns[1]))
        except:
            continue
        try:
            lstRes.append(str(columns[2]))
        except:
            continue
    if lstStalls[0] != 'Stalls' or lstRes[0] != 'Res':
        print lstTimes[0]
        print lstStalls[0]
        print lstRes[0]
        print 'Yes'
        return False
    crs.close()
    return True

#test method
def helloCallBack():
   tkMessageBox.showinfo( "Hello Python", "Hello World")
   return

#test method, was replace with the createVideo() method below
def openBash():
    bashCommand = "ffmpeg -i " + str(v.get()) + " -filter_complex        \"[0:v]split=2[v0][v1]; \
        [v0]trim=start_frame=0:end_frame=50, loop=25:1:49, setpts=N/FRAME_RATE/TB[0v]; \
        [v1]trim=start_frame=50:end_frame=145, scale=320:240, scale=640:480, loop=25:1:94, setpts=N/FRAME_RATE/TB[1v]; \
        [0v][1v]concat=n=2:v=1[v]\"        -map \"[v]\"  outva5.mp4"
    import subprocess
    process = subprocess.Popen([bashCommand], stdout=subprocess.PIPE, shell=True)
    output = process.communicate()[0]
    print bashCommand
    #subprocess.call(["./trim.sh", "HELP"], shell=True)
    return

#check if a file exists
def fileExists(file):

    #if os.path.isfile(file):
     #   return 1
    #else:
     #   return 0
     return os.path.isfile(file)

#check if a folder exists
def folderExists(file):

    #if os.path.isfile(file):
     #   return 1
    #else:
     #   return 0
     return os.path.isdir(file)

#check if a file is of a certain type
def fileType(path, file):

    #if path.endswith(file):
     #   return 1
    #else:
     #   return 0
     print path.endswith(file)
     return path.endswith(file)

#Populates lists from config file if user uses all lines from config file
def readColumn():
    
    crs = open(str(v2.get()), "r")
    crs.readline()
    for columns in ( raw.strip().split() for raw in crs ):  
        #print "Output: " + columns[0]
        try:
            lstTimes.append(str(columns[0]))
            print "Column 0: " + columns[0]
        except:
            tkMessageBox.showwarning('Warning', 'The config file is not configured properly.')
        if CheckStalls.get() == 1:
            try:
                #print "Column 1: " + columns[1]
                #print "Column 2: " + columns[2]
                lstStalls.append(str(columns[1]))
            except:
                continue
        if CheckRes.get() == 1:
            try:
                #print "Column 1: " + columns[1]
                #print "Column 2: " + columns[2]
                lstRes.append(str(columns[2]))
            except:
                continue
    crs.close()
    return

#test method
def test2():
    readColumn()
    for p in lstRes:
        print(p)

#test method
def test3():
    dashify()

#This creates the MP4 output video.
def createVideo():
    
    #This is an example script:
    #ffmpeg -i test.mp4 -filter_complex        "[0:v]split=3[v0][v1][v2]; \
        #[v0]trim=start_frame=0:end_frame=30, loop=25:1:29, setpts=N/FRAME_RATE/TB[0v]; \
	#[v1]trim=start_frame=30:end_frame=101, loop=50:1:70, setpts=N/FRAME_RATE/TB[1v]; \
	#[v2]trim=start_frame=101:end_frame=145, setpts=N/FRAME_RATE/TB[2v]; \
        #[0:a]asplit=3[a0][a1][a2]; \
        #[a0]atrim=start_pts=0:end_pts=57600,asetpts=N/SR/TB[0a]; \
	#[a1]atrim=start_pts=57600:end_pts=193920,asetpts=N/SR/TB[1a]; \
	#[a2]atrim=start_pts=193920:end_pts=280320,asetpts=N/SR/TB[2a]; \
        #[0v][0a][1v][1a][2v][2a]concat=n=3:v=1:a=1[v][a]"        -map "[v]" -map "[a]" outva9.mp4

    #Start of Error Checking

   
    #Check if video file is mp4
    if not fileType(v.get(), '.mp4'):
        tkMessageBox.showwarning('Warning', 'The video file must be an .mp4 file')
        return
    #Check that the name of the output video ends in .mp4    
    if not fileType(txtName.get(), '.mp4'):
        tkMessageBox.showwarning('Warning', 'The output file must be an .mp4 file')
        return

    #End of Error Checking
    
    audioTest = ""
    audioTest = str(checkForAudio())

    #gets resolution of video
    res = getResolution()

    #get number of frames of video
    numFrames = getNumberOfFrames()
    #print 'numframes: ' + str(numFrames)

    #clears lists after error checking
    del lstTimes[:]
    del lstStalls[:]
    del lstRes[:]

    #checks what method to use (depending if the user has specified lines to use in config file or not)
    if txtStart.get() != "" and txtEnd.get() != "":
        readColumnLines()
    else:
        readColumn()

    #Used to create Bash string
    j = 0

    #Main bulk of video statement; includes start, end, loops, res changes, etc.
    strVid = ""

    #Used to split video
    strVid3 = ""

    numLines = len(lstTimes)

    #Beginning statement
    strVid5 = "ffmpeg -i " + str(v.get()) + " -filter_complex \"[0:v] split = "

    #Comes immediately before concat at end
    strVid2 = ""

    #Used to create audio part of script
    strAud2 = ""

    #This adds to the script
    while (j < numLines):
        strVid3 += "[v" + str(j) + "]" #In above example, this creates [v0][v1][v2] (first line)
        if audioTest != "":
            strAud2 += "[a" + str(j) + "]" #In above example, this creates [a0][a1][a2] (first line of audio)
        strVid2 += "[" + str(j) + "v]" #In above example, this creates [0v][0a][1v][1a][2v][2a] (last line)
        if audioTest != "":
            strVid2 += "[" + str(j) + "a]"
            
        j += 1

    i = 0 #counter to go through the three lists
    int1 = 0 #This holds the last 'end frame'. In the example above, it would hold 0, 30, and finally 101
    extraFrames = 0 #this is unused

    #Loop through the lists
    for p in lstTimes:
        #Check that the end frame is bigger than the start frame
        if int(lstTimes[i]) + 1 < int1:
            return
        #Start of the Bash command
        strVid += "; \
        [v" + str(i) +"]trim=start_frame=" + str(int1) + ":end_frame=" + str(int(lstTimes[i])+1) + ", "

        #Checks if the user has checked the CheckRes checkbox (handles resolution changes)
        if CheckRes.get() == 1:
            if lstRes[i] != res:
                strVid += "scale=" + lstRes[i] + ", scale=" + res + ", "

        #Checks if the user has checked the CheckStalls checkbox (handles stalls)
        #Adds loops based on the config file
        if CheckStalls.get() == 1:
            print "Stalls: " + lstStalls[i]
            strVid += "loop=" + lstStalls[i] + ":1:" + str(int(lstTimes[i]) - int1) + ", "

        #End of one line of the bash command
        strVid += "setpts=N/FRAME_RATE/TB[" + str(i) + "v]"

        #Changes int1 to be the end time of the previous line
        int1 = int(lstTimes[i])+1
        i += 1 #increments i

    #This creates a last line to complete the video, if the user did not specify the last frame
    if (int(numFrames)+1) - int1 > 0:
        strVid += "; \
        [v" + str(i) + "]trim=start_frame=" + str(int1) + ":end_frame=" + str(int(numFrames)) + ", setpts=N/FRAME_RATE/TB[" + str(i) + "v]"
        strVid2 += "[" + str(j) + "v]"
        if audioTest != "":
            strVid2 += "[" + str(j) + "a]"
        strVid3 += "[v" + str(j) + "]"
        if audioTest != "":
            strAud2 += "[a" + str(j) + "]"
        numLines += 1

    #This concatenates the video string together. In the above example:
    #strVid5 = ffmpeg -i test.mp4 -filter_complex "[0:v]split=
    #numLines = 3
    #strVid3 = [v0][v1][v2]
    strVid5 += str(numLines) + strVid3

    

    #Audio Starts Here

    

    if audioTest != "":
        
        #gets frame rate, takes the part before the '/' e.g. 25/1 becomes 25
        stringFrame = getFrameRate(v.get()).rpartition('/')[0]
        frameRate = int(stringFrame) 
        sampleRate = int(getSampleRate()) #gets audio sample rate
        samplesPerFrame = sampleRate/frameRate #calculates samples per frame
    

        k = 0 #incremetor
        intAud = 0 #this becomes the end_pts (end sample) of the previous line

        #beginning of audio line
        strAud = "; \
        [0:a]asplit=" + str(numLines) + strAud2

        #calculates the start and end samples based on the frames specified in the config file
        #start and end samples correspond to start and end frames above
        for r in lstTimes:
            lstTimes1 = int(lstTimes[k])+1
            strAud += "; \
            [a" + str(k) + "]atrim=start_pts=" + str(intAud) + ":end_pts=" + str(samplesPerFrame*lstTimes1) + ",asetpts=N/SR/TB[" + str(k) + "a]"

            intAud = samplesPerFrame*lstTimes1 #start sample of next line becomes end sample of last line
            k+=1 #increment k

    
        #Add extra line if the last frame wasn't specified in the config file
        if (int(numFrames)+1) - int1 > 0:
            strAud += "; \
            [a" + str(k) + "]atrim=start_pts=" + str(intAud) + ":end_pts=" + str(samplesPerFrame*int(numFrames)) + ", asetpts=N/SR/TB[" + str(k) + "a]"

        #Audio Ends Here
    else:
        strAud = ""

    #This nearly completes the Bash command. In the above example, this is what stringVid will be:

        #[v0]trim=start_frame=0:end_frame=30, loop=25:1:29, setpts=N/FRAME_RATE/TB[0v]; \
	#[v1]trim=start_frame=30:end_frame=101, loop=50:1:70, setpts=N/FRAME_RATE/TB[1v]; \
	#[v2]trim=start_frame=101:end_frame=145, setpts=N/FRAME_RATE/TB[2v]; \
        #[0:a]asplit=3[a0][a1][a2]; \
        #[a0]atrim=start_pts=0:end_pts=57600,asetpts=N/SR/TB[0a]; \
	#[a1]atrim=start_pts=57600:end_pts=193920,asetpts=N/SR/TB[1a]; \
	#[a2]atrim=start_pts=193920:end_pts=280320,asetpts=N/SR/TB[2a]; \
        #[0v][0a][1v][1a][2v][2a]concat=n=3:v=1:a=1[v][a]"        -map "[v]" -map "[a]" outva9.mp4
    
    strVid += strAud + ";\
    " + strVid2 + "concat=n=" + str(numLines)

    if audioTest == "":
        if CheckStalls.get() == 1:
            strVid += ":v=1[v]\" -map \"[v]\"  outputNew.mp4"
        else:
            strVid += ":v=1[v]\" -map \"[v]\"  " + outFolder.get() + "/" + txtName.get()
    else:
        if CheckStalls.get() == 1:
            strVid += ":v=1:a=1[v][a]\" -map \"[v]\" -map \"[a]\"  outputNew.mp4"
        else:
            strVid += ":v=1:a=1[v][a]\" -map \"[v]\" -map \"[a]\"  " + outFolder.get() + "/" + txtName.get()

    #This adds the first line to complete the command
    strVid4 = strVid5 + strVid

    print strVid4 #testing

    print str(CheckStalls) #testing
    print str(CheckRes) #testing

    #Bash command output logic
    import subprocess
    #process = subprocess.Popen([strVid], stdout=subprocess.PIPE, shell=True)
    #output = process.communicate()[0]

    #outputs strVid4 to Bash
    try:
        subprocess.check_call(strVid4, shell=True)
    except OSError as e: #happens if ffmpeg is not installed
        if e.errno == os.errno.ENOENT:
            tkMessageBox.showwarning('Warning', 'FFmpeg not installed')
            return
    except:
        tkMessageBox.showwarning('Warning', 'An error has occurred.')




    #Start of overlay
    if CheckStalls.get() == 1:
        temp = ""
        l = 0
        k = 0

        strOvr = "ffmpeg -i outputNew.mp4 -i 27.gif -filter_complex \"[0][1]"

        extra = 0
        last = 0
        #print "Start"

        if len(lstTimes) > 1:

            for s in lstTimes[:-1]:
                #print "Start2"
        
                if l == 0:
                    strOvr += " overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(n," + str(int(lstTimes[l]) + extra) + "," + str(int(lstTimes[l]) + int(lstStalls[l])) + ")'[tmp" + str(k)+"]"    
                else:
                    #print "PROBLEM2"
                    extra += int(lstStalls[l-1])
                    #last =
                    if int(lstStalls[l]) != 0:
                        strOvr += "; \
                        " + temp + "[1]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(n," + str(int(lstTimes[l]) + extra) + "," + str(int(lstTimes[l]) + extra + int(lstStalls[l])) + ")'[tmp" + str(k)+"]"
    
                if int(lstStalls[l]) != 0:
                    temp = "[tmp" + str(k) + "]"
                    k += 1
                l += 1
        
            else:
                #print "PROBLEM"
                extra += int(lstStalls[l-1])
                strOvr += "; \
                " + temp + "[1]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(n," + str(int(lstTimes[l]) + extra) + "," + str(int(lstTimes[l]) + extra + int(lstStalls[l])) + ")'"
        else:
            strOvr += " overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:enable='between(n," + str(int(lstTimes[l]) + extra) + "," + str(int(lstTimes[l]) + int(lstStalls[l])) + ")'"     
        


        strOvr += "\" -c:a copy " + outFolder.get() + "/" + txtName.get()

        print strOvr

        #Bash command output logic
        import subprocess
        #process = subprocess.Popen([strVid], stdout=subprocess.PIPE, shell=True)
        #output = process.communicate()[0]

        #outputs strVid4 to Bash
    
        subprocess.check_call(strOvr, shell=True)

    #End of overlay
        
    if fileExists("outputNew.mp4"):
        remove = "rm outputNew.mp4"
        subprocess.check_call(remove, shell=True)
        
    return

#Reads the columns of the text file if a certain number of lines are specified to be read
def readColumnLines():
    
    crs = open(str(v2.get()), "r")
    #crs.readline()
    #print txtStart.get()
    for i, line in enumerate(crs):
        print "This: " + str(i)
        start = txtStart.get()
        end = txtEnd.get()
        test = 0

        if i + 1 == int(start):
        #if i == 2:
            lineRange = int(end) - (int(start))
            k = 0
            for columns in ( raw.strip().split() for raw in crs ):
                if k <= lineRange:
                #print line
                    try:
                        lstTimes.append(str(columns[0]))
                    except:
                        tkMessageBox.showwarning('Warning', 'The config file is not configured properly.')
                    if CheckStalls.get() == 1:
                        try:
                            lstStalls.append(str(columns[1]))
                        except:
                            continue
                    if CheckRes.get() == 1:
                        try:
                            lstRes.append(str(columns[2]))
                        except:
                            continue
                    k +=1
        #elif i > 4:
         #   break
    return

def enableYUV():

    if CheckYUV.get() == 1:
        txtRes['state'] = 'normal'
        txtFrame['state'] ='normal'
        txtDur['state'] = 'normal'
    elif CheckYUV.get() == 0:
        txtRes['state'] = 'disabled'
        txtFrame['state'] ='disabled'
        txtDur['state'] = 'disabled'
        

    return

def enableDash():

    if CheckDash.get() == 1:
        txtFrag['state'] = 'normal'
        txtSeg['state'] ='normal'
    elif CheckDash.get() == 0:
        txtFrag['state'] = 'disabled'
        txtSeg['state'] ='disabled'
        

    return

def checkForAudio():
    bashCommand = "ffprobe -i " + v.get() + " -show_streams -select_streams a -loglevel error "
    #print v
    
    import subprocess
    process = subprocess.Popen([bashCommand], stdout=subprocess.PIPE, shell=True)
    output = process.communicate()[0]
    print "Output: " + output
    return str(output)


def test4():
    #list2 = [1];
    #print str(len(list2));
    print str(fileExists("27.gif"))

#UI Widgets

#background_image = Tkinter.PhotoImage(file="test.gif")
#background_label = Tkinter.Label(top, image=background_image)
#background_label.photo=background_image
#background_label.place(x=0, y=0, relwidth=1, relheight=1)

title = Label( top, font=("Arial", "16", "bold"), bg="#a1dbcd", text="Video Converter").grid(row=1,column=1, columnspan=3)
label = Label( top, font=("Arial", "11", "bold"),bg="#a1dbcd", text="Upload video").grid(row=2,column=1)

#E1 = Entry(top, bd =5, textvariable=v).grid(row=2,column=2) #Upload Video textbox
E1 = Entry(top, textvariable=v).grid(row=2,column=2) #Upload Video textbox
#B = Tkinter.Button(top, text ="Browse", command = lambda: test(int)).grid(row=1,column=3)
B = Tkinter.Button(top, text ="Browse", command = test).grid(row=2,column=3)

label2 = Label( top,bg="#a1dbcd",font=("Arial", "11", "bold"), text="Upload Config File").grid(row=3,column=1)
E12 = Entry(top, textvariable=v2).grid(row=3,column=2) #Upload config file textbox
C = Tkinter.Button(top, text ="Browse", command = readConfig).grid(row=3,column=3)

lblStart = Label( top,bg="#a1dbcd",font=("Arial", "11", "bold"), text="Start Line").grid(row=4,column=1)
txtStart = Entry(top, textvariable=startLine) #Start line (in config file) text box
txtStart.grid(row=4,column=2)

lblEnd = Label( top,bg="#a1dbcd",font=("Arial", "11", "bold"), text="End Line").grid(row=5,column=1)
txtEnd = Entry(top, textvariable=endLine) #End line text box
txtEnd.grid(row=5,column=2)

C1 = Checkbutton(top,bg="#a1dbcd",highlightthickness=0,font=("Arial", "11", "bold"), text = "Stalls", variable = CheckStalls, \
                 onvalue = 1, offvalue = 0, height=2, \
                 width = 10).grid(row=6,column=1) #Checkbox to toggle stalls
C2 = Checkbutton(top,bg="#a1dbcd",highlightthickness=0,font=("Arial", "11", "bold"), text = "Resolution", variable = CheckRes, \
                 onvalue = 1, offvalue = 0, height=2, \
                 width = 10).grid(row=6,column=2) #Checkbox to toggle resolution changes

C3 = Checkbutton(top,bg="#a1dbcd",font=("Arial", "11", "bold"), text = "YUV", variable = CheckYUV, \
                 onvalue = 1, highlightthickness=0,offvalue = 0, height=2, \
                 width = 10, command=enableYUV).grid(row=6,column=3)

C4 = Checkbutton(top,bg="#a1dbcd",font=("Arial", "11", "bold"), text = "DASH", variable = CheckDash, \
                 onvalue = 1, highlightthickness=0,offvalue = 0, height=2, \
                 width = 10, command=enableDash).grid(row=7,column=1) 

lblRes = Label( top,bg="#a1dbcd",font=("Arial", "11", "bold"), text="Enter resolution: ").grid(row=8,column=1)
txtRes = Entry(top, state = DISABLED) 
txtRes.grid(row=8,column=2)

lblFrame = Label( top,bg="#a1dbcd",font=("Arial", "11", "bold"), text="Enter frame rate: ").grid(row=9,column=1)
txtFrame = Entry(top, state = DISABLED) 
txtFrame.grid(row=9,column=2)

lblDur = Label( top, bg="#a1dbcd", font=("Arial", "11", "bold"), text="Number of frames: ").grid(row=10,column=1)
txtDur = Entry(top, state = DISABLED) 
txtDur.grid(row=10,column=2)

lblFrag = Label( top, bg="#a1dbcd", font=("Arial", "11", "bold"), text="Fragment size: ").grid(row=11,column=1)
txtFrag = Entry(top, state = DISABLED) 
txtFrag.grid(row=11,column=2)

lblSeg = Label( top, bg="#a1dbcd", font=("Arial", "11", "bold"), text="Segment size: ").grid(row=12,column=1)
txtSeg = Entry(top, state = DISABLED) 
txtSeg.grid(row=12,column=2)

lblOut = Label( top,bg="#a1dbcd",font=("Arial", "11", "bold"), text="Choose output folder: ").grid(row=13,column=1)
folderText = Entry(top, textvariable=outFolder).grid(row=13,column=2) #Output folder textbox
C = Tkinter.Button(top, text ="Browse", command = outputFolder).grid(row=13,column=3)

lblName = Label( top,bg="#a1dbcd",font=("Arial", "11", "bold"), text="Enter Name: ").grid(row=14,column=1)
txtName = Entry(top) #Output file name entry textbox
txtName.grid(row=14,column=2)


#E1.pack(side = RIGHT)

#Create Button
D = Tkinter.Button(top, height = 3, width = 7, anchor=CENTER, text ="Create", command = createVideoInitial).grid(row=15,column=1, columnspan=3)


#label.pack(side = LEFT)
#B.pack()
top.mainloop()
