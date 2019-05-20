#ifndef steppermotor_H
#define steppermotor_H

#include <QMainWindow>
#include <QString>
#include <QList>

#include <QtSerialPort/QSerialPort>
#include <QtSerialPort/QSerialPortInfo>


#include <QByteArray>
#include <QObject>
#include <QSerialPort>
#include <QTextStream>
#include <QTimer>

namespace Ui {
class steppermotor;
}

class steppermotor : public QMainWindow
{
    Q_OBJECT

public:
    explicit steppermotor(QWidget *parent = nullptr);
    ~steppermotor();
    void get_serial_ports();
    QString write(QString writeData);
    QString reading();
    void received_data();

public slots:
    void on_SetButton_clicked();
    void on_AddButton_clicked();
    void on_AddIntervallButton_clicked();
    void on_UploadButton_clicked();
    void on_ResetButton_clicked();
    void on_StartingPosition_clicked();
    void on_StartButton_clicked();
    void on_ResetReceivedDataButton_clicked();

private:
    void statusprinter(const QString &s);
    void readingprinter(const QString &r);
    QList<float> lambdas;
    Ui::steppermotor *ui;
    QSerialPort comunication_port;
    QByteArray m_writeData;
    QTextStream m_standardOutput;
    qint64 m_bytesWritten = 0;
    QTimer m_timer;
};

#endif // steppermotor_H
