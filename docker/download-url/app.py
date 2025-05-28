import io
import json
import logging
import tempfile
import zipfile

import py7zr
from flask import Flask, Response, request

app = Flask(__name__)

# Set up logging to stdout
logging.basicConfig(level=logging.INFO)


@app.route("/document/<param>", methods=["GET"])
def handle_request(param):
    # Log the request body
    app.logger.info("Request body: %s", request.data.decode("utf-8"))

    auth = request.authorization
    if auth.type != "token" and auth.token != "insecure":
        return Response(status=401)

    match param:
        case "empty":
            return Response(status=204)
        case "error":
            return Response(status=400)
        case "zip":
            temp_zip = io.BytesIO()

            nested_temp_zip = tempfile.NamedTemporaryFile(mode="w+")
            json.dump({"foo": "bar"}, nested_temp_zip)
            nested_temp_zip.flush()

            with zipfile.ZipFile(temp_zip, mode="w") as zip_file:
                zip_file.writestr(zinfo_or_arcname="test.txt", data="test1")
                zip_file.writestr(zinfo_or_arcname="test2.txt", data="test2")
                zip_file.write(arcname="test3.json", filename=nested_temp_zip.name)

            temp_zip.seek(0)

            return Response(
                temp_zip.getvalue(),
                mimetype="application/zip",
            )
        case "7zip":
            temp_zip = io.BytesIO()

            with py7zr.SevenZipFile(temp_zip, mode="w") as seven_zip_file:
                seven_zip_file.writestr(arcname="test.txt", data="test1")
                seven_zip_file.writestr(arcname="test2.txt", data="test2")

                file_data = "a" * 1_000_000  # 1mb
                seven_zip_file.writestr(arcname="test3.txt", data=file_data)

            temp_zip.seek(0)

            return Response(
                temp_zip.getvalue(),
                mimetype="application/x-7z-compressed",
            )
        case "smol7zip":
            temp_zip = io.BytesIO()

            with py7zr.SevenZipFile(temp_zip, mode="w") as seven_zip_file:
                # 500 bytes
                seven_zip_file.writestr(arcname="smol1.txt", data="test1" * 100)
                # 5 bytes
                seven_zip_file.writestr(arcname="smol2.txt", data="test2")

            temp_zip.seek(0)

            return Response(
                temp_zip.getvalue(),
                mimetype="application/x-7z-compressed",
            )

        case _:
            return Response(f"Document '{param}'", mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
