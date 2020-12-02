
def ignore_none_value(values):
    not_none_value = []
    for value in values:
        if value != None:
            not_none_value.append(value)
    return not_none_value

def fetch_tag_value(array, tag_name):
    for item in array:
      if tag_name in item:
        return item[tag_name]
    return None
