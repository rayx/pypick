A Python library for selecting an item from a list of multi-field data in terminal.

# Introduction

PyPick allows you to specify a list of data entries (each entry has multiple fields and is represented by a dict) and optional meta data on how each fields shold be shown and interactived with. It displays these entries in terminal, one row for each etnry and one column for each field. It returns an entry's data when user selects it.

PyPick provides a general API. You can customize it easily for different scenarios, for example:

- Select a host to ssh into (see screenshot below)
- Select a frequently accessed directory
- Select a frequently used command

![docs/images/demo.png](https://github.com/rayx/pypick/raw/master/docs/images/demo.png)

# Install

As Python2 will be EOL'ed soon, PyPick supports only Python3. To install it, run:

    $ python3 -m pip install pypick

# A Quick-Start Guide

## A Simplest Example

Suppose you have two hosts and you'd like to use PyPick to generate a list:

    hosts = [{'name': 'server-5',
              'host': '10.64.4.5',
              'user': ['root', 'rayx'],
              'project': 'project X',
              'description': 'ubuntu 16.04, 192G RAM'},
             {'name': 'server-66',
              'host': '10.64.4.66',
              'user': ['root'],
              'project': 'project Y',
              'description': 'centos 7.4, 96G RAM'}]

The simplest way to do it is to pass the data and specify the fields you'd like to show:

    from pypick import Pick
    
	# NOTE: Add the above 'hosts' variable definition here.

    fields = ['name', 'host', 'user', 'description']
    p = Pick(fields)
    p.add_entries(hosts)
    result = p.run()
    print(result)

The code generates the following list. Each entry takes one row, and each field is displayed in one column.

![docs/images/simplest_example.png](https://github.com/rayx/pypick/raw/master/docs/images/simplest_example.png)

As you may notice, there is a minor issue with the above list. The last field of the first entry is not completely shown. This is because PyPick divides the available space for all columns equally by default. To address the issue, you can either increase the width of your terminal window, or adjust width of other fields in a programmatic way. We'll talk more about this latter.

You can press 'UP' and 'DOWN' (or VI style 'j' and 'k') to navigate through items in the list, press 'ENTER' (or 'SPACE') to select an entry, or press 'ESC' (or 'q') to quit without selecting anyting. 

If you selects an entry, the code returns its value, containing only the fields you specified. For example, if you select the first entry, the data returned is:

    {'description': 'ubuntu 16.04', 'name': 'server-5', 'host': '10.64.4.5', 'user': 'root'}

## Non-Displayed Fields

PyPick allows you to specify fields that are not shown but are returned. For example, the following code generates the same list as above but it returns an additional 'project' field when user selects an entry.

    from pypick import Pick
    
    # NOTE: Add the above 'hosts' variable definition here.
    
    fields = ["name", "host", "user", "description"]
    extra_fields = ["project"]
    p = Pick(fields, extra_fields=extra_fields)
    p.add_entries(data_list)
    result = p.run()
    print(result)
	
## Customizing Field Appearance and Behavior

In previous example, PyPick determines column width for you and uses default foreground/background colors to show them. In practice you often know roughly the size of most fields. In that case, you can use 'width' attribute to specify their column width.

PyPick displays all fields in 'dark blue' foreground color and default background color by default. However, sometimes not all fields are of the same importance. For those less important fields (e.g, a comment field), you may want to visually deemphasize them. That can be done by using 'style' attribute, which is string representing a specific foreground and background color combintation.

When you select an entry, PyPick returns all these fields shown in the list by default. However, sometimes you may want to show a field but don't need its value (e.g., a comment field). In that case, you can set the field's 'return' attribute to False.

In our example, 'description' is a less important field because it provides only additional information not required by ssh command. The following code sets its 'style' attribute so that the field is displayed in dimmed foreground color and sets its 'return' attribute so that the field's value is not returned. The code also sets the width of 'name', 'host' and 'user' fields explicitly so that 'description' field will get more space than in the previous example.

    from pypick import Pick
    
	# NOTE: Add the above 'hosts' variable definition here.

    fields = ["name", "host", "user", "description"]
    field_attrs = {'name': {"width": 20},
                   'host': {"width": 20},
                   'user': {"width": 12},
                   'description': {'return': False,
                                   'style': 'trivial'}}
    p = Pick(fields, field_attrs=field_attrs)
    p.add_entries(hosts)
    result = p.run()
    print(result)

It generates a list like the following. Note 'description' field has more space and its text is displayed in gray white.

![docs/images/field_attributes.png](https://github.com/rayx/pypick/raw/master/docs/images/field_attributes.png)

There is one thing that might puzzle you and I haven't talked about. It's the small triangle after the data of 'user' field. It's an indicator showing that the field have multiple values. In our example, the first entry's 'user' field is list containg more than one values and hence the indicator appears.

If a field value is a list containg more than one items, PyPick displays the first value by default. It also defines a shortcut key allowing user to iterate over other available values. That shortcut key is the first character of the field name by default. So if you navigate to first entry and press 'u', the text in the 'user' field will be 'rayx' instead. If you then press 'ENTER' to select the entry, the code returns:

    {'user': 'rayx', 'host': '10.64.4.5', 'name': 'server-5'}
	
Note 'description' field is not returned because we set this field's 'return' attribute to False.

You can specify a custom shortcut by setting a field's 'shortcut' attribute.

## Defining Entry Attributes

In the last section we talk about defining field attributes to customize field appearance and behavior. In this section we'll talk about entry attributes, which affect an entry's (and hence its columns) appearance.

Entries can have parent/child relationship. Child entry is indented relative to its parent when shown in list. PyPick allows user define the parent/child relationship in a simple approach. Each entry can have a '_level' attribute, which defaults to 0. If entry B follows entry A (note that entries are always in order) and B's '_level' is larger than that of A by 1, then B is A's child and is indented properly.

Some entries can have higher priority than the others. You indicate that to PyPick by setting their '_critical' attributes to True. PyPick highlights those entries with a different foreground color.

Let's change the host data a bit to demonstrate the two features:

    hosts = [{'name': 'server-5',
              'host': '10.64.4.5',
              'user': ['root', 'rayx'],
              'project': 'project X',
              'description': 'ubuntu 16.04, 192G RAM'},
             {'name': 'vm-176',
              'host': '192.168.122.176',
              'user': ['root', 'rayx'],
              'description': 'QEMU test: hotplugging',
              '_level': 1},
             {'name': 'nested-vm',
              'host': '192.168.18.3',
              'user': ['root', 'rayx'],
              'description': 'QEMU test: nested vm',
              '_level': 2},
             {'name': 'vm-37',
              'host': '192.168.122.37',
              'user': ['root', 'rayx'],
              'description': 'QEMU test: virtio-block',
              '_level': 1},
             {'name': 'server-66',
              'host': '10.64.4.66',
              'user': ['root'],
              'project': 'project Y',
              'description': 'centos 7.4, 96G RAM'}]

With the other portion of the code unchanged, the new host data generates a list like the following:

![docs/images/entry_attributes.png](https://github.com/rayx/pypick/raw/master/docs/images/entry_attributes.png)

## Organizing Data Entries into Groups

So far, we add data entries to list directly in all examples and get flat lists. PyPick allows you to organize data entries into groups and add those groups to list. You can mix these two approaches if you like.

To demostrate this feature, let's suppose we have two host lists:

    group1 = [{'name': 'server-5',
               'host': '10.64.4.5',
               'user': ['root', 'rayx'],
               'project': 'project X',
               'description': 'ubuntu 16.04, 192G RAM'},
              {'name': 'server-66',
               'host': '10.64.4.66',
               'user': ['root'],
               'project': 'project Y',
               'description': 'centos 7.4, 96G RAM'}]
    
    group2 = [{'name': 'arm-server',
               'host': '10.64.37.55',
               'user': ['rayx', 'root'],
               'description': 'Centriq 2400, 192G RAM'},
              {'name': 'x86-server',
               'host': '10.64.37.51',
               'user': ['rayx', 'root'],
               'description': 'Xeon Gold 5118, 192G RAM'},
              {'name': 'test-client',
               'host': '10.64.37.182',
               'user': ['rayx', 'root']}]

The code adds them to two groups, respectively:

    from pypick import Pick

    # NOTE: Add the above 'group1' and 'group2' variable definition here

    fields = ['name', 'host', 'user', 'description']
    field_attrs = {'name': {"width": 20},
               'host': {"width": 20},
               'user': {"width": 12},
               'description': {'return': False,
                               'style': 'trivial'}}
	
    p = Pick(fields, field_attrs = field_attrs)
    g1 = p.create_group('Aarch64 Servers')
    g1.add_entries(group1)
	g2 = p.create_group('Benchmarking')
	g2.add_entries(group2)
	result = p.run()
	print(result)

It generates a list like the following:

![docs/images/group.png](https://github.com/rayx/pypick/raw/master/docs/images/group.png)

A group can override the global field attributes. That means a group can have its own rules on which fields to show and how to show them. For simplicity's sake I'll not talk the details here. Please refer to the library's API reference.

## Defining Your Own Theme

PyPick defines a few built-in sytles for you to customize field foreground/background colors. The styles are:

- 'focused': For fields of entry being focused
- 'critical': For fields of entries which have '_critical' set
- 'normal': For regular fields
- 'trivial': For less important fields
- 'misc': For other non-data text (group name, dash line, etc.)

The following are their default values:

    | Style      | Foreground Color | Background Color |
    |------------+------------------+------------------|
    | 'focused'  | 'white'          | 'dark blue'      |
    | 'critical' | 'dark red'       | 'default'        |
    | 'normal'   | 'dark blue'      | 'default'        |
    | 'trivial'  | 'default'        | 'default'        |
    | 'misc'     | 'default'        | 'default'        |

As mentioned above, you can set a field's 'style' attribute to one of them to customize that field's appearance.

What's more, you can also customize these styles default values by calling set_theme() function.

For example 'trivial' style uses default foreground color by default, if you want to deemphasize it further, you can set its foregroud color to 'dark gray' for example. 

Note to Solarized color theme user:

Due to the way how Solarized 16-color palette is organized, the 'dark gray' color is actually located at 'light green' slot. So you should set 'trivial' style's foreground color to 'ligh green' instead.

The following code changes 'trivial' and 'misc' styles. Note the code is written for Solarized color theme. If you aren't using it, perhaps you should consider it :) or adjust the code for your terminal's palette.

    from pypick import Pick, set_theme
    
    group1 = [{'name': 'server-5',
               'host': '10.64.4.5',
               'user': ['root', 'rayx'],
               'project': 'project X',
               'description': 'ubuntu 16.04, 192G RAM'},
              {'name': 'server-66',
               'host': '10.64.4.66',
               'user': ['root'],
               'project': 'project Y',
               'description': 'centos 7.4, 96G RAM'}]
    
    fields = ['name', 'host', 'user', 'description']
    field_attrs = {'name': {"width": 20},
                   'host': {"width": 20},
                   'user': {"width": 12},
                   'description': {'return': False,
                                   'style': 'trivial'}}

    # NOTE: an empty string ('') is interpreted as 'default'
    theme = {'trivial': ('light green', ''), 'misc': ('brown', '')}
    set_theme(theme)
    
    p = Pick(fields, field_attrs = field_attrs)
    g1 = p.create_group('ARM Servers')
    g1.add_entries(group1)
    result = p.run()
    print(result)

It generates a list like the following:

![docs/images/theme.png](https://github.com/rayx/pypick/raw/master/docs/images/theme.png)

# API Reference

For a more complete description on the concepts and API reference, please install the package and run:

    $ python3 -m pydoc pypick
