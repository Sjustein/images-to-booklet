from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os


# Function to add the image number in the top left of the image and make a cutout of the image
def preprocess_image(image_path, number, crop_vector, add_number):
    image = Image.open(image_path)

    # Crop out the same part if the image for every image
    cropped_image = image.crop(crop_vector)
    draw = ImageDraw.Draw(cropped_image)

    # If no number should be added to the image, return the crop here
    if not add_number:
        return cropped_image

    # Use the user provided ttf font and a size of 50 to draw the number on the cropped image
    font = ImageFont.truetype('fonts/font.ttf', 50)

    # Add the image number to the top left of the image
    draw.text((10, 10), str(number), font=font, fill="black")

    return cropped_image


# Function to compile the temporary images into a pdf
def create_pdf_with_images(image_folder, output_pdf, crop_vector, document_title, add_nunber, sequence):
    # Create a blank A4 canvas
    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4

    # Define th grid layout and spacing for the booklet
    images_per_row = 3
    images_per_col = 5
    margin = 30

    # Calculate the scaled image width and height, based on the grid layout
    image_width = (width / images_per_row) * 0.93
    image_height = (height / images_per_col) * 0.93
    page_number = 1

    # Add one row worth of images to the end of the sequence, to compensate for the title
    index_end = sequence[1] + images_per_row

    # Loop through the images
    for i in range(sequence[0], index_end, images_per_row * images_per_col):
        if page_number == 1:
            # Add the header on the first page
            c.setFont("Helvetica", 24)
            c.drawCentredString(width / 2, height - 75, document_title)
            num_rows = images_per_col - 1  # Eén rij minder voor de eerste pagina
        else:
            num_rows = images_per_col

        for row in range(num_rows):
            for col in range(images_per_row):
                img_index = (i + row * images_per_row + col) if page_number == 1 else (
                            i + row * images_per_row + col - images_per_row)
                if img_index > sequence[1]:
                    break

                # Find the current image to be processed
                image_path = os.path.join(image_folder, f'{img_index}.png')
                numbered_image = preprocess_image(image_path, img_index, crop_vector, add_number)

                # Scale the images to an appropriate size to include in the booklet
                aspect_ratio = numbered_image.width / numbered_image.height
                if image_width / aspect_ratio <= image_height:
                    scaled_width = image_width
                    scaled_height = image_width / aspect_ratio
                else:
                    scaled_width = image_height * aspect_ratio
                    scaled_height = image_height

                # Calculate the x and y position of this image
                x_position = (margin) + col * image_width
                y_position = height - (0 + (row + 1) * image_height) - (125 if page_number == 1 else 20)

                # Resize the image with a resolution large enough so it's quality is adequately retained
                numbered_image = numbered_image.resize((int(scaled_width * 2), int(scaled_height * 2)), Image.ANTIALIAS)
                temp_image_path = os.path.join(image_folder, f'temp_{img_index}.png')
                numbered_image.save(temp_image_path)

                # Draw the image on the current page
                c.drawImage(temp_image_path, x_position, y_position, width=scaled_width, height=scaled_height)

        # Add a page number to every page of the document
        c.setFont("Helvetica", 12)
        c.drawString(width - 100, 30, f"Page {page_number}")
        print(f'Finished compiling page {page_number} of the booklet.')
        page_number += 1
        c.showPage()

    c.save()


# Function to cleanup temporary files the script creates
def cleanup(image_folder, id_start, id_end):
    for i in range(id_start, id_end + 1):
        # Define the filename
        filename = os.path.join(image_folder, f'temp_{i}.png')

        # Check if the file exists
        if os.path.exists(filename):
            # Remove the file
            os.remove(filename)
        else:
            print(f'Warning: {filename} does not exist.')

    print('Finished cleanup of temporary images.')


input_folder = 'input'  # Relative folder name containing the input images, relative from the root folder
output_pdf = 'booklet.pdf'  # The output filename
crop_vector = (350, 0, 1250, 750)  # The area to crop out of each image
sequence_start = 0  # Start the image sequence at this number (filename)
sequence_end = 105  # End the image sequence after this number (filename0
document_title = "Booklet title"  # The title printed above the booklet
add_number = True  # Whether to add a number to each image in the top left

# Actually create the pdf
create_pdf_with_images(input_folder, output_pdf, crop_vector, document_title, add_number,
                       (sequence_start, sequence_end))

# Clean up the temporary images generated
cleanup(input_folder, sequence_start, sequence_end)
