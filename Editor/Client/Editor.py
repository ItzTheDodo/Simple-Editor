from tkinter import *
from tkinter.ttk import Scrollbar, Style
from Editor.utils.READONLY import ReadOnly
from Editor.utils.Error_Type import *
import Editor
import os
import subprocess


class Client:

    def __init__(self, VERSION, client_settings, error_out):

        __metadata__ = ReadOnly
        self.VERSION = VERSION
        self.CLIENT_SETTINGS = client_settings
        self.WIDTH = self.CLIENT_SETTINGS.getRes().split("x")[0]
        self.HEIGHT = self.CLIENT_SETTINGS.getRes().split("x")[1]
        self.COLOURS = self.CLIENT_SETTINGS.getSetup()
        self.ERROR_OUT = error_out

        self.BODYFONT = (self.CLIENT_SETTINGS.getText().getFamily(), 25, 'bold')
        self.HEADERFONT = (self.CLIENT_SETTINGS.getText().getFamily(), 50, 'bold', 'underline')
        self.BODYFONTU = (self.CLIENT_SETTINGS.getText().getFamily(), 25, 'bold', 'underline')
        self.SMALLFONT = (self.CLIENT_SETTINGS.getText().getFamily(), self.CLIENT_SETTINGS.getText().getRawSize(), 'bold')
        self.SMALLFONTU = (self.CLIENT_SETTINGS.getText().getFamily(), self.CLIENT_SETTINGS.getText().getRawSize(), 'bold', 'underline')

        self.navigation = os.getcwd()
        self.saved_ram_files = []
        self.stored_files = {}
        self.file_nav_buttons = []
        self.activeFile = ""
        self.processes = []
        self.clipboard = ""

        self.root = Tk()
        self.root.title("Editor IDE v%s" % self.VERSION)
        self.root.geometry("%sx%s+50+30" % (self.WIDTH, self.HEIGHT))
        self.root.resizable(0, 0)
        self.cv = Canvas(self.root, width=int(self.WIDTH), height=int(self.HEIGHT), background=self.COLOURS.getBase())
        self.cv.pack(side='top', fill='both', expand='yes')

        # 105:10
        self._setup_binds()
        self._draw_main_bar(0, 0, 40)
        self.textbox = self._draw_main_text_box(350, 100, 45, 114)
        self._draw_nav_bar(20, 60, 760, 300)
        self._draw_open_file_navigation_bar()

        self.root.protocol("WM_DELETE_WINDOW", self._onClose)
        self.root.mainloop()

    def _onClose(self):
        if Editor.DATAFOLDER.getConfig().getValue("auto-save-files") == "True":
            self._check_open_files_saved(True)
        print("Closing...")
        sys.exit(-1)

    def _setup_binds(self):
        self.root.bind_all("<Control-Key-s>", self._save_file)
        self.root.bind_all("<Control-Key-S>", self._save_all)
        self.root.bind_all("<Control-Key-r>", self._execute)

    def _check_open_files_saved(self, auto_save):
        files_not_saved = []
        for i in self.saved_ram_files:
            with open(i.name, "r") as file:
                try:
                    if not self.stored_files[i.name] == file.read() or (not self.textbox[0].get("1.0", END) == file.read() and self.activeFile == i.name):
                        files_not_saved.append(i)
                        if auto_save:
                            self._save_all(False)
                except KeyError:
                    if not self.textbox[0].get("1.0", END) == file.read() and self.activeFile == i.name:
                        files_not_saved.append(i)
                        if auto_save:
                            self._save_all(False)
                file.close()
        return files_not_saved

    def _draw_open_file_navigation_bar(self):
        width = 935
        height = 40
        self.cv.create_rectangle(350, 60, 350 + width, 60 + height, fill=self.COLOURS.getColours()[1])

        if len(self.saved_ram_files) == 0:
            return

        perFile = (width / len(self.saved_ram_files)) / 10.5
        count = 0

        for i in self.saved_ram_files:
            if self.activeFile == i.name:
                c = self.COLOURS.getColours()[3]
            else:
                c = self.COLOURS.getColours()[2]
            b = Button(self.root, text=i.name, command=lambda n=i.name: self._switch_file(n), width=int(perFile), font=self.SMALLFONT, borderwidth=2, height=1, background=c, cursor="hand2", activebackground=self.COLOURS.getColours()[2], fg=self.COLOURS.getColours()[8])
            self.cv.create_window(((perFile * 10.5) * count) + 355, 65, window=b, anchor="nw")
            b1 = Button(self.root, text="X", command=lambda n=i.name: self._close_file(n), width=2, font=self.SMALLFONT, borderwidth=0, height=1, background=c, cursor="hand2", activebackground=self.COLOURS.getColours()[2], fg=self.COLOURS.getColours()[8])
            self.cv.create_window(((perFile * 10.5) * count) + 355 + ((perFile * 10.5) - perFile * 2), 66, window=b1, anchor="nw")
            self.file_nav_buttons.append(b)
            self.file_nav_buttons.append(b1)
            count += 1

    def _switch_file(self, name):
        self.textbox[0].configure(state="normal")
        current = self.activeFile
        self.activeFile = name
        for i in self.file_nav_buttons:
            i.destroy()
        self._draw_open_file_navigation_bar()

        self.stored_files[current] = self.textbox[0].get("1.0", END)
        if self.stored_files.keys().__contains__(name):
            self.textbox[0].delete("1.0", END)
            self.textbox[0].insert("1.0", self.stored_files[name])
        else:
            with open(name, "r") as file:
                try:
                    self.stored_files[name] = file.read()
                except UnicodeDecodeError:
                    self.ERROR_OUT(EDITOR_ERROR_FILE_UNREADABLE, True)
                    return
                file.close()
            self.textbox[0].delete("1.0", END)
            self.textbox[0].insert("1.0", self.stored_files[name])

    def _find_files(self, filename, search_path):
        result = []
        for root, dir, files in os.walk(search_path):
            if filename in files:
                result.append(os.path.join(root, filename))
        return result

    def _close_file(self, name):
        if self.stored_files.__contains__(name):
            self.stored_files.pop(name)
        if self.activeFile == name:
            self.textbox[0].delete("1.0", END)
            self.activeFile = ""
            self.textbox[0].configure(state="disabled")
        for i in self.saved_ram_files:
            if i.name == name:
                self.saved_ram_files.remove(i)
        for i in self.file_nav_buttons:
            i.destroy()
        self._draw_open_file_navigation_bar()

    def _copy_text(self):
        ranges = self.textbox[0].tag_ranges(SEL)
        if ranges:
            self.clipboard = self.textbox[0].get(*ranges)

    def _paste_clipboard(self):
        self.textbox[0].insert(INSERT, self.clipboard)

    def _cut(self):
        ranges = self.textbox[0].tag_ranges(SEL)
        if ranges:
            self.textbox[0].delete(*ranges)

    def _delete(self):
        cur_file = self.activeFile
        self._close_file(cur_file)
        os.remove(cur_file)
        self._reload_nav_bar()

    def _draw_main_bar(self, x, y, disty):
        self.cv.create_rectangle(x, y, int(self.WIDTH) - x, disty, fill=self.COLOURS.getColours()[1])

        b1 = Menubutton(self.root, text="File", width=5, font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8])
        b1.menu = Menu(b1, tearoff=0, background=self.COLOURS.getColours()[1], activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8], cursor="hand2")
        b1["menu"] = b1.menu
        new_file = IntVar()
        b1.menu.add_radiobutton(label="New File", variable=new_file, command=self._new_file_screen, value="")
        open_file = IntVar()
        b1.menu.add_radiobutton(label="Open", variable=open_file, command=self._open_file_screen, value="")
        save_file = IntVar()
        b1.menu.add_radiobutton(label="Save", variable=save_file, command=self._save_file, value="")
        save_all_file = IntVar()
        b1.menu.add_radiobutton(label="Save All", variable=save_all_file, command=self._save_all, value="")
        self.cv.create_window(x + 3, y + 7, window=b1, anchor="nw")

        b2 = Menubutton(self.root, text="Edit", width=5, font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8])
        b2.menu = Menu(b2, tearoff=0, background=self.COLOURS.getColours()[1], activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8], cursor="hand2")
        b2["menu"] = b2.menu
        copy = IntVar()
        b2.menu.add_radiobutton(label="Copy", variable=copy, command=self._copy_text, value="")
        paste = IntVar()
        b2.menu.add_radiobutton(label="Paste", variable=paste, command=self._paste_clipboard, value="")
        cut = IntVar()
        b2.menu.add_radiobutton(label="Cut", variable=cut, command=self._cut, value="")
        delete = IntVar()
        b2.menu.add_radiobutton(label="Delete", variable=delete, command=self._delete, value="")
        self.cv.create_window(x + 47, y + 7, window=b2, anchor="nw")

        b3 = Menubutton(self.root, text="Run", width=5, font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8])
        b3.menu = Menu(b3, tearoff=0, background=self.COLOURS.getColours()[1], activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8], cursor="hand2")
        b3["menu"] = b3.menu
        run = IntVar()
        b3.menu.add_radiobutton(label="Run..", variable=run, command=self._execute, value="")
        run_file = IntVar()
        b3.menu.add_radiobutton(label="Run File", variable=run_file, command=self._run_file_screen, value="")
        new_run_setup = IntVar()
        b3.menu.add_radiobutton(label="New Run Setup", variable=new_run_setup, command=self._new_run_setup_screen, value="")
        self.cv.create_window(x + 96, y + 7, window=b3, anchor="nw")

        b4 = Menubutton(self.root, text="Help", width=5, font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8])
        b4.menu = Menu(b4, tearoff=0, background=self.COLOURS.getColours()[1], activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8], cursor="hand2")
        b4["menu"] = b4.menu
        nothing = IntVar()
        b4.menu.add_radiobutton(label="Nothing Here..", variable=nothing, command=self._placeholder, value="")
        self.cv.create_window(x + 144, y + 7, window=b4, anchor="nw")

        b6 = Button(self.root, text="| >", command=self._execute, width=5, font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg="#00ff00")
        self.cv.create_window(int(self.WIDTH) - x - 125, y + 7, window=b6, anchor="nw")
        b7 = Button(self.root, text="|=|", command=self._stop_execution, width=5, font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg="#ff0000")
        self.cv.create_window(int(self.WIDTH) - x - 75, y + 7, window=b7, anchor="nw")

    def _execute(self, e=None):
        for i in self.processes:
            if i[1] == self.activeFile and Editor.DATAFOLDER.getConfig().getValue("processes.allow-parallel-run") == "False":
                self.ERROR_OUT(EDITOR_ERROR_PARALLEL_RUN_DISALLOW, True)
                return
        cur_pr = subprocess.Popen(Editor.DATAFOLDER.getConfig().getValue("processes.execution-command") % self.activeFile)
        self.processes.append([cur_pr, self.activeFile])

    def _stop_execution(self):
        cur_pr = self.processes.pop(len(self.processes) - 1)
        cur_pr[0].terminate()

    def _reload_nav_bar(self):
        self.nav_cv.delete()
        self._draw_nav_bar(20, 60, 760, 300)

    def _draw_main_text_box(self, x, y, distx, disty):
        style = Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar", gripcount=0, background=self.COLOURS.getColours()[1], darkcolor=self.COLOURS.getColours()[0], lightcolor=self.COLOURS.getColours()[1], troughcolor=self.COLOURS.getColours()[1], bordercolor=self.COLOURS.getColours()[1], arrowcolor=self.COLOURS.getColours()[8], activebackground=self.COLOURS.getColours()[1])

        scrollx = Scrollbar(self.root, cursor="hand2", orient="vertical")
        text = Text(self.root, height=distx, width=disty, borderwidth=3, highlightbackground=self.COLOURS.getColours()[8], background=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8], yscrollcommand=scrollx.set, relief="groove", insertbackground=self.COLOURS.getColours()[8], state="disabled")
        scrollx.config(command=text.yview)
        self.cv.create_window(x, y, window=text, anchor="nw")
        scrollx.place(in_=text, relx=1.0, relheight=1.0, bordermode="outside")
        return text, scrollx

    def _draw_nav_bar(self, x, y, distx, disty):
        style = Style()
        style.theme_use('default')
        style.configure("Vertical.TScrollbar", gripcount=0, background=self.COLOURS.getColours()[1], darkcolor=self.COLOURS.getColours()[0], lightcolor=self.COLOURS.getColours()[1], troughcolor=self.COLOURS.getColours()[1], bordercolor=self.COLOURS.getColours()[1], arrowcolor=self.COLOURS.getColours()[8], activebackground=self.COLOURS.getColours()[1])

        scrollx = Scrollbar(self.root, cursor="hand2", orient="vertical")
        self.nav_cv = Canvas(self.root, width=disty, height=distx, borderwidth=1, highlightbackground=self.COLOURS.getColours()[8], background=self.COLOURS.getColours()[1], yscrollcommand=scrollx.set, relief="groove")
        self.nav_frame = Frame(self.nav_cv, highlightbackground=self.COLOURS.getColours()[8], background=self.COLOURS.getColours()[1])
        scrollx.config(command=self.nav_cv.yview)
        self.nav_frame.bind("<Configure>", self._nav_frame_conf)
        self.cv.create_window(x, y, window=self.nav_cv, anchor="nw")
        self.nav_cv.create_window((4, 4), window=self.nav_frame, anchor="nw", tags="self.frame")
        scrollx.place(in_=self.nav_cv, relx=1.0, relheight=1.0, bordermode="outside", anchor="nw")

        self.nav_buttons = [[Button(self.root, text="˅ " + self.navigation.split("\\")[len(self.navigation.split("\\")) - 1], command=lambda p=0, path=self.navigation: self._hide_show_open_files(p, path), width=len("˅ " + self.navigation.split("\\")[len(self.navigation.split("\\")) - 1]), font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8]), True, 0, self.navigation, self.navigation.split("\\")[len(self.navigation.split("\\")) - 1], (20, 10)]]
        self.nav_cv.create_window(20, 10, window=self.nav_buttons[0][0], anchor="nw")

        count = 1
        for i in os.listdir(self.navigation):
            if os.path.isdir(os.path.join(self.navigation, i)):
                pl = 30 * count + 15
                self.nav_buttons.append([Button(self.root, text="> " + i, command=lambda j=count, p=os.path.join(self.navigation, i): self._hide_show_open_files(j, p), width=len("> " + i), font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8]), False, count, os.path.join(self.navigation, i), i, (40, pl)])
                self.nav_cv.create_window(40, pl, window=self.nav_buttons[count][0], anchor="nw")
                count += 1
            elif os.path.isfile(os.path.join(self.navigation, i)):
                pl = 30 * count + 15
                self.nav_buttons.append([Button(self.root, text=i, command=lambda j=count, p=os.path.join(self.navigation, i): self._hide_show_open_files(j, p), width=len(i), font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8]), False, count, os.path.join(self.navigation, i), i, (40, pl)])
                self.nav_cv.create_window(40, pl, window=self.nav_buttons[count][0], anchor="nw")
                count += 1

    def _nav_frame_conf(self, e=None):
        self.nav_cv.configure(scrollregion=self.nav_cv.bbox("all"))

    def _hide_show_open_files(self, loc_in_list, path):
        if os.path.isdir(self.nav_buttons[loc_in_list][3]):
            loc = int(loc_in_list)
            # dir
            count = 1
            items = [self.nav_buttons[loc][2], self.nav_buttons[loc][3], self.nav_buttons[loc][4], self.nav_buttons[loc][5]]
            if not self.nav_buttons[loc][1]:
                self.nav_buttons.pop(loc)
                self.nav_buttons.insert(loc, [Button(self.root, text="˅ " + items[2], command=lambda j=items[0], p=items[1]: self._hide_show_open_files(j, p), width=len("˅ " + items[2]), font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8]), True, items[0], items[1], items[2], items[3]])
                xpos = ((items[3][0] / 20) + 1) * 20
                for i in os.listdir(path):
                    if os.path.isdir(os.path.join(path, i)):
                        pl = 30 * (loc + count) + 15
                        self.nav_buttons.insert(loc + count, [Button(self.root, text="> " + i, command=lambda j=loc + count, p=os.path.join(path, i): self._hide_show_open_files(j, p), width=len("> " + i), font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8]), False, loc + count, os.path.join(path, i), i, (xpos, pl)])
                        count += 1
                    elif os.path.isfile(os.path.join(path, i)):
                        pl = 30 * (loc + count) + 15
                        self.nav_buttons.insert(loc + count, [Button(self.root, text=i, command=lambda j=loc + count, p=os.path.join(path, i): self._hide_show_open_files(j, p), width=len(i), font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8]), False, loc + count, os.path.join(path, i), i, (xpos, pl)])
                        count += 1
                rep_button_count = 0
                for i in self.nav_buttons[loc + count:]:
                    pl = 30 * (loc + count + rep_button_count) + 15
                    cur_button = [i[1], loc + count + rep_button_count, i[3], i[4], (i[5][0], pl)]
                    if os.path.isdir(cur_button[2]):
                        if cur_button[0]:
                            arrow = "˅"
                        else:
                            arrow = ">"
                    else:
                        arrow = ""
                    self.nav_buttons.pop(loc + count + rep_button_count)
                    self.nav_buttons.insert(loc + count + rep_button_count, [Button(self.root, text="%s %s" % (arrow, cur_button[3]), command=lambda j=cur_button[1], p=cur_button[2]: self._hide_show_open_files(j, p), width=len("%s %s" % (arrow, cur_button[3])), font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8]), cur_button[0], cur_button[1], cur_button[2], cur_button[3], cur_button[4]])
                    rep_button_count += 1
                self.nav_cv.delete("all")
                for i in self.nav_buttons:
                    self.nav_cv.create_window(i[5][0], i[5][1], window=i[0], anchor="nw")
            else:
                self.nav_buttons.pop(loc)
                self.nav_buttons.insert(loc, [Button(self.root, text="> " + items[2], command=lambda j=items[0], p=items[1]: self._hide_show_open_files(j, p), width=len("> " + items[2]), font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8]), False, items[0], items[1], items[2], items[3]])
                for i in os.listdir(path):
                    if self.nav_buttons[loc + count - (count - 1)][1] and os.path.isdir(self.nav_buttons[loc + count - (count - 1)][3]):
                        item = self._close_sub_files(self.nav_buttons[loc + count - (count - 1)][3], loc + count - (count - 1))
                        count -= item
                    self.nav_buttons.pop(loc + count - (count - 1))
                    count += 1
                for i in range(count - len(os.listdir(path)) - 1):
                    if self.nav_buttons[loc + count - (count - 1)][1] and os.path.isdir(self.nav_buttons[loc + count - (count - 1)][3]):
                        item = self._close_sub_files(self.nav_buttons[loc + count - (count - 1)][3], loc + count - (count - 1))
                        count -= item
                    self.nav_buttons.pop(loc + count - (count - 1))
                    count += 1
                rep_button_count = 0
                for i in self.nav_buttons[loc:]:
                    pl = 30 * (loc + rep_button_count) + 15
                    cur_button = [i[1], loc + rep_button_count, i[3], i[4], (i[5][0], pl)]
                    if os.path.isdir(cur_button[2]):
                        if cur_button[0]:
                            arrow = "˅"
                        else:
                            arrow = ">"
                    else:
                        arrow = ""
                    self.nav_buttons.pop(loc + rep_button_count)
                    self.nav_buttons.insert(loc + rep_button_count, [Button(self.root, text="%s %s" % (arrow, cur_button[3]), command=lambda j=cur_button[1], p=cur_button[2]: self._hide_show_open_files(j, p), width=len("%s %s" % (arrow, cur_button[3])), font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8]), cur_button[0], cur_button[1], cur_button[2], cur_button[3], cur_button[4]])
                    rep_button_count += 1
                self.nav_cv.delete("all")
                for i in self.nav_buttons:
                    self.nav_cv.create_window(i[5][0], i[5][1], window=i[0], anchor="nw")
        elif os.path.isfile(self.nav_buttons[loc_in_list][3]):
            if len(self.saved_ram_files) == 15:
                self.ERROR_OUT(EDITOR_ERROR_TOO_MANY_FILES, True)
            with open(self.nav_buttons[loc_in_list][3], "r") as file:
                self.saved_ram_files.append(file)
            for i in self.file_nav_buttons:
                i.destroy()
            self._draw_open_file_navigation_bar()

    def _close_sub_files(self, path, pos):
        count = 1
        for i in os.listdir(path):
            if os.path.isdir(os.path.join(path, i)) and self.nav_buttons[pos + count][1]:
                item = self._close_sub_files(os.path.join(path, i), pos + count)
                self.nav_buttons.pop(pos + count)
                count -= item
            else:
                self.nav_buttons.pop(pos + count)
        return count

    def _save_file(self, e=None):
        try:
            with open(self.activeFile, "w") as file:
                for i in self.textbox[0].get("1.0", END):
                    file.write(i)
                file.close()
        except FileNotFoundError:
            return

    def _save_all(self, e=None):
        try:
            for i in self.saved_ram_files:
                with open(i.name, "r") as file:
                    try:
                        if not self.stored_files[i.name] == file.read():
                            with open(i.name, "w") as f:
                                for l in self.stored_files[i.name]:
                                    f.write(l)
                                file.close()
                        elif not self.textbox[0].get("1.0", END) == file.read() and self.activeFile == i.name:
                            with open(i.name, "w") as f:
                                for l in self.textbox[0].get("1.0", END):
                                    f.write(l)
                                file.close()
                    except KeyError:
                        if not self.textbox[0].get("1.0", END) == file.read() and self.activeFile == i.name:
                            with open(i.name, "w") as f:
                                for l in self.textbox[0].get("1.0", END):
                                    f.write(l)
                                file.close()
                    file.close()
        except FileNotFoundError:
            return

    def _open_file(self, textentry, tkinter_win):
        with open(os.path.join(self.navigation, textentry.get()), "r") as file:
            self.saved_ram_files.append(file)
        for i in self.file_nav_buttons:
            i.destroy()
        self._draw_open_file_navigation_bar()
        file.close()
        tkinter_win.destroy()

    def _open_file_screen(self):

        if len(self.saved_ram_files) == 15:
            self.ERROR_OUT(EDITOR_ERROR_TOO_MANY_FILES, True)

        open_file_root = Toplevel()
        open_file_root.title("Editor IDE v%s -Open File" % self.VERSION)
        open_file_root.geometry("%sx%s+50+30" % (500, 300))
        open_file_root.resizable(0, 0)
        c = Canvas(open_file_root, width=int(500), height=int(300), background=self.COLOURS.getBase())
        c.pack(side='top', fill='both', expand='yes')

        c.create_text(130, 30, text="Enter File Path", fill=self.COLOURS.getColours()[8], anchor='nw', font=self.BODYFONT)
        textentry1 = Entry(open_file_root, bg=self.COLOURS.getColours()[8])
        c.create_window(260, 150, window=textentry1, width=300, height=30)

        b1 = Button(open_file_root, text="Go", command=lambda: self._open_file(textentry1, open_file_root), width=5, font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8])
        c.create_window(210, 200, window=b1, anchor="nw")

        open_file_root.mainloop()

    def _create_file(self, textentry, tkinter_win):
        with open(os.path.join(self.navigation, textentry.get()), "w") as file:
            file.close()
            tkinter_win.destroy()
            self._reload_nav_bar()

    def _new_file_screen(self):

        new_file_root = Toplevel()
        new_file_root.title("Editor IDE v%s -New File" % self.VERSION)
        new_file_root.geometry("%sx%s+50+30" % (500, 300))
        new_file_root.resizable(0, 0)
        c = Canvas(new_file_root, width=int(500), height=int(300), background=self.COLOURS.getBase())
        c.pack(side='top', fill='both', expand='yes')

        c.create_text(130, 30, text="Enter File Path", fill=self.COLOURS.getColours()[8], anchor='nw', font=self.BODYFONT)
        textentry1 = Entry(new_file_root, bg=self.COLOURS.getColours()[8])
        c.create_window(260, 150, window=textentry1, width=300, height=30)

        b1 = Button(new_file_root, text="Go", command=lambda: self._create_file(textentry1, new_file_root), width=5, font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8])
        c.create_window(210, 200, window=b1, anchor="nw")

        new_file_root.mainloop()

    def _execute_file(self, textentry, tkinter_win):
        for i in self.processes:
            if i[1] == os.path.join(self.navigation, textentry.get()) and Editor.DATAFOLDER.getConfig().getValue("processes.allow-parallel-run") == "False":
                self.ERROR_OUT(EDITOR_ERROR_PARALLEL_RUN_DISALLOW, True)
                return
        cur_pr = subprocess.Popen(Editor.DATAFOLDER.getConfig().getValue("processes.execution-command") % os.path.join(self.navigation, textentry.get()))
        self.processes.append([cur_pr, os.path.join(self.navigation, textentry.get())])
        tkinter_win.destroy()

    def _run_file_screen(self):

        run_file_root = Toplevel()
        run_file_root.title("Editor IDE v%s -Run File" % self.VERSION)
        run_file_root.geometry("%sx%s+50+30" % (500, 300))
        run_file_root.resizable(0, 0)
        c = Canvas(run_file_root, width=int(500), height=int(300), background=self.COLOURS.getBase())
        c.pack(side='top', fill='both', expand='yes')

        c.create_text(130, 30, text="Enter File Path", fill=self.COLOURS.getColours()[8], anchor='nw', font=self.BODYFONT)
        textentry1 = Entry(run_file_root, bg=self.COLOURS.getColours()[8])
        c.create_window(260, 150, window=textentry1, width=300, height=30)

        b1 = Button(run_file_root, text="Go", command=lambda: self._execute_file(textentry1, run_file_root), width=5, font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8])
        c.create_window(210, 200, window=b1, anchor="nw")

        run_file_root.mainloop()

    def _execute_file_new_setup(self, textentry, tkinter_win):
        for i in self.processes:
            if i[1] == self.activeFile and Editor.DATAFOLDER.getConfig().getValue("processes.allow-parallel-run") == "False":
                self.ERROR_OUT(EDITOR_ERROR_PARALLEL_RUN_DISALLOW, True)
                return
        cur_pr = subprocess.Popen(textentry.get() % self.activeFile)
        self.processes.append([cur_pr, self.activeFile])
        tkinter_win.destroy()

    def _new_run_setup_screen(self):

        new_run_setup_root = Toplevel()
        new_run_setup_root.title("Editor IDE v%s -Run File Setup" % self.VERSION)
        new_run_setup_root.geometry("%sx%s+50+30" % (500, 300))
        new_run_setup_root.resizable(0, 0)
        c = Canvas(new_run_setup_root, width=int(500), height=int(300), background=self.COLOURS.getBase())
        c.pack(side='top', fill='both', expand='yes')

        c.create_text(55, 30, text="Enter Execution Command", fill=self.COLOURS.getColours()[8], anchor='nw', font=self.BODYFONT)
        textentry1 = Entry(new_run_setup_root, bg=self.COLOURS.getColours()[8])
        c.create_window(260, 150, window=textentry1, width=300, height=30)

        b1 = Button(new_run_setup_root, text="Go", command=lambda: self._execute_file_new_setup(textentry1, new_run_setup_root), width=5, font=self.SMALLFONT, borderwidth=0, background=self.COLOURS.getColours()[1], cursor="hand2", activebackground=self.COLOURS.getColours()[1], fg=self.COLOURS.getColours()[8])
        c.create_window(210, 200, window=b1, anchor="nw")

        new_run_setup_root.mainloop()

    def _placeholder(self):
        pass
