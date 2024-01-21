from tkinter import *
from tkinter import messagebox
from tkinter import filedialog

max_Y = 0

def write_Head(Feed_freq, mirror):
    lines = ['G0G40G49G80', 'G21', 'G17G90', 'G{}'.format('55' if mirror else '54'), 'G0 Z150.0', f'M3 S{Feed_freq}\n']
    with open(r'C:\Users\Public\temp_py.txt', 'w') as file:
        for line in lines:
            file.write(line + '\n')

def extract_code():
    with open(r'C:\Users\Public\temp_py.txt', 'r') as tmp:
        file_name = filedialog.asksaveasfilename(filetypes=(('NC-Studio code', '*.u00'), ('All files', '*.*')))
        if file_name:
            if not '.u00' in file_name:
                file_name += '.u00'
            f = open(file_name, 'w')
            for i in tmp:
                f.write(i)
            f.close()
            messagebox.showinfo('Успешно', 'G-code записан в файл\n' + file_name)
        else:
            return

def drilling(depth, Feed, step_down):
    line = '\'drilling\n'
    if step_down < depth:
        current_pass = step_down
        line += f'G1 Z-{current_pass}F{Feed}\n' + 'G0 Z1.0\n'
        while depth - current_pass > step_down:
            current_pass += step_down
            line += f'G1 Z-{current_pass}\n' + 'G0 Z1.0\n'
        else:
            return line + f'G1 Z-{depth}\n'
    else:
        return line + f'G1 Z-{depth}F{Feed}\n'

def circular(X, Y, D, Mill):
    circ_step = round(Mill / 2, 3)
    half_D = round(D / 2, 3)
    line = '\'circular\n'
    curr_circ_pass = circ_step
    while half_D - curr_circ_pass > circ_step:
        line += f'G1 X{X + curr_circ_pass}\n'
        line += f'G2 X{X + curr_circ_pass} ' + f'Y{Y} ' + f'I{curr_circ_pass * -1} ' + 'J0.0\n'
        curr_circ_pass += circ_step
    else:
        line += f'G1 X{X + half_D - circ_step}\n'
        line += f'G2 X{X + half_D - circ_step} ' + f'Y{Y} ' + f'I{(half_D - circ_step) * -1:.3f} ' + 'J0.0\n'
    return line

def milling(X, Y, D, depth, Mill, Feed, step_down):
    line = '\'milling\n'
    if step_down < depth:
        current_pass = step_down
        line += f'G1 Z-{current_pass} F{Feed}\n' + circular(X, Y, D, Mill)
        while depth - current_pass > step_down:
            current_pass += step_down
            line += f'G1 Z-{current_pass}\n' + circular(X, Y, D, Mill) + f'G0 X{X} Y{Y}\n'
    return line + f'G1 Z-{depth} F{Feed}\n' + circular(X, Y, D, Mill)

def slot_milling(X, Y_1, Y_2, width, Mill):
    step = round(Mill / 2, 3)
    line = ''
    if width == Mill:
        return line + f'Y{Y_2 - step}\n'
    elif Y_2 - Y_1 == Mill:
        return line + f'X{X + width - step}\n'
    elif width > Mill * 1.5 and Y_2 - Y_1 > Mill * 1.7:
        curr_pass = Mill
        while width - curr_pass > step:
            line += f'Y{Y_2 - Mill}\n'
            curr_pass += step 
            if width - curr_pass > step:
                line += f'X{X + curr_pass}\n'
            else:
                return line + f'X{X + width - step} Y{Y_2 - step}\n' + f'Y{Y_1 + step}\n' + f'X{X + step}\n' + f'Y{Y_2 - step}\n' + f'X{X + width - step}\n'
            line += f'Y{Y_1 + Mill}\n'
            curr_pass += step
            if width - curr_pass > step:
                line += f'X{X + curr_pass}\n'
            else:
                return line + f'X{X + width - step} Y{Y_1 + step}\n' + f'X{X + step}\n' + f'Y{Y_2 - step}\n' + f'X{X + width - step}\n' + f'Y{Y_1 + step}\n'
    return line + f'Y{Y_2 - step}\n' + f'X{X + width - step}\n' + f'Y{Y_1 + step}\n' + f'X{X + step}\n'

