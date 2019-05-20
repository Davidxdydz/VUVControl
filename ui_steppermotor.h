/********************************************************************************
** Form generated from reading UI file 'steppermotor.ui'
**
** Created by: Qt User Interface Compiler version 5.12.1
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_STEPPERMOTOR_H
#define UI_STEPPERMOTOR_H

#include <QtCore/QVariant>
#include <QtWidgets/QApplication>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QDoubleSpinBox>
#include <QtWidgets/QGraphicsView>
#include <QtWidgets/QLabel>
#include <QtWidgets/QLineEdit>
#include <QtWidgets/QListWidget>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QRadioButton>
#include <QtWidgets/QTabWidget>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_steppermotor
{
public:
    QWidget *centralWidget;
    QTabWidget *tabWidget;
    QWidget *Motorcontrol;
    QLabel *IntervallLabel;
    QLabel *PossibleWavelenth;
    QLabel *ReadingText;
    QDoubleSpinBox *StepIntervallSelector;
    QPushButton *UploadButton;
    QPushButton *AddIntervallButton;
    QLabel *lambdaAddLabel;
    QDoubleSpinBox *StartIntervallSelector;
    QDoubleSpinBox *EndIntervallSelector;
    QListWidget *ListWavelength;
    QLabel *StartIntervallLabel;
    QComboBox *SerialPortBox;
    QLabel *EndIntervallLabel;
    QPushButton *ResetButton;
    QLabel *SerialPortLabel;
    QLabel *ReadingHead;
    QDoubleSpinBox *WavelengthSelector;
    QLabel *InfoList;
    QPushButton *AddButton;
    QLabel *StepIntervallLabel;
    QLabel *StatusHead;
    QPushButton *SetButton;
    QLabel *StatusText;
    QPushButton *StartingPosition;
    QLabel *StartingPositionLabel;
    QPushButton *StartButton;
    QWidget *Received_data;
    QPushButton *ResetReceivedDataButton;
    QLabel *ReceivedLabel;
    QListWidget *ListReceivedData;
    QGraphicsView *LivePlot;
    QLabel *LivePlotlabel;
    QPushButton *LivePlot_ResetButton;
    QPushButton *ZoomLivePlot_Button;
    QWidget *Send_result;
    QLabel *EnterEmail_label;
    QLineEdit *Email_Edit;
    QPushButton *SendResult_Button;
    QGraphicsView *Preview;
    QLabel *Preview_label;
    QLabel *DataType_label;
    QRadioButton *DataType1;
    QRadioButton *DataType2;
    QRadioButton *DataType3;
    QLabel *label;
    QRadioButton *OptionData;
    QRadioButton *OptionPlot;

    void setupUi(QMainWindow *steppermotor)
    {
        if (steppermotor->objectName().isEmpty())
            steppermotor->setObjectName(QString::fromUtf8("steppermotor"));
        steppermotor->resize(954, 491);
        centralWidget = new QWidget(steppermotor);
        centralWidget->setObjectName(QString::fromUtf8("centralWidget"));
        tabWidget = new QTabWidget(centralWidget);
        tabWidget->setObjectName(QString::fromUtf8("tabWidget"));
        tabWidget->setGeometry(QRect(0, 0, 961, 501));
        Motorcontrol = new QWidget();
        Motorcontrol->setObjectName(QString::fromUtf8("Motorcontrol"));
        IntervallLabel = new QLabel(Motorcontrol);
        IntervallLabel->setObjectName(QString::fromUtf8("IntervallLabel"));
        IntervallLabel->setGeometry(QRect(340, 100, 201, 31));
        PossibleWavelenth = new QLabel(Motorcontrol);
        PossibleWavelenth->setObjectName(QString::fromUtf8("PossibleWavelenth"));
        PossibleWavelenth->setGeometry(QRect(20, 100, 261, 31));
        ReadingText = new QLabel(Motorcontrol);
        ReadingText->setObjectName(QString::fromUtf8("ReadingText"));
        ReadingText->setGeometry(QRect(90, 390, 471, 51));
        StepIntervallSelector = new QDoubleSpinBox(Motorcontrol);
        StepIntervallSelector->setObjectName(QString::fromUtf8("StepIntervallSelector"));
        StepIntervallSelector->setGeometry(QRect(440, 240, 81, 41));
        StepIntervallSelector->setMinimum(0.500000000000000);
        StepIntervallSelector->setSingleStep(0.500000000000000);
        StepIntervallSelector->setValue(1.000000000000000);
        UploadButton = new QPushButton(Motorcontrol);
        UploadButton->setObjectName(QString::fromUtf8("UploadButton"));
        UploadButton->setGeometry(QRect(610, 250, 91, 31));
        AddIntervallButton = new QPushButton(Motorcontrol);
        AddIntervallButton->setObjectName(QString::fromUtf8("AddIntervallButton"));
        AddIntervallButton->setGeometry(QRect(400, 290, 101, 41));
        lambdaAddLabel = new QLabel(Motorcontrol);
        lambdaAddLabel->setObjectName(QString::fromUtf8("lambdaAddLabel"));
        lambdaAddLabel->setGeometry(QRect(20, 131, 171, 31));
        StartIntervallSelector = new QDoubleSpinBox(Motorcontrol);
        StartIntervallSelector->setObjectName(QString::fromUtf8("StartIntervallSelector"));
        StartIntervallSelector->setGeometry(QRect(440, 135, 81, 41));
        StartIntervallSelector->setMinimum(120.000000000000000);
        StartIntervallSelector->setMaximum(300.000000000000000);
        StartIntervallSelector->setSingleStep(0.500000000000000);
        EndIntervallSelector = new QDoubleSpinBox(Motorcontrol);
        EndIntervallSelector->setObjectName(QString::fromUtf8("EndIntervallSelector"));
        EndIntervallSelector->setGeometry(QRect(440, 190, 81, 41));
        EndIntervallSelector->setMinimum(120.000000000000000);
        EndIntervallSelector->setMaximum(300.000000000000000);
        EndIntervallSelector->setSingleStep(0.500000000000000);
        ListWavelength = new QListWidget(Motorcontrol);
        ListWavelength->setObjectName(QString::fromUtf8("ListWavelength"));
        ListWavelength->setGeometry(QRect(610, 30, 261, 211));
        StartIntervallLabel = new QLabel(Motorcontrol);
        StartIntervallLabel->setObjectName(QString::fromUtf8("StartIntervallLabel"));
        StartIntervallLabel->setGeometry(QRect(350, 140, 71, 31));
        SerialPortBox = new QComboBox(Motorcontrol);
        SerialPortBox->setObjectName(QString::fromUtf8("SerialPortBox"));
        SerialPortBox->setGeometry(QRect(180, 30, 91, 31));
        EndIntervallLabel = new QLabel(Motorcontrol);
        EndIntervallLabel->setObjectName(QString::fromUtf8("EndIntervallLabel"));
        EndIntervallLabel->setGeometry(QRect(350, 190, 71, 41));
        ResetButton = new QPushButton(Motorcontrol);
        ResetButton->setObjectName(QString::fromUtf8("ResetButton"));
        ResetButton->setGeometry(QRect(770, 250, 91, 31));
        SerialPortLabel = new QLabel(Motorcontrol);
        SerialPortLabel->setObjectName(QString::fromUtf8("SerialPortLabel"));
        SerialPortLabel->setGeometry(QRect(20, 40, 141, 17));
        ReadingHead = new QLabel(Motorcontrol);
        ReadingHead->setObjectName(QString::fromUtf8("ReadingHead"));
        ReadingHead->setGeometry(QRect(10, 390, 67, 17));
        WavelengthSelector = new QDoubleSpinBox(Motorcontrol);
        WavelengthSelector->setObjectName(QString::fromUtf8("WavelengthSelector"));
        WavelengthSelector->setGeometry(QRect(40, 171, 81, 41));
        WavelengthSelector->setMinimum(120.000000000000000);
        WavelengthSelector->setMaximum(300.000000000000000);
        WavelengthSelector->setSingleStep(0.500000000000000);
        InfoList = new QLabel(Motorcontrol);
        InfoList->setObjectName(QString::fromUtf8("InfoList"));
        InfoList->setGeometry(QRect(610, 10, 111, 17));
        AddButton = new QPushButton(Motorcontrol);
        AddButton->setObjectName(QString::fromUtf8("AddButton"));
        AddButton->setGeometry(QRect(140, 171, 101, 41));
        StepIntervallLabel = new QLabel(Motorcontrol);
        StepIntervallLabel->setObjectName(QString::fromUtf8("StepIntervallLabel"));
        StepIntervallLabel->setGeometry(QRect(350, 246, 91, 31));
        StatusHead = new QLabel(Motorcontrol);
        StatusHead->setObjectName(QString::fromUtf8("StatusHead"));
        StatusHead->setGeometry(QRect(10, 360, 51, 17));
        SetButton = new QPushButton(Motorcontrol);
        SetButton->setObjectName(QString::fromUtf8("SetButton"));
        SetButton->setGeometry(QRect(180, 70, 91, 31));
        StatusText = new QLabel(Motorcontrol);
        StatusText->setObjectName(QString::fromUtf8("StatusText"));
        StatusText->setGeometry(QRect(70, 360, 481, 17));
        StartingPosition = new QPushButton(Motorcontrol);
        StartingPosition->setObjectName(QString::fromUtf8("StartingPosition"));
        StartingPosition->setGeometry(QRect(60, 290, 151, 31));
        StartingPositionLabel = new QLabel(Motorcontrol);
        StartingPositionLabel->setObjectName(QString::fromUtf8("StartingPositionLabel"));
        StartingPositionLabel->setGeometry(QRect(20, 260, 241, 21));
        StartButton = new QPushButton(Motorcontrol);
        StartButton->setObjectName(QString::fromUtf8("StartButton"));
        StartButton->setGeometry(QRect(690, 290, 91, 31));
        tabWidget->addTab(Motorcontrol, QString());
        Received_data = new QWidget();
        Received_data->setObjectName(QString::fromUtf8("Received_data"));
        ResetReceivedDataButton = new QPushButton(Received_data);
        ResetReceivedDataButton->setObjectName(QString::fromUtf8("ResetReceivedDataButton"));
        ResetReceivedDataButton->setGeometry(QRect(130, 390, 131, 31));
        ReceivedLabel = new QLabel(Received_data);
        ReceivedLabel->setObjectName(QString::fromUtf8("ReceivedLabel"));
        ReceivedLabel->setGeometry(QRect(60, 20, 111, 17));
        ListReceivedData = new QListWidget(Received_data);
        ListReceivedData->setObjectName(QString::fromUtf8("ListReceivedData"));
        ListReceivedData->setGeometry(QRect(60, 40, 281, 341));
        LivePlot = new QGraphicsView(Received_data);
        LivePlot->setObjectName(QString::fromUtf8("LivePlot"));
        LivePlot->setGeometry(QRect(510, 80, 361, 271));
        LivePlotlabel = new QLabel(Received_data);
        LivePlotlabel->setObjectName(QString::fromUtf8("LivePlotlabel"));
        LivePlotlabel->setGeometry(QRect(510, 50, 67, 17));
        LivePlot_ResetButton = new QPushButton(Received_data);
        LivePlot_ResetButton->setObjectName(QString::fromUtf8("LivePlot_ResetButton"));
        LivePlot_ResetButton->setGeometry(QRect(700, 380, 91, 31));
        ZoomLivePlot_Button = new QPushButton(Received_data);
        ZoomLivePlot_Button->setObjectName(QString::fromUtf8("ZoomLivePlot_Button"));
        ZoomLivePlot_Button->setGeometry(QRect(560, 380, 91, 31));
        tabWidget->addTab(Received_data, QString());
        Send_result = new QWidget();
        Send_result->setObjectName(QString::fromUtf8("Send_result"));
        EnterEmail_label = new QLabel(Send_result);
        EnterEmail_label->setObjectName(QString::fromUtf8("EnterEmail_label"));
        EnterEmail_label->setGeometry(QRect(30, 290, 111, 21));
        Email_Edit = new QLineEdit(Send_result);
        Email_Edit->setObjectName(QString::fromUtf8("Email_Edit"));
        Email_Edit->setGeometry(QRect(120, 290, 311, 25));
        SendResult_Button = new QPushButton(Send_result);
        SendResult_Button->setObjectName(QString::fromUtf8("SendResult_Button"));
        SendResult_Button->setGeometry(QRect(190, 340, 131, 51));
        Preview = new QGraphicsView(Send_result);
        Preview->setObjectName(QString::fromUtf8("Preview"));
        Preview->setGeometry(QRect(530, 80, 361, 321));
        Preview_label = new QLabel(Send_result);
        Preview_label->setObjectName(QString::fromUtf8("Preview_label"));
        Preview_label->setGeometry(QRect(530, 50, 67, 17));
        DataType_label = new QLabel(Send_result);
        DataType_label->setObjectName(QString::fromUtf8("DataType_label"));
        DataType_label->setGeometry(QRect(30, 30, 141, 31));
        DataType1 = new QRadioButton(Send_result);
        DataType1->setObjectName(QString::fromUtf8("DataType1"));
        DataType1->setGeometry(QRect(30, 70, 112, 23));
        DataType1->setAutoRepeat(false);
        DataType2 = new QRadioButton(Send_result);
        DataType2->setObjectName(QString::fromUtf8("DataType2"));
        DataType2->setGeometry(QRect(160, 70, 112, 23));
        DataType3 = new QRadioButton(Send_result);
        DataType3->setObjectName(QString::fromUtf8("DataType3"));
        DataType3->setGeometry(QRect(290, 70, 112, 23));
        label = new QLabel(Send_result);
        label->setObjectName(QString::fromUtf8("label"));
        label->setGeometry(QRect(30, 160, 151, 17));
        OptionData = new QRadioButton(Send_result);
        OptionData->setObjectName(QString::fromUtf8("OptionData"));
        OptionData->setGeometry(QRect(60, 200, 112, 23));
        OptionPlot = new QRadioButton(Send_result);
        OptionPlot->setObjectName(QString::fromUtf8("OptionPlot"));
        OptionPlot->setGeometry(QRect(240, 200, 112, 23));
        tabWidget->addTab(Send_result, QString());
        steppermotor->setCentralWidget(centralWidget);

        retranslateUi(steppermotor);

        tabWidget->setCurrentIndex(0);


        QMetaObject::connectSlotsByName(steppermotor);
    } // setupUi

    void retranslateUi(QMainWindow *steppermotor)
    {
        steppermotor->setWindowTitle(QApplication::translate("steppermotor", "StepperMotor control", nullptr));
        IntervallLabel->setText(QApplication::translate("steppermotor", "Add measurement interval:", nullptr));
        PossibleWavelenth->setText(QApplication::translate("steppermotor", "Possible wavelenth: 120 nm to 300 nm", nullptr));
        ReadingText->setText(QString());
        UploadButton->setText(QApplication::translate("steppermotor", "Upload", nullptr));
        AddIntervallButton->setText(QApplication::translate("steppermotor", "Add", nullptr));
        lambdaAddLabel->setText(QApplication::translate("steppermotor", "Add single position [nm]:", nullptr));
        StartIntervallLabel->setText(QApplication::translate("steppermotor", "Start [nm]:", nullptr));
        EndIntervallLabel->setText(QApplication::translate("steppermotor", "End [nm]:", nullptr));
        ResetButton->setText(QApplication::translate("steppermotor", "Reset", nullptr));
        SerialPortLabel->setText(QApplication::translate("steppermotor", "Selected Serial Port:", nullptr));
        ReadingHead->setText(QApplication::translate("steppermotor", "Reading:", nullptr));
        InfoList->setText(QApplication::translate("steppermotor", "Saved positions:", nullptr));
        AddButton->setText(QApplication::translate("steppermotor", "Add", nullptr));
        StepIntervallLabel->setText(QApplication::translate("steppermotor", "Step [nm]:", nullptr));
        StatusHead->setText(QApplication::translate("steppermotor", "Status:", nullptr));
        SetButton->setText(QApplication::translate("steppermotor", "Set", nullptr));
        StatusText->setText(QString());
        StartingPosition->setText(QApplication::translate("steppermotor", "Starting Position", nullptr));
        StartingPositionLabel->setText(QApplication::translate("steppermotor", "Go to Starting Position (120 nm):", nullptr));
        StartButton->setText(QApplication::translate("steppermotor", "Start", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(Motorcontrol), QApplication::translate("steppermotor", "Motor control", nullptr));
        ResetReceivedDataButton->setText(QApplication::translate("steppermotor", "Reset", nullptr));
        ReceivedLabel->setText(QApplication::translate("steppermotor", "Received data:", nullptr));
        LivePlotlabel->setText(QApplication::translate("steppermotor", "Live Plot:", nullptr));
        LivePlot_ResetButton->setText(QApplication::translate("steppermotor", "Reset", nullptr));
        ZoomLivePlot_Button->setText(QApplication::translate("steppermotor", "Zoom", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(Received_data), QApplication::translate("steppermotor", "Received data", nullptr));
        EnterEmail_label->setText(QApplication::translate("steppermotor", "Enter Email:", nullptr));
        SendResult_Button->setText(QApplication::translate("steppermotor", "Send result ", nullptr));
        Preview_label->setText(QApplication::translate("steppermotor", "Preview:", nullptr));
        DataType_label->setText(QApplication::translate("steppermotor", "Select data type:", nullptr));
        DataType1->setText(QApplication::translate("steppermotor", "Type 1", nullptr));
        DataType2->setText(QApplication::translate("steppermotor", "Type 2", nullptr));
        DataType3->setText(QApplication::translate("steppermotor", "Type 3", nullptr));
        label->setText(QApplication::translate("steppermotor", "What should be sent?", nullptr));
        OptionData->setText(QApplication::translate("steppermotor", "Data", nullptr));
        OptionPlot->setText(QApplication::translate("steppermotor", "Plots", nullptr));
        tabWidget->setTabText(tabWidget->indexOf(Send_result), QApplication::translate("steppermotor", "Send result", nullptr));
    } // retranslateUi

};

namespace Ui {
    class steppermotor: public Ui_steppermotor {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_STEPPERMOTOR_H
