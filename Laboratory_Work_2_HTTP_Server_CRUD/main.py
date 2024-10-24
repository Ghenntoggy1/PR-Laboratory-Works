from fastapi import FastAPI

from router.prices import router

if __name__ == '__main__':
    app = FastAPI()
    app.include_router(router)


    @app.get('/')
    def welcome():
        return {'message': 'Welcome to my FastAPI application'}


