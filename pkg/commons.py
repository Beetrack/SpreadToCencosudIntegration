
def ignore_none_value(values):
    not_none_value = []
    for value in values:
        if value != None:
            not_none_value.append(value)
    return not_none_value

def fetch_tag_value(array, tag_name):
    print(array, type(array))
    print(tag_name, type(tag_name))
    for item in array:
        print("item :",item)
        print("item[name] :", item['name'])
        if tag_name == item['name']:
            return item['value']
    return None
