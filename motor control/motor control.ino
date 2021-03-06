//This runs on arduino nano
//Old Bootloader

//ints on arduino are 16 bits, which overflow on large movements... --> longs

//New version, less functions but way easier setup now that the motor calibration process is fixed

/*
This is just the stepper control, operated over serial messages:
every message has to start with "$", followed by a three character
control sequence and (always) a (floating point) number.
every function returns a status message over serial, ending with \r\n.
If an error occured, the message will start with "error".


caw         set current wavelength, position is now zero

gtp         go to position
gtw         go to wavelength

rot         rotate unconditionally by angle in degrees

tst         echos "connected!"

examples:
$gtp 1000
$rst 0              the number is not used but required, can be anything
$gtw 135.5
*/

enum PIN
{
  Enable = 4,          //Enable the Motor
  Direction = 5,       //Direction of the Motor: HIGH is clockwise
  Step = 6,            //Change to step once in Direction
  NextPos = 7,         //?
  ArrivedPosition = 8, //?
  LowerEndSwitch = 2,  //switch to turn motor off at absolute minimum position
  UpperEndSwitch = 3   //switch to turn motor off at absolute maximum position
};

enum ERROR
{
  LowerEndStop = -1,
  UpperEndStop = 1,
  zeroWavelengthNotSet = 2
};
const int baudrate = 9600;
const long stepsPerRotation = 1600;
const float nmPerRotation = 2;
long a[255];
char buffer[3];
const long moveDelay = 500; //move interval in microseconds
long currentPosition = -1;
float zeroWavelength = -10000;

void setup()
{
  pinMode(PIN::Enable, OUTPUT);
  pinMode(PIN::Direction, OUTPUT);
  pinMode(PIN::Step, OUTPUT);
  pinMode(PIN::NextPos, INPUT_PULLUP);
  pinMode(PIN::LowerEndSwitch, INPUT_PULLUP);
  pinMode(PIN::UpperEndSwitch, INPUT_PULLUP);

  digitalWrite(PIN::Enable, HIGH);
  digitalWrite(PIN::Step, LOW);
  digitalWrite(PIN::LowerEndSwitch, HIGH);
  digitalWrite(PIN::UpperEndSwitch, HIGH);

  Serial.begin(baudrate);
  Serial.println("connected and ready!");
}

//dirty hack to restart the program
void (*resetFunc)(void) = 0;

//performs one step in the current direction
int performStep(char direction)
{
  digitalWrite(PIN::Direction, direction);
  if (!digitalRead(PIN::UpperEndSwitch) && direction == HIGH)
  {
    return ERROR::UpperEndStop;
  }
  if (!digitalRead(PIN::LowerEndSwitch) && direction == LOW)
  {
    return ERROR::LowerEndStop;
  }
  digitalWrite(PIN::Step, !digitalRead(PIN::Step));
  currentPosition += direction * 2 - 1; //keep track of current position
  delayMicroseconds(moveDelay);
  return 0;
}

long wavelength2Position(float wavelength)
{
  return (float)(wavelength-zeroWavelength)/(float)nmPerRotation*stepsPerRotation;
}
float position2Wavelength(long position)
{
  return position/(float)stepsPerRotation*(float)nmPerRotation + zeroWavelength;
}

//rotates by angle in degrees
int rotate(float angle)
{
  char direction = angle>0;
  angle = abs(angle);
  long steps = angle / 360.0 * stepsPerRotation;
  for (long i = 0; i < steps; i++)
  {
    int r = performStep(direction);
    if (r)
      return r;
  }
  return 0;
}

//drives the motor to position
//throws an error if range not set or out of range
int goToPosition(long position)
{
  //set Direction
  char direction = position>currentPosition;

  //move to position
  while (position != currentPosition)
  {
    int r = performStep(direction);
    if (r)
      return r;
  }
  return 0;
}
int goToWavelength(float wavelength)
{
    if(zeroWavelength< -1000){
        return ERROR::zeroWavelengthNotSet;
    }
  return goToPosition(wavelength2Position(wavelength));
}

void interpretMessage()
{
  //messages start with $
  while (Serial.available() < 4 || Serial.read() != '$')
    ;
  //3 bytes instruction
  String instruction = Serial.readStringUntil(' ');
  float value = Serial.parseFloat();
  String response = "unknown command: " + instruction;
  if (instruction == "rst") //reset
  {
    resetFunc();
  }
  if (instruction == "tst")
  {
    response = "connected!";
  }
  if (instruction == "caw")
  {
        currentPosition = 0;
        zeroWavelength = value;
        response = "current position set to " + String(currentPosition) +"=" + String(position2Wavelength(currentPosition))+"nm";
  }
  if (instruction == "gtp") //go to position
  {
    int r = goToPosition((long)value);
    if (r == 0)
    {
      response = "position: " + String(currentPosition);
    }
    if (r == ERROR::LowerEndStop || r == ERROR::UpperEndStop)
    {
      //aborted due to failsafe switches
      response = "error: failsafe triggered";
    }
  }
  if (instruction == "gtw") //go to wavelength
  {
    int r = goToWavelength(value);
    if (r == 0)
    { //it worked!
      response = "wavelength [nm]: " + String(position2Wavelength(currentPosition));
    }
    if (r == ERROR::zeroWavelengthNotSet)
    { //range not set correctly
      response = "error: range not set";
    }
    if (r == ERROR::LowerEndStop || r == ERROR::UpperEndStop)
    {
      //aborted due to failsafe switches
      response = "error: failsafe triggered";
    }
  }
  if (instruction == "rot")
  {
    int r = rotate(value);
    if (r == ERROR::LowerEndStop || r == ERROR::UpperEndStop)
    {
      //aborted due to failsafe switches
      response = "error: failsafe triggered";
    }
    if (r == 0)
      response = "rotated " + String(value) + " degrees";
  }
  Serial.println(response);
}
void loop()
{
  interpretMessage();
}
