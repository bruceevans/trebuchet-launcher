import sys

if sys.platform == 'win32':
    import win32ui
    import win32gui
    import win32api
    import win32con
else:
    print("need mac solution")

from PIL import Image

def isWindows():
    if sys.platform == 'win32':
        return True

def getIcon(path, iconName):

    if isWindows():
        print("Path is ", path)
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)

        large, small = win32gui.ExtractIconEx(path, 0)
        win32gui.DestroyIcon(large[0])

        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
        hdc = hdc.CreateCompatibleDC()

        hdc.SelectObject(hbmp)
        hdc.DrawIcon((0, 0), small[0])

        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGBA',
            (32, 32),
            bmpstr,
            'raw',
            'BGRA', 0, 1
        )
        img.save(iconName)
    else:
        print("On a mac, saving icon")
