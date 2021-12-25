from flask import Flask, request, jsonify
from werkzeug.wrappers import Request, Response
from werkzeug.utils import secure_filename
from multiprocessing import Process
import time
import ratios

import sys
if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    import Tkinter
    tkinter = Tkinter #I decided to use a library reference to avoid potential naming conflicts with people's programs.
else:
    import tkinter
from PIL import Image, ImageTk
import tkinter.font as tkFont

def showPIL(pilImage):
    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()

    root.attributes('-fullscreen', True)
    root.focus_set()
    root.bind("<Escape>", lambda e: e.widget.quit())

    # Full screen canvas
    root.geometry("%dx%d+0+0" % (w, h)) #Dimensions
    canvas = tkinter.Canvas(root,width=w,height=h)
    canvas.pack()
    canvas.configure(background='black')

    imgWidth, imgHeight = pilImage.size
    if imgWidth > w or imgHeight > h: #Fit image to window
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(w/2,h/2,image=image)


    # Score board canvas
    home_res = "87"
    away_res = "100"
    quarter = "1"
    # print(tkFont.families())
    font_size_score = int(ratios.score_font_size * h)
    font_size_score_quarter = int(ratios.quarter_font_size * h)
    bebas_score = tkFont.Font(family='Bebas Neue',size=font_size_score, weight='bold')
    bebas_quarter = tkFont.Font(family='Bebas Neue',size=font_size_score_quarter, weight='bold')

    canvas.create_text(ratios.home_res_position_x * w, ratios.res_position_y * h,fill="white",font=bebas_score, text=home_res)
    canvas.create_text(ratios.away_res_position_x_triple * w, ratios.res_position_y * h,fill="white",font=bebas_score, text=away_res)
    
    canvas.create_text(w/2, ratios.quarter_position_y * h,fill="white",font=bebas_quarter, text=quarter)

    root.mainloop()

home_team_global = ''
away_team_global = ''

app = Flask(__name__)

@app.route('/api/v1.0/teamlogo', methods = ['POST'])
def addTeamLogo():
    file = request.files['file']
    # Read the image via file.stream
    file.save('teamLogos/' + secure_filename(file.filename))

    return jsonify({'msg': 'success'})

@app.route('/api/v1.0/teamandplayers', methods = ['POST'])
def teamandplayers():
    home_team_global = request.get_json()
    away_team_global = request.get_json()
    
    return jsonify({'msg': 'success'})

# Helper function to easly  parallelize multiple functions
def parallelize_functions(*functions):
    processes = []
    for function in functions:
        p = Process(target=function)
        p.start()
        processes.append(p)
    for p in processes:
        p.join()

    
def while_function(): 
    pilImage = Image.open("scoreboard/background.png")
    showPIL(pilImage)

def run_app():
    # print("Not working Flask!")
    app.run(host="0.0.0.0",debug=False)

if __name__ == '__main__':
    if __name__ == '__main__':
        parallelize_functions(while_function, run_app)
    
