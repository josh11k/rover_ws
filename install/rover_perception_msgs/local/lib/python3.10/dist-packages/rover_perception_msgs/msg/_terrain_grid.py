# generated from rosidl_generator_py/resource/_idl.py.em
# with input from rover_perception_msgs:msg/TerrainGrid.idl
# generated code does not contain a copyright notice


# Import statements for member types

# Member 'traversability'
# Member 'min_z'
# Member 'max_z'
# Member 'mean_z'
# Member 'roughness'
# Member 'plane_slope_deg'
# Member 'point_count'
# Member 'total_weight'
import array  # noqa: E402, I100

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_TerrainGrid(type):
    """Metaclass of message 'TerrainGrid'."""

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
                'rover_perception_msgs.msg.TerrainGrid')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__terrain_grid
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__terrain_grid
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__terrain_grid
            cls._TYPE_SUPPORT = module.type_support_msg__msg__terrain_grid
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__terrain_grid

            from nav_msgs.msg import MapMetaData
            if MapMetaData.__class__._TYPE_SUPPORT is None:
                MapMetaData.__class__.__import_type_support__()

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class TerrainGrid(metaclass=Metaclass_TerrainGrid):
    """Message class 'TerrainGrid'."""

    __slots__ = [
        '_header',
        '_info',
        '_traversability',
        '_min_z',
        '_max_z',
        '_mean_z',
        '_roughness',
        '_plane_slope_deg',
        '_point_count',
        '_total_weight',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'info': 'nav_msgs/MapMetaData',
        'traversability': 'sequence<int8>',
        'min_z': 'sequence<float>',
        'max_z': 'sequence<float>',
        'mean_z': 'sequence<float>',
        'roughness': 'sequence<float>',
        'plane_slope_deg': 'sequence<float>',
        'point_count': 'sequence<int32>',
        'total_weight': 'sequence<float>',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['nav_msgs', 'msg'], 'MapMetaData'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('int8')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('float')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('float')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('float')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('float')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('float')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('int32')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('float')),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        from nav_msgs.msg import MapMetaData
        self.info = kwargs.get('info', MapMetaData())
        self.traversability = array.array('b', kwargs.get('traversability', []))
        self.min_z = array.array('f', kwargs.get('min_z', []))
        self.max_z = array.array('f', kwargs.get('max_z', []))
        self.mean_z = array.array('f', kwargs.get('mean_z', []))
        self.roughness = array.array('f', kwargs.get('roughness', []))
        self.plane_slope_deg = array.array('f', kwargs.get('plane_slope_deg', []))
        self.point_count = array.array('i', kwargs.get('point_count', []))
        self.total_weight = array.array('f', kwargs.get('total_weight', []))

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
        if self.header != other.header:
            return False
        if self.info != other.info:
            return False
        if self.traversability != other.traversability:
            return False
        if self.min_z != other.min_z:
            return False
        if self.max_z != other.max_z:
            return False
        if self.mean_z != other.mean_z:
            return False
        if self.roughness != other.roughness:
            return False
        if self.plane_slope_deg != other.plane_slope_deg:
            return False
        if self.point_count != other.point_count:
            return False
        if self.total_weight != other.total_weight:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if __debug__:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property
    def info(self):
        """Message field 'info'."""
        return self._info

    @info.setter
    def info(self, value):
        if __debug__:
            from nav_msgs.msg import MapMetaData
            assert \
                isinstance(value, MapMetaData), \
                "The 'info' field must be a sub message of type 'MapMetaData'"
        self._info = value

    @builtins.property
    def traversability(self):
        """Message field 'traversability'."""
        return self._traversability

    @traversability.setter
    def traversability(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'b', \
                "The 'traversability' array.array() must have the type code of 'b'"
            self._traversability = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, int) for v in value) and
                 all(val >= -128 and val < 128 for val in value)), \
                "The 'traversability' field must be a set or sequence and each value of type 'int' and each integer in [-128, 127]"
        self._traversability = array.array('b', value)

    @builtins.property
    def min_z(self):
        """Message field 'min_z'."""
        return self._min_z

    @min_z.setter
    def min_z(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'f', \
                "The 'min_z' array.array() must have the type code of 'f'"
            self._min_z = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'min_z' field must be a set or sequence and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._min_z = array.array('f', value)

    @builtins.property
    def max_z(self):
        """Message field 'max_z'."""
        return self._max_z

    @max_z.setter
    def max_z(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'f', \
                "The 'max_z' array.array() must have the type code of 'f'"
            self._max_z = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'max_z' field must be a set or sequence and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._max_z = array.array('f', value)

    @builtins.property
    def mean_z(self):
        """Message field 'mean_z'."""
        return self._mean_z

    @mean_z.setter
    def mean_z(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'f', \
                "The 'mean_z' array.array() must have the type code of 'f'"
            self._mean_z = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'mean_z' field must be a set or sequence and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._mean_z = array.array('f', value)

    @builtins.property
    def roughness(self):
        """Message field 'roughness'."""
        return self._roughness

    @roughness.setter
    def roughness(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'f', \
                "The 'roughness' array.array() must have the type code of 'f'"
            self._roughness = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'roughness' field must be a set or sequence and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._roughness = array.array('f', value)

    @builtins.property
    def plane_slope_deg(self):
        """Message field 'plane_slope_deg'."""
        return self._plane_slope_deg

    @plane_slope_deg.setter
    def plane_slope_deg(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'f', \
                "The 'plane_slope_deg' array.array() must have the type code of 'f'"
            self._plane_slope_deg = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'plane_slope_deg' field must be a set or sequence and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._plane_slope_deg = array.array('f', value)

    @builtins.property
    def point_count(self):
        """Message field 'point_count'."""
        return self._point_count

    @point_count.setter
    def point_count(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'i', \
                "The 'point_count' array.array() must have the type code of 'i'"
            self._point_count = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, int) for v in value) and
                 all(val >= -2147483648 and val < 2147483648 for val in value)), \
                "The 'point_count' field must be a set or sequence and each value of type 'int' and each integer in [-2147483648, 2147483647]"
        self._point_count = array.array('i', value)

    @builtins.property
    def total_weight(self):
        """Message field 'total_weight'."""
        return self._total_weight

    @total_weight.setter
    def total_weight(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'f', \
                "The 'total_weight' array.array() must have the type code of 'f'"
            self._total_weight = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'total_weight' field must be a set or sequence and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._total_weight = array.array('f', value)
