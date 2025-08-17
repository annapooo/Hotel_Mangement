from PIL import Image
 

# Open an image file
with Image.open('./assets/startbg.jpeg') as img:
    # Resize image
    img = img.resize((448,400))
    # Save it back to disk
    img.save('resized_image.png')
