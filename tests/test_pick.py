from pypick import Pick

def test_basic():
    data_list = [{"name": "server-5",
                  "host": "10.64.4.5",
                  "user": ["root", "rayx"],
                  "project": "project X",
                  "description": "ubuntu 16.04"},
                 {"name": "server-66",
                  "host": "10.64.4.66",
                  "user": ["root"],
                  "project": "project Y",
                  "description": "centos 7.4"}]

    fields = ["name", "host", "user", "description"]
    p = Pick(fields)
    g1 = p.create_group("My Hosts")
    g1.add_entries(data_list)
    result = p.run()
    print(result)
