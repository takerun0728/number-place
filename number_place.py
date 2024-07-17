import tkinter
import time
from threading import Thread, Lock
from collections import deque
 
WINDOW_W = 560
WINDOW_H = 610
BOX_START = 10
BOX_SIZE = 60
FONT_SIZE = 25
DISP_PERIOD = 50
MIN_DELAY = -5
MAX_DELAY = -1
DEFAULT = [[0, 0, 0, 2, 1, 0, 0, 4, 0],
           [0, 4, 3, 0, 7, 0, 0, 0, 5],
           [0, 8, 0, 0, 0, 0, 6, 0, 0],
           [4, 0, 0, 3, 0, 0, 0, 0, 0],
           [5, 3, 0, 0, 0, 0, 0, 8, 1],
           [0, 0, 0, 0, 0, 1, 0, 0, 2],
           [0, 0, 2, 0, 0, 0, 0, 5, 0],
           [9, 0, 0, 0, 8, 0, 3, 1, 0],
           [0, 6, 0, 0, 5, 4, 0, 0, 0]]

fixed = [[False for _ in range(9)] for _ in range(9)]
value = [[0 for _ in range(9)] for _ in range(9)]
disp_queue = deque()
first = True
disp_lock = Lock()
window = tkinter.Tk()
delay_exp = tkinter.DoubleVar(master=window, value=-2)
delay = 10**delay_exp.get()

def start():
    btn_start["state"] = "disable"
    btn_def["state"] = "disable"
    thread = Thread(target=process)
    thread.start()

def process():
    global first, fixed, value, delay

    if first:
        first = False
        for i in range(9):
            for j in range(9):
                if box[i][j].get() != "":
                    fixed[i][j] = True
                    try:
                        value[i][j] = int(box[i][j].get())
                    except:
                        pass
    else:
        for i in range(9):
            for j in range(9):
                if not fixed[i][j]:
                    value[i][j] = 0
                    add_disp_queue(i, j, 0)

    i, j = fixed_chk(0, 0, fixed, next)
    if i == 9: return

    while True:
        value[i][j] += 1
        if value[i][j] == 10:
            value[i][j] = 0
            add_disp_queue(i, j ,0)

            i, j = back(i, j)
            if i == -1: break
            i, j = fixed_chk(i, j, fixed, back)
        else:
            add_disp_queue(i, j, value[i][j])

            if check(i, j, value):
                i, j = next(i, j)
                if i == 9: break
                i, j = fixed_chk(i, j, fixed, next)

        time.sleep(delay)
    btn_start["state"] = "active"
    btn_def["state"] = "active"

def add_disp_queue(i, j, val):
    disp_lock.acquire()
    disp_queue.append((i, j, val))
    disp_lock.release()

def fixed_chk(i, j, fixed, direction):
    while fixed[i][j]:
        i, j = direction(i, j)
        if i == -1 or i == 9:
            break
    return i, j

def next(i, j):
    j += 1
    if j == 9:
        j = 0
        i += 1
    return i, j

def back(i, j):
    j -= 1
    if j == -1:
        j = 8
        i -= 1

    return i, j

def check(i, j, value):
    return check_row(i, value) and check_col(j, value) and check_area(i, j, value)

def check_row(i, value):
    cnt = [0] * 9
    for j in range(9):
        if value[i][j] != 0:
            if cnt[value[i][j]-1] != 0:
                return False
            else:
                cnt[value[i][j]-1] = 1
    return True

def check_col(j, value):
    cnt = [0] * 9
    for i in range(9):
        if value[i][j] != 0:
            if cnt[value[i][j]-1] != 0:
                return False
            else:
                cnt[value[i][j]-1] = 1
    return True

def check_area(i, j, value):
    cnt = [0] * 9
    x = j // 3
    y = i // 3
    for i2 in range(y*3, y*3+3):
        for j2 in range(x*3, x*3+3):
            if value[i2][j2] != 0:
                if cnt[value[i2][j2]-1] != 0:
                    return False
                else:
                    cnt[value[i2][j2]-1] = 1
    return True

def display():
    while disp_queue:
        disp_lock.acquire()
        i, j, val = disp_queue.popleft()
        disp_lock.release()
        box[i][j].delete(0, tkinter.END)
        if val:
            box[i][j].insert(tkinter.END, f"{val}")
    window.after(DISP_PERIOD, display)

def set_delay(event=None):
    global delay
    if delay_exp.get() == MIN_DELAY:
        delay = 0
    else:
        delay = 10**delay_exp.get()

def set_default(event=None):
    global first
    first = True
    for i in range(9):
        for j in range(9):
            add_disp_queue(i, j, DEFAULT[i][j])

if __name__ == '__main__':
    window.title("Number Place")
    window.geometry(f"{WINDOW_W}x{WINDOW_H}")
    window.resizable(False, False)
    box = []
    for i in range(9):
        box.append([])
        for j in range(9):
            box[i].append(tkinter.Entry(font=("", FONT_SIZE)))
            box[i][j]['justify'] = tkinter.CENTER
            box[i][j].place(x=BOX_START+j*BOX_SIZE, y=BOX_START+i*BOX_SIZE, width=BOX_SIZE, height=BOX_SIZE)
    
    bottom = tkinter.Frame(window)
    bottom.pack(side=tkinter.BOTTOM)
    btn_start = tkinter.Button(bottom, text="Start", command=start)
    btn_start.pack(side=tkinter.LEFT)
    btn_def = tkinter.Button(bottom, text="Default", command=set_default)
    btn_def.pack(side=tkinter.LEFT)
    delay_scl = tkinter.Scale(bottom,
                              variable=delay_exp,
                              command = set_delay,
                              orient=tkinter.HORIZONTAL,
                              length=400,
                              width=20,
                              sliderlength=20,
                              from_=MIN_DELAY,
                              to=MAX_DELAY,
                              resolution=0.1)
    delay_scl.pack(side=tkinter.RIGHT)

    window.after(DISP_PERIOD, display)
    window.mainloop()