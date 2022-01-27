from re import match
from tkinter import PhotoImage
from flask import Flask, json, request, jsonify
from flask.scaffold import _matching_loader_thinks_module_is_package
from werkzeug.wrappers import Request, Response
from werkzeug.utils import secure_filename
from multiprocessing import Pipe, Process, Queue
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
import os

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0')
    os.environ.__setitem__('DISPLAY', ':0')

# canvas = None
root = None
should_update = False

def get_team_data(players):
    points = 0
    fouls = 0
    first_quarter_points = 0
    second_quarter_points = 0
    third_quarter_points = 0
    fourth_quarter_points = 0
    for x in players:
        points = points + x["points_first_quarter"] + x["points_second_quarter"] + x["points_third_quarter"] + x["points_fourth_quarter"] + x["points_overtime"]
        first_quarter_points = first_quarter_points + x["points_first_quarter"]
        second_quarter_points = second_quarter_points + x["points_second_quarter"]
        third_quarter_points = third_quarter_points + x["points_third_quarter"]
        fourth_quarter_points = fourth_quarter_points + x["points_fourth_quarter"]
        fouls = fouls + x["fouls_first_quarter"] + x["fouls_second_quarter"] + x["fouls_third_quarter"] + x["fouls_fourth_quarter"] + x["fouls_overtime"]
        
    return points, fouls, first_quarter_points, second_quarter_points, third_quarter_points, fourth_quarter_points

def get_quarter_team_fouls(players):
    first_quarter = 0
    second_quarter = 0
    third_quarter = 0
    fourth_quarter = 0
    for x in players:
        first_quarter = first_quarter + x["fouls_first_quarter"] 
        second_quarter = second_quarter + x["fouls_second_quarter"] 
        third_quarter = third_quarter + x["fouls_third_quarter"]
        fourth_quarter = fourth_quarter + x["fouls_fourth_quarter"] + x["fouls_overtime"]

    return [first_quarter, second_quarter, third_quarter, fourth_quarter]

def update_scoreboard():
    return 

