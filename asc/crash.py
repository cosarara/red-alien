
import sys
import traceback
def crash(exception):
    info = traceback.format_exc()
    try:
        crash_qt(info)
    except ImportError:
        try:
            crash_tk(info)
        except ImportError:
            crash_cli(exception)

def crash_qt(info):
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None,"Error",
            "Something bad happened:\n" + info)

def crash_tk(info):
    import tkinter as tk

    root = tk.Tk()
    T = tk.Text(root, height=2, width=30)
    T.pack(fill=tk.BOTH, expand=1)
    T.insert(tk.END, "Something bad happened:\n" + info)
    QUIT = tk.Button(text="QUIT", command=root.quit)

    QUIT.pack({"side": "left"})
    tk.mainloop()

def crash_cli(ex):
    print("Sry, can't GUI. Something bad happened, read this:")
    raise ex

if __name__ == "__main__":
    try:
        aww
    except Exception as e:
        crash(e)

