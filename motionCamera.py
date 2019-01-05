#!/usr/bin/python2.7

#GUI
from Tkinter import *

#Camera
from picamera import PiCamera

#for images
from PIL import Image

#email
import smtplib

#for logging and timing
import time
import io

#motion detection algorithm
def motionDetection(func, duration, email, text):

    #height and width of camera pictures/video
    #higher resolution gives more detal but uses more memory
    highResX = 1280
    highResY = 720

    #low res is used only to detect motion
    #lower resolution has quicker cycles but has less accurate readings
    lowResX = 100
    lowResY = 50

    lastImage = 0

    #the threshold for the images to be different
    changedThreshold = 20

    #max value for images to be seen as identical
    notChanged = 5

    #array of pictures for detecting motion
    images = []

    timesCalled = 0

    #threshold for pixels to be different
    pixelThreshold = 35

    camera.resolution = (lowResX, lowResY)
    #camera.start_preview()

    while(True):
        stream = io.BytesIO()
        camera.capture(stream, format='png')
        stream.seek(0)

        #makes the array 2 length
        if(len(images) != 2):
            images.append(Image.open(stream))
        #refreshes the image
        else:
            images[0] = Image.open(stream)

        differentPixels = 0
        #runs this if there are 2 images
        if len(images) != 1:

            #counts the number of pixels that have a difference over a threshold
            #runs through x pixels
            for x in range(0, lowResX):
                #runs through y pixels
                for y in range(0, lowResY):

                    #Add Up All RGB Values For Current Pixel
                    controlImage = images[1].getpixel((x,y))
                    testedImage = images[0].getpixel((x,y))

                    value = (controlImage[0] + controlImage[1] + controlImage[2])
                    value -= (testedImage[0] + testedImage[1] + testedImage[2])

                    pixelDifference = abs(value)


                    #if the difference in the pixel's color is above
                    #a threshold then it is counted as different
                    if(pixelDifference > pixelThreshold):
                        differentPixels += 1

            #calulates the percent of changed pixels
            changedPercent = (differentPixels * 100) / (lowResX * lowResY)
            print(changedPercent)

            #if the percent is at of higher than a threshold a recording method is called
            if(changedPercent >= changedThreshold):

                #sets the camera to a high res
                camera.resolution = (highResX, highResY)

                #emails user if requested
                if email:
                    emailing()

                #texts user
                if text:
                    texting()

                #logs the events
                #if log:
                #    logging()
                #calls the video or picture function
                func(timesCalled)
                timesCalled += 1

                #sets the resolution back to the low res mode
                camera.resolution = (lowResX,lowResY)


            elif(changedPercent <= notChanged):
                images[1] = images[0]

            #removes false readings in case of being moved
            elif (lastImage == changedPercent):
                images[1] = images[0]

            lastImage = changedPercent



#Takes several pictures in quick sucession
def burstCapturing(timesCalled):

    #wait between burst shots in seconds
    timeBetweenBurst = 0.5

    #pictures per burst
    picturesBursted = 5

    for num in range(1, picturesBursted + 1):

        temp = (picturesBursted * timesCalled) + num
        #the file is named then saved in the same folder as the program

        fileName = ("/home/pi/Desktop/image%02d.png") % (temp)
        camera.capture(fileName)

        #waiting period between pictures
        time.sleep(timeBetweenBurst)




#records video of a certain length
def recordVideo(timesCalled):

    #recording length in seconds
    recordLength = 5

    #h264 is a raw video file which can be converted to mp4
    fileName = ("/home/pi/Desktop/video%02d.h264") % (timesCalled + 1)

    #records the video
    camera.start_recording(fileName)
    time.sleep((recordLength))
    camera.stop_recording()




#for emailing when changes occur
def emailing():

    #user names of sender and reciever 
    fromAddress = ''
    toAddress  = ''

    #the message to be sent
    message = "Motion detected"

    # login credentials
    username = ''
    password = ''

    #gets server
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()

    #logs on
    server.login(username,password)

    #sends message
    server.sendmail(fromAddress, toAddress, message)
    server.quit()


#texts user when motion is detected    
def texting():

    #The emailing information to text user

    #Alltel                         [10-digit phone number]@message.alltel.com

    #AT&T (formerly Cingular)       [10-digit phone number]@txt.att.net
    #                               [10-digit phone number]@mms.att.net (MMS)

    #Boost Mobile                   [10-digit phone number]@myboostmobile.com

    #Project Fi                     [10-digit phone number]@msg.fi.google.com

    #Sprint PCS                     [10-digit phone number]@messaging.sprintpcs.com
    #                               [10-digit phone number]@pm.sprint.com (MMS)

    #T-Mobile	                    [10-digit phone number]@tmomail.net

    #US Cellular                    [10-digit phone number]@email.uscc.net (SMS)
    #                               [10-digit phone number]@mms.uscc.net (MMS)

    #Verizon                        [10-digit phone number]@vtext.com
    #                               [10-digit phone number]@vzwpix.com (MMS)

    #Virgin Mobile USA              [10-digit phone number]@vmobl.com


    #user names of sender and reciever 
    fromAddress = ''
    toAddress  = ''

    #the message to be sent
    message = "Motion detected"

    # login credentials
    username = ''
    password = ''

    #gets server
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()

    #logs on
    server.login(username,password)

    #sends message
    server.sendmail(fromAddress, toAddress, message)
    server.quit()



#logs the motion detection occurances
def logging():

    localtime = time.asctime( time.localtime(time.time()) )
    #appends a log
    myFile = open ("log.txt", "a")
    myFile.write("/home/pi/Desktop/Motion detected at: " + localtime + "\n")
    myFile.close()



#The base of the GUI, its title, and size    
base = Tk()
base.title("Security Camera Setup")
base.geometry("300x150")


#the label telling the user how to continue
label = Label(base, text = "Close this to continue")
label.pack()


#the checkbox for email notifications
emailBox = BooleanVar()
emailCheckBox = Checkbutton(base, variable = emailBox, text = "get email notifications?")
emailCheckBox.pack()


#checkbox for texting
textBox = BooleanVar()
textCheckBox = Checkbutton(base, variable = textBox, text = "get text notifications?")
textCheckBox.pack()


#checkbox for keeping a log
#logBox = BooleanVar()
#logCheckBox = Checkbutton(base, variable = logBox, text = "Have a log?")
#logCheckBox.pack()


#the radio button for selecting the mode
modeVal = IntVar()
radioMode = Radiobutton(base, text = "Burst picture mode", value = 1, variable = modeVal)
radioMode.pack()
radioMode = Radiobutton(base, text = "Video mode", value = 2, variable = modeVal)
radioMode.pack()


#displays the GUI
base.mainloop()



#declare the camera
camera = PiCamera()

#frames per second of video, max at 720p is 60
camera.framerate = 30


#sets the values for emailing, texting, and logging values
emailMe = False
if emailBox.get() == 1:
    emailMe = True

textMe = False
if textBox.get() == 1:
    textMe = True

#logMe = False
#if logBox.get() == 1:
#    logMe = True

if modeVal.get() == 1:
    motionDetection(burstCapturing, roundsOfDuration, emailMe, textMe)

elif modeVal.get() == 2:
    motionDetection(recordVideo, roundsOfDuration, emailMe, textMe)

camera.stop_preview()
