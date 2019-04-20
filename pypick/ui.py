# Copyright (C) 2019 by Huan Xiong. All Rights Reserved.
# Licensed under GPLv3 or later. See LICENSE file under top level directory.

import signal
import sys
import urwid
from wcwidth import wcswidth


class NoSpace(Exception):
    """Raised if there isn't enough space to display a column"""
    pass


class Theme:
    DEFAULT = {'focused': ('white', 'dark blue'),
               'critical': ('dark red', ''),
               'normal': ('dark blue', ''),
               'trivial': ('', ''),
               'misc': ('', '')}
    COMPANION_SUFFIX = '_non_text'

    def __init__(self, theme={}):
        self.theme = sanitize_input(theme, self.DEFAULT)
        self.create_companions()

    def create_companions(self):
        # A style applies to all characters in a column, including the
        # 'blank space' (they are not blank, but padded with blank space
        # characters). So, if a style contains 'underline' attribute,
        # spaces in the column are also underlined. That causes the UI
        # ugly. To address this issue, for each style containing
        # 'underline' attribute, a companion style is created for it,
        # which has 'underline' removed. These companion styles are used
        # for displaying non-text characters (e.g., space, indicator,
        # etc.) in the column.
        for k, v in self.theme.copy().items():
            fg, bg = v
            if 'underline' in fg:
                new_fg = ','.join([i for i in fg.split(',')
                                   if i.strip() != 'underline'])
                # Add a companion for this style
                self.theme[k + self.COMPANION_SUFFIX] = (new_fg, bg)

    def get_companion(self, style):
        companion = style + self.COMPANION_SUFFIX
        if companion in self.theme:
            return companion
        return style

    def get_palette(self):
        palette = []
        for name, value in self.theme.items():
            fg, bg = value
            palette.append((name, fg, bg))
        return palette


