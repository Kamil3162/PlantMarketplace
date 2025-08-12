

def get_objects_range(page: int, page_size:int):
    start = page * page_size
    end = start + page_size
    return start, end