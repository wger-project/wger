# This file is part of wger Workout Manager.
#
# wger is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import os
import time
import uuid as py_uuid


def uuid7() -> py_uuid.UUID:
    """
    NOTE: this is only needed because currently there isn't a UUIDv7 implementation
    in the python standard library. Once that becomes available, this function can
    be deleted and its uses replaced.

    Generate a UUIDv7.

    Layout:
    - 48 bits: Unix timestamp in milliseconds
    - 12 bits: Random data (or sequence counter if strict monotonicity is needed)
    - 2 bits: Variant (set to 0b10)
    - 4 bits: Version (set to 0b0111)
    - 62 bits: Random data
    """

    # Get current time in milliseconds
    timestamp_ms = int(time.time() * 1000)
    b = list(os.urandom(16))

    # Fill timestamp (big-endian)
    b[0] = (timestamp_ms >> 40) & 0xFF
    b[1] = (timestamp_ms >> 32) & 0xFF
    b[2] = (timestamp_ms >> 24) & 0xFF
    b[3] = (timestamp_ms >> 16) & 0xFF
    b[4] = (timestamp_ms >> 8) & 0xFF
    b[5] = timestamp_ms & 0xFF

    # Set version (nibble 12, index 6)
    # version 7 => 0111
    # current byte value: vvvvrrrr
    # destination: 0111rrrr
    b[6] = (b[6] & 0x0F) | 0x70

    # Set variant (nibble 16, index 8)
    # variant 10 => 10
    # current byte value: vvvrrrrr
    # destination: 10xr rrrr
    b[8] = (b[8] & 0x3F) | 0x80

    return py_uuid.UUID(bytes=bytes(b))
