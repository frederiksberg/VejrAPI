# VejrAPI

## Endpoints

### **/getforecast**

Wrapper for api.met.no

* **URL**

    /getforecast

* **Method**

    `GET`

* **URL Params**

    **Optional**

    `lat=[float]`

    `lon=[float]`

    `height=[integer]`

* **Success Response**

    * **Code:** 200  
      **Content:** `{"success": True, "result": [<observations>]}`

* **Error Response**

    * **Code:** 500 INTERNAL SERVER ERROR

* **Sample Call**

    ```sh
    $ curl "http://<url>/getforecast"
    ```

* **Notes**

    met.no's api only provides new data every hour. Therefore this API is backed by a redis cache, that serve consecutive calls within the same hour.