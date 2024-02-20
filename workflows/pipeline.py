from lk_elections_py import ScreenShot
# import os

def main():
    ss = ScreenShot.random()
    # os.startfile(ss.image_path)
    ss.tweet()
    


if __name__ == "__main__":
    main()
