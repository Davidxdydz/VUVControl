//arduino nano

int Enable = 4;
int Dir = 5;
int Pulse = 6;
int nextpos = 7;
int arrived_position = 8;
int lower_end_switch = 2;
int upper_end_switch = 3;

long  a[255];
int i, ii, b, pb, sp, us;
const double nm_init = 120.0;
double nm_positions, nm_prev, nm_shift[15], data;

void nm ();


void setup() {

  pinMode (Enable, OUTPUT);
  pinMode (Dir, OUTPUT);
  pinMode (Pulse, OUTPUT);
  pinMode (nextpos, INPUT_PULLUP);
  pinMode (lower_end_switch, INPUT_PULLUP);
  pinMode (upper_end_switch, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(upper_end_switch), upper_stopswitch, LOW);
  attachInterrupt(digitalPinToInterrupt(lower_end_switch), lower_stopswitch, LOW);
  digitalWrite(Enable, HIGH);
  digitalWrite(Pulse, LOW);
  digitalWrite(lower_end_switch, HIGH);
  digitalWrite(upper_end_switch, HIGH);  

  b = 500;

  Serial.begin (9600);
}

void(*resetFunc)(void) = 0;

void loop() {
  i++;
  nm (nm_positions);
  if (nm_positions !=0) 
  {
  nm_shift[i] = nm_init - nm_positions;
  } 

if (nm_positions == 0) 
{
  ii = i+1;
  i = 1;
loop_04:
  if (Serial.parseFloat() != 1) {
  goto loop_04;
  }
    Serial.println("Go to starting Position");
    sp = digitalRead(lower_end_switch);
    while (digitalRead(lower_end_switch) == HIGH){
        digitalWrite(Dir, LOW);
        digitalWrite(Pulse, !digitalRead(Pulse));
        delayMicroseconds(b);
        }
    Serial.println("Starting position arrived");
    delay(1000);
   if (nm_shift[i] < 0) {digitalWrite(Dir, HIGH);
    nm_shift[i] = -nm_shift[i];}
  else {}
    a[i] = 800 * nm_shift[i];
    Serial.println("Motor is running");


//going to positions
loop_01:
  if (a[i] >= 0) {
    digitalWrite(Pulse, !digitalRead(Pulse));
    a[i]--;
    delayMicroseconds(b);
    goto loop_01;
  }
  else
  {
    i++;
    if (i != ii) {goto loop_04;}
    else {i = 0;}
  }
}
}


void nm (int) {
  loop_03:
  while (Serial.available() > 0) {Serial.read();}
  Serial.print (i);
  Serial.print (" position in nm = ");

  while (Serial.available() == 0) {}

  nm_positions = Serial.parseFloat();
  
   if (nm_positions == 0) {
    Serial.println();
    Serial.println ("Wavelenth list completed");  
   goto finito;
}
 
    if ((120 > nm_positions) or (nm_positions > 300)) {
    Serial.println ("OUT OF RANGE! (min 120nm, max 300nm)");
    goto loop_03;
    }
    else {
  Serial.print (nm_positions);
  Serial.print ("nm");


}
finito:
    Serial.println ();
   
}


void upper_stopswitch(){
 
    Serial.println("Error, motor hit the boundary!");
    Serial.println("Resetting Programm");
    Serial.println("Going to starting position");
    delayMicroseconds(1000);
    while (digitalRead(lower_end_switch) == HIGH){
        digitalWrite(Dir, LOW);
        digitalWrite(Pulse, !digitalRead(Pulse));
        delayMicroseconds(b);
        }
// Problem: does not show the complete error message
    resetFunc();   
}

//switch used for starting position
void lower_stopswitch(){
  digitalWrite(Pulse, !digitalRead(Pulse));
}
