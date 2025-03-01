import tello
from ui import TelloUI

# https://tello.oneoffcoder.com/python-manual-control.html

def main():
    drone = tello.Tello('', 8889)  
    vplayer = TelloUI(drone)
    vplayer.root.mainloop() 


if __name__ == '__main__':
    main()