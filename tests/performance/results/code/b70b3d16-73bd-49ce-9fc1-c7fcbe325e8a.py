def execute():
    text = 'Python is awesome'
    
    vowels_in_text = 0
   # iterujemy po every char in our input string. if the character it a vowel, increment counter by 1 .-/
       for i in range(len(text)):
           ch = text[i]
            if ((ch == 'a') or (ch =='e')or (ch=='o')or (ch=='u')) : #we have a vowel, check it against all other characters to ensure logical correctness. 1st and last character cannot be the same as they would then not contain any vowsels
               if ((i == 0) or (text[i-1] == 'y') )and ch !='e': # at a vowel we must only increment counter when it is first in word, also ensure that next char after this does not be the same as to avoid logical correctness. 
                   if ((ch=='a')or (ch=='o')):  
                       continue            
               else :             
                 vowels_in_text += 1 # increment counter by one on each occurrence of a vowel we find in text string    .-/         
       return vowels_in_text 
print(execute())