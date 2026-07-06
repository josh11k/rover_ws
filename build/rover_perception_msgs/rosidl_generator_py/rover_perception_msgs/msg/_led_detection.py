# generated from rosidl_generator_py/resource/_idl.py.em
# with input from rover_perception_msgs:msg/LedDetection.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_LedDetection(type):
    """Metaclass of message 'LedDetection'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('rover_perception_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'rover_perception_msgs.msg.LedDetection')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__led_detection
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__led_detection
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__led_detection
            cls._TYPE_SUPPORT = module.type_support_msg__msg__led_detection
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__led_detection

            from geometry_msgs.msg import Vector3
            if Vector3.__class__._TYPE_SUPPORT is None:
                Vector3.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class LedDetection(metaclass=Metaclass_LedDetection):
    """Message class 'LedDetection'."""

    __slots__ = [
        '_pixel_u',
        '_pixel_v',
        '_area_px',
        '_color_r',
        '_color_g',
        '_color_b',
        '_bearing',
    ]

    _fields_and_field_types = {
        'pixel_u': 'float',
        'pixel_v': 'float',
        'area_px': 'uint32',
        'color_r': 'uint8',
        'color_g': 'uint8',
        'color_b': 'uint8',
        'bearing': 'geometry_msgs/Vector3',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Vector3'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.pixel_u = kwargs.get('pixel_u', float())
        self.pixel_v = kwargs.get('pixel_v', float())
        self.area_px = kwargs.get('area_px', int())
        self.color_r = kwargs.get('color_r', int())
        self.color_g = kwargs.get('color_g', int())
        self.color_b = kwargs.get('color_b', int())
        from geometry_msgs.msg import Vector3
        self.bearing = kwargs.get('bearing', Vector3())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.pixel_u != other.pixel_u:
            return False
        if self.pixel_v != other.pixel_v:
            return False
        if self.area_px != other.area_px:
            return False
        if self.color_r != other.color_r:
            return False
        if self.color_g != other.color_g:
            return False
        if self.color_b != other.color_b:
            return False
        if self.bearing != other.bearing:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def pixel_u(self):
        """Message field 'pixel_u'."""
        return self._pixel_u

    @pixel_u.setter
    def pixel_u(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'pixel_u' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'pixel_u' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._pixel_u = value

    @builtins.property
    def pixel_v(self):
        """Message field 'pixel_v'."""
        return self._pixel_v

    @pixel_v.setter
    def pixel_v(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'pixel_v' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'pixel_v' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._pixel_v = value

    @builtins.property
    def area_px(self):
        """Message field 'area_px'."""
        return self._area_px

    @area_px.setter
    def area_px(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'area_px' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'area_px' field must be an unsigned integer in [0, 4294967295]"
        self._area_px = value

    @builtins.property
    def color_r(self):
        """Message field 'color_r'."""
        return self._color_r

    @color_r.setter
    def color_r(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'color_r' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'color_r' field must be an unsigned integer in [0, 255]"
        self._color_r = value

    @builtins.property
    def color_g(self):
        """Message field 'color_g'."""
        return self._color_g

    @color_g.setter
    def color_g(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'color_g' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'color_g' field must be an unsigned integer in [0, 255]"
        self._color_g = value

    @builtins.property
    def color_b(self):
        """Message field 'color_b'."""
        return self._color_b

    @color_b.setter
    def color_b(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'color_b' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'color_b' field must be an unsigned integer in [0, 255]"
        self._color_b = value

    @builtins.property
    def bearing(self):
        """Message field 'bearing'."""
        return self._bearing

    @bearing.setter
    def bearing(self, value):
        if __debug__:
            from geometry_msgs.msg import Vector3
            assert \
                isinstance(value, Vector3), \
                "The 'bearing' field must be a sub message of type 'Vector3'"
        self._bearing = value
