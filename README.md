Steps to run project

1. Clone the project
2. RUN docker-compose up --build
3. Open url http://localhost:8080/docs, it will swagger UI, you will find API's related to url shortner
4. While creating short_code, brand name can be mentioned from 3-10 chars long, if not it will generate new short_code
5. Open short_url link in new tab it will redirect to indended long URL
6. Admin route used to get all urls data and it is paginated
7. Another admin route with secret key is used to get perticular url's admin data 
