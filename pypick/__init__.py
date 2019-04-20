# Copyright (C) 2019 by Huan Xiong. All Rights Reserved.
# Licensed under GPLv3 or later. See LICENSE file under top level directory.

"""
Selecting an item from a list of multi-field data in terminal

The module defines the following public interfaces:

    Classes:
        Pick: The main API of this module. A Pick instance takes a
            list of multi-field data entries, and optional meta data
            on each field's appearance and behavior. It displays data
            entries in text based UI, one row for each data entry and
            one column for each field. It returns an entry's data when
            user selects it.
        Group: Data entries can be added to list directly, or be organized
            into groups. A group contains a list of entries and can
            define its own rules on which fields to show and how to show
            them.

    Exceptions:
        NoSpace: Raised if there isn't enough space to display a column

    Functions:
        set_theme(): Customize the theme of the UI.

1. Data Entries
---------------

A data entry has mutliple fields and is represented by a dictionary.
For example, a data entry for SSH login may be like the follwoing:

    {'name': 'server-5',
     'host': '10.64.4.5',
     'user': ['root', 'rayx'],
     'project': 'project X',
     'description': 'ubuntu 16.04'}

From Pick's perspective, a data entry's fields fall into these categories:

    - Fields that are shown in UI.
    - Fields that aren't shown in UI, but will be returned when the
      entry is selected.
    - Other Fields. These fields are ignored by Pick.

For fields shown in UI, pick allows user to define their UI appearance
and behavior. See field attributes in next section.

A data entry may also have some special fields, which don't contain
data but entry attributes, like if this is high priorty data entry, or
if this is a child entry of the one prior to it. Entry attributes apply
to all fields of this entry and affect their UI. See entry attributes
in next section.

Data entries can be organized into groups. A group can override global
fields attributes and define its own rules on which fields to show and
how to show them.

2. Field Attributes and Entry Attirbutes
----------------------------------------

Meta data include field attributes and entry attributes (attributes
that apply to a data entry and hence all its fields).

Field attributes describes UI attributes of a field. They are
specified when creating a Pick instance. The following field
attributes are supported:

  - width (type: int, default: None):
        Width of the column to show the field. If not specified, the
        column width is calculated automatically.
  - style (type: str, default: 'normal'):
        Style of the column. See more on this below.
  - shortcut (type: str representing key press, default: see below):
        This is only useful if the field data is a list, in which
        case the first value in the list is showed by default.
        Shortcut is a key press that allows user to iterate over
        available values in the list. If field value is a list
        containing more than one items and user doesn't specify a
        shortcut, Pick will generate one automatically by using the
        first character of the field's name.

        The following are examples of valid shortcut value: 'u', 'U',
        ' ' (space), 'ctrl u', 'f1', 'right', etc.

  - return (type: boolean, default: True):
        Whether to return the field's data when the entry is selected.

Entry attributes describes entry wide attributes that may afffect
its UI. The following entry attributes are supported:

  - _level (type: int, default: 0):
        This is used to define the parent/child relationship between
        a data entry and the one prior to it.
  - _critical (type: boolean, default: False):
        A critical data entry is highlighted in UI.

3. Theme
--------

Depending on their attributes and states, fields may be displayed in
different foreground and background color combinations. The
foreground/background color combination is called text style in Pick.
A text style has a name so it can be referenced.

Pick defines five text styles:

  - 'focused': Text style to display item being focused
  - 'cirtical': Text style to display items which have '_critical' set
  - 'normal': Default text style to display fields
  - 'trivial': Text style to display unimportant ('trivial') fields
  - 'default': Text style to display title (e.g., group name, etc.)

User can reference these text style names in fields attributes.

User can customize these text style values (that is, their foreground
and background colors) by calling set_theme(). Text style value is
a tuple of this format:

  (fg_color, bg_color)

Please refer to urwid document at the following link for valid fg/bg
color values:

http://urwid.org/manual/displayattributes.html#standard-foreground-colors

4. Usage Example
----------------

The following is a simple example. It shows two entries. For each
entry, its 'name', 'host', 'user', 'description' fields are shown.
When user selects an entry, its 'name', 'host', 'user', and 'project'
fields are returned.

    $ cat test_pick.py
    from pypick import Pick

    data_list = [{'name': 'server-5',
                  'host': '10.64.4.5',
                  'user': ['root', 'rayx'],
                  'project': 'project X',
                  'description': 'ubuntu 16.04'},
                 {'name': 'server-66',
                  'host': '10.64.4.66',
                  'user': ['root'],
                  'project': 'project Y',
                  'description': 'centos 7.4'}]

    fields = ['name', 'host', 'user', 'description']
    extra_fields = ['project']
    field_attrs = {'description': {'return': False}}

    p = Pick(fields, extra_fields, field_attrs)
    g1 = p.create_group('group1')
    g1.add_entries(data_list)
    result = p.run()
    print(result)

    $ python3 test_pick.py
    {'user': 'rayx', 'project': 'project X', 'name': 'server-5',
     'host': '10.64.4.5'}
"""

from .pick import Pick, Group
from .ui import set_theme, NoSpace

__all__ = ['Pick', 'Group', 'NoSpace', 'set_theme']
__version__ = '0.2.0'
__license__ = 'GPLv3+'
__author__ = 'Huan Xiong <huan.xiong@outlook.com>'
