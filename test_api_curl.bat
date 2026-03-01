@echo off
REM Test Layer 1 preprocessing via API using cURL

echo Testing Layer 1 Preprocessing Pipeline via API
echo ================================================

REM Start the server first: uvicorn main:app --reload
REM Then run this script

echo.
echo Uploading test image...
curl -X POST "http://localhost:8000/api/upload/drawing" ^
  -H "accept: application/json" ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@test_blueprint.jpg"

echo.
echo.
echo Test complete! Check the response above.
