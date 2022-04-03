# Web ＠
import requests
import json
# Time 🕦
import time
# Visualisation 📊
import pandas as pd

# Self 😁
from utils import text_2_hashtags


def posts_2_data(n_posts,out,timeout=5,wait=500):
    
    with open(f"{out}_posts.json", 'r') as f:
        posts = json.loads(f.read()) 
    
    print(f"{out}_posts.json opened ✅")  
    posts_data , coms , h_ = 3*([],)
    
    i , ok_req , no_ok_req , kick_req = 4*(0,)

    print("Retrieving data from posts ...")
    for post in posts:
        if(i < n_posts):
            url = f"https://www.instagram.com/p/{post['shortcode']}/?__a=1"
            while 1:
                try:
                    req = requests.get(url,timeout = timeout)
                    time.sleep(wait)
                except Exception as e:
                    continue
                break
            # Succes ✅
            if (req.status_code == 200):
                i += 1
                ok_req += 1
                data = json.loads(req.text)
                try:
                    location = data['graphql']['shortcode_media']['location']['name']
                except:
                    location = ''

                likes=data['graphql']['shortcode_media']['edge_media_preview_like']['count'] 
                try :
                    n_coms = data['graphql']['shortcode_media']['edge_media_to_parent_comment']['count']
                except :
                    n_coms = data['graphql']['shortcode_media']['edge_media_to_comment']['count']
                
                coms=[]
                try :
                    for nodes in data['graphql']['shortcode_media']['edge_media_to_parent_comment']['edges']:
                        coms.append(nodes['node']['text'])
                except:
                    try : 
                        for nodes in data['graphql']['shortcode_media']['edge_media_to_comment']['edges']:
                            coms.append(nodes['node']['text'])
                    except : 
                        coms.append("")

                url_img = data['graphql']['shortcode_media']['display_url']
                
                if (len(data['graphql']['shortcode_media']['edge_media_to_caption']['edges'])>0):
                    text=data['graphql']['shortcode_media']['edge_media_to_caption']['edges'][0]['node']['text'] #ok
                else :
                    text=""
                    
                h_ = text_2_hashtags(text,"#")
                posts_data.append({'shortcode': post['shortcode'],'likes': likes,'hashtags': h_,'#_of_coms' : n_coms ,'coms': coms ,'text': text,'url_img' : url_img,'location': location})
                req.status_code=404
            # Error ⛔️
            else :
                no_ok_req += 1
        time.sleep(10)
                

    with open(out+'_posts_data.json', 'w') as outfile:
        json.dump(posts_data, outfile) 
        
    df = pd.read_json(f"{out}_posts_2_data.json")
    df.to_csv(f"{out}_posts_2_data_results.csv")
    
    # Yooooho 🥳
    print(f"Kicked requests : {kick_req}")
    print(f"{out}'_posts_data.json has been created ✅")
    print(f"{out}'_posts_2_data_results.csv has been created ✅")