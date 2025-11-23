"""Simple barcode/QR decoder that reads FOLDER_NAME from environment.

Behavior:
- Reads folder name in this order: command-line --folder-name -> ENV FOLDER_NAME -> 'default_folder'
- Loads an image named 'barcode_qrcode.jpg' from that folder and decodes barcodes/QR codes.
"""

import os
import logging
from pyzbar.pyzbar import decode
from PIL import Image
from dataclasses import dataclass
from typing import Optional
from uipath import UiPath


@dataclass
class InputArgs:
    file_path: str
    folder_path: Optional[str] = None
    bucket_name: Optional[str] = None


@dataclass
class OutputResult:
    barcodes: [str]
    qrcodes: [str]


def extract_barcodes_and_qrcodes(sdk: UiPath, folder_path: str, bucket_name: str, file_path: str ):
    result = OutputResult(barcodes=[], qrcodes=[])
    # Load the image containing barcodes or QR codes
    image_path = sdk.buckets.download( name = bucket_name, 
                 blob_file_path=file_path, 
                 destination_path=os.path.join("/tmp", file_path),
                 folder_path=folder_path)
    image = Image.open( os.path.join("/tmp", file_path) )
    # Decode the barcodes/QR codes
    decoded_objects = decode(image)
    # Print the detected data
    for obj in decoded_objects:
#        print("Type:", obj.type)
#        print("Data:", obj.data.decode('utf-8'))
        if obj.type == "QRCODE":
            result.qrcodes.append( obj.data.decode('utf-8') )
        else: 
            result.barcodes.append( obj.data.decode('utf-8') )
    return result

def main( input: InputArgs ):
    sdk = UiPath()
   
    result = extract_barcodes_and_qrcodes(
                                       sdk, 
                                       folder_path = input.folder_path if input.folder_path != None else os.environ.get('FOLDER_NAME', 'SamsungService'), 
                                       bucket_name = input.bucket_name if input.bucket_name != None else os.environ.get('BUCKET_NAME', 'RepairRequests'),
                                       file_path = input.file_path )
    sdk.buckets.delete_file(
                        folder_path = input.folder_path if input.folder_path != None else os.environ.get('FOLDER_NAME', 'SamsungService'), 
                        name = input.bucket_name if input.bucket_name != None else os.environ.get('BUCKET_NAME', 'RepairRequests'),
                        blob_file_path = input.file_path)
    return result