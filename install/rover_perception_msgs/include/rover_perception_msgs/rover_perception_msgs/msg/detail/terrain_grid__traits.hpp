// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rover_perception_msgs:msg/TerrainGrid.idl
// generated code does not contain a copyright notice

#ifndef ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__TRAITS_HPP_
#define ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "rover_perception_msgs/msg/detail/terrain_grid__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'info'
#include "nav_msgs/msg/detail/map_meta_data__traits.hpp"

namespace rover_perception_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const TerrainGrid & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: info
  {
    out << "info: ";
    to_flow_style_yaml(msg.info, out);
    out << ", ";
  }

  // member: traversability
  {
    if (msg.traversability.size() == 0) {
      out << "traversability: []";
    } else {
      out << "traversability: [";
      size_t pending_items = msg.traversability.size();
      for (auto item : msg.traversability) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: min_z
  {
    if (msg.min_z.size() == 0) {
      out << "min_z: []";
    } else {
      out << "min_z: [";
      size_t pending_items = msg.min_z.size();
      for (auto item : msg.min_z) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: max_z
  {
    if (msg.max_z.size() == 0) {
      out << "max_z: []";
    } else {
      out << "max_z: [";
      size_t pending_items = msg.max_z.size();
      for (auto item : msg.max_z) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: mean_z
  {
    if (msg.mean_z.size() == 0) {
      out << "mean_z: []";
    } else {
      out << "mean_z: [";
      size_t pending_items = msg.mean_z.size();
      for (auto item : msg.mean_z) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: roughness
  {
    if (msg.roughness.size() == 0) {
      out << "roughness: []";
    } else {
      out << "roughness: [";
      size_t pending_items = msg.roughness.size();
      for (auto item : msg.roughness) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: plane_slope_deg
  {
    if (msg.plane_slope_deg.size() == 0) {
      out << "plane_slope_deg: []";
    } else {
      out << "plane_slope_deg: [";
      size_t pending_items = msg.plane_slope_deg.size();
      for (auto item : msg.plane_slope_deg) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: point_count
  {
    if (msg.point_count.size() == 0) {
      out << "point_count: []";
    } else {
      out << "point_count: [";
      size_t pending_items = msg.point_count.size();
      for (auto item : msg.point_count) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: total_weight
  {
    if (msg.total_weight.size() == 0) {
      out << "total_weight: []";
    } else {
      out << "total_weight: [";
      size_t pending_items = msg.total_weight.size();
      for (auto item : msg.total_weight) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TerrainGrid & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: info
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "info:\n";
    to_block_style_yaml(msg.info, out, indentation + 2);
  }

  // member: traversability
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.traversability.size() == 0) {
      out << "traversability: []\n";
    } else {
      out << "traversability:\n";
      for (auto item : msg.traversability) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: min_z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.min_z.size() == 0) {
      out << "min_z: []\n";
    } else {
      out << "min_z:\n";
      for (auto item : msg.min_z) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: max_z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.max_z.size() == 0) {
      out << "max_z: []\n";
    } else {
      out << "max_z:\n";
      for (auto item : msg.max_z) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: mean_z
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.mean_z.size() == 0) {
      out << "mean_z: []\n";
    } else {
      out << "mean_z:\n";
      for (auto item : msg.mean_z) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: roughness
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.roughness.size() == 0) {
      out << "roughness: []\n";
    } else {
      out << "roughness:\n";
      for (auto item : msg.roughness) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: plane_slope_deg
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.plane_slope_deg.size() == 0) {
      out << "plane_slope_deg: []\n";
    } else {
      out << "plane_slope_deg:\n";
      for (auto item : msg.plane_slope_deg) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: point_count
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.point_count.size() == 0) {
      out << "point_count: []\n";
    } else {
      out << "point_count:\n";
      for (auto item : msg.point_count) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: total_weight
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.total_weight.size() == 0) {
      out << "total_weight: []\n";
    } else {
      out << "total_weight:\n";
      for (auto item : msg.total_weight) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TerrainGrid & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace rover_perception_msgs

namespace rosidl_generator_traits
{

[[deprecated("use rover_perception_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const rover_perception_msgs::msg::TerrainGrid & msg,
  std::ostream & out, size_t indentation = 0)
{
  rover_perception_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rover_perception_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const rover_perception_msgs::msg::TerrainGrid & msg)
{
  return rover_perception_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<rover_perception_msgs::msg::TerrainGrid>()
{
  return "rover_perception_msgs::msg::TerrainGrid";
}

template<>
inline const char * name<rover_perception_msgs::msg::TerrainGrid>()
{
  return "rover_perception_msgs/msg/TerrainGrid";
}

template<>
struct has_fixed_size<rover_perception_msgs::msg::TerrainGrid>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rover_perception_msgs::msg::TerrainGrid>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rover_perception_msgs::msg::TerrainGrid>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__TRAITS_HPP_
