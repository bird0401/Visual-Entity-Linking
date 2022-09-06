insert_new_img_url = (
  "INSERT INTO img_urls (img_url) "
  "VALUE(%s)")
img_url = 'f'
print(insert_new_img_url%img_url)