import requests 



import pytube as pt

a = pt.Search('why you did this')
print(a.results[0].URL)