import logging
import zipfile
import io

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

    if param == "empty":
        return Response(status=204)

    if param == "error":
        return Response(status=400)

    if param == "zip":
        temp_zip = io.BytesIO()

        with zipfile.ZipFile(temp_zip, mode="w") as zip_file:
            zip_file.writestr(zinfo_or_arcname="test.txt", data="test1")
            zip_file.writestr(zinfo_or_arcname="test2.txt", data="test2")

        temp_zip.seek(0)

        return Response(
            temp_zip.getvalue(),
            mimetype="application/zip",
        )

    if param == "7zip":
        temp_zip = io.BytesIO()

        with py7zr.SevenZipFile(temp_zip, mode="w") as seven_zip_file:
            seven_zip_file.writestr(arcname="test.txt", data="test1")
            seven_zip_file.writestr(arcname="test2.txt", data="test2")

        temp_zip.seek(0)

        return Response(
            temp_zip.getvalue(),
            mimetype="application/x-7z-compressed",
        )

    return Response(
        f"Document '{param}'",
        mimetype="text/plain",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
