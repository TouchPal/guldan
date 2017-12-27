# -*- coding: utf-8 -*-


class Metric(object):
    def __init__(self, measurement, tags, name, value):
        self.measurement = measurement
        self.tags = tags
        self.name = name
        self.value = value

    def get_uniq_name(self):
        tags_list = ["{}={}".format(k, v) for k, v in self.tags.items()]
        tags_str = ",".join(tags_list)

        if not tags_str:
            final_str = self.measurement
        else:
            final_str = "{},{}".format(self.measurement, tags_str)

        return "{} {}".format(final_str, self.name)

    def __str__(self):
        return "[measurement: {}, tags: {}, name: {}, value: {}]".format(
            self.measurement, self.tags, self.name, self.value
        )