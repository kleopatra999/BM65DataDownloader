import serial

class Measurement(object):
    def __init__(self, data):
        self.status = bin(data[0])
        self.systolic = data[1] + 25
        self.diastolic = data[2] + 25
        self.pulse =  data[3]
        self.month = data[4]
        self.day = data[5]
        self.hours = data[6]
        self.minutes = data[7]
        self.year = data[8] + 2000
        self.time = "{0}-{1:02}-{2:02} {3:02}:{4:02}".format(self.year,
                                                             self.month,
                                                             self.day,
                                                             self.hours,
                                                             self.minutes)

    def __str__(self):
        return "\n".join(["Time               : {0}",
                          "Systolic pressure  : {1} mmHg",
                          "Diastolic pressure : {2} mmHg",
                          "Pulse              : {3} BPM",
                          "Status bits        : {4}"]).format(self.time,
                                                              self.systolic,
                                                              self.diastolic,
                                                              self.pulse,
                                                              self.status)

class BeurerBM65(object):
    def __init__(self, port):
        self.port = port

    def sendBytes(self, connection, byteList, responseLength = 1):
        connection.write(''.join([chr(byte) for byte in byteList]))
        response = connection.read(responseLength)
        return [ord(char) for char in response]
    
    def bytesToString(self, bytes):
        return "".join([chr(byte) for byte in bytes])

    def getMeasurements(self):
        ser = serial.Serial(
            port = self.port,
            baudrate = 4800,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 1)
        
        pong = self.sendBytes(ser, [0xAA])
        print "Sent ping. Expected 0x55, got {0}".format(hex(pong[0]))
        
        description = self.bytesToString(self.sendBytes(ser, [0xA4], 32))
        print "Requested device description. Got '{0}'".format(description)
        
        measurementCount = self.sendBytes(ser, [0xA2])[0]
        print "Found {0} measurement(s)...".format(measurementCount)
        
        for idx in range(measurementCount):
            yield Measurement(self.sendBytes(ser, [0xA3, idx + 1], 9))
        
        print "Done. Closing connection..."     
        ser.close()

if __name__ == "__main__":
    conn = BeurerBM65("/dev/ttyUSB0")
    for idx, measurement in enumerate(conn.getMeasurements()):
        print ""
        print "MEASUREMENT {0}".format(idx + 1)
        print measurement