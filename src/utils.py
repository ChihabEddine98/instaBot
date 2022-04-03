# In this file you will find our
# Utilities that haelped us a lot !

# Text ---> hashtags Or mentions (# or @)
def text_2_hashtags(txt="",tag="#"):
    i , n , h_ = 0,len(txt),[]
    tags = [" ",".","#","\\","@"] if tag == "@" else [" ",".","#","\\"]
    
    while(txt.find(tag,i,n) > 0 ):
        a = txt.index("#",i,n)+1
        if (a < n):
            c_i = a
            h = ""
            while(c_i < n and txt[c_i] not in tags ):
                h += txt[c_i]
                c_i += 1
            h_.append(h)
            i = c_i
        else :
            a += 1
            i = a
    return h_
            