def showPIL(pilImage, root, q, child_conn):
    match_data = q.get()

    root = tkinter.Tk()
    w, h = root.winfo_screenwidth() , root.winfo_screenheight()

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
        ratio = max(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(w/2,h/2,image=image)

    # Match data polishing
    home_team = match_data["home_team"]
    away_team = match_data["away_team"]
    home_res, home_team_fouls, home_first_quarter_score, home_second_quarter_score, home_third_quarter_score, home_fourth_quarter_score  = get_team_data(home_team["players"])
    away_res, away_team_fouls, away_first_quarter_score, away_second_quarter_score, away_third_quarter_score, away_fourth_quarter_score = get_team_data(away_team["players"])

    home_team_quarter_fouls = get_quarter_team_fouls(home_team["players"])
    away_team_quarter_fouls = get_quarter_team_fouls(away_team["players"])

    home_team_timeouts = 0
    away_team_timeouts = 0
    # Score board canvas
    quarter = "Q" + match_data["period"]
    if (str(match_data["period"]) == "OT" ):
        current_quarter = 5
    else :
        current_quarter = int(match_data["period"])
    home_team_fouls_current_quarter = home_team_quarter_fouls[current_quarter-1]
    away_team_fouls_current_quarter = away_team_quarter_fouls[current_quarter-1]
    

    home_team_name = home_team["name"]
    away_team_name = away_team["name"]

    quarter_time = "00:00"

    num_home_players = len(home_team["players"])
    num_away_players = len(away_team["players"])
    home_players = home_team["players"]
    away_players = away_team["players"]
    
    # Fonts

    # print(tkFont.families())
    font_size_score = int(ratios.score_font_size * h)
    font_size_score_quarter = int(ratios.quarter_font_size * h)
    font_size_player_data = int(ratios.player_name_font_size * h)
    font_size_team_foul = int(ratios.team_foul_font_size * h)
    bebas_score = tkFont.Font(family='Bebas Neue',size=font_size_score, weight='bold')
    bebas_quarter = tkFont.Font(family='Bebas Neue',size=font_size_score_quarter, weight='bold')
    bebas_team_foul = tkFont.Font(family='Bebas Neue',size=font_size_team_foul, weight='bold')
    bebas_player_data = tkFont.Font(family='Bebas Neue',size=font_size_player_data, weight='bold')

    # canvas = show_logos(w, h, canvas)
    # Show home logo
    home_logo_image=Image.open('/home/mgacademy/Development/MG/teamLogos/home_default.png')
    home_logo_image_ratio = home_logo_image.width/home_logo_image.height # 600/400 = 3/2 = 1.5

    width = int(ratios.home_image_w * w)
    height = width * home_logo_image_ratio

    home_logo_image_resized=home_logo_image.resize((width, int(height)))
    home_logo=ImageTk.PhotoImage(home_logo_image_resized)
    canvas.create_image(ratios.home_image_x * w, ratios.home_image_y * h, image=home_logo)

    # Show away logo
    away_logo_image=Image.open('/home/mgacademy/Development/MG/teamLogos/away_default.png')
    away_logo_image_ratio = away_logo_image.width/away_logo_image.height # 600/400 = 3/2 = 1.5

    width = int(ratios.away_image_w * w)
    height = width * away_logo_image_ratio
    away_logo_image_resized=away_logo_image.resize((width, int(height)))
    away_logo=ImageTk.PhotoImage(away_logo_image_resized)
    canvas.create_image(ratios.away_image_x * w, ratios.away_image_y * h, image=away_logo)

    # Show data

    canvas = show_team_data(w, h, canvas, bebas_score, home_res, away_res, bebas_quarter, bebas_team_foul, quarter, home_team_name, away_team_name, home_team_fouls_current_quarter, away_team_fouls_current_quarter, home_team_timeouts, away_team_timeouts)
    canvas = show_quarter_data(w, h, canvas, current_quarter, bebas_quarter, home_first_quarter_score, away_first_quarter_score, home_second_quarter_score, away_second_quarter_score, home_third_quarter_score, away_third_quarter_score, home_fourth_quarter_score, away_fourth_quarter_score)

    # Show quarter time
    canvas.create_text(w/2, ratios.quarter_time_position_y * h,fill="white",font=bebas_score, text=quarter_time, tag="quarter_time")

    canvas = show_player_data(w, h, canvas, num_home_players, num_away_players, home_players, away_players, bebas_player_data)
    
    root.update_idletasks()
    root.update()

    while True:
        # if should_update:
        
        if child_conn.poll(1):
            match_data = child_conn.recv()
            
            if "current_time" in match_data:
                quarter_time = match_data["current_time"]
                canvas.delete("quarter_time")
                minutes = int( int(quarter_time) / 1000 / 60 )
                seconds = int( int( int(quarter_time) / 1000 ) % 60 )
                if (seconds < 10):
                    seconds = "0" + str(seconds)
                canvas.create_text(w/2, ratios.quarter_time_position_y * h,fill="white",font=bebas_score, text=str(minutes) + ":" + str(seconds), tag="quarter_time")
            else:

                home_team = match_data["home_team"]
                away_team = match_data["away_team"]
                home_res, home_team_fouls, home_first_quarter_score, home_second_quarter_score, home_third_quarter_score, home_fourth_quarter_score  = get_team_data(home_team["players"])
                away_res, away_team_fouls, away_first_quarter_score, away_second_quarter_score, away_third_quarter_score, away_fourth_quarter_score = get_team_data(away_team["players"])

                home_team_quarter_fouls = get_quarter_team_fouls(home_team["players"])
                away_team_quarter_fouls = get_quarter_team_fouls(away_team["players"])

                home_team_timeouts = home_team["timeouts"]
                away_team_timeouts = away_team["timeouts"]
            
                quarter = "Q" + match_data["period"]
                current_quarter_index = current_quarter
                if (str(match_data["period"]) == "OT" ):
                    current_quarter = 5
                    current_quarter_index = 4
                else :
                    current_quarter = int(match_data["period"])
                
                home_team_fouls_current_quarter = home_team_quarter_fouls[current_quarter_index-1]
                away_team_fouls_current_quarter = away_team_quarter_fouls[current_quarter_index-1]
                home_team_name = home_team["name"]
                away_team_name = away_team["name"]

                num_home_players = len(home_team["players"])
                num_away_players = len(away_team["players"])
                home_players = home_team["players"]
                away_players = away_team["players"]

                canvas = show_team_data(w, h, canvas, bebas_score, home_res, away_res, bebas_quarter, bebas_team_foul, quarter, home_team_name, away_team_name, home_team_fouls_current_quarter, away_team_fouls_current_quarter, home_team_timeouts, away_team_timeouts)
                canvas = show_quarter_data(w, h, canvas, current_quarter, bebas_quarter, home_first_quarter_score, away_first_quarter_score, home_second_quarter_score, away_second_quarter_score, home_third_quarter_score, away_third_quarter_score, home_fourth_quarter_score, away_fourth_quarter_score)
                canvas = show_player_data(w, h, canvas, num_home_players, num_away_players, home_players, away_players, bebas_player_data)

            root.update_idletasks()
            root.update()
        # else:
            # print("NONE YET")        

        # Show players stats
        
    # root.mainloop()ers stats
    
    return canvas

def show_player_data(w, h, canvas: tkinter.Canvas, num_home_players, num_away_players, home_players, away_players, bebas_player_data):
    # Show home players
    for x in range(num_home_players):
        canvas.delete("hfouls"+str(x))
        canvas.delete("hlast_name"+str(x))
        canvas.delete("hnumber"+str(x))
        canvas.delete("hpoints"+str(x))

        player = home_players[x]
    
        fouls = player["fouls_first_quarter"] + player["fouls_second_quarter"] + player["fouls_third_quarter"] + player["fouls_fourth_quarter"] + player["fouls_overtime"]
        player_color = "gray" if fouls == 5 else "white"
        canvas.create_text(ratios.home_first_player_fouls_x * w, (ratios.first_player_name_y + 0.04*x) * h,fill="white",font=bebas_player_data, text=num_to_dots_fouls(fouls), anchor=tkinter.W, tag="hfouls"+str(x))

        canvas.create_text(ratios.home_first_player_name_x * w, (ratios.first_player_name_y + 0.04*x) * h,fill=player_color,font=bebas_player_data, text=player["last_name"], anchor=tkinter.E, tag="hlast_name"+str(x))
        canvas.create_text(ratios.home_first_player_number_x * w, (ratios.first_player_name_y + 0.04*x) * h,fill=player_color,font=bebas_player_data, text=player["number"], anchor=tkinter.W, tag="hnumber"+str(x))

        points = player["points_first_quarter"] + player["points_second_quarter"] + player["points_third_quarter"] + player["points_fourth_quarter"] + player["points_overtime"]
        canvas.create_text(ratios.home_first_player_points_x * w, (ratios.first_player_name_y + 0.04*x) * h,fill="white",font=bebas_player_data, text=points, anchor=tkinter.W, tag="hpoints"+str(x))

    # Show away players
    for x in range(num_away_players):
        canvas.delete("afouls"+str(x))
        canvas.delete("alast_name"+str(x))
        canvas.delete("anumber"+str(x))
        canvas.delete("apoints"+str(x))

        player = away_players[x]
        
        fouls = player["fouls_first_quarter"] + player["fouls_second_quarter"] + player["fouls_third_quarter"] + player["fouls_fourth_quarter"] + player["fouls_overtime"]
        player_color = "gray" if fouls == 5 else "white"
        canvas.create_text(ratios.away_first_player_fouls_x * w, (ratios.first_player_name_y + 0.04*x) * h,fill="white",font=bebas_player_data, text=num_to_dots_fouls(fouls), anchor=tkinter.W, tag="afouls"+str(x))

        canvas.create_text(ratios.away_first_player_name_x * w, (ratios.first_player_name_y + 0.04*x) * h,fill=player_color,font=bebas_player_data, text=player["last_name"], anchor=tkinter.E, tag="alast_name"+str(x))
        canvas.create_text(ratios.away_first_player_number_x * w, (ratios.first_player_name_y + 0.04*x) * h,fill=player_color,font=bebas_player_data, text=player["number"], anchor=tkinter.W, tag="anumber"+str(x))
        
        points = player["points_first_quarter"] + player["points_second_quarter"] + player["points_third_quarter"] + player["points_fourth_quarter"] + player["points_overtime"]
        canvas.create_text(ratios.away_first_player_points_x * w, (ratios.first_player_name_y + 0.04*x) * h,fill="white",font=bebas_player_data, text=points, anchor=tkinter.W, tag="apoints"+str(x))


    return canvas

def show_quarter_data(screen_w: int, screen_h: int, canvas: tkinter.Canvas, current_quarter, bebas_quarter, home_first_quarter_score, away_first_quarter_score, home_second_quarter_score, away_second_quarter_score, home_third_quarter_score, away_third_quarter_score, home_fourth_quarter_score, away_fourth_quarter_score):
    # Show score per quarter
    canvas.delete("hfqs")
    canvas.delete("afqs")
    quarter_color = "gray" if current_quarter > 1 else "white"
    canvas.create_text(ratios.first_quarter_position_x * screen_w, ratios.quarter_score_position_y * screen_h,fill=quarter_color,font=bebas_quarter, text=home_first_quarter_score, tag="hfqs")
    canvas.create_text(ratios.first_quarter_position_x * screen_w, (ratios.quarter_score_position_y + 0.065) * screen_h,fill=quarter_color,font=bebas_quarter, text=away_first_quarter_score, tag="afqs")

    canvas.delete("hsqs")
    canvas.delete("asqs")
    quarter_color = "gray" if current_quarter > 2 else "white"
    quarter_score_x_coords = (ratios.first_quarter_position_x + 0.04 * 1)* screen_w
    canvas.create_text(quarter_score_x_coords, ratios.quarter_score_position_y * screen_h,fill=quarter_color,font=bebas_quarter, text=home_second_quarter_score, tag="hsqs")
    canvas.create_text(quarter_score_x_coords, (ratios.quarter_score_position_y + 0.065) * screen_h,fill=quarter_color,font=bebas_quarter, text=away_second_quarter_score, tag="asqs")

    canvas.delete("htqs")
    canvas.delete("atqs")
    quarter_color = "gray" if current_quarter > 3 else "white"
    quarter_score_x_coords = (ratios.first_quarter_position_x + 0.04 * 2)* screen_w
    canvas.create_text(quarter_score_x_coords, ratios.quarter_score_position_y * screen_h,fill=quarter_color,font=bebas_quarter, text=home_third_quarter_score, tag="htqs")
    canvas.create_text(quarter_score_x_coords, (ratios.quarter_score_position_y + 0.065) * screen_h,fill=quarter_color,font=bebas_quarter, text=away_third_quarter_score, tag="atqs")

    canvas.delete("hfoqs")
    canvas.delete("afoqs")
    quarter_color = "gray" if current_quarter > 4 else "white"
    quarter_score_x_coords = (ratios.first_quarter_position_x + 0.04 * 3)* screen_w
    canvas.create_text(quarter_score_x_coords, ratios.quarter_score_position_y * screen_h,fill=quarter_color,font=bebas_quarter, text=home_fourth_quarter_score, tag="hfoqs")
    canvas.create_text(quarter_score_x_coords, (ratios.quarter_score_position_y + 0.065) * screen_h,fill=quarter_color,font=bebas_quarter, text=away_fourth_quarter_score, tag="afoqs")

    return canvas

def show_team_data(screen_w: int, screen_h: int, canvas: tkinter.Canvas, bebas_score, home_res, away_res, bebas_quarter, bebas_team_foul, quarter, home_team_name, away_team_name, home_team_fouls_current_quarter, away_team_fouls_current_quarter, home_team_timeouts, away_team_timeouts):

    # Show scores
    canvas.delete("home_res")
    canvas.delete("away_res")
    canvas.create_text(ratios.home_res_position_x * screen_w, ratios.res_position_y * screen_h,fill="white",font=bebas_score, text=home_res, anchor=tkinter.W, tag="home_res")
    canvas.create_text(ratios.away_res_position_x * screen_w, ratios.res_position_y * screen_h,fill="white",font=bebas_score, text=away_res, anchor=tkinter.E, tag="away_res")
    
    # Show quarter
    canvas.delete("quarter")
    canvas.create_text(screen_w/2, ratios.quarter_position_y * screen_h,fill="white",font=bebas_quarter, text=quarter, tag="quarter")

    # Show team names
    canvas.delete("home_team_name")
    canvas.delete("away_team_name")
    canvas.create_text(ratios.home_res_position_x * screen_w, ratios.team_name_position_y * screen_h,fill="white",font=bebas_quarter, text=home_team_name, anchor=tkinter.W, tag="home_team_name")
    canvas.create_text(ratios.away_res_position_x * screen_w, ratios.team_name_position_y * screen_h,fill="white",font=bebas_quarter, text=away_team_name, anchor=tkinter.E, tag="away_team_name")

    # Show team fouls
    canvas.delete("home_team_fouls")
    canvas.delete("away_team_fouls")

    home_team_foul_color = "red" if home_team_fouls_current_quarter > 4 else "white"
    away_team_foul_color = "red" if away_team_fouls_current_quarter > 4 else "white"
    home_team_fouls_current_quarter = 5 if home_team_fouls_current_quarter > 4 else home_team_fouls_current_quarter
    away_team_fouls_current_quarter = 5 if away_team_fouls_current_quarter > 4 else away_team_fouls_current_quarter
    canvas.create_text(ratios.home_res_position_x * screen_w, ratios.team_foul_position_y * screen_h,fill=home_team_foul_color,font=bebas_team_foul, text="F: " + str(home_team_fouls_current_quarter), anchor=tkinter.W, tag="home_team_fouls")
    canvas.create_text(ratios.away_res_position_x * screen_w, ratios.team_foul_position_y * screen_h,fill=away_team_foul_color,font=bebas_team_foul, text="F: " + str(away_team_fouls_current_quarter), anchor=tkinter.E, tag="away_team_fouls")
    
    canvas.delete("home_team_timeouts")
    canvas.delete("away_team_timeouts")
    canvas.create_text(ratios.home_res_position_x * screen_w, ratios.team_foul_position_y * screen_h + 50 ,fill="gray",font=bebas_team_foul, text="T: " + str(home_team_timeouts), anchor=tkinter.W, tag="home_team_timeouts")
    canvas.create_text(ratios.away_res_position_x * screen_w, ratios.team_foul_position_y * screen_h + 50 ,fill="gray",font=bebas_team_foul, text="T: " + str(away_team_timeouts), anchor=tkinter.E, tag="away_team_timeouts")

    return canvas

def show_logos(screen_w: int, screen_h: int, canvas: tkinter.Canvas):
    # Show home logo
    home_logo_image=Image.open('/home/mgacademy/Development/MG/teamLogos/home.png')
    home_logo_image_ratio = home_logo_image.width/home_logo_image.height # 600/400 = 3/2 = 1.5

    width = int(ratios.home_image_w * screen_w)
    height = width * home_logo_image_ratio

    home_logo_image_resized=home_logo_image.resize((width, int(height)))
    home_logo=ImageTk.PhotoImage(home_logo_image_resized)
    canvas.create_image(ratios.home_image_x * screen_w, ratios.home_image_y * screen_h, image=home_logo)

    # Show away logo
    away_logo_image=Image.open('/home/mgacademy/Development/MG/teamLogos/away_default.png')
    away_logo_image_ratio = away_logo_image.width/away_logo_image.height # 600/400 = 3/2 = 1.5

    width = int(ratios.away_image_w * screen_w)
    height = width * away_logo_image_ratio
    away_logo_image_resized=away_logo_image.resize((width, int(height)))
    away_logo=ImageTk.PhotoImage(away_logo_image_resized)
    canvas.create_image(ratios.away_image_x * screen_w, ratios.away_image_y * screen_h, image=away_logo)

    return canvas
    
def num_to_dots_fouls(num_fouls):
    fouls_string = ""
    for x in range(num_fouls):
        fouls_string = fouls_string + "*"
    return fouls_string

home_team_global = ''
away_team_global = ''

app = Flask(__name__)

@app.route('/teamlogo', methods = ['POST'])
def addTeamLogo():
    file = request.files['file']
    if (file.filename.lower().endswith(('.png', '.jpg', '.jpeg'))):
        # Read the image via file.stream
        file.save('/home/mgacademy/Development/MG/teamLogos/' + secure_filename(file.filename))

    return jsonify({'msg': 'success'})

@app.route('/startmatch', methods = ['POST'])
def startmatch():
    match_data = request.get_json()
    parent_conn.send(match_data)
    
    # parallelize_functions(scoreboard_function)
    return jsonify({'msg': 'success'})

@app.route('/updatematchdata', methods = ['POST'])
def updatematchdata():
    # print(request.json)
    match_data = request.get_json()
    print(match_data)
    parent_conn.send(match_data)
    
    # parallelize_functions(scoreboard_function)
    return jsonify({'msg': 'success'})

@app.route('/updateclock', methods = ['POST'])
def updateclock():
    match_data = request.get_json()
    print(match_data)
    parent_conn.send(match_data)
    
    # parallelize_functions(scoreboard_function)
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

def scoreboard_function(q, child_conn: Pipe): 
    pilImage = Image.open("/home/mgacademy/Development/MG/scoreboard/background.jpg")
    # print(child_conn.recv())
    
    showPIL(pilImage, root, q, child_conn)

def run_app():
    # print("Not working Flask!")
    
    # app.run(host="0.0.0.0",debug=False, ssl_context=('cert.pem', 'key.pem'))
    app.run(host="0.0.0.0",debug=False)

parent_conn, child_conn = Pipe()

if __name__ == '__main__':
    q = Queue()
    f = open('/home/mgacademy/Development/MG/mock_data.json')
    match_data = json.load(f)
    f.close()

    q.put(match_data)
    p = Process(target=scoreboard_function, args=(q,child_conn,))
    p.start()
    parallelize_functions(run_app)
    p.join()
    
