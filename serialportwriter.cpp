
#include "serialportwriter.h"
#include"steppermotor.h"
#include <QCoreApplication>

SerialPortWriter::SerialPortWriter(QSerialPort *m_serialPort, QObject *parent) :
    QObject(parent),
    m_serialPort(m_serialPort),
    m_standardOutput(stdout)
{
    m_timer.setSingleShot(true);
 /*   connect(m_serialPort, &QSerialPort::bytesWritten,
            this, &SerialPortWriter::handleBytesWritten);
    connect(m_serialPort, &QSerialPort::errorOccurred,
            this, &SerialPortWriter::handleError);
    connect(&m_timer, &QTimer::timeout, this, &SerialPortWriter::handleTimeout);   */
}

void steppermotor::handleError(QSerialPort::SerialPortError serialPortError)
{
    if (serialPortError == QSerialPort::WriteError) {
        m_standardOutput << QObject::tr("An I/O error occurred while writing"
                                        " the data to port %1, error: %2")
                            .arg(comunication_port->portName())
                            .arg(comunication_port->errorString())
                         << endl;
    }


}


void steppermotor::handleTimeout()
{
    m_standardOutput << QObject::tr("Operation timed out for port %1, error: %2")
                        .arg(comunication_port->portName())
                        .arg(comunication_port->errorString())
                     << endl;
}

void steppermotor::handleBytesWritten(qint64 bytes)
{
    m_bytesWritten += bytes;
    if (m_bytesWritten == m_writeData.size()) {
    }
}


