import serial

# Configure the COM port
port = "COM3"  # Replace with the appropriate COM port name
baudrate = 9600

try:
    # Open the COM port
    ser = serial.Serial(port, baudrate=baudrate)
    print("Serial connection established.")

    # Read data from the Arduino
    while True:
        data = input('input data:')
        ser.write(data.encode())
        # Read a line of data from the serial port
        line = ser.readline().decode().strip()

        if line:
            print("Received:", line)

except serial.SerialException as se:
    print("Serial port error:", str(se))

except KeyboardInterrupt:
    pass

finally:
    # Close the serial connection
    if ser.is_open:
        ser.close()
        print("Serial connection closed.")