class Column:
    """
    A Column instance is reponsible for showing, updating, and
    returning value of an entry's field.

    Args:
         item (object): Item widget instance to which this column belongs.
         index (int): 0-based index of the column, increasing from left
             to right.
         name (str): field name
         value_candicates (str or list): field value. Note user
             may pass a list of values.
         column_attrs (dict): a dict containing this field's attributes.
    """
    ATTRS = {'width': None,
             'style': 'normal',
             'shortcut': None,
             'return': True}
    SPACE = ' '
    LIST_INDICATOR = '▾'
    LEVEL_INDICATOR = '⤷'

    def __init__(self, item, index, name, value_candidates, column_attrs):
        self.item = item
        self.index = index
        self.name = name
        self.value_candidates = value_candidates
        self.value_index = 0

        column_attrs = sanitize_input(column_attrs, self.ATTRS)
        self.width = column_attrs['width']
        self.style = column_attrs['style']
        self.shortcut = column_attrs['shortcut']
        self.will_return = column_attrs['return']

        # Calculate value and shortcut. Shortcut is set only when
        # 1) user sets it, _and_ 2) the field value is a list containing
        # more than one items.
        shortcut = self.shortcut
        self.shortcut = None
        if isinstance(self.value_candidates, list):
            if value_candidates:
                self.value = str(value_candidates[0])
                if len(value_candidates) > 1:
                    self.shortcut = shortcut
                    # Assign a default shortcut based on column name
                    # if user doesn't specify one.
                    if not self.shortcut:
                        self.shortcut = self.name[0]
            else:
                self.value = ''
        else:
            self.value = str(value_candidates)

    def chop_text(self, u, width):
        """
        Remove characters from the end of a unicode string until its
        display width is equal or less than the given width. It works
        with wide characters which has variable  display width.

        Args:
            u (str): a unicode string
            width (int): a width limit

        Returns:
            str: A substr that meets with the width limit.
        """
        while len(u) > 0 and wcswidth(u) > width:
            u = u[0:-1]
        return u

    def get_text_and_attrs(self, focus=False, width=0):
        """Return text to be displayed in this column.

        Args:
            focus (boolen): If the item to which the column belongs is
                being focused or not.
            width (int): The maximum width that is allowd.

        Returns:
            bytes: UTF-8 encoding of the unicode string to be displayed.
            list: A list of display attributes in run-length encoding.
        """
        text = []
        attrs = []

        def _create_text_and_attrs(snippet, style):
            text_width = sum([wcswidth(t) for t in text])
            if text_width + wcswidth(snippet) >= width:
                snippet = self.chop_text(snippet, width - text_width - 1)
                if snippet:
                    text.append(snippet)
                    attrs.append((style, len(snippet)))
                raise NoSpace()
            else:
                text.append(snippet)
                attrs.append((style, len(snippet)))

        # Determine the style (fg/bg colors) to render the column's text
        # 1) Get it from user input (or use default)
        style = self.style
        # 2) Columns of a critical data item should use 'critical' style,
        # unless the column is a trivial one.
        if self.item.is_critical() and style != 'trivial':
            style = 'critical'
        # 3) Columns of a focused data item should use 'focused' style.
        if focus:
            style = 'focused'
        # Theme is a global variable.
        companion_style = theme.get_companion(style)

        # Generate text and its run-length encoded attributes
        try:
            # 1) Add two leading spaces in the first colum of an item
            if not self.index:
                _create_text_and_attrs(self.SPACE * 2, companion_style)
            # 2) Indent the text of the first column of a child item
            if self.item.get_level() and not self.index:
                indent = self.SPACE * self.item.get_level() * 2 + \
                    self.LEVEL_INDICATOR + self.SPACE
                _create_text_and_attrs(indent, companion_style)
            # 3) Add the column's value
            _create_text_and_attrs(self.value, style)
            # 4) Append an indicator if it has multiple values
            if self.shortcut:
                _create_text_and_attrs(self.LIST_INDICATOR, companion_style)
        except NoSpace:
            pass
        finally:
            # 5) Add Padding
            size = width - sum([wcswidth(t) for t in text])
            if size:
                text.append(self.SPACE * size)
                attrs.append((companion_style, size))

        # Urwid TextCanvas accepts bytes, instead of unicode string
        text_b = bytearray()
        for index, snippet in enumerate(text):
            snippet_b = snippet.encode()
            text_b.extend(snippet_b)
            style, _ = attrs[index]
            attrs[index] = (style, len(snippet_b))
        return bytes(text_b), attrs

    def update_value(self):
        """Get the next value in value list and set column value to it.

           The function is called only if self.shortcut is not None.
        """
        self.value_index = (self.value_index + 1) % len(self.value_candidates)
        self.value = self.value_candidates[self.value_index]


