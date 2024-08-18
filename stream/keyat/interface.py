import serial
import io
import string

class Interface():

    def __init__(self, port):
        self.p = port
        #self.brate = 9600
        self.brate = 1200

    def add_args(self, parser):
        parser.add_argument('--string', '-s', action="store", help='Send a string of text')

    def string_clean(self, text):
        printable = set(string.printable)
        text = text.replace("~","~+54~:41~-54").replace("^","~+54~:07~-54").replace("\\n","~:28").replace("\n","~:28").encode("ascii", "ignore").decode()
        return text

    def parse_args(self,args):

        if args.string is not None:
            self.string = self.string_clean(args.string)

        self.send()


    def command(self, command):
        with serial.Serial(self.p, self.brate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, rtscts=0, xonxoff=1) as ser:
            ser.write("~"+command)

    def send(self, data=None):

        if data is None:
            data = self.string
        else:
            text = self.string_clean(data)

        with serial.Serial(self.p, self.brate, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, rtscts=0, xonxoff=1) as ser:
            ser.write((text+"\r").encode("utf-8"))
            ser.flush()


