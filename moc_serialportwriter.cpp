/****************************************************************************
** Meta object code from reading C++ file 'serialportwriter.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.12.1)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "serialportwriter.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'serialportwriter.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.12.1. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_SerialPortWriter_t {
    QByteArrayData data[8];
    char stringdata0[104];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_SerialPortWriter_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_SerialPortWriter_t qt_meta_stringdata_SerialPortWriter = {
    {
QT_MOC_LITERAL(0, 0, 16), // "SerialPortWriter"
QT_MOC_LITERAL(1, 17, 18), // "handleBytesWritten"
QT_MOC_LITERAL(2, 36, 0), // ""
QT_MOC_LITERAL(3, 37, 5), // "bytes"
QT_MOC_LITERAL(4, 43, 13), // "handleTimeout"
QT_MOC_LITERAL(5, 57, 11), // "handleError"
QT_MOC_LITERAL(6, 69, 28), // "QSerialPort::SerialPortError"
QT_MOC_LITERAL(7, 98, 5) // "error"

    },
    "SerialPortWriter\0handleBytesWritten\0"
    "\0bytes\0handleTimeout\0handleError\0"
    "QSerialPort::SerialPortError\0error"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_SerialPortWriter[] = {

 // content:
       8,       // revision
       0,       // classname
       0,    0, // classinfo
       3,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       0,       // signalCount

 // slots: name, argc, parameters, tag, flags
       1,    1,   29,    2, 0x08 /* Private */,
       4,    0,   32,    2, 0x08 /* Private */,
       5,    1,   33,    2, 0x08 /* Private */,

 // slots: parameters
    QMetaType::Void, QMetaType::LongLong,    3,
    QMetaType::Void,
    QMetaType::Void, 0x80000000 | 6,    7,

       0        // eod
};

void SerialPortWriter::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        auto *_t = static_cast<SerialPortWriter *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
/*        case 0: _t->handleBytesWritten((*reinterpret_cast< qint64(*)>(_a[1]))); break;
        case 1: _t->handleTimeout(); break;
        case 2: _t->handleError((*reinterpret_cast< QSerialPort::SerialPortError(*)>(_a[1]))); break;    */
        default: ;
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject SerialPortWriter::staticMetaObject = { {
    &QObject::staticMetaObject,
    qt_meta_stringdata_SerialPortWriter.data,
    qt_meta_data_SerialPortWriter,
    qt_static_metacall,
    nullptr,
    nullptr
} };


const QMetaObject *SerialPortWriter::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *SerialPortWriter::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_SerialPortWriter.stringdata0))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int SerialPortWriter::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 3)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 3;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 3)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 3;
    }
    return _id;
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
