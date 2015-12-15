
# this is a simple example of using pycoin to create statically generated
# addresses to define products and costs -- I do not suggest this as a long-term
# solution

# ku P:test -n tDASH -s 0p/0
# wallet key                : DRKVrRogV4fTickSWLd8TNQ7bhcYQ1CSpoTVBSUF2bGmJEyCWUUcM8Rmf93AMQwPkj\
#                               K8NJXZh3JVbmJ4MY7zMaPiqXybS8t9cTUMk6LTE6HKnaYi
# public version            : DRKPuUaqv1rR8uUBNF5HASizoNxrvhVA3gMkvgGtYAFyhC52LVESdYEDE3D663m2gh\
#                               gQ9nj4sT8KF1H6eJKhsP9dX5CQTf6oiWwiEbsTawgKDUkA

# ku DRKPuUaqv1rR8uUBNF5HASizoNxrvhVA3gMkvgGtYAFyhC52LVESdYEDE3D663m2ghgQ9nj4sT8KF1H6eJKhsP9dX5CQTf6oiWwiEbsTawgKDUkA -s 1-10 | grep address | grep -v uncomp
# Dash address              : y7P3T9E2Y7gqJ2y247AyefpgWAHWqj8dfd
# Dash address              : yAPuFAatxqVbLtPts5o6gUH7gEB1VNFS4i
# Dash address              : y84kKgjfwJKeweT5nUMoEpjLkEbrtbgPxg
# Dash address              : xzi4RtjK8g8djjJf7cEHQcsx7iBXAHTgUb
# Dash address              : y4hmW7eTd4H3MveQAyK3YpFQ2UwdSkfA53
# Dash address              : y71MqEE56LrYAUzNcmw3XY22SaiFovHXzf
# Dash address              : y4KHwqZqFWp2Xyz1TGXtmXmtDwkbPoXB8j
# Dash address              : y8AYYjKgNRAhvcSzyiaghvEaN5BhoxyJH9
# Dash address              : yBh6FPVzUiEHgrCq7ob8uRKDzno9zbhKrs
# Dash address              : y2ju9GACnDbx7vAvbeixkbLtAxZm9TdexK

LOCK_THRESHOLD = 3


def trigger(x, y):
    """ dispense a product from row x, column y """
    # something clever here
    print "dispense row %i, col %i" % (x, y)
    pass

products = {
    "y7P3T9E2Y7gqJ2y247AyefpgWAHWqj8dfd": {
        "label": "coca cola",
        "cost": 1,
        "callback": lambda: trigger(0, 0)},
    "yAPuFAatxqVbLtPts5o6gUH7gEB1VNFS4i": {
        "label": "sprite",
        "cost": 2,
        "callback": lambda: trigger(0, 1)},
    "y84kKgjfwJKeweT5nUMoEpjLkEbrtbgPxg": {
        "label": "foo",
        "cost": 3,
        "callback": lambda: trigger(0, 2)},
    "xzi4RtjK8g8djjJf7cEHQcsx7iBXAHTgUb": {
        "label": "foo",
        "cost": 4,
        "callback": lambda: trigger(0, 3)},
    "y4hmW7eTd4H3MveQAyK3YpFQ2UwdSkfA53": {
        "label": "foo",
        "cost": 5,
        "callback": lambda: trigger(0, 4)},
    "y71MqEE56LrYAUzNcmw3XY22SaiFovHXzf": {
        "label": "foo",
        "cost": 1.1,
        "callback": lambda: trigger(1, 0)},
    "y4KHwqZqFWp2Xyz1TGXtmXmtDwkbPoXB8j": {
        "label": "foo",
        "cost": 2.1,
        "callback": lambda: trigger(1, 1)},
    "y8AYYjKgNRAhvcSzyiaghvEaN5BhoxyJH9": {
        "label": "foo",
        "cost": 3.1,
        "callback": lambda: trigger(1, 2)},
    "yBh6FPVzUiEHgrCq7ob8uRKDzno9zbhKrs": {
        "label": "foo",
        "cost": 4.1,
        "callback": lambda: trigger(1, 3)},
    "y2ju9GACnDbx7vAvbeixkbLtAxZm9TdexK": {
        "label": "foo",
        "cost": 5.1,
        "callback": lambda: trigger(1, 4)},
}
