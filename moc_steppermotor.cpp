/****************************************************************************
** Meta object code from reading C++ file 'steppermotor.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.12.1)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "steppermotor.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'steppermotor.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.12.1. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_steppermotor_t {
    QByteArrayData data[10];
    char stringdata0[219];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_steppermotor_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_steppermotor_t qt_meta_stringdata_steppermotor = {
    {
QT_MOC_LITERAL(0, 0, 12), // "steppermotor"
QT_MOC_LITERAL(1, 13, 20), // "on_SetButton_clicked"
QT_MOC_LITERAL(2, 34, 0), // ""
QT_MOC_LITERAL(3, 35, 20), // "on_AddButton_clicked"
QT_MOC_LITERAL(4, 56, 29), // "on_AddIntervallButton_clicked"
QT_MOC_LITERAL(5, 86, 23), // "on_UploadButton_clicked"
QT_MOC_LITERAL(6, 110, 22), // "on_ResetButton_clicked"
QT_MOC_LITERAL(7, 133, 27), // "on_StartingPosition_clicked"
QT_MOC_LITERAL(8, 161, 22), // "on_StartButton_clicked"
QT_MOC_LITERAL(9, 184, 34) // "on_ResetReceivedDataButton_cl..."

    },
    "steppermotor\0on_SetButton_clicked\0\0"
    "on_AddButton_clicked\0on_AddIntervallButton_clicked\0"
    "on_UploadButton_clicked\0on_ResetButton_clicked\0"
    "on_StartingPosition_clicked\0"
    "on_StartButton_clicked\0"
    "on_ResetReceivedDataButton_clicked"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_steppermotor[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       8,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags
       1,    0,   54,    2, 0x0a /* Public */,
       3,    0,   55,    2, 0x0a /* Public */,
       4,    0,   56,    2, 0x0a /* Public */,
       5,    0,   57,    2, 0x0a /* Public */,
       6,    0,   58,    2, 0x0a /* Public */,
       7,    0,   59,    2, 0x0a /* Public */,
       8,    0,   60,    2, 0x0a /* Public */,
       9,    0,   61,    2, 0x0a /* Public */,

 // slots: parameters
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,

       0        // eod
};

void steppermotor::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<steppermotor *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
        case 0: _t->on_SetButton_clicked(); break;
        case 1: _t->on_AddButton_clicked(); break;
        case 2: _t->on_AddIntervallButton_clicked(); break;
        case 3: _t->on_UploadButton_clicked(); break;
        case 4: _t->on_ResetButton_clicked(); break;
        case 5: _t->on_StartingPosition_clicked(); break;
        case 6: _t->on_StartButton_clicked(); break;
        case 7: _t->on_ResetReceivedDataButton_clicked(); break;
        default: ;
        }
    }
    Q_UNUSED(_a);
}

QT_INIT_METAOBJECT const QMetaObject steppermotor::staticMetaObject = { {
    &QMainWindow::staticMetaObject,
    qt_meta_stringdata_steppermotor.data,
    qt_meta_data_steppermotor,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *steppermotor::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *steppermotor::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_steppermotor.stringdata0))
        return static_cast<void*>(this);
    return QMainWindow::qt_metacast(_clname);
}

int steppermotor::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QMainWindow::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 8)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 8;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 8)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 8;
    }
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
