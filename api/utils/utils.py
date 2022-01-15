def get_image_slug(image):
    parts = str.split(image, "/")
    last_part = parts[len(parts) - 1]
    slug_parts = str.split(last_part, ".")
    return slug_parts[0]
