import logging

from flask import Flask, Response, request, make_response

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

    response =  make_response(f"Document '{param}'")
    response.mimetype = "text/plain"
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
