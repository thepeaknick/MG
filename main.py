from flask import Flask, request, jsonify
from werkzeug.wrappers import Request, Response
from werkzeug.utils import secure_filename

import sys
if sys.version_info[0] == 2:  # the tkinter library changed it's name from Python 2 to 3.
    import Tkinter
    tkinter = Tkinter #I decided to use a library reference to avoid potential naming conflicts with people's programs.
else:
    import tkinter
from PIL import Image, ImageTk

def showPIL(pilImage):
    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()    
    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
    canvas = tkinter.Canvas(root,width=w,height=h)
    canvas.pack()
    canvas.configure(background='black')
    imgWidth, imgHeight = pilImage.size
    if imgWidth > w or imgHeight > h:
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(w/2,h/2,image=image)
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

if __name__ == '__main__':
    app.run(debug=True)

pilImage = Image.open("/scoreboard/background.png")
showPIL(pilImage)