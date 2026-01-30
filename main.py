from fastapi import FastAPI


app = FastAPI(
    title="FastAPI JWT Auth Practice", 
)



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)