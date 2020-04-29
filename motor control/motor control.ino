//This runs on arduino nano
//Old Bootloader

//ints on arduino are 16 bits, which overflow on large movements... --> longs

/*
This is just the stepper control, operated over serial messages:
every message has to start with "$", followed by a three character
control sequence and (always) a (floating point) number.
every function returns a status message over serial, ending with \r\n.
If an error occured, the message will start with "error".



rst         reset the program

mip         set minimum position
map         set maximum position
max         set maximum position to current
miw         set minimum wavelength
maw         set maximum wavelength
caw         set current wavelength

fmi         find and set minimum position using the switches
fma         find and set maximum position using the switches

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
  PositionRangeNotSet = 2,
  WavelengthRangeNotSet = 3,
  PositionOutOfRange = 4
};
const int baudrate = 9600;
const long stepsPerRotation = 1600;
long a[255];
char buffer[3];
const long moveDelay = 500; //move interval in microseconds
long currentPosition = -1;
long maxPosition = -1;    //no minPosition required, 0 gets set as min
float minWavelength = -10000; //in nanometer
float maxWavelength = -10000;

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

void findMinimum()
{
  while (!performStep(LOW))
  {
  }
  currentPosition = 0;
}

void findMaximum()
{
  while (!performStep(HIGH))
  {
  }
  maxPosition = currentPosition;
}
long wavelength2Position(float wavelength)
{
  return (wavelength - minWavelength) / (maxWavelength - minWavelength) * (float)maxPosition;
}
float position2Wavelength(long position)
{
  return (float)currentPosition / (float)maxPosition * (maxWavelength - minWavelength) + minWavelength;
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
  if (maxPosition < 0 || currentPosition < 0)
  {
    return ERROR::PositionRangeNotSet;
  }

  if (position > maxPosition || position < 0)
  {
    return ERROR::PositionOutOfRange;
  }

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
  if (maxWavelength < -1000 || minWavelength < -1000)
  {
    return ERROR::WavelengthRangeNotSet;
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
      if(maxPosition<0||minWavelength<-1000||maxWavelength<-1000)
      {
        response = "error: can't set current wavelength if ranges are not set";
      }else{
        currentPosition = wavelength2Position(value);
        response = "current position set to " + String(currentPosition) +"=" + String(position2Wavelength(currentPosition))+"nm";
      }
  }
  if (instruction == "gtp") //go to position
  {
    int r = goToPosition((long)value);
    if (r == 0)
    {
      response = "position: " + String(currentPosition);
    }
    if (r == ERROR::PositionOutOfRange)
    { //out of range
      response = "error: measurement position out of range, min is 0 and max is " + String(maxPosition);
    }
    if (r == ERROR::PositionRangeNotSet)
    { //range not set correctly
      response = "error: range not set";
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
    if (r == ERROR::PositionOutOfRange)
    { //out of range
      response = "error: wavelength out of range, min is " + String(minWavelength) + " and max is " + String(maxWavelength);
    }
    if (r == ERROR::WavelengthRangeNotSet)
    { //range not set correctly
      response = "error: range not set";
    }
    if (r == ERROR::LowerEndStop || r == ERROR::UpperEndStop)
    {
      //aborted due to failsafe switches
      response = "error: failsafe triggered";
    }
  }
  if (instruction == "mac")
  { //set maximum position
    maxPosition = currentPosition;
    response = "maximum position set to " + String(currentPosition);
  }
  if (instruction == "mip")
  { //set minimum position
    currentPosition = (long)value;
    response = "minimum position set to " + String(value);
  }
  if (instruction == "map")
  { //set maximum position
    maxPosition = (long)value;
    response = "maximum position set to " + String(value);
  }
  if (instruction == "miw")
  { //set minimum wavelength
    minWavelength = value;
    response = "minimum Wavelength set to " + String(value);
  }
  if (instruction == "maw")
  { //set maximum wavelength
    maxWavelength = value;
    response = "maximum Wavelength set to " + String(value);
  }
  if (instruction == "fmi")
  {
    findMinimum();
    response = "minimum set";
  }
  if (instruction == "fma")
  {
    findMaximum();
    response = "maximum set to " + String(maxPosition);
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
