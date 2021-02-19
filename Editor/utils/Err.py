from tkinter import *
from Editor import *
from Editor.utils.Error_Type import *

bodyfont = (SETTINGS.getText().getFamily(), 15)


def err(error, toplevel):
    def stop():
        errortk.destroy()
        return
    if toplevel:
        errortk = Toplevel()
    else:
        errortk = Tk()
    if not type(error) == ErrorType:
        raise EditorException(EDITOR_ERROR_INVALID_TYPE)
    errortk.title("Editor v1.0 -Err " + "-code " + str(error.getCode()))
    errortk.geometry("1000x200")
    ce = Canvas(errortk, width=1000, height=200)
    ce.pack(side='top', fill='both', expand='yes')
    errortk.resizable(0, 0)

    img = PhotoImage(file=DATAFOLDER.join(DATAFOLDER.getImgItemsFolder(), "Err.gif"))

    ce.create_image(40, 75, image=img, anchor='nw')
    ce.create_text(250, 50, text="There is an error: " + error.getMSG(), fill="Black", anchor='nw', font=('times', 20, 'bold'))
    ce.create_image(885, 75, image=img, anchor='nw')
    b1 = Button(errortk, text="Continue", command=stop, width=20, font=bodyfont, borderwidth=0, background="white", cursor="hand2", highlightbackground="blue", relief="sunken")
    ce.create_window(480, 150, window=b1)

    errortk.mainloop()
    return
