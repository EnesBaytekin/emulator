from os import name as os_name

if os_name == "posix":
    
    from tty import setraw
    from termios import tcgetattr, tcsetattr, TCSADRAIN
    from sys import stdin
    from os import O_NONBLOCK
    from fcntl import fcntl, F_GETFL, F_SETFL
    def get_character():
        fd = stdin.fileno()
        old_settings = tcgetattr(fd)
        old_flags = fcntl(fd, F_GETFL)
        try:
            setraw(fd)
            fcntl(fd, F_SETFL, old_flags | O_NONBLOCK)
            byte = stdin.buffer.raw.read(1)
            if byte is not None:
                try:
                    return byte.decode()
                except:
                    return ""
            else:
                return None
        finally:
            fcntl(fd, F_SETFL, old_flags)
            tcsetattr(fd, TCSADRAIN, old_settings)

    from os import system
    def clear_terminal():
        system("clear")

elif os_name == "nt":

    from msvcrt import getwch, kbhit
    def get_character():
        if kbhit():
            return getwch()
        else:
            return None

    from os import system
    def clear_terminal():
        system("cls")

