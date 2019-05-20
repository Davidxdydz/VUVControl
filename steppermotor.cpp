#include "steppermotor.h"
#include "ui_steppermotor.h"
#include "serialportwriter.h"
#include <QCoreApplication>
#include "QDebug"
#include <QTime>
#include <QThread>
#include<QIODevice>

steppermotor::steppermotor(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::steppermotor)
{
    ui->setupUi(this);
}


steppermotor::~steppermotor()
{
    delete ui;
}


//to search for serial ports
void steppermotor::get_serial_ports(){
    QList<QSerialPortInfo> systemports = QSerialPortInfo::availablePorts();
    ui->SerialPortBox->clear();
    for (int i = 0; i < systemports.size(); ++i) {
        ui->SerialPortBox->addItem(systemports[i].portName());
    }
}


//Defines the text in the status printer
void steppermotor::statusprinter(const QString &s){
    ui->StatusText->clear();
    ui->StatusText->setText(s);
}


// Defines the text in the reading printer
void steppermotor::readingprinter(const QString &r){
    ui->ReadingText->clear();
    ui->ReadingText->setText(r);
    qApp->processEvents();
}

//Selects the serial port and opens it
void steppermotor::on_SetButton_clicked()
{
    comunication_port.setPortName(ui->SerialPortBox->currentText());
    comunication_port.open(QIODevice::ReadWrite);
    if (comunication_port.portName()!=""){
        QString s = "Port was set";
        statusprinter(s);
    }
    else {
        QString s = "No port set.";
        statusprinter(s);
        }
}


//Lets the engine drive to the starting position
void steppermotor::on_StartingPosition_clicked()
{
    write("120.0 /r"); //Signal for Starting Position
    QThread::msleep(1000);
    write("0");
    QThread::msleep(1000);
    write("1");
    QThread::msleep(1000);
    if (reading() == "Go to Starting Position")
    {
        QString s = "Go to Starting Positoin!";
        readingprinter(reading());
    }
    else {
        QString s = "Error, motor does not respond!";
        statusprinter(s);
         }
}


//Adds a single value to the list
void steppermotor::on_AddButton_clicked()
{
    double a;
    a= ui->WavelengthSelector->value();
    lambdas.append(a);
    ui->ListWavelength->addItem("Position "+QString::number(lambdas.size()-1+1)+ ": "+QString::number(lambdas[lambdas.size()-1])+" nm");
}


//Adds a section of wavelengths to the list
void steppermotor::on_AddIntervallButton_clicked()
{
    double start;
    double end;
    double step;
    start = ui->StartIntervallSelector ->value();
    end = ui->EndIntervallSelector->value();
    step = ui -> StepIntervallSelector->value();
    for(int i =0; start+i*step <= end; i++)
    {
        double b = start + i*step;
        lambdas.append(b);
        ui->ListWavelength->addItem("Position "+QString::number(lambdas.size()-1+1)+ ": "+QString::number(lambdas[lambdas.size()-1])+" nm");
    }
}


//Communication via the serial port
QString steppermotor::write(QString writeData)
{
    const QByteArray requestData = writeData.toUtf8();
    comunication_port.write(requestData);
    QString r;
   if (comunication_port.waitForBytesWritten(100))
    {
        // read response
        if (comunication_port.waitForReadyRead(100))
        {
            QByteArray responseData = comunication_port.readAll();
            while (comunication_port.waitForReadyRead(100))
                responseData += comunication_port.readAll();
            r = QString::fromUtf8(responseData);
            qDebug()<< r;
            return r;
        }
        else
        {
            qDebug() << (tr("Wait read response timeout %1")
                         .arg(QTime::currentTime().toString()));
            return r;
        }
    }
    else
    {
    }
}


//does not do anything right now
QString steppermotor::reading()
{
    QString r;
    return r;
}


//should represent recorded data
void steppermotor::received_data()
{

}


//sends the engine the wavelengths
void steppermotor::on_UploadButton_clicked()
{
    if (lambdas.size() > 0)
    {
        if (comunication_port.portName() != "")
        {
            lambdas.append(0); //Signal for finishing
            QString s = "Sending list.";
            statusprinter(s);
            for (int i = 0; i < lambdas.size(); i++ )
            {
                QString data = QString::number(lambdas[i]);
                data.append("\r");
                readingprinter(write(data)); //redingtext wird nicht im loop aktualisiert
                QThread::msleep(1000);
                qApp->processEvents();
            }
        }
        else
        {
            QString s = "No port set!";
            statusprinter(s);
        }
    }
    else
    {
        QString s = "No wavelength set!";
        statusprinter(s);
    }
    QString s = "Finished sending";
    statusprinter(s);
}


//Starts the engine (to be completed: when to continue)
void steppermotor::on_StartButton_clicked()
{
    for (int i = 0; i < lambdas.size(); i++){
    QString s = "Going to starting position";
    statusprinter(s);
    QString t = "Starting motor!";
    statusprinter(t);
    readingprinter(write("1"));
    QThread::msleep(1000);
    qApp->processEvents();
    QThread::msleep(5000); //Still needs to be changed; Wanted: Wait until enough data has been recorded
    received_data();
    }
}


//Wavelength list is emptied
void steppermotor::on_ResetButton_clicked()
{
   lambdas.clear();
   ui->ListWavelength->clear();
   QString s = "Emptying the Wavelenght List!";
   statusprinter(s);
}


//deletes the list of received data
void steppermotor::on_ResetReceivedDataButton_clicked()
{
    ui->ListReceivedData->clear();
    QString s = "Received data deleted";
    statusprinter(s);
}
