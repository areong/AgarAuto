'''
Requirements
    pywin32
    Pillow
    Desktopmagic
'''

from desktopmagic.screengrab_win32 import getScreenAsImage
import win32api, win32con
import math
import tkinter
from PIL import ImageTk

class AgarAuto:
    def __init__(self):
        self.screenWidth = 1
        self.screenHeight = 1
        self.centerX = 1
        self.centerY = 1
        self.resizeRatio = 4

        self.clickRadius = 100  # Click distance fomr the center
        self.numDirections = 16
        self.angleInterval = 2 * math.pi / self.numDirections
        self.clickAngles = [0 + i * self.angleInterval for i in range(self.numDirections)]
        self.clickPoints = [[int(math.cos(angle) * self.clickRadius), int(math.sin(angle) * self.clickRadius)] for angle in self.clickAngles]
        # The mid points between two angles in clickAngles
        self.splittingAngles = [-0.5 * self.angleInterval + i * self.angleInterval for i in range(self.numDirections + 2)]
        self.areaOfAngleRegions = [0 for i in range(self.numDirections)]
        self.nonWhiteAreaOfAngleRegions = [0 for i in range(self.numDirections)]

    def displayImage(self, image):
        root = tkinter.Tk()
        tkimage = ImageTk.PhotoImage(image)
        tkinter.Label(root, image=tkimage).pack()
        root.mainloop()

    def getScreenSize(self):
        image = getScreenAsImage()
        self.screenWidth, self.screenHeight = image.size
        self.centerX = self.screenWidth // 2
        self.centerY = self.screenHeight // 2
        for index in range(self.numDirections):
            self.clickPoints[index][0] += self.centerX
            self.clickPoints[index][1] += self.centerY
            #print(index)
            #print(self.clickPoints[index][0])
            #print(self.clickPoints[index][1])
        #print(screenWidth)
        #print(screenHeight)
        #print(centerX)
        #print(centerY)

    def click(self, x, y):
        '''
        x and y are integers.
        '''
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def xyToAngle(self, x, y):
        if x == 0:
            if y >= 0:
                return math.pi / 2
            else:
                return math.pi * 3 / 2
        else:
            angle = math.atan(y / x)
            if x < 0:
                if y > 0:
                    angle += math.pi
                else:
                    angle += math.pi
            else:
                if y < 0:
                    angle += 2 * math.pi
            return angle

    def angleToAngleRegionIndex(self, angle):
        return int((angle + self.angleInterval / 2) / self.angleInterval) % self.numDirections

    def calculateAngleRegionsArea(self):
        for y in range(self.screenHeight // self.resizeRatio):
            for x in range(self.screenWidth // self.resizeRatio):
                angle = self.xyToAngle(x * self.resizeRatio - self.centerX, y * self.resizeRatio - self.centerY)
                index = self.angleToAngleRegionIndex(angle)
                self.areaOfAngleRegions[index] += 1
        #for index in range(self.numDirections):
        #    print(self.areaOfAngleRegions[index])

    def run(self):
        self.getScreenSize()
        self.calculateAngleRegionsArea()
        while True:
            image = getScreenAsImage()
            imageSmall = image.resize((self.screenWidth // self.resizeRatio, self.screenHeight // self.resizeRatio))
            #self.displayImage(imageSmall)
            #break
            data = imageSmall.getdata()
            self.nonWhiteAreaOfAngleRegions = [0 for i in range(self.numDirections)]
            for y in range(self.screenHeight // self.resizeRatio):
                for x in range(self.screenWidth // self.resizeRatio):
                    i = y * self.screenWidth // self.resizeRatio + x
                    if data[i][0] < 255 and data[i][1] < 255 and data[i][2] < 255:
                        xRealShifted = x * self.resizeRatio - self.centerX
                        yRealShifted = y * self.resizeRatio - self.centerY
                        angle = self.xyToAngle(xRealShifted, yRealShifted)
                        index = self.angleToAngleRegionIndex(angle)
                        distance = math.sqrt(xRealShifted ** 2 + yRealShifted ** 2)
                        weight = 1
                        if distance > 200:
                            weight = 1 / (distance - 200) ** 2
                        self.nonWhiteAreaOfAngleRegions[index] += 1
            # Divide by area
            for index in range(self.numDirections):
                self.nonWhiteAreaOfAngleRegions[index] /= self.areaOfAngleRegions[index]
            # Find angle region with most ratio of white pixels
            maxWhiteIndex = 0
            minimum = 1e8
            for index in range(self.numDirections):
                if self.nonWhiteAreaOfAngleRegions[index] < minimum:
                    minimum = self.nonWhiteAreaOfAngleRegions[index]
                    maxWhiteIndex = index
            # Click on the point with the angle
            self.click(self.clickPoints[maxWhiteIndex][0], self.clickPoints[maxWhiteIndex][1])

if __name__ == '__main__':
    agarAuto = AgarAuto()
    agarAuto.run()