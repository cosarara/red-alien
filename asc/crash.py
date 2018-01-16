
import sys
import traceback

default_excepthook = sys.excepthook

def crash(t, v, trace):
    info = "\n".join(traceback.format_exception(t, v, trace))
    try:
        crash_qt(info)
    except ImportError:
        try:
            crash_tk(info)
        except ImportError:
            crash_cli(t, v, trace)
    sys.exit(1)

def crash_qt(info):
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMessageBox.critical(None, "Error",
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

def crash_cli(t, v, trace):
    default_excepthook(t, v, trace)

sys.excepthook = crash

if __name__ == "__main__":
    aww # pylint: disable=undefined-variable