def slotting(X, Y_1, Y_2, width, depth, Mill, Feed, step_down):
    step = round(Mill / 2, 3)
    line = '\'moving\n'
    if width > Mill * 1.5 and Y_2 - Y_1 > Mill * 2:
        line += f'G0 X{X + Mill} Y{Y_1 + Mill}\n'
    else:
        line += f'G0 X{X + step} Y{Y_1 + step}\n'
    line +=  'Z5.0\n\'slotting\n'
    if step_down < depth:
        line += f'G1 Z-{step_down} F{Feed}\n' + slot_milling(X, Y_1, Y_2, width, Mill)
        current_pass = step_down
        while depth - current_pass > step_down:
            line += '\'moving\n'
            if width > Mill * 1.5 and Y_2 - Y_1 > Mill * 2:
                line += f'G0 Z-{current_pass - 1}\n' + f'X{X + Mill} Y{Y_1 + Mill}\n'
            else:
                line += f'G0 Z-{current_pass - 1}\n' + f'G0 X{X + step} Y{Y_1 + step}\n'
            line +=  '\'slotting\n'
            current_pass += step_down
            line += f'G1 Z-{current_pass}\n' + slot_milling(X, Y_1, Y_2, width, Mill)
        else:
            line += '\'moving\n'
            if width > Mill * 1.5 and Y_2 - Y_1 > Mill * 2:
                line += f'G0 Z-{current_pass - 1}\n' + f'X{X + Mill} Y{Y_1 + Mill}\n'
            else:
                line += f'G0 Z-{current_pass - 1}\n' + f'G0 X{X + step} Y{Y_1 + step}\n'
            line +=  '\'slotting\n'
    return line + f'G1 Z-{depth} F{Feed}\n' + slot_milling(X, Y_1, Y_2, width, Mill)

def calculate_Gcode(X, Y, D, depth, Mill, Feed, step_down, slot, mirror):
    global max_Y
    if D < Mill:
        messagebox.showwarning('Некорректные данные', 'Диаметр отверстия меньше диаметра фрезы')
        return False
    with open(r'C:\Users\Public\temp_py.txt', 'a') as file:
        if slot:
            Y_1, Y_2 = float(Y[0]), float(Y[1])
            if max_Y < Y_2: max_Y = Y_2
            if mirror == True:
                X = X - D
            file.write(slotting(X, Y_1, Y_2, D, depth, Mill, Feed, step_down))
        else:
            file.write('\'moving\n' + f'G0 X{X} Y{Y}\n' + 'Z5.0\n')
            if D == Mill:
                file.write(drilling(depth, Feed, step_down))
            else:
                file.write(milling(X, Y, D, depth, Mill, Feed, step_down))
        file.write('G0 Z10.0\n\n')
    return True

