"""Test filename timestamp parsing"""
from exif_service import parse_filename_timestamp

test_files = [
    'PXL_20250331_091108066.jpg',
    'IMG_20250115_142530.jpg',
    '20241225_183045.jpg',
    'IMG-20250210-WA0023.jpg',
    'Screenshot_20250401-093027.png',
    'VID_20250215_162340.mp4',
    'random_image.jpg',
    'photo_with_1770265575020_numbers.jpg'
]

print('FILENAME TIMESTAMP PARSER TEST')
print('=' * 50)
for f in test_files:
    result = parse_filename_timestamp(f)
    if result['timestamp']:
        ts = result['timestamp']
        print(f'{f}')
        print(f'  Camera: {result["camera_type"]}')
        print(f'  Date: {ts.strftime("%B %d, %Y")}')
        print(f'  Time: {ts.strftime("%I:%M:%S %p")}')
        print()
    else:
        print(f'{f} -> No timestamp found')
        print()
