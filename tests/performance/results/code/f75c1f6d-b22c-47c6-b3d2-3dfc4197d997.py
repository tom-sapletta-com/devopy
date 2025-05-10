def execute():
    text = "Wielo rosy kot ogromnych, bardzo silne go nie znalazl. Pytaniu lubi się maluj na czerwony tyle skrzyni jak to pychania."  # przyklad teksu
    vowels = 'aeiouAEIOU'  
    
    count = 0      
    for char in text:          
        if char.isalpha():     
            if (char in vowels):                  
                count += 1                       
                
    return "W teksie otrzymano {} samogłoski.".format(count)   # zwraca liczebność wystąpienia 
                                                                #samougłekw na danym tekscie (tutaj jestem przykazam dobraty!)