def check_table():
    global max_Y
    settings = [Mill_tf.get(), Freq_tf.get(), Feed_tf.get(), Step_Down_tf.get()]
    for i in range(4):
        if not settings[i] or settings[i] == '.' or float(settings[i]) == 0:
            return messagebox.showwarning('Отсутствие данных', 'Проверьте заполнение полей настройки')
        for j in settings[i]:
            if not j.isnumeric() and j != '.':
                return messagebox.showwarning('Некорректный ввод чисел', 'Проверьте вводимые символы в полях настройки')
        if i == 0:
            Mill = float(settings[i])
        elif i == 1:
            Freq = int(float(settings[i]))
        elif i == 2:
            Feed = int(float(settings[i]))
        elif i == 3:
            step_down = float(settings[i])                  
    result = False
    max_Y = 0
    mirror = Mirror.get()
    write_Head(Freq, mirror)
    for row in set:
        count = False
        slot = False
        for cell in range(4):
            for i, sign in enumerate(row[cell].get()):
                if not sign.isnumeric() and sign != '.' and sign != ';' and sign != '-':
                    return messagebox.showwarning('Некорректный ввод чисел', 'Проверьте  вводимые символы')
                else:
                    if cell == 0 and i != 0 and sign == '-':
                        count = True
                    if cell == 1 and sign == ';':
                        slot = True
            if cell == 0:
                X = row[cell].get()
            elif cell == 1:
                Y = row[cell].get()
            elif cell == 2:
                D = row[cell].get()
            elif cell == 3:
                depth = row[cell].get()
        if X and Y and D and depth and X != '.' and X != '-' and Y != '.' and Y != '-' and Y != ';' and D != '.' and depth != '.':
            D, depth = float(D), float(depth)
            if D == 0:
                return messagebox.showwarning('Некорректные данные', 'Диаметр отверстия = 0')
            elif D < 0:
                return messagebox.showwarning('Некорректные данные', 'Отрицательный диаметр отверстия')
            elif depth < 0:
                return messagebox.showwarning('Некорректные данные', 'Отрицательная глубина фрезерования')
            else:
                if count:
                    X = X.split('-')
                    X = float(X[0]) - float(X[1])
                else:
                    X = float(X)
                if slot:
                    Y = Y.split(';')
                else:
                    Y = float(Y)
                    if max_Y < Y: max_Y = Y
                if mirror:
                    X *= -1                
                if calculate_Gcode(X, Y, D, depth, Mill, Feed, step_down, slot, mirror):
                    result = True
                else:
                    return
        elif not X and not Y and not D and not depth and result:
            with open(r'C:\Users\Public\temp_py.txt', 'a') as file:
                file.write('\'end\n' + 'G0 Z150.0\n' + 'M5\n' + f'Y{max_Y + 100.000}\n' + 'M30')
            return extract_code()
        else:
            return messagebox.showwarning('Неполные данные', 'Проверьте заполнение необходимых полей')

window = Tk()
window.title('Фрезерование отверстий относительно верха заготовки')
window.geometry('650x730')

frame0 = Frame(window)
frame0.pack(expand=True)
canvas = Canvas(frame0, width=500, height=480, borderwidth=0, background="#ffffff")

frame = Frame(frame0)
frame.pack(expand=True)

Mill_lb = Label(frame, text="Диаметр фрезы")
Mill_lb.grid(row=0, column=0)
Mill_tf = Entry(frame, width=18)
Mill_tf.grid(row=1, column=0)

Freq_lb = Label(frame, text="Шпиндель об/мин")
Freq_lb.grid(row=0, column=1)
Freq_tf = Entry(frame, width=18)
Freq_tf.grid(row=1, column=1)

Feed_lb = Label(frame, text="Подача мм/мин")
Feed_lb.grid(row=0, column=2)
Feed_tf = Entry(frame, width=18)
Feed_tf.grid(row=1, column=2)

Step_Down_lb = Label(frame, text="Шаг по Z")
Step_Down_lb.grid(row=0, column=3)
Step_Down_tf = Entry(frame, width=18)
Step_Down_tf.grid(row=1, column=3)

Mirror = BooleanVar()
Mirror.set(0)
check_btn = Checkbutton(frame, text="Зеркально", variable=Mirror, onvalue=1, offvalue=0)
check_btn.grid(row=2, column=0)

cal_btn = Button(frame, text='Сформировать G-code', command=check_table)
cal_btn.grid(row=2, column=3, pady=40)

X_lb = Label(frame, text="X\n", width=20)
X_lb.grid(row=3, column=0)

Y_lb = Label(frame, text="Y\n(паз Y1;Y2)", width=20)
Y_lb.grid(row=3, column=1)

D_lb = Label(frame, text="Диаметр отверстия\n(ширина паза)", width=20)
D_lb.grid(row=3, column=2)

depth_lb = Label(frame, text="Глубина\n", width=20)
depth_lb.grid(row=3, column=3)

frame2 = Frame(canvas, background="#ffffff")
vsb = Scrollbar(frame0, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vsb.set)
vsb.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((4, 4), window=frame2, anchor="nw")

set = []
for i in range(150):
    X = Entry(frame2, width=23)
    X.grid(row = 4 + i, column = 0)
    Y = Entry(frame2, width=24)
    Y.grid(row = 4 + i, column = 1)
    D = Entry(frame2, width=25)
    D.grid(row = 4 + i, column = 2)
    depth = Entry(frame2, width=20)
    depth.grid(row = 4 + i, column = 3)
    set.append([X, Y, D, depth])

canvas.update_idletasks()
canvas.configure(scrollregion=canvas.bbox("all"))

window.mainloop()
