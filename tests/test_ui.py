from pypick.ui import Column, Item, Group, List, EventLoop

def test_basic():
    name_column_attrs = {"width":20,
                         "shortcut": None,
                         "return": True,
                         "style": "normal"}
    name = ("name", "ＷＩＤＥ－ＣＨＡＲＡＣＴＥＲ", name_column_attrs)

    user_column_attrs = {"width": 20,
                         "shortcut": 'u',
                         "return": True,
                         "style": "normal"}
    user = ("user", ["root", "rayx"], user_column_attrs)

    host_column_attrs = {"width":20,
                         "shortcut": None,
                         "return": True,
                         "style": "normal"}
    host = ("host", "192.168.1.18", host_column_attrs)

    desc_column_attrs = {"width": None,
                         "shortcut": None,
                         "return": False,
                         "style": "trivial"}
    desc = ("desc", "this is a comment.", desc_column_attrs)

    fields = [name, user, host, desc]
    extra_fields = {"field_X": "X", "field_Y": "Y"}

    item1 = Item(fields, {}, {})
    item2 = Item(fields, {}, {"_level": 1, "_critical": True})
    item3 = Item(fields, extra_fields, {"_level": 2})
    group1 = Group([item1, item2, item3], name="group1")

    item4 = Item(fields, {}, {})
    item5 = Item(fields, extra_fields, {"_level": 1})
    group2 = Group([item4, item5], name="group2")

    list = List([group1, group2])
    result = EventLoop(list).run()
    print(result)
