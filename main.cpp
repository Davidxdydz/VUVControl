#include "steppermotor.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    steppermotor w;
    w.get_serial_ports();
    w.show();

    return a.exec();
}