class Item(urwid.Widget):
    """
    An Item instance is a urwid widget which shows a data entry in
    columns (one column for each field).

    Args:
        columns (list of tuple): A list of column data. Each item
            represents a column, in this format: (name, value, attrs).

                name (str): Column name.
                Value (str): Column value. Note it can be a list.
                attrs (dict): A dict containing the column's attribute
                    name/value pairs.
        hidden_columns (dict): A dict containing non-displayed field
            name/value pairs.
        item_attrs (dict): A dict containing the data entry's attributes.

    Raises:
        NoSpace: Raised if there isn't enough space to show columns.
    """
    _sizing = frozenset(['flow'])
    ATTRS = {'_level': 0,
             '_critical': False}

    def __init__(self, columns, hidden_columns, item_attrs):
        super(Item, self).__init__()
        self.hidden_columns = hidden_columns
        self.item_attrs = sanitize_input(item_attrs, self.ATTRS)
        self.columns = self.create_columns(columns, item_attrs)

    def is_critical(self):
        return self.item_attrs['_critical']

    def get_level(self):
        return self.item_attrs['_level']

    def create_columns(self, columns, item_attrs):
        columnobjs = []
        for index, column in enumerate(columns):
            name, value_candidates, column_attrs = column
            columnobjs.append(Column(self, index, name, value_candidates,
                                     column_attrs))
        return columnobjs

    def rows(self, size, focus=False):
        return 1

    def render(self, size, focus=False):
        (maxcol, ) = size
        self.set_columns_width(maxcol)
        text, attrs = self.get_text_and_attributes(focus=focus)
        return urwid.TextCanvas(text, attrs, maxcol=maxcol)

    def get_text_and_attributes(self, focus=False):
        itemtext_b = bytearray()
        attrs = []
        for c in self.columns:
            width = c.width if c.width else c._width
            column_text, column_attrs = c.get_text_and_attrs(focus=focus,
                                                             width=width)
            itemtext_b.extend(column_text)
            attrs.extend(column_attrs)
        return [bytes(itemtext_b)], [attrs]

    def set_columns_width(self, maxcol):
        used = sum([c.width for c in self.columns if c.width])
        if used > maxcol:
            raise NoSpace("There isn't enough space to show all columns")

        no_width = [c for c in self.columns if not c.width]
        for c in no_width:
            c._width = int((maxcol - used) / len(no_width))

    def selectable(self):
        return True

    def keypress(self, size, key):
        global result
        if key in ('enter', ' '):
            result = self.hidden_columns
            for c in self.columns:
                if c.will_return:
                    result[c.name] = c.value
            raise urwid.ExitMainLoop()
        else:
            c = self.get_column_by_shortcut(key)
            if c:
                c.update_value()
                self._invalidate()
                return
        return key

    def get_column_by_shortcut(self, key):
        for c in self.columns:
            if key == c.shortcut:
                return c
        return None


class Group(urwid.Pile):
    def __init__(self, items, name=None):
        blank = urwid.Text('')
        title = urwid.AttrMap(urwid.Text('[ %s ]' % name), 'misc')
        divider = urwid.AttrMap(urwid.Divider('-'), 'misc')
        if name:
            inner_widgets = [blank, title, divider] + items
        else:
            inner_widgets = [blank] + items
        super(Group, self).__init__(inner_widgets)

        # Add VIM-like 'j' and 'k' key behavior
        cmd_map = urwid.CommandMap().copy()
        cmd_map['j'] = 'cursor down'
        cmd_map['k'] = 'cursor up'
        self._command_map = cmd_map


class List (urwid.ListBox):
    def __init__(self, groups):
        it = urwid.SimpleListWalker(groups)
        super(List, self).__init__(it)

        # Add VIM-like 'j' and 'k' key behavior
        cmd_map = urwid.CommandMap().copy()
        cmd_map['j'] = 'cursor down'
        cmd_map['k'] = 'cursor up'
        self._command_map = cmd_map


class EventLoop(urwid.MainLoop):
    def __init__(self, widget):
        super(EventLoop, self).__init__(widget,
                                        palette=theme.get_palette(),
                                        unhandled_input=self.global_keypress)

    def run(self):
        try:
            super(EventLoop, self).run()
        except KeyboardInterrupt:
            pass
        return result # This is a global variable in this module.

    def global_keypress(self, key):
        if key in ('q', 'esc'):
            raise urwid.ExitMainLoop()


def sanitize_input(user_input, spec):
    # Check unknown keys
    for name in user_input.keys():
        if name not in spec.keys():
            raise ValueError('Unknown key: %s in %s' %
                             (name, user_input))

    # Add missing items with their default values
    d = user_input.copy()
    for name, value in spec.items():
        if name not in d:
            d[name] = value
    return d


def set_theme(new_theme):
    """Set a custom theme.

    Args:
        theme (dict): A dict containing text style name/value pairs.
            Text style value is a tuple containing fg/bg colors.

    For more details see Theme section in 'pydoc3 pypick' command output.
    """
    global theme
    theme = Theme(new_theme)


theme = Theme()
result = None
