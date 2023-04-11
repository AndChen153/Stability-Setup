import collections
import collections.abc
from pptx import Presentation
from pptx.util import Inches
import numpy as np
from pptx.enum.text import PP_ALIGN

# Create a new PowerPoint presentation
class PowerPointCreator:
    '''
    Class to create powerpoints for collected data
    '''

    def __init__(self, pno_paths: dict, scan_paths: dict, experimentTitle: str, leadName: str) -> None:
        self.prs = Presentation()
        # self.prs.slide_width = Inches(16)
        # self.prs.slide_height = Inches(9)
        self.pno = pno_paths
        self.scan = scan_paths
        self.experiement = experimentTitle

        # create title slide
        title_slide_layout = self.prs.slide_layouts[0]
        slide              = self.prs.slides.add_slide(title_slide_layout)
        title              = slide.shapes.title
        subtitle           = slide.placeholders[1]

        title.text = self.experiement
        # title.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        subtitle.text = leadName

        self.slide1Title()
        self.slide3PNO()
        # self.slide3_1()
        self.slide5DarkJV()
        self.slide6LightJV()


    def slide1Title(self):
        slide_layout = self.prs.slide_layouts[1]
        measurementParams = np.loadtxt(self.pno["csv"], delimiter=",", dtype=str)[0:5,0:2]
        # startDate = self.pno["csv"].split('\\')[-1].split(" ")[0][3:]

        slide = self.prs.slides.add_slide(slide_layout)
        shapes = slide.shapes

        title_shape = shapes.title

        title_shape.text = 'Measurement Conditions'

        body_shape = slide.placeholders[1]
        tf = body_shape.text_frame
        tf.text = np.array2string(measurementParams).translate({ord(i): None for i in '[]\'\''})


        body_shape = slide.placeholders[1]
        tf = body_shape.text_frame
        tf.text = np.array2string(measurementParams).translate({ord(i): None for i in '[]\'\''})
        # tf.text += "\n Start Date:"
        # tf.text += startDate


    def slide2Metrics(self):
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)

    def slide3PNO(self):
        slide_layout = self.prs.slide_layouts[5]
        slide = self.prs.slides.add_slide(slide_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        title_shape.text = 'Averaged PNO Traces (ALL)'
        device0PNO = slide.shapes.add_picture(self.pno["imagePnO"], Inches(1.41), Inches(1.4), Inches(3.6)) #left dist, top dist, width
        device1PNO = slide.shapes.add_picture(self.pno["imagePnO"], Inches(5.39), Inches(1.4), Inches(3.6)) #left dist, top dist, height
        device2PNO = slide.shapes.add_picture(self.pno["imagePnO"], Inches(1.41), Inches(4.41), Inches(3.6)) #left dist, top dist, height
        device3PNO = slide.shapes.add_picture(self.pno["imagePnO"], Inches(5.39), Inches(4.41), Inches(3.6)) #left dist, top dist, height

    def slide3_1(self):
        slide_layout = self.prs.slide_layouts[5]
        slide = self.prs.slides.add_slide(slide_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        title_shape.text = 'Averaged PNO Traces (exluding dead cells)'
        device0PNO = slide.shapes.add_picture(self.scan["imagePnO"], Inches(0), Inches(1.92), Inches(2.5)) #left dist, top dist, width
        device1PNO = slide.shapes.add_picture(self.scan["imagePnO"], Inches(2.5), Inches(1.92), Inches(2.5)) #left dist, top dist, height
        device2PNO = slide.shapes.add_picture(self.scan["imagePnO"], Inches(0), Inches(3.82), Inches(2.5)) #left dist, top dist, height
        device3PNO = slide.shapes.add_picture(self.scan["imagePnO"], Inches(2.5), Inches(3.82), Inches(2.5)) #left dist, top dist, height

    def slide4JVParams():


    def slide5DarkJV(self):
        slide_layout = self.prs.slide_layouts[5]
        slide = self.prs.slides.add_slide(slide_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        title_shape.text = 'Dark JV Before |  Dark JV After'
        device0BeforeDark = slide.shapes.add_picture(self.scan["imageDark"], Inches(0), Inches(1.92), Inches(2.5)) #left dist, top dist, width
        device1BeforeDark = slide.shapes.add_picture(self.scan["imageDark"], Inches(2.5), Inches(1.92), Inches(2.5)) #left dist, top dist, height
        device2BeforeDark = slide.shapes.add_picture(self.scan["imageDark"], Inches(0), Inches(3.82), Inches(2.5)) #left dist, top dist, height
        device3BeforeDark = slide.shapes.add_picture(self.scan["imageDark"], Inches(2.5), Inches(3.82), Inches(2.5)) #left dist, top dist, height

        device0AfterDark = slide.shapes.add_picture(self.scan["imageDark"], Inches(5), Inches(1.92), Inches(2.5)) #left dist, top dist, height
        device1AfterDark = slide.shapes.add_picture(self.scan["imageDark"], Inches(7.5), Inches(1.92), Inches(2.5)) #left dist, top dist, height
        device2AfterDark = slide.shapes.add_picture(self.scan["imageDark"], Inches(5), Inches(3.82), Inches(2.5)) #left dist, top dist, height
        device3AfterDark = slide.shapes.add_picture(self.scan["imageDark"], Inches(7.5), Inches(3.82), Inches(2.5)) #left dist, top dist, height



    def slide6LightJV(self):
        slide_layout = self.prs.slide_layouts[5]
        slide = self.prs.slides.add_slide(slide_layout)
        shapes = slide.shapes
        title_shape = shapes.title
        title_shape.text = 'Light JV Before |   Light JV After'

        device0BeforeLight = slide.shapes.add_picture(self.scan["imageLight"], Inches(0), Inches(1.92), Inches(2.5)) #left dist, top dist, width
        device1BeforeLight = slide.shapes.add_picture(self.scan["imageLight"], Inches(2.5), Inches(1.92), Inches(2.5)) #left dist, top dist, height
        device2BeforeLight = slide.shapes.add_picture(self.scan["imageLight"], Inches(0), Inches(3.82), Inches(2.5)) #left dist, top dist, height
        device3BeforeLight = slide.shapes.add_picture(self.scan["imageLight"], Inches(2.5), Inches(3.82), Inches(2.5)) #left dist, top dist, height

        device0AfterLight = slide.shapes.add_picture(self.scan["imageLight"], Inches(5), Inches(1.92), Inches(2.5)) #left dist, top dist, height
        device1AfterLight = slide.shapes.add_picture(self.scan["imageLight"], Inches(7.5), Inches(1.92), Inches(2.5)) #left dist, top dist, height
        device2AfterLight = slide.shapes.add_picture(self.scan["imageLight"], Inches(5), Inches(3.82), Inches(2.5)) #left dist, top dist, height
        device3AfterLight = slide.shapes.add_picture(self.scan["imageLight"], Inches(7.5), Inches(3.82), Inches(2.5)) #left dist, top dist, height


    def save(self) -> str:
        loc = "./dataVisualization/" + self.experiement + ".pptx"
        self.prs.save(loc)
        print("saved at " + loc)
        return loc


if __name__ == '__main__':
    pno = {"imagePnO":r"C:\Users\achen\Dropbox\code\Stability-Setup\data\March-15-2023 goodTests\PnOMar-15-2023 13_29_55.png",
           "csv": r"C:\Users\achen\Dropbox\code\Stability-Setup\data\March-15-2023 goodTests\PnOMar-15-2023 13_29_55.csv"}
    scan = {"imageLight":r"C:\Users\achen\Dropbox\code\Stability-Setup\data\March-15-2023 goodTests\scanlightMar-15-2023 13_28_50.png",
            "csvLight":r"C:\Users\achen\Dropbox\code\Stability-Setup\data\March-15-2023 goodTests\scanlightMar-15-2023 13_28_50.csv",
            "imageDark":r"C:\Users\achen\Dropbox\code\Stability-Setup\data\March-15-2023 goodTests\scanlightMar-15-2023 13_28_50.png",
            "csvDark":r"C:\Users\achen\Dropbox\code\Stability-Setup\data\March-15-2023 goodTests\scanlightMar-15-2023 13_28_50.csv"}
    ppt = PowerPointCreator(pno, scan, "Example Auto PPT", "Andrew Chen")
    ppt.save()