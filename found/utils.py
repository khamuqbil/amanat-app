import qrcode

def generate_qr_code(serial_number, item):
    # Concatenate the serial number and item as the data for the QR code
    data = f"Serial Number: {serial_number}\nItem: {item}"

    # Create an instance of the QRCode class
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)

    # Add the data to the QR code
    qr.add_data(data)

    # Create the QR code image
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code image to a file or return the image object
    # qr_image.save('path/to/save/qr_code.png')
    return qr_image