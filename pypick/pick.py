# Copyright (C) 2019 by Huan Xiong. All Rights Reserved.
# Licensed under GPLv3 or later. See LICENSE file under top level directory.

from . import ui


class Pick:
    """
    A Pick instance takes a list of multi-field data entries, and optional
    meta data on each field's appearance and behavior. It displays data
    entries in text based UI, one row for each data entry and one column
    for each field. It returns an entry's data when user selects it.

    For more details see 'pydoc3 pypick' command output.

    Args:
        fields (list of str): Name of the fields shown in UI
        extra_fields (list of str): Name of the fields not shown but will
            be returned if user selects the entry in UI.
        field_attrs (dict of dict): Describing UI attributes of the fields
            shown in UI. Each item describes one field. Item name is field
            name, item value is dictionary containing field attributes.

    Raises:
        ValueError: Raised if argument value is valid.
        NoSpace: Raised if there isn't enough space to display a column.
    """
    def __init__(self, fields, extra_fields=[], field_attrs={}):
        # Check user input
        # 1) fields and extra_fields shouldn't have same item.
        # 2) field_attrs shoud contain only attrs for items in fields.
        for i in fields:
            if i in extra_fields:
                raise ValueError("'%s' shouldn't be in both fields and "
                                 "extra_fields" % i)
        for i in field_attrs:
            if i not in fields:
                raise ValueError("fields doesn't have '%s', but field_attrs "
                                 "defines attrs for it" % i)
        self.fields = fields
        self.extra_fields = extra_fields
        self.field_attrs = field_attrs
        self.groups = []
        self.create_group(Group.DEFAULT_GROUP)

    def create_group(self, name, fields_spec=None):
        """ Create a group.

        Args:
            name (str): group name
            fields_spec (tuple or None): If this argument is None, the
                group uses the global definition of fields, extra_fields,
                field_attrs. Otherwise, the tuple is of this format:
                (fileds, extra_fields, field_attrs). Please refer to
                parameters of Pick.__init__().

        Returns:
            A Group instance.
        """
        if fields_spec:
            fields, extra_fields, field_attrs = fields_spec
        else:
            fields, extra_fields, field_attrs = self.fields, \
                self.extra_fields, self.field_attrs
        g = Group(name, fields, extra_fields, field_attrs)
        self.groups.append(g)
        return g

    def add_entries(self, entries):
        """Add entries.

        Args:
            entries (list): list of data. Its item is a dict representing
            a multi-field data.
        """
        default_group = self.groups[0]
        default_group.add_entries(entries)

    def run(self):
        """Show data list in UI and wait for user to select an item

        Returns:
            A dict containing fields of the data entry user selected.
        """
        group_widgets = []
        for g in self.groups:
            group_widgets.append(g._create_widget())
        list = ui.List(group_widgets)
        return ui.EventLoop(list).run()


class Group:
    """
    A Group instance contains a list of data entries. A group has a
    name and can define its own rules on which fields should be shown
    and what UI attributes each of them has.

    To instantiate the class, user should call Pick.create_group()
    rather than call its constructor directly.

    Args:
         name (str): Group name
         fields (list): See fields parameter of Pick.__init__()
         extra_fields (list): See extra_fields parameter of Pick.__init__()
         field_attrs (list): See field_attrs parameter of Pick.__init__()

    """
    DEFAULT_GROUP = '_global'

    def __init__(self, name, fields, extra_fields, field_attrs):
        self.name = name
        self.fields = fields
        self.extra_fields = extra_fields
        self.field_attrs = field_attrs
        self.entries = []

    def add_entries(self, entries):
        """Add entries to the group.

        Args:
            entries (list): list of data. Its item is a dict representing
            a multi-field data.
        """
        self.entries.extend(entries)

    def _create_widget(self):
        item_widgets = []
        # Create an Item widget for each entry, then use them to create
        # a Group widget.
        for entry in self.entries:
            columns = []
            columns_hidden = {}
            # Process fields shown in UI
            for field in self.fields:
                value = entry.get(field, '')
                attrs = self.field_attrs.get(field, {})
                columns.append((field, value, attrs))
            # Process extra fields that are not shown
            for field in self.extra_fields:
                columns_hidden[field] = entry.get(field, '')
            item_attrs = dict((k, v) for k, v in entry.items()
                              if self._is_item_attr(k))
            item = ui.Item(columns, columns_hidden, item_attrs)
            item_widgets.append(item)
        if self.name == self.DEFAULT_GROUP:
            return ui.Group(item_widgets)
        else:
            return ui.Group(item_widgets, name=self.name)

    def _is_item_attr(self, name):
        return name in [i for i in ui.Item.ATTRS]
