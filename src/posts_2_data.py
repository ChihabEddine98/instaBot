# Web ＠
import requests
import json
# Time 🕦
import time
import datetime
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
    
    
############################################################################################
def posts_2_data_tags(tag,n_posts,out,min_likes,timeout):
    
    print(f"Retrieving [{n_posts}] posts data from hashtag: #{tag}")

    # Initialization Broo's
    posts_data = []
    end_cursor = ''
    ok_req , no_ok_req , kick_req  = 3*(0,)
    kick_lim = 10 
    now = datetime.datetime.now()
    now_month , now_day = tuple(map(str,[now.month,now.day]))
    pages_ret , posts_ret = 2*(0,)
    
    now_month = f"0{now_month}" if len(now_month) == 1 else now_month
    now_day   = f"0{now_day}" if len(now_day) == 1 else now_day

    
    now = f"{now_day}{now_month}{now.year}"
    timeout += 2
    time_limit = time.time()
    
    while(posts_ret < n_posts):
        if ( time.time() - time_limit > timeout) : 
            print("Oups ! 😭 Timeout run awaay")
            break
        url = f"https://www.instagram.com/explore/tags/{tag}/?__a=1&max_id={end_cursor}"
        kicked_times=0
        while True and kicked_times < kick_lim:
            try:
                r = requests.get(url,timeout = 2)
            except Exception as e:
                time.sleep(1)
                kick_req += 1
                kicked_times+=1
                continue
            break
        if ( r.status_code == 200):
            raw_data = r.text
            data = json.loads(raw_data.strip(),strict = False)
            
            edge_hashtag= data['graphql']['hashtag']
            edge_hashtag_to_media=edge_hashtag['edge_hashtag_to_media']
            
            end_cursor = edge_hashtag_to_media ['page_info']['end_cursor'] # value for the next page
            
            edges = edge_hashtag_to_media ['edges'] # list with posts
            if(posts_ret==0):
                tag_id = edge_hashtag['id']
                tag_name = tag
                number_of_post_with_hashtag = edge_hashtag_to_media['count']
            page_time_start=time.time()
            for node in edges:
                if(posts_ret<n_posts):
                    post=node['node']
                    likes=post['edge_liked_by']['count']
                    if(likes>=min_likes):
                        owner_id = post['owner']['id']
                        timestamp = post['taken_at_timestamp']
                        shortcode=post['shortcode']
                        try :
                            number_coms=post['edge_media_to_comment']['count'] 
                        except :
                            number_coms=post['edge_media_parent_to_comment']['count']

                        coms=[]

                        url_img=post['display_url'] 
                        edges_media=post['edge_media_to_caption']['edges']
                        if (len(edges_media)>0):
                            text=edges_media[0]['node']['text'] 
                        else :
                            text=""

                        hashtags=text_2_hashtags(text)
                        mentions=text_2_hashtags(text,"@")
                        
                        if( post["is_video"]==False):
                            img_description=post["accessibility_caption"]
                            if(img_description.find(":") !=-1):
                                img_description=img_description[img_description.index(":")+1:]
                            else:
                                img_description="Null"
                        else:
                            img_description="Video"
                        posts_data.append({'tag_id': tag_id,'tag_name': tag_name,'extraction_date':now,
                                           'posts_W_hashtag':number_of_post_with_hashtag,'owner_id': owner_id,
                                           'shortcode': shortcode,'timestamp': timestamp,'likes': likes,
                                           'hashtags': hashtags,'mentions': mentions,'coms' : number_coms ,
                                           'text': text,'img_description' : img_description,'url_img' : url_img
                                           })
                        r.status_code=404
                        posts_ret+=1
                        if (posts_ret%10==0):
                            print(posts_ret," Posts retrieved")
                        time_limit=time.time()
            pages_ret+=1
            page_time_end=time.time()
        else :
            no_ok_req+=1
                
    print("Kicked requests : ",kick_req)
    
    with open("#"+out+'_posts_data.json', 'w') as outfile:
        json.dump(posts_data, outfile)
    print("#"+out+'_posts_data.json has been created ✅')
    
    