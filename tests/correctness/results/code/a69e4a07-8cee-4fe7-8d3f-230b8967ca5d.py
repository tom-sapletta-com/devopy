def execute():
    def filter_even_numbers(lst):
        return [x for x in lst if x % 2 == 0]

    result = filter_even_numbers([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    return result